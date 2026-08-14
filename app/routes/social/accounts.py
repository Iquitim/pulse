import logging
import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db, User, SocialAccount, TierConfig, log_activity
from app.routes.dependencies import get_current_user
from app.routes.schemas import ConnectAccountRequest
from app.social.registry import get_social_network_client
from app import security

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Contas Sociais"])

@router.get("/api/social-accounts")
async def get_social_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = db.query(SocialAccount).filter(SocialAccount.user_id == current_user.id).all()
    return [
        {
            "id": a.id,
            "platform": a.platform,
            "account_handle": a.account_handle,
            "is_connected": a.is_connected,
            "created_at": a.created_at.isoformat()
        } for a in accounts
    ]

@router.post("/api/social-accounts")
async def connect_social_account(req: ConnectAccountRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.platform not in ("bluesky", "twitter", "threads"):
        raise HTTPException(status_code=400, detail="Plataforma não suportada.")
        
    try:
        credentials_str = json.dumps(req.credentials)
        encrypted_creds = security.encrypt_value(credentials_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")
        
    try:
        client = get_social_network_client(req.platform, encrypted_creds)
        connected = client.connect()
        if not connected:
            raise HTTPException(status_code=400, detail="Não foi possível conectar com as credenciais fornecidas.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro de conexão: {str(e)}")
        
    existing = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == req.platform,
        SocialAccount.account_handle == req.account_handle
    ).first()
    
    if existing:
        existing.encrypted_credentials = encrypted_creds
        existing.is_connected = True
    else:
        connected_count = db.query(SocialAccount).filter(SocialAccount.user_id == current_user.id).count()
        tier_config = db.query(TierConfig).filter(TierConfig.tier_name == current_user.plan_tier).first()
        if tier_config and connected_count >= tier_config.max_accounts:
            raise HTTPException(
                status_code=400,
                detail=f"Limite de contas conectadas excedido para o plano {current_user.plan_tier}. Máximo de {tier_config.max_accounts} contas permitidas."
            )
            
        existing = SocialAccount(
            user_id=current_user.id,
            platform=req.platform,
            account_handle=req.account_handle,
            encrypted_credentials=encrypted_creds,
            is_connected=True
        )
        db.add(existing)
        
    db.commit()
    log_activity(db, current_user.id, "connect_social_account", f"Conta {req.account_handle} conectada com sucesso no {req.platform}.")
    return {"status": "success", "message": f"Conta {req.account_handle} no {req.platform} conectada com sucesso."}

@router.delete("/api/social-accounts/{id}")
async def disconnect_social_account(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(SocialAccount).filter(
        SocialAccount.id == id,
        SocialAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Conta de rede social não encontrada.")
        
    platform = account.platform
    handle = account.account_handle
    db.delete(account)
    db.commit()
    log_activity(db, current_user.id, "disconnect_social_account", f"Conta {handle} desconectada do {platform}.")
    return {"status": "success", "message": "Conta desconectada com sucesso."}
