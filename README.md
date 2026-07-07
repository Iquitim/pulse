# Pulse — Agente Editorial Autônomo e Multiusuário Open-Source para Bluesky e Twitter/X

O **Pulse** é um agente open-source de agendamento, geração e publicação automática de conteúdo multiplataforma (suportando **Bluesky** e **Twitter/X**), com suporte a múltiplos provedores de IA. Projetado para ser **self-hosted**, ele dá controle total sobre dados, custos e fluxo editorial.

Suporta **Ollama local** (100% privado e gratuito), **Google Gemini** e APIs compatíveis com **OpenAI** (DeepSeek, Groq, OpenRouter) por meio do ecossistema **LangChain**. Interface moderna (estilo *Linear* / *Vercel*) em Vanilla CSS3 + ES Modules nativos, backend em FastAPI.

---

## 📸 Visual do Projeto

### 🌐 Landing Page & Login
![Landing Page](docs/screenshots/landing.png)
![Login Form](docs/screenshots/login.png)

### 📅 Painel Principal (Overview & Calendário)
![Visão Geral](docs/screenshots/overview.png)
![Calendário Editorial](docs/screenshots/calendar.png)

### ⚙️ Configurações (Modelos de IA & Contas)
![Configurações](docs/screenshots/settings.png)

---

## ✨ Funcionalidades

### 🤖 IA e Geração de Conteúdo
- **Múltiplos Provedores de IA**: Alterne entre Ollama, Gemini e OpenAI-compatíveis com um clique. O servidor marcado como **Ativo** é usado globalmente pelo Pulse
- **Teste de Conexão Integrado**: Valide modelo e credenciais diretamente no formulário com o botão **Testar Conexão ⚡**
- **Instalador Integrado do Ollama**: Diagnóstico de hardware, download automático multiplataforma e gerenciamento de modelos direto pela interface
- **Score de Qualidade**: Avaliação de clareza, gancho, especificidade e detecção automática de clichês de IA via análise híbrida (LLM + regex server-side)
- **Insights de Métricas**: Análise de engajamento (curtidas, reposts, respostas) com recomendações de novos temas
- **Prompt Modular (Instruções + Persona)**: Separação clara entre a biografia/tom do autor e as diretrizes gerais de formatação do Bluesky, permitindo que o Pulse seja adaptado a qualquer perfil sem misturar regras de formatação.
- **Aba de Instruções Integrada**: Documentação nativa cobrindo conexões do Bluesky (App Passwords), setup do Ollama local e práticas para evitar a "semelhança com IA".
- **Segurança de Chaves**: As chaves de API são criptografadas (Fernet) no banco de dados. Nenhuma chave padrão do `.env` é usada como fallback silencioso.

### 📅 Calendário e Agendamento
- **Modo Recorrente**: Publicação automática a cada X horas com tema aleatório e seleção visual da rede social de destino
- **Modo Personalizado**: Mural interativo estilo post-its com rotação orgânica para planejar posts por data e hora
- **Modo de Geração (IA vs Uso Manual)**: Botão deslizante (toggle switch) no calendário para alternar entre "Geração por IA" (Tema, Objetivo e CTA) e "Uso Manual" (onde você escreve o texto exato do post com limite de 280 caracteres, que pula a etapa de geração por IA e publica diretamente no horário agendado, ou pode ser carregado no criador de rascunhos)
- **Agendamento Inteligente**: Modal redesenhado que divide data e hora. A data é travada para seleções na grade (apenas o horário é configurado) e editável no agendamento avulso, com suporte a cores de marca (cards) e ícones visíveis em modo escuro
- **Aprovação Prévia**: Opção de salvar como rascunho para revisão antes da publicação

### 📝 Editor e Banco de Ideias
- **Editor com Preview**: Mockup visual do post no Bluesky antes de publicar, agora com seletor visual de rede social de destino para filtrar postagens
- **Banco de Ideias**: Capture rascunhos livres com indicação da rede social de destino (com badges visuais) e converta-os automaticamente em posts com a tag "💡 Ideia do Usuário" e com a rede social pré-selecionada no criador
- **Avaliação Automática**: Posts agendados (recorrentes ou calendário) passam por análise de qualidade antes da publicação, salvando a pontuação no histórico

### 🔐 Segurança e Administração
- **Autenticação JWT** com hashing bcrypt
- **Criptografia Fernet** para credenciais de redes sociais e chaves de API
- **Níveis de Cotas de Recursos** (Pessoal, Entusiasta, Coletivo) com limites editáveis para controlar o consumo de APIs e evitar abusos em instâncias compartilhadas
- **Logs de Auditoria** completos por usuário (últimas 50 atividades visíveis na aba Visão Geral)
- **Cadastro Configurável**: Aberto, por convite ou desativado
- **Gestão de Usuários**: Administrador pode alterar perfis, banir, deletar ou renovar cotas manualmente

