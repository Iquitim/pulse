import os
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import config

# Re-export all models from app.models for seamless backward compatibility
from app.models import (
    Base,
    User,
    InviteCode,
    AuditLog,
    SocialAccount,
    MediaAsset,
    PostHistory,
    EditorialItem,
    Idea,
    AgentConfig,
    LLMServer,
    TierConfig,
    SystemSetting,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_PERSONA_DESCRIPTION
)

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

# Helper function to initialize database tables and apply schema migrations
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

    # Manual schema migration to add media_id to editorial_calendar if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE editorial_calendar ADD COLUMN media_id INTEGER REFERENCES media_assets(id);"))
            logger.info("Coluna 'media_id' adicionada com sucesso à tabela editorial_calendar.")
    except Exception:
        pass

    # Manual schema migration to add media_id to posts_history if not present
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE posts_history ADD COLUMN media_id INTEGER REFERENCES media_assets(id);"))
            logger.info("Coluna 'media_id' adicionada com sucesso à tabela posts_history.")
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

# Helper activity and audit log functions
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
