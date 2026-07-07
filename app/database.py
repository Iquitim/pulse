import os
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app import config

logger = logging.getLogger(__name__)

# Base directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database URL configuration
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'pulse.db')}")

# Set up engine
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Default prompt and persona constants
DEFAULT_SYSTEM_PROMPT = """Você é o Pulse, um assistente editorial inteligente que escreve posts curtos para redes sociais (como o Bluesky).

Você deve escrever incorporando a Persona fornecida.

Tarefa:
Escreva um post para o Bluesky sobre: {theme}

Tom do post:
{tone}

Regras Gerais de Escrita:
* Máximo de 280 caracteres.
* Sem hashtags.
* Sem aspas no início/fim.
* Sem introduções ou explicações ("aqui está um post...", "olá pessoal").
* Sem threads.
* Sem prometer resultados milagrosos.
* Sem inventar dados ou notícias.
* Sem exagero publicitário.
* No máximo 1 emoji, apenas se for natural.
* Use português brasileiro.
* Escreva de forma curta, fluida e com personalidade.

Estilo desejado:
* Uma reflexão curta.
* Uma observação prática.
* Um aprendizado de bastidor.
* Uma provocação leve.
* Uma pergunta que convide conversa.
* Uma frase que pareça escrita por uma pessoa real, não por uma marca.

Retorne apenas o post final, pronto para ser publicado."""

DEFAULT_PERSONA_DESCRIPTION = """Nome: Persona de Exemplo
Voz e Atitude:
* Especialista na sua área de atuação (ex: tecnologia, marketing, design).
* Gosta de falar sobre tópicos práticos do dia a dia, compartilhando aprendizados reais.
* Prefere um tom honesto, simples e útil, sem promessas milagrosas.
* Evita clichês corporativos, autoridade forçada ou linguagem artificial.
* Fala de forma natural, como uma pessoa real conversando com um colega."""

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # "admin" or "user"
    is_active = Column(Boolean, default=True)
    plan_tier = Column(String, default="free")  # "free", "pro", "desk"
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")
    agent_config = relationship("AgentConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    posts_history = relationship("PostHistory", back_populates="user", cascade="all, delete-orphan")
    editorial_items = relationship("EditorialItem", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    ideas = relationship("Idea", back_populates="user", cascade="all, delete-orphan")
    llm_servers = relationship("LLMServer", back_populates="user", cascade="all, delete-orphan")

class InviteCode(Base):
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    plan_tier = Column(String, default="free")
    max_uses = Column(Integer, default=1)
    uses_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False)  # "bluesky", "twitter", "threads"
    account_handle = Column(String, nullable=False)  # e.g. @silvano.bsky.social
    encrypted_credentials = Column(Text, nullable=False)  # encrypted credentials
    is_connected = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="social_accounts")
    posts_history = relationship("PostHistory", back_populates="social_account")

class PostHistory(Base):
    __tablename__ = "posts_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    social_account_id = Column(Integer, ForeignKey("social_accounts.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # "success", "failed", "draft"
    theme = Column(String, nullable=False)
    tone = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    uri = Column(String, nullable=True)
    cid = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    likes = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    quality_score = Column(Integer, nullable=True)
    
    user = relationship("User", back_populates="posts_history")
    social_account = relationship("SocialAccount", back_populates="posts_history")

class AgentConfig(Base):
    __tablename__ = "agent_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_active = Column(Boolean, default=False)
    requires_approval = Column(Boolean, default=False)
    interval_hours = Column(Integer, default=6)
    tone = Column(String, default="informativo")
    themes_csv = Column(Text, default="Tecnologia,Inteligência Artificial,Programação")
    system_prompt = Column(Text, default=DEFAULT_SYSTEM_PROMPT)
    persona_description = Column(Text, default=DEFAULT_PERSONA_DESCRIPTION)
    scheduling_mode = Column(String, default="recorrente")  # "recorrente" or "personalizado"
    channel = Column(String, default="bluesky")
    
    # LLM Settings
    llm_provider = Column(String, default="gemini") # "gemini", "ollama", "openai_compatible"
    llm_model = Column(String, default="gemini-2.5-flash-lite")
    llm_base_url = Column(String, nullable=True)
    llm_api_key_encrypted = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="agent_config")

