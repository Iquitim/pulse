import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app import config
from app import database
from app.routes import router as api_router
from app.scheduler import scheduler, sync_scheduler

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando AetherPost Backend (lifespan startup)...")
    
    # Verificação de Chaves Padrão de Desenvolvimento (Inseguras)
    from app.security import JWT_SECRET_KEY, ENCRYPTION_KEY
    if JWT_SECRET_KEY == "pulse-default-jwt-secret-key-32-chars-long-minimum-!!":
        logger.warning("\n" + "!"*80)
        logger.warning("⚠️ CRITICAL SECURITY WARNING: JWT_SECRET_KEY is using the default insecure value!")
        logger.warning("You MUST set a unique JWT_SECRET_KEY in your .env file for production.")
        logger.warning("!"*80 + "\n")
        
    if ENCRYPTION_KEY == "nSo9pQzaOxO8UR5HjnoPj8Tbgno7FGDj6I3a9T9nPss=":
        logger.warning("\n" + "!"*80)
        logger.warning("⚠️ CRITICAL SECURITY WARNING: ENCRYPTION_KEY is using the default development key!")
        logger.warning("You MUST set a unique base64 Fernet ENCRYPTION_KEY in your .env file for production.")
        logger.warning("!"*80 + "\n")

    # Inicializa as tabelas do banco de dados SQL
    database.init_db()
    
    # Semeia configurações de planos padrão (TierConfig) se a tabela estiver vazia
    from app.database import get_db_session, TierConfig, User, InviteCode, AgentConfig
    with get_db_session() as db:
        tier_count = db.query(TierConfig).count()
        if tier_count == 0:
            logger.info("Nenhuma configuração de tier encontrada. Semeando planos padrão...")
            free_tier = TierConfig(
                tier_name="free",
                max_themes=3,
                max_accounts=1,
                max_calendar_items=5,
                daily_post_limit=2
            )
            pro_tier = TierConfig(
                tier_name="pro",
                max_themes=15,
                max_accounts=3,
                max_calendar_items=50,
                daily_post_limit=10
            )
            desk_tier = TierConfig(
                tier_name="desk",
                max_themes=100,
                max_accounts=10,
                max_calendar_items=1000,
                daily_post_limit=50
            )
            db.add_all([free_tier, pro_tier, desk_tier])
            db.commit()
            logger.info("Planos padrão semeados com sucesso (free, pro, desk).")
    
    # Cria usuário administrador e código de convite mestre padrão caso o banco esteja zerado
    from app.database import get_db_session, User, InviteCode, AgentConfig
    from app.security import hash_password
    import secrets
    with get_db_session() as db:
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count == 0:
            logger.info("Nenhum usuário administrador encontrado. Criando admin padrão...")
            
            # Credenciais padrões para o open-source
            raw_password = "admin123"
            raw_invite = "PULSE-OPEN-SOURCE"
            
            admin_pwd = hash_password(raw_password)
            admin_user = User(
                email="admin@pulse.com",
                hashed_password=admin_pwd,
                role="admin",
                plan_tier="desk",
                must_change_password=False
            )
            db.add(admin_user)
            db.flush()
            
            admin_config = AgentConfig(
                user_id=admin_user.id,
                is_active=False,
                requires_approval=False,
                interval_hours=6,
                tone="informativo"
            )
            db.add(admin_config)
            
            default_code = InviteCode(
                code=raw_invite,
                plan_tier="desk",
                max_uses=100
            )
            db.add(default_code)
            db.commit()
            
            # Print em destaque no terminal
            print("\n" + "="*80)
            print("🚀 CREDENCIAIS DO ADMINISTRADOR PADRÃO DO PULSE 🚀")
            print(f" E-mail: admin@pulse.com")
            print(f" Senha:  {raw_password}")
            print(f" Código de Convite da Instância: {raw_invite}")
            print(" Altere a senha padrão após acessar as Configurações por segurança.")
            print("="*80 + "\n")
            
            logger.info(f"🔑 Admin padrão criado: admin@pulse.com / Senha: {raw_password}")
            logger.info(f"🔑 Código de convite padrão gerado: {raw_invite}")

    # Inicia o scheduler
    scheduler.start()
    # Sincroniza os jobs agendados ativos
    sync_scheduler()
    yield
    logger.info("Finalizando Pulse Backend (lifespan shutdown)...")
    # Graceful shutdown of scheduler
    scheduler.shutdown()

