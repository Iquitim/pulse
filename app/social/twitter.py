import logging
import time
import requests
import base64
import json
import tweepy
from app.social.base import BaseSocialNetwork
from app import config, security

logger = logging.getLogger(__name__)

class TwitterNetwork(BaseSocialNetwork):
    def __init__(self, credentials: dict):
        self.credentials = credentials
        # Chaves de Desenvolvedor (OAuth 1.0a)
        self.api_key = credentials.get("api_key")
        self.api_secret = credentials.get("api_secret")
        self.access_token = credentials.get("access_token")
        self.access_token_secret = credentials.get("access_token_secret")
        
        # OAuth 2.0
        self.refresh_token = credentials.get("refresh_token")
        self.expires_at = credentials.get("expires_at")
        self.user_id = credentials.get("user_id")
        self.account_handle = credentials.get("account_handle")
        
        # Define o modo com base na presença de chaves de API manuais
        self.is_oauth2 = "api_key" not in credentials or not credentials.get("api_key")

    def connect(self) -> bool:
        if self.is_oauth2:
            if not self.access_token:
                logger.error("Token de acesso do Twitter OAuth 2.0 ausente.")
                return False

            # Verifica se o token expirou ou expira nos próximos 60 segundos
            if not self.expires_at or time.time() >= (self.expires_at - 60):
                if self.refresh_token:
                    try:
                        self.refresh_oauth_token()
                    except Exception as e:
                        logger.error(f"Erro ao atualizar token do Twitter OAuth 2.0: {e}")
                        return False
                else:
                    logger.error("Token do Twitter expirado e nenhum refresh_token disponível.")
                    return False

            # Valida a credencial realizando uma chamada simples ao perfil do usuário
            try:
                client = tweepy.Client(bearer_token=self.access_token)
                me = client.get_me()
                if me and me.data:
                    logger.info(f"Conexão do Twitter OAuth 2.0 válida para: @{me.data.username}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Erro ao validar conexão com o Twitter OAuth 2.0: {e}")
                return False
        else:
            # Chaves de Desenvolvedor (OAuth 1.0a)
            if not self.api_key or not self.api_secret or not self.access_token or not self.access_token_secret:
                logger.error("Chaves de desenvolvedor do Twitter (OAuth 1.0a) incompletas.")
                return False
            try:
                client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
                me = client.get_me()
                if me and me.data:
                    logger.info(f"Conexão do Twitter (Chaves Dev) válida para: @{me.data.username}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Erro ao validar chaves de desenvolvedor do Twitter (OAuth 1.0a): {e}")
                return False

    def check_connection(self) -> bool:
        return self.connect()

    def refresh_oauth_token(self):
        from app.database import get_db_session, SocialAccount, get_system_setting
        
        logger.info(f"Atualizando token do Twitter para: {self.account_handle}")
        
        with get_db_session() as db:
            client_id = get_system_setting(db, "twitter_client_id")
            client_secret = get_system_setting(db, "twitter_client_secret")
            
            if not client_id:
                raise Exception("Cannot refresh Twitter token: Client ID is not configured.")
                
            url = "https://api.twitter.com/2/oauth2/token"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": client_id
            }
            
            if client_secret:
                auth_str = f"{client_id}:{client_secret}"
                b64_auth = base64.b64encode(auth_str.encode()).decode()
                headers["Authorization"] = f"Basic {b64_auth}"
                
            res = requests.post(url, headers=headers, data=data)
            if res.status_code != 200:
                raise Exception(f"Twitter token refresh failed ({res.status_code}): {res.text}")
                
            token_data = res.json()
            
            # Atualiza atributos locais
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            
            expires_in = token_data.get("expires_in", 7200)
            self.expires_at = time.time() + expires_in
            
            # Salva o novo token atualizado no banco de dados de forma criptografada
            if self.user_id and self.account_handle:
                save_data = {
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "expires_at": self.expires_at,
                    "user_id": self.user_id,
                    "account_handle": self.account_handle,
                    "token_type": token_data.get("token_type"),
                    "scope": token_data.get("scope")
                }
                
                credentials_str = json.dumps(save_data)
                encrypted_creds = security.encrypt_value(credentials_str)
                
                acc = db.query(SocialAccount).filter(
                    SocialAccount.user_id == self.user_id,
                    SocialAccount.platform == "twitter",
                    SocialAccount.account_handle == self.account_handle
                ).first()
                if acc:
                    acc.encrypted_credentials = encrypted_creds
                    db.commit()
                    logger.info(f"Token do Twitter OAuth 2.0 atualizado e persistido com sucesso para {self.account_handle}")

    def publish(self, content: str) -> dict:
        # Garante que as credenciais estejam válidas
        self.connect()
        
        try:
            if self.is_oauth2:
                client = tweepy.Client(bearer_token=self.access_token)
            else:
                client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
                
            result = client.create_tweet(text=content)
            
            tweet_id = None
            if result and hasattr(result, "data") and result.data:
                tweet_id = result.data.get("id")
            
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}" if tweet_id else None
            
            logger.info(f"Tweet publicado com sucesso! URL: {tweet_url}")
            return {
                "status": "success",
                "uri": tweet_url,
                "cid": str(tweet_id) if tweet_id else None
            }
        except Exception as e:
            logger.error(f"Erro ao publicar no Twitter/X (@{self.account_handle or 'Manual'}): {e}")
            raise e