class EditorialItem(Base):
    __tablename__ = "editorial_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_history_id = Column(Integer, ForeignKey("posts_history.id"), nullable=True)
    theme = Column(String, nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String, default="planejado")  # "planejado", "publicado", "falhou"
    objective = Column(Text, nullable=True)
    cta = Column(String, nullable=True)
    channel = Column(String, default="bluesky")  # "bluesky", "twitter", "threads"
    is_manual = Column(Boolean, default=False)
    manual_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="editorial_items")
    post_history = relationship("PostHistory", backref="editorial_item", uselist=False)

class TierConfig(Base):
    __tablename__ = "tier_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    tier_name = Column(String, unique=True, nullable=False)  # "free", "pro", "desk"
    max_themes = Column(Integer, default=5)
    max_accounts = Column(Integer, default=1)
    max_calendar_items = Column(Integer, default=10)
    daily_post_limit = Column(Integer, default=3)

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")

class Idea(Base):
    __tablename__ = "ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # "pending", "converted"
    channel = Column(String, default="bluesky")
    
    user = relationship("User", back_populates="ideas")

class LLMServer(Base):
    __tablename__ = "llm_servers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # "gemini", "ollama", "openai_compatible"
    model = Column(String, nullable=False)
    base_url = Column(String, nullable=True)
    api_key_encrypted = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="llm_servers")



