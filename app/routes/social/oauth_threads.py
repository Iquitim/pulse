import logging
import json
import time
import requests
import secrets
import urllib.parse
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db, User, SocialAccount, TierConfig, log_activity, get_system_setting
from app import security, config

logger = logging.getLogger(__name__)

router = APIRouter(tags=["OAuth Threads"])

def get_threads_redirect_uri(request: Request, db: Session) -> str:
    custom_uri = get_system_setting(db, "threads_redirect_uri")
    if not custom_uri:
        custom_uri = config.THREADS_REDIRECT_URI
    if custom_uri and custom_uri.strip():
        return custom_uri.strip()
    
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/api/social/threads/callback"

@router.get("/api/social/threads/login")
async def threads_login(
    token: str,
    request: Request,
    response: Response,
    handle: str = "",
    db: Session = Depends(get_db)
):
    app_id = get_system_setting(db, "threads_app_id") or config.THREADS_APP_ID
    app_secret = get_system_setting(db, "threads_app_secret") or config.THREADS_APP_SECRET

    if not app_id or not app_secret:
        raise HTTPException(
            status_code=400,
            detail="A integração com o Threads (Meta) não foi configurada pelo administrador."
        )

    payload = security.verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Sessão inválida.")
    user_email = payload["sub"]
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inválido.")

    redirect_uri = get_threads_redirect_uri(request, db)
    state = secrets.token_urlsafe(24)

    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": "threads_basic,threads_content_publish",
        "response_type": "code",
        "state": state
    }
    auth_url = f"https://threads.net/oauth/authorize?{urllib.parse.urlencode(params)}"
    
    redirect_resp = RedirectResponse(auth_url)
    redirect_resp.set_cookie(key="th_oauth_state", value=state, httponly=True, max_age=600, samesite="lax")
    redirect_resp.set_cookie(key="th_oauth_user_id", value=str(user.id), httponly=True, max_age=600, samesite="lax")
    if handle:
        redirect_resp.set_cookie(key="th_oauth_handle", value=handle, httponly=True, max_age=600, samesite="lax")
    return redirect_resp

@router.get("/api/social/threads/callback", response_class=HTMLResponse)
async def threads_callback(
    request: Request,
    response: Response,
    code: str = None,
    state: str = None,
    error: str = None,
    error_reason: str = None,
    error_description: str = None,
    db: Session = Depends(get_db)
):
    if error:
        err_msg = error_description or error_reason or error
        return HTMLResponse(content=f"""
            <html>
                <body>
                    <script>
                        window.opener.postMessage({{error: "{err_msg}"}}, "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)

    cookie_state = request.cookies.get("th_oauth_state")
    cookie_user_id_str = request.cookies.get("th_oauth_user_id")
    cookie_handle = request.cookies.get("th_oauth_handle")

    response.delete_cookie(key="th_oauth_state")
    response.delete_cookie(key="th_oauth_user_id")
    response.delete_cookie(key="th_oauth_handle")

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
    redirect_uri = get_threads_redirect_uri(request, db)

    app_id = get_system_setting(db, "threads_app_id") or config.THREADS_APP_ID
    app_secret = get_system_setting(db, "threads_app_secret") or config.THREADS_APP_SECRET

    try:
        # 1. Troca de code por Short-Lived Access Token
        token_url = "https://graph.threads.net/oauth/access_token"
        token_payload = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code
        }
        res = requests.post(token_url, data=token_payload, timeout=15)
        if res.status_code != 200:
            raise Exception(f"Erro ao obter token do Threads ({res.status_code}): {res.text}")
            
        short_token_data = res.json()
        short_token = short_token_data.get("access_token")
        threads_user_id = short_token_data.get("user_id")

        if not short_token:
            raise Exception("Token de acesso não retornado pelo Threads.")

        # 2. Troca de Short-Lived Token por Long-Lived Token (60 dias)
        exchange_url = "https://graph.threads.net/access_token"
        exchange_params = {
            "grant_type": "th_exchange_token",
            "client_secret": app_secret,
            "access_token": short_token
        }
        ex_res = requests.get(exchange_url, params=exchange_params, timeout=15)
        if ex_res.status_code == 200:
            long_token_data = ex_res.json()
            access_token = long_token_data.get("access_token", short_token)
            expires_in = long_token_data.get("expires_in", 5184000)
        else:
            access_token = short_token
            expires_in = 5184000

        # 3. Consulta informações do perfil
        profile_url = "https://graph.threads.net/v1.0/me"
        prof_res = requests.get(profile_url, params={"fields": "id,username,name", "access_token": access_token}, timeout=10)
        username = None
        if prof_res.status_code == 200:
            prof_data = prof_res.json()
            username = prof_data.get("username")
            threads_user_id = prof_data.get("id", threads_user_id)

        handle = f"@{username}" if username else (cookie_handle or f"threads_user_{threads_user_id}")

        save_data = {
            "access_token": access_token,
            "user_id": str(threads_user_id),
            "account_handle": handle,
            "expires_at": time.time() + expires_in,
            "app_user_id": user_id
        }
        encrypted_creds = security.encrypt_value(json.dumps(save_data))

        existing = db.query(SocialAccount).filter(
            SocialAccount.user_id == user_id,
            SocialAccount.platform == "threads",
            SocialAccount.account_handle == handle
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
                platform="threads",
                account_handle=handle,
                encrypted_credentials=encrypted_creds,
                is_connected=True
            )
            db.add(new_acc)

        db.commit()
        log_activity(db, user_id, "connect_social_account", f"Conta {handle} conectada com sucesso no Threads via OAuth 2.0.")

        return HTMLResponse(content="""
            <html>
                <body>
                    <script>
                        window.opener.postMessage("threads_connected", "*");
                        window.close();
                    </script>
                </body>
            </html>
        """)

    except Exception as e:
        logger.error(f"Erro ao processar callback do Threads: {e}")
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
