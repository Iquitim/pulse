import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import tweepy
from app import config
from app import security
from app import scheduler
from app.database import get_db, User, SocialAccount, TierConfig, log_activity
from app.social.registry import get_social_network_client
from app.routes.dependencies import get_current_user
from app.routes.schemas import ConnectAccountRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/status")
async def get_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.database import LLMServer
    active_server = db.query(LLMServer).filter(
        LLMServer.user_id == current_user.id,
        LLMServer.is_active == True
    ).first()
    
    llm_ok = False
    llm_name = "Não configurado"
    
    if active_server:
        llm_name = active_server.name
        if active_server.provider == "gemini":
            if active_server.api_key_encrypted:
                llm_ok = True
        elif active_server.provider == "ollama":
            llm_ok = True
        elif active_server.provider == "openai_compatible":
            if active_server.base_url and active_server.api_key_encrypted:
                llm_ok = True
    
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
            
    job_id = f"posting_job_{current_user.id}"
    job = scheduler.scheduler.get_job(job_id)
    next_run = None
    if job and job.next_run_time:
        next_run = job.next_run_time.isoformat()
        
    from app.database import AgentConfig
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
        "scheduler": {
            "active": scheduler_active,
            "next_run": next_run,
            "mode": scheduling_mode
        }
    }

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

@router.get("/api/social/twitter/login")
async def twitter_login(
    handle: str,
    token: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    from app.database import get_system_setting
    client_id = get_system_setting(db, "twitter_client_id")
    client_secret = get_system_setting(db, "twitter_client_secret")

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=400,
            detail="A integração com o Twitter / X não foi configurada pelo administrador."
        )

    payload = security.verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Sessão inválida.")
    user_email = payload["sub"]
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inválido.")

    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/social/twitter/callback"
    
    try:
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["tweet.read", "tweet.write", "users.read", "offline.access"]
        )
        
        authorization_url = oauth2_handler.get_authorization_url()
        state = oauth2_handler.state
        code_verifier = oauth2_handler.code_verifier
        
        response.set_cookie(key="tw_oauth_state", value=state, httponly=True, max_age=600, samesite="lax")
        response.set_cookie(key="tw_oauth_verifier", value=code_verifier, httponly=True, max_age=600, samesite="lax")
        response.set_cookie(key="tw_oauth_handle", value=handle, httponly=True, max_age=600, samesite="lax")
        response.set_cookie(key="tw_oauth_user_id", value=str(user.id), httponly=True, max_age=600, samesite="lax")
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(authorization_url)
    except Exception as e:
        logger.error(f"Erro ao iniciar fluxo OAuth Twitter: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao iniciar login com Twitter: {str(e)}")

@router.get("/api/social/twitter/callback", response_class=HTMLResponse)
async def twitter_callback(
    request: Request,
    response: Response,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    if error:
        return HTMLResponse(content=f"""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({{error: "{error}"}}, "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)
        
    cookie_state = request.cookies.get("tw_oauth_state")
    cookie_verifier = request.cookies.get("tw_oauth_verifier")
    cookie_handle = request.cookies.get("tw_oauth_handle")
    cookie_user_id_str = request.cookies.get("tw_oauth_user_id")
    
    response.delete_cookie(key="tw_oauth_state")
    response.delete_cookie(key="tw_oauth_verifier")
    response.delete_cookie(key="tw_oauth_handle")
    response.delete_cookie(key="tw_oauth_user_id")
    
    if not cookie_state or not state or cookie_state != state:
        return HTMLResponse(content="""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({error: "Erro de validação de estado (CSRF). Tente novamente."}, "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)
        
    if not cookie_verifier or not cookie_user_id_str or not cookie_handle:
        return HTMLResponse(content="""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({error: "Sessão expirada. Tente novamente."}, "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)
        
    user_id = int(cookie_user_id_str)
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/social/twitter/callback"
    
    from app.database import get_system_setting
    client_id = get_system_setting(db, "twitter_client_id")
    client_secret = get_system_setting(db, "twitter_client_secret")
    
    try:
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["tweet.read", "tweet.write", "users.read", "offline.access"]
        )
        
        oauth2_handler.state = state
        oauth2_handler.code_verifier = cookie_verifier
        
        token_data = oauth2_handler.fetch_token(str(request.url))
        
        credentials_str = json.dumps(token_data)
        encrypted_creds = security.encrypt_value(credentials_str)
        
        existing = db.query(SocialAccount).filter(
            SocialAccount.user_id == user_id,
            SocialAccount.platform == "twitter",
            SocialAccount.account_handle == cookie_handle
        ).first()
        
        if existing:
            existing.encrypted_credentials = encrypted_creds
            existing.is_connected = True
        else:
            user = db.query(User).filter(User.id == user_id).first()
            connected_count = db.query(SocialAccount).filter(SocialAccount.user_id == user_id).count()
            tier_config = db.query(TierConfig).filter(TierConfig.tier_name == user.plan_tier).first()
            if tier_config and connected_count >= tier_config.max_accounts:
                return HTMLResponse(content=f"""
                    <html>
                        <body>
                            <script>
                                window.opener.postMessage({{error: "Limite de contas excedido para o plano {user.plan_tier}."}}, "*");
                                window.close();
                            </script>
                        </body>
                    </html>
                """)
                
            new_acc = SocialAccount(
                user_id=user_id,
                platform="twitter",
                account_handle=cookie_handle,
                encrypted_credentials=encrypted_creds,
                is_connected=True
            )
            db.add(new_acc)
            
        db.commit()
        log_activity(db, user_id, "connect_social_account", f"Conta {cookie_handle} conectada com sucesso no twitter via OAuth 2.0.")
        
        return HTMLResponse(content="""
            <html>
                <body>
                    <script>
                        window.opener.postMessage("twitter_connected", "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)
        
    except Exception as e:
        logger.error(f"Erro ao processar callback do Twitter: {e}")
        return HTMLResponse(content=f"""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({{error: "{str(e)}"}}, "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)