# Context manager for DB sessions
@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# FastAPI dependency helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to initialize database tables
def init_db():
    Base.metadata.create_all(bind=engine)
    # Manual schema migration to add scheduling_mode if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN scheduling_mode VARCHAR DEFAULT 'recorrente';"))
            logger.info("Coluna 'scheduling_mode' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass
        
    # Manual schema migration to add must_change_password if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN must_change_password BOOLEAN DEFAULT 0;"))
            logger.info("Coluna 'must_change_password' adicionada com sucesso à tabela users.")
    except Exception:
        pass

    # Manual schema migration to add quality_score to posts_history if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE posts_history ADD COLUMN quality_score INTEGER;"))
            logger.info("Coluna 'quality_score' adicionada com sucesso à tabela posts_history.")
    except Exception:
        pass

    # Manual schema migration to add LLM Provider columns if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN llm_provider VARCHAR DEFAULT 'gemini';"))
            logger.info("Coluna 'llm_provider' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass

    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN llm_model VARCHAR DEFAULT 'gemini-2.5-flash-lite';"))
            logger.info("Coluna 'llm_model' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass

    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN llm_base_url VARCHAR;"))
            logger.info("Coluna 'llm_base_url' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass

    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN llm_api_key_encrypted TEXT;"))
            logger.info("Coluna 'llm_api_key_encrypted' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass

    # Manual schema migration to add persona_description if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN persona_description TEXT;"))
            logger.info("Coluna 'persona_description' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass

    # Manual schema migration to add channel if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE agent_configs ADD COLUMN channel VARCHAR DEFAULT 'bluesky';"))
            logger.info("Coluna 'channel' adicionada com sucesso à tabela agent_configs.")
    except Exception:
        pass

    # Manual schema migration to add channel to ideas table if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE ideas ADD COLUMN channel VARCHAR DEFAULT 'bluesky';"))
            logger.info("Coluna 'channel' adicionada com sucesso à tabela ideas.")
    except Exception:
        pass

    # Manual schema migration to add is_manual to editorial_calendar table if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE editorial_calendar ADD COLUMN is_manual BOOLEAN DEFAULT 0;"))
            logger.info("Coluna 'is_manual' adicionada com sucesso à tabela editorial_calendar.")
    except Exception:
        pass

    # Manual schema migration to add manual_content to editorial_calendar table if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE editorial_calendar ADD COLUMN manual_content TEXT;"))
            logger.info("Coluna 'manual_content' adicionada com sucesso à tabela editorial_calendar.")
    except Exception:
        pass

    # Migrate any existing Silvano-themed prompts to the new generic system defaults
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "UPDATE agent_configs "
                "SET system_prompt = :new_prompt, persona_description = :new_persona "
                "WHERE system_prompt LIKE '%Silvano Lima de Barros%' "
                "   OR system_prompt LIKE '%Silvano%';"
            ), {"new_prompt": DEFAULT_SYSTEM_PROMPT, "new_persona": DEFAULT_PERSONA_DESCRIPTION})
            logger.info("Configurações legadas contendo 'Silvano' migradas para o padrão genérico.")
    except Exception as e:
        logger.error(f"Erro ao migrar dados de prompt antigos: {e}")

    logger.info("Banco de dados inicializado com sucesso.")

# Markdown exporter
def save_post_to_markdown(content: str, theme: str, tone: str, user_id: Optional[int] = None):
    try:
        posts_dir = os.path.join(BASE_DIR, "posts")
        os.makedirs(posts_dir, exist_ok=True)
        
        safe_theme = "".join([c for c in theme if c.isalnum() or c in (" ", "_", "-")]).strip().replace(" ", "_")
        if not safe_theme:
            safe_theme = "geral"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(posts_dir, f"post_{timestamp}_{safe_theme}.md")
        
        active_model = "Desconhecido"
        if user_id:
            try:
                # Local import to prevent circular dependencies
                from app.database import get_db_session, LLMServer
                with get_db_session() as db_sess:
                    active_server = db_sess.query(LLMServer).filter(
                        LLMServer.user_id == user_id,
                        LLMServer.is_active == True
                    ).first()
                    if active_server:
                        active_model = f"{active_server.provider.upper()} ({active_server.model})"
            except Exception as inner_e:
                logger.error(f"Erro ao buscar modelo ativo para markdown: {inner_e}")

        md_content = f"""# Post Publicado

**Data/Hora:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
**Rede Social:** Bluesky
**Tema:** {theme}
**Tom:** {tone}

## Conteúdo do Post

```text
{content}
```

---
*Gerado por Pulse Agent usando {active_model}*
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        logger.info(f"Post salvo em arquivo markdown: {filename}")
    except Exception as e:
        logger.error(f"Erro ao salvar post em markdown: {e}")

# Helper log functions to replace legacy ones
def log_activity(db, user_id: int, action: str, details: Optional[str] = None):
    try:
        new_log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()
        logger.info(f"Atividade registrada: {action} para usuário {user_id}")
    except Exception as e:
        logger.error(f"Erro ao registrar log de auditoria: {e}")

def log_draft_post(db, user_id: int, content: str, theme: str, tone: str = "informativo"):
    new_entry = PostHistory(
        user_id=user_id,
        status="draft",
        theme=theme,
        tone=tone,
        content=content
    )
    db.add(new_entry)
    db.commit()
    log_activity(db, user_id, "post_draft_created", f"Rascunho criado. Tema: {theme}")

def log_successful_post(db, user_id: int, content: str, theme: str, tone: str, uri: Optional[str] = None, cid: Optional[str] = None, social_account_id: Optional[int] = None, quality_score: Optional[int] = None):
    new_entry = PostHistory(
        user_id=user_id,
        social_account_id=social_account_id,
        status="success",
        theme=theme,
        tone=tone,
        content=content,
        uri=uri,
        cid=cid,
        quality_score=quality_score
    )
    db.add(new_entry)
    db.commit()
    
    # Save post as Markdown file
    save_post_to_markdown(content, theme, tone, user_id=user_id)
    log_activity(db, user_id, "post_published", f"Post publicado com sucesso. Tema: {theme}")

def log_failed_post(db, user_id: int, error_msg: str, theme: str, tone: str = "informativo"):
    new_entry = PostHistory(
        user_id=user_id,
        status="failed",
        theme=theme,
        tone=tone,
        content="",
        error_message=error_msg
    )
    db.add(new_entry)
    db.commit()
    log_activity(db, user_id, "post_failed", f"Falha na publicação do post. Erro: {error_msg[:100]}")

def check_daily_post_limit(db, user_id: int) -> bool:
    from datetime import timedelta
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return True
    
    tier_config = db.query(TierConfig).filter(TierConfig.tier_name == user.plan_tier).first()
    if not tier_config:
        return True
        
    limit = tier_config.daily_post_limit
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    posts_last_24h = db.query(PostHistory).filter(
        PostHistory.user_id == user.id,
        PostHistory.status == "success",
        PostHistory.timestamp >= time_threshold
    ).count()
    return posts_last_24h < limit


def get_system_setting(db, key: str, env_name: str = None, default: str = None) -> str:
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting and setting.value:
            try:
                from app import security
                return security.decrypt_value(setting.value)
            except Exception:
                return setting.value
    except Exception:
        pass
    if env_name:
        import os
        return os.getenv(env_name, default)
    return default



