# Pulse — Plataforma Editorial Autônoma e Multiusuário para Redes Sociais

O **Pulse** é uma plataforma open-source e *self-hosted* para orquestração editorial, geração assistida por IA, agendamento e publicação automatizada em múltiplas redes sociais (com suporte ativo e integrado a **Bluesky**, **Twitter/X** e **Meta Threads**).

Desenvolvido para ambientes que exigem governança e soberania sobre dados e custos operacionais, o Pulse suporta modelos locais via **Ollama** (execução privada on-premise), **Google Gemini** e provedores compatíveis com a especificação **OpenAI** (Groq, DeepSeek, OpenRouter) por meio da camada de abstração do **LangChain**.

A arquitetura combina um backend assíncrono em **FastAPI** com persistência relacional (**SQLAlchemy**) e um frontend desacoplado e responsivo construído em **HTML5**, **Vanilla CSS3** e **JavaScript modular (ES Modules)**.

---

## Demonstração da Interface

### Autenticação e Apresentação
![Landing Page](docs/screenshots/landing.png)
![Formulário de Login](docs/screenshots/login.png)

### Painel Operacional e Calendário
![Visão Geral](docs/screenshots/overview.png)
![Calendário Editorial](docs/screenshots/calendar.png)

### Configurações de Modelos e Conectores
![Configurações](docs/screenshots/settings.png)

---

## Arquitetura e Funcionalidades

### Motor de Inteligência Artificial e Geração de Conteúdo
* **Provedores de LLM Intercambiáveis**: Suporte dinâmico a Ollama local, Google Gemini e APIs compatíveis com OpenAI. O provedor ativo é selecionado e gerenciado diretamente pela interface administrativa.
* **Validação de Conectividade**: Mecanismo de health check para verificação em tempo real de credenciais e disponibilidade dos endpoints de inferência.
* **Gerenciador Embutido de Ollama**: Utilitário integrado para diagnóstico de hardware (CPU, memória, aceleração gráfica), download multiplataforma de binários e gerenciamento de modelos locais (`ollama pull`, listagem e remoção).
* **Avaliação Heurística e Semântica de Qualidade**: Análise pré-publicação que avalia clareza, ganchos textuais (*hooks*), especificidade e mitigação de clichês típicos de geração sintética através de pipeline híbrido (LLM + expressões regulares).
* **Engenharia de Prompt Modular**: Desacoplamento estrutural entre as diretrizes de persona (tom, identidade, vocabulário) e as restrições técnicas do canal de distribuição (limite de caracteres, formatação de links e hashtags).

### Calendário e Agendamento Editorial
* **Modo Recorrente (Batch/Interval)**: Publicação autônoma em intervalos configuráveis de horas, com seleção automatizada de temas pré-aprovados e direcionamento por rede social.
* **Modo de Agendamento Pontual**: Painel visual com alocação por data e horário específico.
* **Modos de Operação (Geração por IA vs. Manual)**: Alternância direta entre geração assistida por IA (a partir de tema, objetivo e chamada para ação) e composição manual estrita com validação de limites de caracteres (280 caracteres para Bluesky/Twitter/Threads).
* **Controle de Rascunhos e Aprovação**: Fluxo opcional de retenção em rascunho para auditoria e revisão humana antes do disparo.

### Banco de Ideias e Editor
* **Editor com Visualização em Tempo Real (Live Preview)**: Renderização fidedigna do card de publicação conforme o layout de cada plataforma de destino.
* **Captura Estruturada de Ideias**: Repositório de conceitos e anotações com marcação de rede social de destino e pipeline de conversão direta em agendamentos.
* **Histórico e Telemetria Editorial**: Rastreamento de publicações executadas, pontuação de qualidade obtida e métricas de engajamento (curtidas, reposts e respostas).

