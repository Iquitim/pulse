import logging
import time
import requests
import json
from app.social.base import BaseSocialNetwork
from app import security

logger = logging.getLogger(__name__)

THREADS_GRAPH_BASE_URL = "https://graph.threads.net/v1.0"
THREADS_GRAPH_AUTH_URL = "https://graph.threads.net"

class ThreadsNetwork(BaseSocialNetwork):
    def __init__(self, credentials: dict):
        self.credentials = credentials or {}
        self.access_token = self.credentials.get("access_token")
        self.user_id = self.credentials.get("user_id")
        self.account_handle = self.credentials.get("account_handle", "")
        self.expires_at = self.credentials.get("expires_at")
        self.app_user_id = self.credentials.get("app_user_id")

    def connect(self) -> bool:
        if not self.access_token:
            logger.error("Token de acesso do Threads ausente.")
            return False

        # Verifica se o token expira nos próximos 5 dias (432.000 segundos) e tenta renovar
        if self.expires_at and (time.time() >= (self.expires_at - 432000)):
            try:
                self.refresh_token()
            except Exception as e:
                logger.warning(f"Não foi possível renovar o token do Threads: {e}")

        # Valida a credencial e obtém dados atualizados do perfil
        try:
            url = f"{THREADS_GRAPH_BASE_URL}/me"
            params = {
                "fields": "id,username,name,threads_profile_picture_url",
                "access_token": self.access_token
            }
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if not self.user_id:
                    self.user_id = data.get("id")
                if not self.account_handle and data.get("username"):
                    uname = data.get("username")
                    self.account_handle = f"@{uname}" if not uname.startswith("@") else uname
                logger.info(f"Conexão do Threads válida para {self.account_handle or self.user_id}")
                return True
            else:
                logger.error(f"Falha ao validar token do Threads ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao validar conexão com Threads: {e}")
            return False

    def check_connection(self) -> bool:
        return self.connect()

    def refresh_token(self) -> bool:
        """
        Renova o token de longa duração (Long-Lived Token) do Threads por mais 60 dias.
        """
        from app.database import get_db_session, SocialAccount
        
        logger.info(f"Renovando Long-Lived Token do Threads para @{self.account_handle or self.user_id}")
        url = f"{THREADS_GRAPH_AUTH_URL}/refresh_access_token"
        params = {
            "grant_type": "th_refresh_token",
            "access_token": self.access_token
        }
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            raise Exception(f"Falha na renovação do token do Threads ({res.status_code}): {res.text}")
            
        data = res.json()
        self.access_token = data.get("access_token", self.access_token)
        expires_in = data.get("expires_in", 5184000)  # Padrão de 60 dias
        self.expires_at = time.time() + expires_in
        
        # Persiste o novo token atualizado no banco de dados
        if self.app_user_id and self.account_handle:
            with get_db_session() as db:
                save_data = {
                    "access_token": self.access_token,
                    "user_id": self.user_id,
                    "account_handle": self.account_handle,
                    "expires_at": self.expires_at,
                    "app_user_id": self.app_user_id
                }
                encrypted_creds = security.encrypt_value(json.dumps(save_data))
                acc = db.query(SocialAccount).filter(
                    SocialAccount.user_id == self.app_user_id,
                    SocialAccount.platform == "threads",
                    SocialAccount.account_handle == self.account_handle
                ).first()
                if acc:
                    acc.encrypted_credentials = encrypted_creds
                    db.commit()
                    logger.info(f"Token do Threads atualizado e salvo no banco para @{self.account_handle}")
        return True

    def publish(self, content: str) -> dict:
        """
        Publica um post de texto no Threads seguindo o fluxo de duas etapas (Container + Publish).
        """
        # Garante que a conexão e o user_id estão estabelecidos
        if not self.connect() or not self.user_id:
            raise Exception("Não foi possível conectar à conta do Threads para publicação.")

        try:
            # Etapa 1: Criação do Container de Mídia / Texto
            create_url = f"{THREADS_GRAPH_BASE_URL}/{self.user_id}/threads"
            create_payload = {
                "media_type": "TEXT",
                "text": content,
                "access_token": self.access_token
            }
            create_res = requests.post(create_url, data=create_payload, timeout=15)
            if create_res.status_code != 200:
                raise Exception(f"Erro ao criar container no Threads ({create_res.status_code}): {create_res.text}")
                
            creation_data = create_res.json()
            creation_id = creation_data.get("id")
            if not creation_id:
                raise Exception(f"ID do container não retornado pelo Threads: {create_res.text}")

            # Etapa 2: Publicação do Container
            publish_url = f"{THREADS_GRAPH_BASE_URL}/{self.user_id}/threads_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            publish_res = requests.post(publish_url, data=publish_payload, timeout=15)
            if publish_res.status_code != 200:
                raise Exception(f"Erro ao publicar container no Threads ({publish_res.status_code}): {publish_res.text}")

            publish_data = publish_res.json()
            post_id = publish_data.get("id")

            # Monta a URL pública do post
            clean_handle = self.account_handle.lstrip('@')
            if clean_handle and post_id:
                post_url = f"https://www.threads.net/@{clean_handle}/post/{post_id}"
            elif post_id:
                post_url = f"https://threads.net/t/{post_id}"
            else:
                post_url = None

            logger.info(f"Post no Threads publicado com sucesso! URL: {post_url}")
            return {
                "status": "success",
                "uri": post_url,
                "cid": str(post_id) if post_id else None
            }
        except Exception as e:
            logger.error(f"Erro ao publicar no Threads (@{self.account_handle or self.user_id}): {e}")
            raise e