### 🌐 Conectividade
- **Bluesky (atproto)**: Conector ativo e funcional
- **Twitter/X**: Integração real via OAuth 2.0 (popup seguro de autorização com refresh token persistido e rotacionado automaticamente no banco) ou Chaves de Desenvolvedor (cadastro manual pelo próprio usuário)
- **Threads**: Canal visual estruturado e indicado em desenvolvimento ("Em Breve" com marcação visual na interface)

### 💬 UX e Feedback Visual
- **Toast Notifications**: Notificações flutuantes com animações suaves e cores por tipo (sucesso, erro, alerta, info)

---

## 🚀 Como Rodar

### Opção A: Setup Rápido (Recomendado)

```bash
git clone https://github.com/Iquitim/pulse.git
cd pulse
python start.py
```

O script cria o ambiente virtual, instala dependências, gera chaves de segurança e inicia o servidor automaticamente.

> No Linux/macOS, use `python3 start.py` se necessário.

### Opção B: Docker (Recomendado para Produção)

1. **Configurar variáveis de ambiente**:
   ```bash
   cp .env.example .env
   ```
   *O `start.py` gera chaves JWT e Fernet automaticamente (Opção A). Para Docker, gere-as manualmente ou use as instruções do `.env.example`. Chaves de API de IA são configuradas pela interface web.*

