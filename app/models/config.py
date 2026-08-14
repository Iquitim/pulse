from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

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