### Gestão de Mídias
* **Armazenamento Isolado por Usuário**: Upload de imagens (JPG, PNG, GIF, WebP de até 10 MB) e vídeos (MP4 de até 50 MB) armazenados sob o diretório `uploads/user_<id>/` com identificadores únicos sanitizados (UUID v4).
* **Biblioteca de Mídias**: Interface para gerenciamento, pré-visualização e exclusão de arquivos enviados.
* **Envio Multiplataforma**: Integração com a API ATProto do Bluesky (`upload_blob` e `AppBskyEmbedImages`) e suporte a anexos no Twitter/X.

### Segurança e Controle de Acesso
* **Autenticação e Sessões**: Emissão e validação de tokens JWT (*JSON Web Tokens*) com senhas hasheadas via `bcrypt`.
* **Criptografia em Repouso**: Chaves de API e segredos de redes sociais são criptografados no banco de dados através do algoritmo `Fernet` (criptografia simétrica de 128 bits com autenticação HMAC-SHA256).
* **Políticas de Cota por Nível de Usuário**: Sistema de *tiers* configuráveis (*free*, *pro*, *desk*) que regulam limites diários de publicação, contas vinculadas e temas cadastrados.
* **Trilha de Auditoria**: Registro transacional das últimas ações administrativas e operacionais por usuário.
* **Controle de Cadastro**: Modos de registro público aberto, restrito por código de convite ou totalmente desabilitado.

### Conectores Sociais
* **Bluesky**: Integração completa via protocolo ATProto (`atproto` SDK) para texto e upload de mídia.
* **Twitter/X**: Suporte via OAuth 2.0 PKCE (com renovação e rotação de tokens, além de Redirect URI configurável para compatibilidade com localhost e proxies reversos) ou credenciais diretas de API de Desenvolvedor (OAuth 1.0a).
* **Meta Threads**: Integração oficial via Meta Threads Graph API (OAuth 2.0 com renovação automática de Long-Lived Tokens de 60 dias e publicação em duas etapas por criação de container).

---

## Estrutura do Repositório

