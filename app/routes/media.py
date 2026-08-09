import os
import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db, User, MediaAsset, EditorialItem, log_activity
from app.routes.dependencies import get_current_user
from app.routes.schemas import MediaAssetResponse, AttachMediaRequest, EditorialItemResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Galeria de Mídias"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime"}
ALLOWED_MIME_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB

def _build_media_response(asset: MediaAsset) -> MediaAssetResponse:
    url = f"/uploads/user_{asset.user_id}/{asset.filename}"
    return MediaAssetResponse(
        id=asset.id,
        filename=asset.filename,
        original_name=asset.original_name,
        mime_type=asset.mime_type,
        file_size=asset.file_size,
        storage_path=asset.storage_path,
        url=url,
        created_at=asset.created_at
    )

@router.post("/api/media/upload", response_model=MediaAssetResponse, summary="Fazer Upload de Mídia", description="Envia uma imagem (JPG, PNG, GIF, WebP) ou vídeo (MP4) de até 10MB/50MB para ser anexado a postagens agendadas.")
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type or file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de arquivo não suportado ({file.content_type}). Use imagens (JPG, PNG, GIF, WebP) ou vídeo MP4."
        )

    # Read bytes to check size
    contents = await file.read()
    file_size = len(contents)
    
    max_allowed = MAX_VIDEO_SIZE if file.content_type.lower() in ALLOWED_VIDEO_TYPES else MAX_IMAGE_SIZE
    if file_size > max_allowed:
        max_mb = max_allowed // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo excede o limite máximo permitido de {max_mb} MB."
        )

    # Prepare user upload directory
    user_dir = os.path.join(UPLOADS_DIR, f"user_{current_user.id}")
    os.makedirs(user_dir, exist_ok=True)

    # Generate sanitized unique filename
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext:
        ext = ".png" if "image" in file.content_type.lower() else ".mp4"
    
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(user_dir, unique_filename)

    # Save to disk
    with open(file_path, "wb") as f:
        f.write(contents)

    rel_storage_path = os.path.join("uploads", f"user_{current_user.id}", unique_filename)

    # DB Record
    media_asset = MediaAsset(
        user_id=current_user.id,
        filename=unique_filename,
        original_name=file.filename or unique_filename,
        mime_type=file.content_type.lower(),
        file_size=file_size,
        storage_path=rel_storage_path
    )
    db.add(media_asset)
    db.commit()
    db.refresh(media_asset)

    log_activity(db, current_user.id, "upload_media", f"Upload de mídia: {media_asset.original_name} ({file_size} bytes)")
    return _build_media_response(media_asset)

@router.get("/api/media", response_model=List[MediaAssetResponse], summary="Listar Galeria de Mídias do Usuário", description="Retorna todos os arquivos de mídia (imagens e vídeos) salvos pelo usuário autenticado.")
async def get_user_media(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assets = db.query(MediaAsset).filter(MediaAsset.user_id == current_user.id).order_by(MediaAsset.created_at.desc()).all()
    return [_build_media_response(a) for a in assets]

@router.delete("/api/media/{media_id}", summary="Excluir Arquivo de Mídia", description="Remove um arquivo de mídia do banco de dados e apaga o arquivo físico do disco.")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    asset = db.query(MediaAsset).filter(MediaAsset.id == media_id, MediaAsset.user_id == current_user.id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Arquivo de mídia não encontrado.")

    # Unlink from editorial items
    items = db.query(EditorialItem).filter(EditorialItem.media_id == asset.id).all()
    for item in items:
        item.media_id = None

    # Remove file from disk if exists
    abs_path = os.path.join(BASE_DIR, asset.storage_path)
    if os.path.exists(abs_path):
        try:
            os.remove(abs_path)
        except Exception as e:
            logger.warning(f"Erro ao deletar arquivo de mídia {abs_path}: {e}")

    db.delete(asset)
    db.commit()

    log_activity(db, current_user.id, "delete_media", f"Mídia excluída ID {media_id}")
    return {"status": "success", "message": "Arquivo de mídia excluído com sucesso."}

@router.post("/api/calendar/{calendar_item_id}/media", response_model=EditorialItemResponse, summary="Anexar ou Alterar Mídia de Post Agendado", description="Permite vincular, alterar ou remover a mídia de uma postagem já existente no calendário editorial.")
async def attach_media_to_calendar_item(
    calendar_item_id: int,
    req: AttachMediaRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(EditorialItem).filter(EditorialItem.id == calendar_item_id, EditorialItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do calendário não encontrado.")

    if req.media_id:
        asset = db.query(MediaAsset).filter(MediaAsset.id == req.media_id, MediaAsset.user_id == current_user.id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Mídia informada não pertence ao usuário.")
        item.media_id = asset.id
    else:
        item.media_id = None

    db.commit()
    db.refresh(item)

    media_resp = _build_media_response(item.media) if item.media else None
    return EditorialItemResponse(
        id=item.id,
        theme=item.theme,
        scheduled_date=item.scheduled_date,
        status=item.status,
        objective=item.objective,
        cta=item.cta,
        channel=item.channel,
        is_manual=item.is_manual,
        manual_content=item.manual_content,
        post_history_id=item.post_history_id,
        media_id=item.media_id,
        media=media_resp,
        created_at=item.created_at
    )
