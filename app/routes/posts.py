import os
import random
import logging
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from atproto import Client

from app import config
from app import database
from app import agent
from app import security
from app.database import get_db, User, SocialAccount, PostHistory, AgentConfig, EditorialItem, check_daily_post_limit
from app.social.registry import get_social_network_client
from app.routes.dependencies import get_current_user
from app.routes.schemas import DraftRequest, PostDraftRequest, PostNowRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/history")
async def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    history_entries = db.query(PostHistory).filter(
        PostHistory.user_id == current_user.id
    ).order_by(PostHistory.timestamp.desc()).limit(100).all()
    
    res = []
    for h in history_entries:
        res.append({
            "id": h.id,
            "timestamp": h.timestamp.isoformat(),
            "status": h.status,
            "theme": h.theme,
            "tone": h.tone,
            "content": h.content,
            "uri": h.uri,
            "cid": h.cid,
            "likes": h.likes,
            "reposts": h.reposts,
            "replies": h.replies,
            "error": h.error_message,
            "quality_score": h.quality_score
        })
    return res

@router.post("/api/generate-draft")
async def generate_draft(req: DraftRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
    
    themes = []
    if config_data and config_data.themes_csv:
        themes = [t.strip() for t in config_data.themes_csv.split(",") if t.strip()]
        
    theme = req.theme or (random.choice(themes) if themes else "Geral")
    tone = req.tone or (config_data.tone if config_data else "informativo")
    sys_prompt = req.system_prompt or (config_data.system_prompt if config_data else "")
    
    try:
        content = agent.generate_post_content(theme, tone, sys_prompt, idea_text=req.idea_text, config_data=config_data)
        return {"status": "success", "theme": theme, "content": content}
    except Exception as e:
        logger.error(f"Erro ao gerar rascunho para usuário {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/post-draft")
async def post_draft(req: PostDraftRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not req.content or len(req.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="O conteúdo do post não pode estar vazio.")
    if len(req.content) > 280:
        raise HTTPException(status_code=400, detail="O conteúdo excede o limite de 280 caracteres.")
        
    if not check_daily_post_limit(db, current_user.id):
        raise HTTPException(
            status_code=400,
            detail=f"Limite diário de publicações excedido para o seu plano. Por favor, faça um upgrade para continuar publicando."
        )
        
    social_accounts_query = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_connected == True
    )
    if req.channel:
        social_accounts_query = social_accounts_query.filter(SocialAccount.platform == req.channel)
    social_accounts = social_accounts_query.all()
    
    if not social_accounts:
        raise HTTPException(status_code=400, detail="Por favor, conecte ao menos uma rede social no painel.")
        
    config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
    tone = config_data.tone if config_data else "informativo"
    
    quality_score = None
    try:
        analysis = agent.analyze_post_quality(req.content, tone, config_data=config_data)
        quality_score = analysis.get("score_geral")
    except Exception as qa_err:
        logger.error(f"Erro ao avaliar qualidade do post rascunhado: {qa_err}")

    associated_calendar_item = None
    if req.draft_id:
        associated_calendar_item = db.query(EditorialItem).filter(
            EditorialItem.post_history_id == req.draft_id
        ).first()

    errors = []
    successes = 0
    
    for account in social_accounts:
        try:
            client = get_social_network_client(account.platform, account.encrypted_credentials)
            resp = client.publish(req.content)
            database.log_successful_post(
                db,
                current_user.id,
                req.content,
                req.theme,
                tone,
                uri=resp.get("uri"),
                cid=resp.get("cid"),
                social_account_id=account.id,
                quality_score=quality_score
            )
            successes += 1
        except Exception as e:
            logger.error(f"Erro ao publicar no {account.platform}: {e}")
            errors.append(f"{account.platform}: {str(e)}")
            database.log_failed_post(db, current_user.id, f"Falha ao publicar no {account.platform}: {str(e)}", req.theme, tone)
            
    if successes == 0:
        raise HTTPException(status_code=500, detail="; ".join(errors))
        
    calendar_item = None
    if req.calendar_item_id:
        calendar_item = db.query(EditorialItem).filter(
            EditorialItem.id == req.calendar_item_id,
            EditorialItem.user_id == current_user.id
        ).first()
    elif associated_calendar_item:
        calendar_item = associated_calendar_item
        
    if calendar_item:
        latest_post = db.query(PostHistory).filter(
            PostHistory.user_id == current_user.id,
            PostHistory.status == "success"
        ).order_by(PostHistory.id.desc()).first()
        if latest_post:
            calendar_item.status = "publicado"
            calendar_item.post_history_id = latest_post.id
            db.commit()
            
    if req.draft_id:
        db.query(PostHistory).filter(
            PostHistory.id == req.draft_id,
            PostHistory.user_id == current_user.id
        ).delete()
        db.commit()
                
    return {"status": "success", "content": req.content, "theme": req.theme}

@router.post("/api/post-now")
async def post_now(req: Optional[PostNowRequest] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not check_daily_post_limit(db, current_user.id):
        raise HTTPException(
            status_code=400,
            detail=f"Limite diário de publicações excedido para o seu plano. Por favor, faça um upgrade para continuar publicando."
        )

    config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
    themes = []
    if config_data and config_data.themes_csv:
        themes = [t.strip() for t in config_data.themes_csv.split(",") if t.strip()]
        
    tone = config_data.tone if config_data else "informativo"
    system_prompt = config_data.system_prompt if config_data else ""
    
    theme = None
    if req and req.theme:
        theme = req.theme
        
    if not theme or theme == "random":
        if not themes:
            raise HTTPException(status_code=400, detail="Por favor, configure ao menos um tema no painel.")
        theme = random.choice(themes)
        
    social_accounts_query = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.is_connected == True
    )
    if req and req.channel:
        social_accounts_query = social_accounts_query.filter(SocialAccount.platform == req.channel)
    social_accounts = social_accounts_query.all()
    
    if not social_accounts:
        raise HTTPException(status_code=400, detail="Nenhuma rede social ativa conectada.")
        
    try:
        content = agent.generate_post_content(theme, tone, system_prompt, config_data=config_data)
        logger.info(f"Conteúdo gerado para postagem imediata: '{content}'")
        
        quality_score = None
        try:
            analysis = agent.analyze_post_quality(content, tone, config_data=config_data)
            quality_score = analysis.get("score_geral")
        except Exception as qa_err:
            logger.error(f"Erro ao avaliar qualidade do post imediato: {qa_err}")

        successes = 0
        errors = []
        for account in social_accounts:
            try:
                client = get_social_network_client(account.platform, account.encrypted_credentials)
                resp = client.publish(content)
                database.log_successful_post(
                    db,
                    current_user.id,
                    content,
                    theme,
                    tone,
                    uri=resp.get("uri"),
                    cid=resp.get("cid"),
                    social_account_id=account.id,
                    quality_score=quality_score
                )
                successes += 1
            except Exception as inner_err:
                errors.append(f"{account.platform}: {str(inner_err)}")
                database.log_failed_post(db, current_user.id, f"Falha no {account.platform}: {str(inner_err)}", theme, tone)
                
        if successes == 0:
            raise HTTPException(status_code=500, detail="; ".join(errors))
            
        if req and req.calendar_item_id:
            item = db.query(EditorialItem).filter(
                EditorialItem.id == req.calendar_item_id,
                EditorialItem.user_id == current_user.id
            ).first()
            if item:
                latest_post = db.query(PostHistory).filter(PostHistory.user_id == current_user.id).order_by(PostHistory.id.desc()).first()
                if latest_post:
                    item.status = "publicado"
                    item.post_history_id = latest_post.id
                    db.commit()
            
        return {"status": "success", "theme": theme, "content": content}
    except Exception as e:
        logger.error(f"Erro em publicação manual para {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/refresh-metrics")
async def refresh_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == "bluesky",
        SocialAccount.is_connected == True
    ).first()
    
    if not account:
        raise HTTPException(status_code=400, detail="Nenhuma conta ativa do Bluesky conectada.")
        
    try:
        decrypted_json_str = security.decrypt_value(account.encrypted_credentials)
        credentials = json.loads(decrypted_json_str)
        handle = credentials.get("handle")
        password = credentials.get("password")
    except Exception:
        raise HTTPException(status_code=500, detail="Falha ao decifrar credenciais da conta.")
        
    try:
        client = Client()
        client.login(handle, password)
        
        feed = client.get_author_feed(actor=handle, limit=30)
        
        history_entries = db.query(PostHistory).filter(
            PostHistory.user_id == current_user.id,
            PostHistory.status == "success"
        ).all()
        
        history_by_uri = {entry.uri: entry for entry in history_entries if entry.uri}
        
        updated_count = 0
        new_imported_count = 0
        
        if feed and feed.feed:
            for post_item in feed.feed:
                post = post_item.post
                uri = post.uri
                
                likes = post.like_count or 0
                reposts = post.repost_count or 0
                replies = post.reply_count or 0
                
                entry = history_by_uri.get(uri)
                if not entry:
                    post_text_clean = post.record.text.strip() if post.record.text else ""
                    for h_entry in history_entries:
                        h_content_clean = h_entry.content.strip() if h_entry.content else ""
                        if h_content_clean == post_text_clean and not h_entry.uri:
                            entry = h_entry
                            entry.uri = uri
                            entry.cid = post.cid
                            history_by_uri[uri] = entry
                            break
                            
                if entry:
                    entry.likes = likes
                    entry.reposts = reposts
                    entry.replies = replies
                    updated_count += 1
                else:
                    new_entry = PostHistory(
                        user_id=current_user.id,
                        social_account_id=account.id,
                        timestamp=datetime.fromisoformat(post.record.created_at.replace("Z", "+00:00")) if hasattr(post.record, "created_at") else datetime.utcnow(),
                        status="success",
                        theme="Externo",
                        tone="informativo",
                        content=post.record.text or "",
                        uri=uri,
                        cid=post.cid,
                        likes=likes,
                        reposts=reposts,
                        replies=replies
                    )
                    db.add(new_entry)
                    new_imported_count += 1

        db.commit()
        msg = f"Métricas atualizadas ({updated_count} atualizados"
        if new_imported_count > 0:
            msg += f", {new_imported_count} posts externos importados"
        msg += ")."
        
        return {"status": "success", "message": msg}
    except Exception as e:
        logger.error(f"Erro ao sincronizar métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