```text
.
├── app.py                      # Ponto de entrada da aplicação FastAPI e ciclo de vida (lifespan)
├── start.py                    # Script de inicialização, configuração de ambiente e bootstrap
├── pulse.db                    # Banco de dados padrão SQLite (gerado na inicialização)
├── requirements.txt            # Dependências Python do projeto
├── pytest.ini                  # Configurações do executor de testes Pytest
├── Dockerfile                  # Manifesto de compilação da imagem Docker
├── docker-compose.yml          # Definição de orquestração de contêineres
├── app/                        # Núcleo da aplicação backend
│   ├── __init__.py
│   ├── config.py               # Configurações globais e carregamento de variáveis
│   ├── database.py             # Sessões do banco e inicializador
│   ├── models/                 # Modelos relacionais (SQLAlchemy)
│   │   ├── __init__.py         # Re-exportador dos modelos
│   │   ├── base.py             # Declaração da Base ORM
│   │   ├── user.py             # Modelos User, InviteCode, AuditLog
│   │   ├── social.py           # Modelo SocialAccount
│   │   ├── content.py          # Modelos PostHistory, EditorialItem, Idea, MediaAsset
│   │   └── config.py           # Modelos AgentConfig, LLMServer, TierConfig, SystemSetting
│   ├── security.py             # Autenticação JWT, hashing bcrypt e criptografia Fernet
│   ├── scheduler.py            # Orquestrador de tarefas periódicas e agendamentos (APScheduler)
│   ├── agent.py                # Pipeline de prompts, avaliação de qualidade e LangChain
│   ├── ollama_installer.py     # Diagnóstico de hardware e instalador do runtime Ollama
│   ├── routes/                 # Roteamento da API RESTful (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py             # Agregador e montagem dos roteadores
│   │   ├── views.py            # Renderização de templates Jinja2
│   │   ├── dependencies.py     # Injeção de dependências e validação de permissões
│   │   ├── schemas.py          # Schemas de validação e serialização Pydantic
│   │   ├── auth.py             # Rotas de autenticação e gerenciamento de conta
│   │   ├── social/             # Gestão de conexões sociais e OAuth 2.0
│   │   │   ├── __init__.py     # Agregador das rotas sociais
│   │   │   ├── status.py       # Telemetria e status de conexões (/api/status)
│   │   │   ├── accounts.py     # CRUD de contas (/api/social-accounts)
│   │   │   ├── oauth_twitter.py # Login e callbacks OAuth 2.0 do Twitter
│   │   │   └── oauth_threads.py # Login e callbacks OAuth 2.0 do Threads
│   │   ├── config.py           # Configurações operacionais e servidores LLM
│   │   ├── posts.py            # Geração, histórico e execução de publicações
│   │   ├── calendar.py         # Operações de CRUD do calendário editorial
│   │   ├── ideas.py            # Repositório de ideias e métricas de qualidade
│   │   ├── media.py            # Upload, recuperação e exclusão de arquivos de mídia
│   │   ├── admin.py            # Administração de usuários, convites e cotas
│   │   └── ollama.py           # Endpoints de controle e telemetria do Ollama
│   └── social/                 # Drivers de integração com redes sociais
│       ├── base.py             # Classe abstrata BaseSocialNetwork
│       ├── registry.py         # Registro e resolução dinâmica de provedores
│       ├── bluesky.py          # Driver ATProto (Bluesky) com suporte a mídia
│       ├── twitter.py          # Driver Twitter/X (OAuth 2.0 e Chaves de API)
│       └── threads.py          # Driver Meta Threads (OAuth 2.0, Long-Lived Token, 2-Step Publish)
├── static/                     # Ativos estáticos do frontend
│   ├── style.css               # Folha de estilos central
│   ├── css/                    # Módulos de estilos CSS segmentados
│   │   ├── base.css            # Variáveis globais, tipografia e reset
│   │   ├── landing.css         # Estilização da página de apresentação
│   │   ├── auth.css            # Modais e formulários de autenticação
│   │   ├── header.css          # Barra superior de navegação e status
│   │   ├── panels.css          # Painéis de controle e abas principais
│   │   ├── calendar.css        # Visualização de grade e cards do calendário
│   │   ├── mockup.css          # Renderização de preview das publicações
│   │   ├── library.css         # Banco de ideias e tabelas de histórico
│   │   ├── metrics.css         # Indicadores e gráficos de métricas
│   │   ├── tabs.css            # Componentes de abas e alternadores
│   │   ├── terminal.css        # Janela de logs e diagnóstico
│   │   └── themes.css          # Paletas e definições de tema visual
│   └── js/                     # Código JavaScript desacoplado (ES Modules)
│       ├── main.js             # Ponto de inicialização do frontend
│       ├── state.js            # Gerenciamento de estado global da aplicação
│       ├── logger.js           # Utilitário de notificações e logging em tela
│       ├── api.js              # Barrel de exportação de clientes de API
│       ├── ui.js               # Barrel de exportação de renderizadores
│       ├── api/                # Clientes HTTP por domínio de serviço
│       ├── events/             # Controladores de eventos e interações da UI
│       └── ui/                 # Funções puras de renderização de componentes
├── templates/                  # Templates HTML renderizados via Jinja2
│   ├── index.html              # Casca principal da aplicação (Single Page Interface)
│   └── components/             # Fragmentos modulares de interface
│       ├── landing.html        # Página de apresentação institucional
│       ├── auth.html           # Diálogos de login e registro
│       ├── header.html         # Cabeçalho da aplicação e status de conexão
│       ├── navigation.html     # Menu de navegação por abas
│       ├── head_theme_loader.html # Script inline de prevenção de flash de tema
│       ├── tab_overview.html   # Painel de visão geral e métricas rápidas
│       ├── tab_editor.html     # Editor de conteúdo e gerador assistido
│       ├── tab_calendar.html   # Grade e formulário de agendamento
│       ├── tab_library.html    # Repositório de ideias e histórico
│       ├── tab_config.html     # Configurações do agente, LLMs e credenciais
│       ├── tab_admin.html      # Painel de governança e controle de usuários
│       ├── tab_instructions.html # Documentação e guias de integração
│       ├── metrics.html        # Componente de resumo de engajamento
│       └── modal.html          # Modais compartilhados (Tutorial, Ollama, Mídia)
├── tests/                      # Suíte de testes automatizados
│   ├── conftest.py             # Fixtures globais e banco de testes em memória
│   ├── api/                    # Testes de integração de endpoints RESTful
│   │   ├── test_auth_api.py
│   │   ├── test_admin_api.py
│   │   ├── test_calendar_api.py
│   │   ├── test_config_api.py
│   │   ├── test_ideas_api.py
│   │   ├── test_media_api.py
│   │   ├── test_posts_api.py
│   │   └── test_threads_api.py
│   └── unit/                   # Testes unitários de regras de negócio
│       ├── test_security.py
│       ├── test_agent_quality.py
│       └── test_social_connectors.py
├── uploads/                    # Diretório local de armazenamento de mídias por usuário
├── docs/                       # Documentação adicional e imagens ilustrativas
└── logs/                       # Arquivos de log de execução em tempo de execução
```

