import logging
import json
import tweepy
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User, SocialAccount, TierConfig, log_activity, get_system_setting
from app import security, config

logger = logging.getLogger(__name__)

router = APIRouter(tags=["OAuth Twitter"])

def get_twitter_redirect_uri(request: Request, db: Session) -> str:
    custom_uri = get_system_setting(db, "twitter_redirect_uri")
    if not custom_uri:
        custom_uri = config.TWITTER_REDIRECT_URI
    if custom_uri and custom_uri.strip():
        return custom_uri.strip()
    
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/api/social/twitter/callback"

@router.get("/api/social/twitter/login")
async def twitter_login(
    handle: str,
    token: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    client_id = get_system_setting(db, "twitter_client_id") or config.TWITTER_CLIENT_ID
    client_secret = get_system_setting(db, "twitter_client_secret") or config.TWITTER_CLIENT_SECRET

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

    redirect_uri = get_twitter_redirect_uri(request, db)
    
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
        
        redirect_response = RedirectResponse(authorization_url)
        redirect_response.set_cookie(key="tw_oauth_state", value=state, httponly=True, max_age=600, samesite="lax")
        redirect_response.set_cookie(key="tw_oauth_verifier", value=code_verifier, httponly=True, max_age=600, samesite="lax")
        redirect_response.set_cookie(key="tw_oauth_handle", value=handle, httponly=True, max_age=600, samesite="lax")
        redirect_response.set_cookie(key="tw_oauth_user_id", value=str(user.id), httponly=True, max_age=600, samesite="lax")
        return redirect_response
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
        error_desc = request.query_params.get("error_description", error)
        return HTMLResponse(content=f"""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({{error: "{error_desc}"}}, "*");
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
        
    if not cookie_user_id_str or not code:
        return HTMLResponse(content="""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({error: "Sessão ou código de autorização inválido."}, "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)
        
    user_id = int(cookie_user_id_str)
    redirect_uri = get_twitter_redirect_uri(request, db)
    
    client_id = get_system_setting(db, "twitter_client_id") or config.TWITTER_CLIENT_ID
    client_secret = get_system_setting(db, "twitter_client_secret") or config.TWITTER_CLIENT_SECRET
    
    try:
        oauth2_handler = tweepy.OAuth2UserHandler(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["tweet.read", "tweet.write", "users.read", "offline.access"]
        )
        
        token_data = oauth2_handler.fetch_token(request.url._url)
        
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_at = token_data.get("expires_at")
        
        twitter_user_id = None
        username = None
        try:
            client = tweepy.Client(bearer_token=access_token)
            me = client.get_me()
            if me and me.data:
                twitter_user_id = str(me.data.id)
                username = f"@{me.data.username}"
        except Exception as e:
            logger.warning(f"Não foi possível consultar perfil do Twitter: {e}")
            
        if username:
            cookie_handle = username
            
        save_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "client_id": client_id,
            "client_secret": client_secret,
            "twitter_user_id": twitter_user_id,
            "account_handle": cookie_handle,
            "app_user_id": user_id
        }
        encrypted_creds = security.encrypt_value(json.dumps(save_data))
        
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