API_DESCRIPTION = """
## ⚡ Pulse — Agente Editorial Autônomo & Multiusuário

Bem-vindo à documentação oficial da API do **Pulse**! Esta API RESTful gerencia a criação, revisão, agendamento e publicação automatizada de conteúdo multiplataforma (**Bluesky** e **Twitter/X**) utilizando modelos de Inteligência Artificial (**Ollama local**, **Google Gemini** e APIs compatíveis com **OpenAI**).

---

### 📖 Dicionário de Termos do Pulse

| Termo | Definição no Ecossistema Pulse |
|---|---|
| **Agente Editorial** | O robô inteligente configurado por usuário responsável por ler diretrizes, gerar textos e agendar postagens. |
| **Tema (Theme)** | Assunto ou tópico de discussão cadastrado pelo usuário (ex: *Programação, IA, Bastidores*) utilizado pelo agente para gerar publicações. |
| **Persona** | A descrição da personalidade, tom de voz e biografia do autor (ex: *Desenvolvedor sênior conciso e bem-humorado*) que orienta a escrita da IA. |
| **Rascunho (Draft)** | Conteúdo gerado pela IA ou redigido manualmente aguardando aprovação ou agendamento antes da publicação final. |
| **Plano / Cota (Plan Tier)** | O nível de recurso do usuário (`free`, `pro`, `desk`) que estabelece limites diários de postagens, número de temas e conexões. |
| **App Password** | Senha de aplicativo gerada nas configurações do Bluesky para permitir a conexão segura via protocolo **ATProto** sem expor a senha principal. |
| **Score de Qualidade** | Indicador métrico de 0 a 100 calculado por regex e LLM que avalia a especificidade do texto e previne clichês típicos de IA. |
| **Modo Recorrente vs. Personalizado** | **Recorrente**: disparo automático a cada X horas selecionando temas aleatórios. **Personalizado**: agendamento em datas e horários específicos no mural. |

---

### ⚠️ Dicionário de Erros e Códigos HTTP

| Código | Significado | Causa Comum no Pulse |
|---|---|---|
| **`200 OK`** | Sucesso | Requisição processada com êxito. |
| **`400 Bad Request`** | Dados Inválidos | Limite do plano excedido, data agendada no passado, e-mail duplicado ou código de convite inválido. |
| **`401 Unauthorized`** | Não Autorizado | Token JWT ausente, expirado ou credenciais de e-mail/senha incorretas. |
| **`403 Forbidden`** | Acesso Negado | Usuário tentando acessar rotas administrativas (`/api/admin/*`) sem permissão ou com troca de senha obrigatória pendente. |
| **`404 Not Found`** | Recurso Não Encontrado | O Servidor LLM, post, item do calendário ou usuário informado não existe no banco de dados. |
| **`422 Unprocessable Entity`** | Erro de Validação | Um ou mais campos obrigatórios faltam no corpo JSON ou possuem tipos de dados incompatíveis. |
| **`500 Internal Error`** | Erro de Servidor | Falha inesperada ao conectar com serviços externos de IA ou APIs das redes sociais. |

---

### 🔐 Guia Rápido de Autenticação no Swagger UI
1. Expanda a seção **🔐 Autenticação** e execute o endpoint `POST /api/auth/login`.
2. Copie o `access_token` retornado no corpo da resposta.
3. Clique no botão **🔓 Authorize** no topo desta página, cole o token no campo de texto e confirme.
4. Agora todas as requisições enviadas pela documentação estarão autenticadas automaticamente!
"""

openapi_tags = [
    {
        "name": "🔐 Autenticação",
        "description": "Endpoints para login, registro de usuários, dados da sessão (/me) e alteração de senha."
    },
    {
        "name": "🤖 Servidores LLM",
        "description": "Configurações de agentes de IA, Prompts, Personas e CRUD de servidores de IA (Ollama, Gemini, OpenAI)."
    },
    {
        "name": "📝 Postagens & Qualidade",
        "description": "Geração de rascunhos com IA, histórico de publicações, avaliação de qualidade e sincronização de métricas."
    },
    {
        "name": "📅 Calendário Editorial",
        "description": "Agendamento de posts no mural interativo, edição de datas/horários e alternância entre Modo IA e Modo Manual."
    },
    {
        "name": "💡 Banco de Ideias",
        "description": "Captura de ideias brutas, conversão de pensamentos em rascunhos e geração de insights analíticos."
    },
    {
        "name": "🌐 Redes Sociais",
        "description": "Vinculação de contas do Bluesky (ATProto), Twitter/X (OAuth 2.0 / API Keys) e Threads (Meta)."
    },
    {
        "name": "🦙 Gerenciamento Ollama",
        "description": "Ferramenta integrada de download, status e diagnósticos de hardware para o Ollama local."
    },
    {
        "name": "⚡ Administração & Cotas",
        "description": "Endpoints restritos a administradores para controle de usuários, planos de cotas, códigos de convite e logs de auditoria."
    }
]

app = FastAPI(
    title="Pulse API — Agente Editorial Autônomo",
    description=API_DESCRIPTION,
    version="1.0.0",
    openapi_tags=openapi_tags,
    contact={
        "name": "Pulse Open Source Project",
        "url": "https://github.com/Iquitim/pulse",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    swagger_ui_parameters={
        "docExpansion": "list",
        "filter": True,
        "syntaxHighlight.theme": "monokai"
    },
    lifespan=lifespan
)

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routes from the routes module
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Iniciando servidor Pulse em http://{config.HOST}:{config.PORT}")
    uvicorn.run(app, host=config.HOST, port=config.PORT)


