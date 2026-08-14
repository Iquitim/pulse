import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, User, SocialAccount, AgentConfig
from app.routes.dependencies import get_current_user
from app.social.registry import get_social_network_client
from app import scheduler

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Status"])

@router.get("/api/status")
async def get_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.database import LLMServer
    from app.agent import test_connection
    from app.security import decrypt_value

    active_server = db.query(LLMServer).filter(
        LLMServer.user_id == current_user.id,
        LLMServer.is_active == True
    ).first()

    llm_ok = False
    llm_name = "Nenhum servidor ativo"
    if active_server:
        llm_name = f"{active_server.provider.upper()} ({active_server.model})"
        try:
            api_key = None
            if active_server.api_key_encrypted:
                api_key = decrypt_value(active_server.api_key_encrypted)
            llm_ok = test_connection(
                active_server.provider,
                active_server.model,
                active_server.base_url,
                api_key
            )
        except Exception as e:
            logger.warning(f"Falha ao checar conexão do LLM: {e}")
            llm_ok = False
    
    bsky_account = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == "bluesky",
        SocialAccount.is_connected == True
    ).first()
    
    bsky_ok = False
    bsky_handle = "Não configurado"
    if bsky_account:
        try:
            bsky_handle = bsky_account.account_handle
            client = get_social_network_client("bluesky", bsky_account.encrypted_credentials)
            bsky_ok = client.connect()
        except Exception:
            bsky_ok = False

    twitter_account = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == "twitter",
        SocialAccount.is_connected == True
    ).first()
    
    twitter_ok = False
    twitter_handle = "Não configurado"
    if twitter_account:
        try:
            twitter_handle = twitter_account.account_handle
            client = get_social_network_client("twitter", twitter_account.encrypted_credentials)
            twitter_ok = client.connect()
        except Exception:
            twitter_ok = False

    threads_account = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == "threads",
        SocialAccount.is_connected == True
    ).first()
    
    threads_ok = False
    threads_handle = "Não configurado"
    if threads_account:
        try:
            threads_handle = threads_account.account_handle
            client = get_social_network_client("threads", threads_account.encrypted_credentials)
            threads_ok = client.connect()
        except Exception:
            threads_ok = False
            
    job_id = f"posting_job_{current_user.id}"
    job = scheduler.scheduler.get_job(job_id)
    next_run = None
    if job and job.next_run_time:
        next_run = job.next_run_time.isoformat()
        
    config_data = db.query(AgentConfig).filter(AgentConfig.user_id == current_user.id).first()
    is_active = config_data.is_active if config_data else False
    scheduling_mode = config_data.scheduling_mode if config_data else "recorrente"
    
    scheduler_active = False
    if is_active:
        if scheduling_mode == "recorrente":
            scheduler_active = (job is not None)
        else:
            scheduler_active = True
            
    return {
        "gemini": {
            "connected": llm_ok,
            "name": llm_name
        },
        "bsky": {
            "connected": bsky_ok,
            "handle": bsky_handle
        },
        "twitter": {
            "connected": twitter_ok,
            "handle": twitter_handle
        },
        "threads": {
            "connected": threads_ok,
            "handle": threads_handle
        },
        "scheduler": {
            "active": scheduler_active,
            "next_run": next_run,
            "mode": scheduling_mode
        }
    }