---

## Instalação e Execução

### Opção 1: Inicialização Automática (Ambiente Local)

O script `start.py` orquestra a criação do ambiente virtual Python, a instalação de dependências, a geração automática de chaves criptográficas seguras no arquivo `.env` e a inicialização do servidor:

```bash
git clone https://github.com/Iquitim/pulse.git
cd pulse
python3 start.py
```

Após a inicialização, acesse a aplicação em `http://localhost:8000`.

### Opção 2: Implantação com Docker Compose

1. **Configurar as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   ```
   *Certifique-se de configurar chaves seguras para `JWT_SECRET_KEY` e `ENCRYPTION_KEY` antes de prosseguir.*

2. **Compilar e executar o contêiner**:
   ```bash
   docker compose up -d
   ```

A aplicação estará disponível em `http://localhost:8000`.

### Opção 3: Execução Manual

```bash
git clone https://github.com/Iquitim/pulse.git
cd pulse

# Criação e ativação do ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalação das dependências
pip install -r requirements.txt

# Inicialização da configuração
cp .env.example .env

# Execução do servidor FastAPI
python3 app.py
```

---

## Credenciais Iniciais do Sistema

Na primeira execução, o banco de dados é inicializado automaticamente com os seguintes acessos padrão:

| Atributo | Valor Padrão |
|---|---|
| **E-mail do Administrador** | `admin@pulse.com` |
| **Senha Provisória** | `admin123` |
| **Código de Convite Mestre** | `PULSE-OPEN-SOURCE` |

> **Nota de Segurança**: Altere a senha padrão imediatamente após o primeiro login acessando **Configurações > Segurança da Conta**.

---

## Variáveis de Ambiente

As configurações sensíveis e parâmetros de infraestrutura são definidos no arquivo `.env`:

```env
# Chave de assinatura para tokens JWT (mínimo de 32 caracteres)
JWT_SECRET_KEY=sua_chave_secreta_jwt_de_pelo_menos_32_caracteres

# Chave simétrica Fernet (Base64) para cifragem de credenciais
# Gerar via: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=sua_chave_fernet_base64

# String de conexão com o banco de dados (SQLite por padrão; suporte a PostgreSQL)
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/pulse_db

# Parâmetros de rede do servidor HTTP
PORT=8000
HOST=127.0.0.1

# Políticas de cadastro de usuários
ALLOW_PUBLIC_REGISTRATION=True   # Permite o autocadastro de novos usuários
REQUIRE_INVITE_CODE=False        # Exige código de convite emitido por um administrador

# [Opcional] Credenciais Globais do Twitter/X OAuth 2.0 (podem ser configuradas via painel Admin)
# TWITTER_CLIENT_ID=seu_client_id
# TWITTER_CLIENT_SECRET=seu_client_secret
# TWITTER_REDIRECT_URI=http://127.0.0.1:8000/api/social/twitter/callback

# [Opcional] Credenciais Globais do Meta Threads OAuth 2.0 (podem ser configuradas via painel Admin)
# THREADS_APP_ID=seu_meta_app_id
# THREADS_APP_SECRET=seu_meta_app_secret
# THREADS_REDIRECT_URI=http://127.0.0.1:8000/api/social/threads/callback
```