2. **Subir os containers**:
   ```bash
   docker compose up -d
   ```
   Acesse [http://localhost:8000](http://localhost:8000).

### Opção C: Manual

```bash
git clone https://github.com/Iquitim/pulse.git
cd pulse
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

---

## 🔑 Credenciais Padrão

No primeiro boot, o Pulse cria automaticamente:

| Campo | Valor |
|---|---|
| **E-mail** | `admin@pulse.com` |
| **Senha** | `admin123` |
| **Código de Convite** | `PULSE-OPEN-SOURCE` |

Acesse [http://localhost:8000](http://localhost:8000) e altere a senha padrão em **Configurações > Segurança da Conta**.

---

## ⚙️ Variáveis de Ambiente (.env)

```env
# Chaves de API, modelos de IA e credenciais globais do Twitter/X
# são configurados diretamente pela interface web (Biblioteca de LLMs e aba Admin).
# Não é necessário adicioná-los ao .env.

# JWT
JWT_SECRET_KEY=sua_chave_secreta_jwt_de_pelo_menos_32_caracteres

# Criptografia Fernet (Base64) para credenciais de redes sociais
# Gerar: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=sua_chave_fernet

# [Opcional] Banco de dados PostgreSQL para produção
# DATABASE_URL=postgresql://usuario:senha@localhost:5432/pulse_db

# Servidor (padrões: 127.0.0.1:8000)
PORT=8000
HOST=127.0.0.1

# Configurações de instância
ALLOW_PUBLIC_REGISTRATION=True   # Se True, qualquer visitante pode criar conta
REQUIRE_INVITE_CODE=False        # Se True, exige código de convite do admin
```

> 💡 **Nota sobre Configurações Globais (Multi-Admin)**: Todas as configurações de integração e chaves globais (como as credenciais do X/Twitter OAuth 2.0) são salvas no banco de dados através da aba **Admin** do sistema. Estas configurações são **compartilhadas por todos os administradores** (se houver mais de um, todos visualizam e editam as mesmas variáveis) e aplicam-se globalmente para toda a instância e usuários.

---

## 🧱 Estrutura do Projeto

### Backend (Python / FastAPI)

```
app/
├── routes/                  # Rotas divididas por domínio de API
│   ├── dependencies.py      # Injeção de dependências (JWT, permissões)
│   ├── schemas.py           # Validação de dados com Pydantic
│   ├── views.py             # Renderização de páginas HTML (Jinja2)
│   ├── auth.py              # Login, registro e troca de senhas
│   ├── social.py            # Conexões e status das contas sociais
│   ├── config.py            # Configurações do agente e servidores LLM
│   ├── posts.py             # Geração de rascunhos, histórico e publicação
│   ├── calendar.py          # CRUD do calendário editorial
│   ├── ideas.py             # Banco de ideias, score de qualidade e insights
│   ├── admin.py             # Moderação de usuários, convites e cotas
│   ├── ollama.py            # Diagnóstico, instalação e gestão do Ollama
│   └── main.py              # Agregador de todas as rotas
├── social/                  # Conectores de redes sociais
│   ├── base.py              # Interface abstrata BaseSocialNetwork
│   ├── bluesky.py           # Conector ativo (atproto)
│   ├── twitter.py           # Conector ativo (OAuth 2.0 e Chaves Dev via Tweepy)
│   ├── threads.py           # Mock estrutural (sob construção)
│   └── registry.py          # Registro global e resolução de drivers
├── agent.py                 # Orquestração do LLM via LangChain
├── database.py              # Modelos SQLAlchemy e controle transacional
├── scheduler.py             # Agendador (APScheduler)
├── security.py              # Hash de senhas e criptografia Fernet
└── ollama_installer.py      # Diagnóstico de hardware e instalador portátil
```

### Frontend (HTML / CSS / JS)

```
static/
├── js/
│   ├── api/                 # Chamadas HTTP por domínio
│   │   ├── client.js        # Cliente HTTP base com interceptador JWT
│   │   ├── auth.js          # Login, cadastro e senhas
│   │   ├── social.js        # CRUD de contas sociais
│   │   ├── config.js        # Parâmetros do agente
│   │   ├── posts.js         # Rascunhos, histórico e métricas
│   │   ├── calendar.js      # Agendamento editorial
│   │   ├── ideas.js         # Ideias e avaliação de qualidade
│   │   ├── admin.js         # Cotas de uso, logs e administração
│   │   └── ollama.js        # Instalação e modelos Ollama
│   ├── ui/                  # Componentes visuais modulares (Renders)
│   │   ├── common.js        # Utilitários compartilhados e badges
│   │   ├── overview.js      # Métricas e logs de atividades
│   │   ├── editor.js        # Indicadores do editor e score de qualidade
│   │   ├── library.js       # Banco de ideias, histórico e insights
│   │   ├── calendar.js      # Grade do calendário editorial
│   │   ├── config.js        # Temas, chaves, servidores e contas
│   │   ├── tutorial.js      # Passos do guia Bluesky
│   │   └── ollama.js        # Diagnóstico e lista de modelos locais
│   ├── events/              # Controladores de eventos modulares (Listeners)
│   │   ├── auth.js          # Login, cadastro e alteração de senhas
│   │   ├── editor.js        # Rascunhos, atalhos IA e contagem
│   │   ├── library.js       # Banco de ideias e tabela de histórico
│   │   ├── calendar.js      # Clique na grade, presets e agendamento
│   │   ├── config.js        # Temas, intervalos e LLM servidores
│   │   ├── admin.js         # Gestão de usuários, cotas e convites
│   │   ├── ollama.js        # Instalador local e pull de modelos
│   │   └── tutorial.js      # Passos e ações do modal do tutorial
│   ├── state.js             # Estado global da aplicação
│   ├── logger.js            # Console virtual e toast notifications
│   ├── ui.js                # Re-exportação centralizada (Barrel)
│   ├── main.js              # Inicializador e registro de eventos (Boot)
│   └── api.js               # Re-exportação centralizada de chamadas HTTP
├── css/                     # Folhas de estilo por componente
│   ├── base.css, landing.css, calendar.css, auth.css,
│   │   header.css, mockup.css, ...
│   └── style.css            # Ponto de entrada central (@import)
templates/
├── components/              # Componentes HTML (Jinja2)
│   ├── landing.html         # Landing page informativa
│   ├── tab_editor.html      # Editor de posts com preview
│   ├── tab_config.html      # Configurações e servidores LLM
│   ├── tab_calendar.html    # Calendário editorial
│   └── modal.html           # Modais (Tutorial Bluesky, Ollama, Modelos)
```

---

## 🚦 Status do Desenvolvimento

| Módulo | Status |
|---|---|
| Autenticação e JWT | ✅ Funcional |
| Calendário Editorial (Mural) | ✅ Funcional |
| Bluesky (atproto) | ✅ Funcional |
| Twitter/X (OAuth 2.0 & Chaves Dev) | ✅ Funcional |
| Threads | 🚧 Sob Construção (Em Breve) |
| Banco de Ideias | ✅ Funcional |
| Análise de Qualidade (IA + Clichês) | ✅ Funcional |
| Insights de Métricas | ✅ Funcional |
| Logs de Auditoria | ✅ Funcional |
| Biblioteca de Servidores LLM | ✅ Funcional |
| Instalador Ollama Integrado | ✅ Funcional |
| Diagnóstico de Hardware | ✅ Funcional |

---

## 🔌 Contribuições

O Pulse é um projeto comunitário. Leia o [CONTRIBUTING.md](CONTRIBUTING.md) para entender as diretrizes de desenvolvimento e a estrutura de conectores em `app/social/`. Abra um Pull Request ou reporte problemas via Issue.

---

## 📄 Licença

Distribuído sob a **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para detalhes.