> **Configurações Globais Compartilhadas & Redirecionamentos OAuth**:
> - Chaves de API de provedores de IA e credenciais dos aplicativos Twitter/X e Meta Threads podem ser gerenciadas diretamente pela interface administrativa (**Admin**) ou pelo arquivo `.env`.
> - **Validação no X Developer Portal**: O Twitter/X exige correspondência exata de URI. Para desenvolvimento local, cadastre tanto `http://127.0.0.1:8000/api/social/twitter/callback` quanto `http://localhost:8000/api/social/twitter/callback` nas configurações do aplicativo no portal do X. Em ambientes com proxies reversos ou domínios customizados, defina explicitamente o `TWITTER_REDIRECT_URI`.
> - **Validação no Meta for Developers**: No produto Threads, adicione o `Redirect URI` configurado em **Threads > App Settings > Redirect Callback URLs**.

---

## Documentação Interativa da API (Swagger / OpenAPI)

O backend disponibiliza documentação interativa completa dos endpoints RESTful gerada automaticamente pelo FastAPI:

* **Swagger UI Interativo**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (permite testar requisições, autenticar via Bearer Token e explorar schemas de payload).
* **ReDoc Alternativo**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (visualização técnica e formatada de referência da API).

---

## Matriz de Módulos e Funcionalidades

| Módulo / Domínio | Componente | Status |
|---|---|---|
| **Autenticação** | Emissão de tokens JWT e gestão de sessões | Estável |
| **Segurança** | Criptografia Fernet em banco e hash bcrypt | Estável |
| **Redes Sociais** | Conector ATProto (Bluesky) para texto e mídia | Estável |
| **Redes Sociais** | Conector Twitter/X (OAuth 2.0 com rotação de tokens) | Estável |
| **Redes Sociais** | Conector Meta Threads (Graph API, OAuth 2.0, renovação de token) | Estável |
| **Geração de Conteúdo** | Orquestração LangChain (Ollama, Gemini, OpenAI) | Estável |
| **Qualidade de Post** | Análise heurística e detecção de clichês sintéticos | Estável |
| **Agendamento** | Execução periódica e agendamento pontual (APScheduler) | Estável |
| **Galeria de Mídia** | Upload, isolamento e anexação de imagens/vídeos | Estável |
| **Administração** | Gestão de cotas de recursos (*tiers*), convites e logs | Estável |
| **Documentação da API** | Swagger UI (`/docs`) e ReDoc (`/redoc`) | Estável |
| **Testes Automatizados** | Suíte de 47 testes cobrindo rotas, OAuth 2.0 e regras unitárias | Estável |

---

## Testes Automatizados

O projeto utiliza o framework `pytest` para testes unitários e de integração, executados em banco SQLite isolado em memória (`sqlite:///:memory:`).

Para executar toda a suíte de testes:

```bash
pytest
```

Para executar testes com relatório de cobertura:

```bash
pytest --cov=app tests/
```

---

## Fluxo de Versionamento (Git Flow)

O repositório segue o modelo de branches **Git Flow**:

* `main`: Ramo estável destinado exclusivamente a versões de produção.
* `staging`: Ramo de homologação e validação prévia à liberação em produção.
* `develop`: Ramo de integração contínua onde novas implementações são unificadas.
* `feature/*`: Ramos dedicados ao desenvolvimento de novas funcionalidades.
* `fix/*`: Ramos dedicados à correção de defeitos identificados.

Todos os envios para `main`, `staging` e `develop` são validados automaticamente pela esteira de CI/CD do **GitHub Actions**.

---

## Contribuição

Contribuições para o desenvolvimento do Pulse são bem-vindas. Antes de submeter código, consulte as diretrizes detalhadas no arquivo [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Licença

Este projeto é distribuído sob os termos da [Licença MIT](LICENSE).
