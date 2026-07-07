<p align="center">
  <img src="frontend/public/logo.png" alt="Logo do Gastor" width="96" />
</p>

<h1 align="center">Gastor</h1>

<p align="center">
  <strong>Plataforma de trading algorítmico, backtesting, paper trading, testnet e automação assistida por IA.</strong>
</p>

<p align="center">
  <img alt="Backend FastAPI" src="https://img.shields.io/badge/backend-FastAPI-009688">
  <img alt="Frontend Next.js" src="https://img.shields.io/badge/frontend-Next.js%2016-111111">
  <img alt="Banco PostgreSQL" src="https://img.shields.io/badge/database-PostgreSQL%2015-336791">
  <img alt="MCP e Aura" src="https://img.shields.io/badge/IA-Aura%20%2B%20MCP-6c5ce7">
  <img alt="Documentação PT-BR" src="https://img.shields.io/badge/docs-PT--BR-blue">
</p>

---

## Visão Geral

Gastor é um ecossistema completo para traders quantitativos que desejam validar hipóteses com rigor estatístico antes de arriscar capital real. A plataforma reúne construtor de estratégias, backtests, otimização, paper trading, testnet multi-exchange, logs auditáveis de decisão e uma assistente de IA chamada **Aura**.

> **Nota:** operação com dinheiro real ainda não está implementada. Os modos atuais são `paper` e `testnet`.

## Índice

- [Conceito: Dados > Intuição](#-conceito-dados--intuição)
- [Por que usar o Gastor?](#-por-que-usar-o-gastor)
- [Novidades e Evolução da Plataforma](#-novidades-da-versão-v80-mcp-integration--aura)
- [Instalação Rápida](#-instalação-rápida-docker)
- [Fontes de Dados](#-fontes-de-dados)
- [Autenticação e Segurança](#-autenticação-e-segurança)
- [Navegação e Interface](#-navegação-e-interface)
- [Live Trading: Paper e Testnet](#-live-trading--paper--testnet-multi-exchange)
- [Resolução de Problemas](#-resolução-de-problemas-faq)
- [Arquitetura](#-arquitetura)
- [Testes](#-testes)
- [Stack](#-stack)
- [Pesquisa de Estratégias](#-pesquisa-de-estratégias-research-v3)
- [Deploy em Produção](#-deploy-em-produção-vps)
- [Roadmap](#-roadmap)
- [Licença](#-licença)

## Como Ler Este README

Este README foi mantido como documento único do projeto. As seções abaixo preservam o histórico, as decisões técnicas, os fluxos de uso, os comandos operacionais e o roadmap em um só lugar. A organização prioriza leitura executiva no topo e profundidade técnica nas seções seguintes.

## Capacidades Principais

| Área | O que o Gastor oferece |
|------|-------------------------|
| Estratégias | Catálogo de estratégias, builder visual e estratégias customizadas |
| Backtesting | Simulações com taxas, PnL, drawdown, profit factor, Sortino e validações FTMO |
| Otimização | Grid Search para testar combinações de parâmetros com rapidez |
| Paper/Testnet | Sessões com preços reais e execução simulada ou sandbox |
| Multi-exchange | Binance, Bybit e OKX, com fallback de dados por agregadores |
| Auditoria | Decision Logs completos para cada BUY/SELL |
| IA | Aura integrada ao produto e clientes externos via MCP |
| Administração | Tiers, convites, usuários, métricas e controles operacionais |

---

## 🧠 Conceito: Dados > Intuição

O diferencial do Gastor é o foco em **evidência estatística**. Em vez de operar baseado em "feeling", você constrói regras lógicas e as submete a testes massivos em dados históricos.

### Fluxo de Trabalho

1. **🗣️ Conversar**: Descreva sua hipótese para a **Aura** (assistente de IA) ou monte regras visuais no Strategy Builder. 12 estratégias clássicas (RSI, MACD, Bollinger) servem de ponto de partida.
2. **✅ Validar**: Backtest com split treino/teste, métricas profissionais (Sharpe, Sortino, drawdown, profit factor) e check automático das regras FTMO. Pro desbloqueia Grid Search.
3. **🎮 Simular**: Paper trading com preços reais ou Binance Testnet / Bybit Testnet / OKX Demo Trading com ordens reais sem dinheiro real. Até 5 sessões em paralelo no Desk, com restauração automática.
4. **🧠 Decidir**: Decision logs auditáveis em cada BUY/SELL — indicadores, candle, regras, latência, motivo de saída. Export CSV/JSONL pareado para ML, com filtro por exchange.
5. **🚀 Live Trading**: (Fase 9 — planejado) Automatize a execução com dinheiro real via API de qualquer exchange suportada.

---

## 🎯 Por que usar o Gastor?

- 📉 **Visualizar overfitting:** veja como estratégias que parecem perfeitas no passado falham em novos dados.
- ⚡ **Otimização rápida:** teste milhares de combinações de parâmetros em segundos.
- 🧱 **Construtor visual:** crie estratégias complexas sem escrever código.
- ✅ **Validação FTMO:** verifique automaticamente se uma estratégia passaria nas regras de mesa proprietária.

---

## 🚀 Novidades da Versão (v8.0 MCP Integration & Aura)

### 🤖 MCP Agêntico + Aura by Gastor — Model Context Protocol (v8.0)

Gastor ganhou uma **interface agêntica completa** via MCP, e uma assistente de IA embutida chamada **Aura by Gastor** (referida apenas como "Aura" no dia a dia — feminino: *a* Aura). Qualquer LLM — Claude Desktop, Cursor, VS Code ou a UI `/chat` onde mora a Aura — pode consultar mercado, rodar backtests, criar estratégias e operar paper trading diretamente no Gastor via tool calling.

*   **Servidor MCP embutido:** FastMCP SDK oficial montado em `/mcp` (Streamable HTTP transport) dentro do mesmo backend FastAPI. Controlado pela env var `MCP_ENABLED` — **habilitado em produção desde v8.3** (Phase B). Autenticação via `MCPAuthMiddleware` exige tokens MCP-escopados (`aud="mcp"`, JTI registrado em `mcp_tokens`); o JWT principal da API **não funciona** contra `/mcp` por defesa em profundidade.
*   **19 ferramentas organizadas por tier:** Catálogo distribuído em 9 módulos (`market`, `strategies`, `education`, `backtest`, `builder`, `optimizer`, `live`, `decision_logs`, `metrics`). Tier gating via `TOOL_TIER_MAP`. Auditoria de v8.1 removeu 5 entradas fantasma (`market_sentiment`, `export_decision_logs`, `find_best_strategy`, `full_strategy_analysis`, `session_performance_report`) e adicionou `get_trade_pair`. Teste bidirecional impede regressão.

    | Tier | Ferramentas disponíveis |
    |------|-------------------------|
    | **Free** (8) | `get_market_data`, `get_market_summary`, `list_strategies`, `get_strategy_details`, `list_saved_strategies`, `explain_indicator`, `suggest_indicators`, `get_system_health` |
    | **Pro** (+6) | `run_backtest`, `compare_strategies`, `run_grid_search`, `create_strategy`, `explain_strategy`, `get_decision_logs`, `get_trade_pair` |
    | **Desk** (+5) | `list_sessions`, `get_session_details`, `start_session`, `stop_session` |
    | **Admin** | Bypass completo — todas as tools, em qualquer tier |

*   **Resources + Prompts:** `gastor://strategies/catalog` (catálogo completo) e `gastor://indicators` (lista de indicadores técnicos). Templates de conversa pré-configurados: `build_strategy`, `analyze_strategy`, `market_overview`, `learn_indicator`.
*   **Aura — assistente interna (`/chat`):** A **Aura** é a UI de chat do Gastor, com ponte OpenAI-compatible implementada em [backend/api/routes/chat.py](backend/api/routes/chat.py). Fluxo: mensagem do usuário → backend anexa system prompt + histórico → chama LLM com function definitions geradas de `TOOL_TIER_MAP` → executa tool calls com tier gating → devolve resposta final + lista de tool calls. Renderiza cada tool call como card expansível (ferramenta, args, resultado). Suporta até 5 rodadas de tool calls encadeadas por mensagem.
*   **Configuração LLM por usuário (criptografada):** Cada usuário traz sua própria API key em **Painel do Usuário → Integrações → IA & Assistente** (`/user/panel`). Suporta qualquer endpoint OpenAI-compatible: OpenAI (default), Anthropic via proxy (LiteLLM), LocalAI, Ollama com adapter. A API key é **criptografada com Fernet** antes de persistir em `user_configs.llm_api_key_encrypted` (reusa `core.security.encrypt_value`). `GET /api/chat/config` **nunca** devolve a key — apenas um flag `has_api_key`. Endpoints: `GET/POST/DELETE /api/chat/config`. Fallback: se o usuário não tiver key, o backend tenta `OPENAI_API_KEY` ou `LLM_API_KEY` do ambiente.
*   **Clients externos suportados:** Claude Desktop, Cursor e VS Code via configuração MCP padrão (`url`, `transport: streamable-http`, `Authorization: Bearer <jwt>`). Ver guia completo em [docs/mcp.md](docs/mcp.md).
*   **Cobertura de testes:** 36 testes dedicados — `test_mcp_auth.py` (23 testes: invariantes do `TOOL_TIER_MAP`, `check_tool_access` por tier, bypass de admin, ciclo ASGI do middleware), `test_chat_config.py` (7 testes: round-trip Fernet, bloqueio de exposição da key via GET, preservação da key existente ao salvar sem `api_key`), `test_mcp_server.py` (6 smoke tests: boot do server, registro de todas as tools/resources/prompts, drift detection **bidirecional** entre `TOOL_TIER_MAP` e tools registradas — falha tanto se houver tool fantasma no map quanto tool registrada sem entrada).

```
Client MCP  ──  POST /mcp  ──►  MCPAuthMiddleware  ──►  FastMCP app
 (JWT)                           (valida token)         (dispatch tool)
```

> 📖 Guia completo em [docs/mcp.md](docs/mcp.md): arquitetura, tier gating, configuração de clients externos (Claude Desktop, Cursor, VS Code), Aura (assistente interna), e troubleshooting.

---

## 🚀 Novidades da Versão (v8.3 MCP Hardening — Phase B)

### 🔐 MCP em Produção com Defesa em Profundidade

A v8.3 transforma o MCP de feature interna para canal externo de produção, com 8 camadas de proteção em série antes de qualquer tool ser executada por um cliente externo.

*   **Tokens MCP escopados (`aud="mcp"`):** Tokens dedicados em `mcp_tokens` (id, jti, name, expires_at, last_used_at, revoked_at, allowed_ips). JWT do app principal **não funciona** contra `/mcp` (rejeitado pela aud). Defesa simétrica: o token MCP também não funciona contra a API principal. Expiração de 90 dias com renovação manual.
*   **Audit log completo (`mcp_audit_log`):** Cada tool call gera uma linha com `user_id`, `tool_name`, `category`, `args_summary` (truncado a 500 chars), `source` (`aura_chat` | `mcp_external`), `client_ip`, `user_agent`, `success`, `error_summary`, `duration_ms`. Best-effort — falha de log nunca bloqueia a chamada.
*   **Rate limit por categoria de tool:** Token-bucket in-process (sem Redis) por (user_id, category). Tools caras como `run_backtest` (Pro: 10/min) e `run_grid_search` (Pro: 5/min) têm buckets apertados. Free não tem acesso a categorias Pro+.
*   **Cost cap diário:** Free 20 / Pro 200 / Desk 1.000 chamadas/dia, contagem derivada do audit log (sucesso apenas — falhas não contam). Reset meia-noite UTC. Endpoint `GET /api/mcp/tokens/usage` para o usuário ver progresso.
*   **Alerta Telegram no primeiro uso:** Snapshot de `last_used_at` antes do bump permite detectar a primeira chamada de cada token. Telegram envia IP, User-Agent e timestamp BRT. Sinal de segurança crítico — se chegou alerta de token desconhecido = comprometido.
*   **IP allowlist por token:** Lista opcional de IPs/CIDR (`MCPToken.allowed_ips`). Vazio = qualquer IP. Suporta IPv4 e IPv6. Tolera entradas malformadas (typo do usuário não bloqueia o resto da lista).
*   **Painel admin de analytics:** `/admin/mcp` — KPIs (total/sucesso/falhas/taxa), rollups por tool/usuário/categoria/origem, audit log com filtros, seletor de janela (1h a 30d). Backed por `GET /api/admin/mcp/analytics`.
*   **UI para o usuário final:** `/user/panel → Integrações → IA & Assistente` ganha o painel "Conectar cliente MCP externo" — endpoint URL com copy, barra de uso diário com cores (verde/âmbar/vermelho), criação de token (com IP allowlist opcional), banner com o JWT raw exibido **uma única vez**, lista de tokens com status (Em uso / Nunca usado / Expirado / Revogado) e botão de revogar.
*   **Documentação acessível:** Página `/docs/mcp` em pt-BR adaptada do `docs/mcp.md` interno, com tabs por cliente (Claude Desktop / Cursor / VS Code), copy buttons, troubleshooting e seção de segurança.

#### Ordem de checagens em cada chamada de tool MCP

```
Bearer token → MCPAuthMiddleware
  ↓ verify JWT signature + exp
  ↓ require aud="mcp"
  ↓ lookup jti em mcp_tokens
  ↓ check revoked_at, expires_at
  ↓ check IP allowlist (se configurado)
  ↓ bump last_used_at  →  Telegram alert se primeira vez
  ↓ load + detach User
require_mcp_tool_access(tool, ctx)
  ↓ tier gate (TOOL_TIER_MAP)
  ↓ daily cost cap (mcp_audit_log COUNT)
  ↓ rate limit per category (token bucket)
  ↓ audit log entry (best-effort)
tool.fn(...)
  ↓ resultado
audit log entry com duration_ms (best-effort)
```

#### Cobertura de testes

- `test_mcp_tokens.py` (15) — issuance, listing, revogação idempotente, defense em profundidade (API principal rejeita aud="mcp" e vice-versa), JTI desconhecido, expiração, IP allowlist match exato + CIDR, PATCH em token revogado.
- `test_mcp_audit.py` (8) — record persiste com lookup automático de categoria, truncamento de args, swallow de erros de DB, isolamento por usuário, filtros admin (tool_name + success), analytics agrega corretamente, window filter.
- `test_mcp_rate_limit.py` (9) — admin bypass, burst+block, Pro vs Free, bloqueio de categoria, isolamento per-user e per-category, refill por elapsed, GC sob pressão de memória.
- `test_mcp_cost_cap.py` (8) — usage_today conta só sucessos, ignora dia anterior, tier-aware, endpoint `/usage` retorna estado correto.

Suite total: **207 testes passando**, zero regressões em relação à v8.0.

---

## 🚀 Novidades da Versão (v5.0 Multi-Exchange)

### 🔄 Suporte Multi-Exchange (Binance + Bybit + OKX)
*   **Abstração de Exchange:** Novo módulo `core/exchange/` com registry centralizado, client CCXT genérico e normalização de símbolos. Suporte completo a Binance, Bybit e OKX — inclusive contas unificadas (Unified Account) e passphrase (OKX).
*   **Precisão de Ordens:** Antes de cada ordem, o sistema consulta `market['precision']` via CCXT e trunca a quantidade para baixo (nunca arredonda), evitando rejeições por exchange.
*   **WebSocket Multi-Exchange:** Streams de kline com parsers específicos por exchange (Binance: URL direta, Bybit/OKX: subscribe JSON pós-conexão). Watchdog anti-stale reutilizado.
*   **Data Loader Expandido:** Fallback chain agora inclui Bybit e OKX como fontes de dados OHLCV via CCXT.
*   **Decision Logs Multi-Exchange:** Campo `exchange_name` em todos os logs de decisão, com filtro `?exchange_name=bybit` nos endpoints de listagem e export (CSV/JSONL).
*   **Frontend:** Seletor de exchange no cadastro de chaves API (com campo passphrase condicional para OKX), badges coloridos por exchange na lista de sessões e detalhes, monitor de saldo para qualquer exchange.
*   **Backward-Compatible:** Todos os defaults são `"binance"`. Aliases deprecated mantidos em `testnet/` para compatibilidade com código existente. Migrações SQL com `DEFAULT 'binance'`.

### 🐛 Correções (v5.0.1)

*   **PnL com Entry Cost:** O cálculo de PnL realizado e não-realizado agora considera o custo total da entrada (`entry_cost`), que inclui a taxa de compra. Antes, a fórmula `net_sell - (qty × entry_price)` ignorava a fee de compra, gerando resultados levemente otimistas. Agora: `pnl = net_sell - entry_cost` e `unrealized = (qty × price_atual) - entry_cost`. Nova coluna `entry_cost` no model `PaperPosition` (backward-compatible com fallback para posições antigas).
*   **Unrealized PnL On-the-Fly:** O endpoint de detalhes da sessão agora calcula `unrealized_pnl` em tempo real usando `entry_cost`, em vez de ler o valor potencialmente defasado do banco de dados. O engine também recalcula `unrealized_pnl` ao restaurar sessões (`_sync_state`), corrigindo a inconsistência onde realizado + não-realizado não somava ao equity total.
*   **Migration Rollback (PostgreSQL):** Corrigido bug crítico no sistema de migrations onde `except: pass` sem `conn.rollback()` deixava a transação em estado "aborted" no PostgreSQL. Uma migration falhada (ex: coluna já existente) abortava **todas** as migrations seguintes silenciosamente. Agora cada falha faz `rollback()` e continua normalmente.
*   **Entrypoint Ordering:** O `entrypoint.sh` agora roda migrations **antes** do `promote_admin.py`. Antes, o script de promoção tentava consultar colunas que ainda não existiam, falhando silenciosamente.
*   **Timestamps com Timezone:** Colunas de timestamp no `TradeDecisionLog` (`executed_at`, `ws_receive_at`, `signal_detected_at`, `candle_open_at`) agora usam `TIMESTAMPTZ`, consistente com `PaperTrade`. Isso corrige a discrepância onde trades mostravam horário BRT e decisões mostravam UTC.
*   **Telegram — Resolução de Chat ID:** Notificações de trade (BUY/SELL/sessão) agora consultam a tabela `TelegramConfig` do banco de dados como fallback quando o frontend não envia o `chat_id` na criação da sessão. Também aplica o fallback na restauração de sessões existentes com `chat_id` vazio. Isso garante que usuários com Telegram configurado recebam alertas sem depender do frontend.
*   **Data Loader — Normalização de Símbolos:** Corrigido bug onde `normalize_to_ccxt()` recebia apenas o ativo base ("SOL") em vez do par completo ("SOLUSDT") ao rotear para Bybit/OKX como fonte de dados. A função não conseguia identificar a moeda quote, gerando erro de normalização.
*   **Telegram — HTML Parsing:** Corrigido erro 400 do Telegram ("Unsupported start tag") que impedia notificações de SELL e de estratégias com operadores `<`, `>`, `<=` nos indicadores. O dict de triggers estruturado (`buy_rules`/`sell_rules` com campos `operator`) era passado diretamente ao template HTML do Telegram, onde operadores como `"<"` eram interpretados como tags HTML. Fix: (1) `html_escape()` em todos os valores dinâmicos no template, (2) `_flatten_triggers()` transforma o dict estruturado em dict plano legível antes de enviar.
*   **Dashboard — Timezone do Gráfico:** O gráfico de candlestick (lightweight-charts) exibia timestamps em UTC, mostrando horários ~2-3h no futuro para usuários BRT. Adicionado `timeFormatter` (crosshair/tooltip) e `tickMarkFormatter` (eixo de tempo) customizados que convertem para o timezone local do navegador via `toLocaleTimeString()`. Ambos os formatters tratam os 5 tipos de tick mark (ano, mês, dia, hora, hora+segundos).
*   **Paper Trading — Lógica AND/OR nos Triggers:** A avaliação de sinais (`signals.py`) usava lógica fixa (BUY=AND, SELL=OR) para todas as estratégias, incluindo customizadas que podiam ter lógica diferente configurada no builder. Refatorado para respeitar a estrutura de grupos: cada regra agora carrega `group_id` e `group_logic`, e a avaliação combina regras dentro de grupos e grupos entre si com a lógica correta. Suporta expressões mistas como `(A AND B) OR C`.
*   **Decision Logs — Enriquecimento de Indicadores:** O `indicators_snapshot` nos logs de decisão agora inclui **todos os indicadores disponíveis** (não apenas os da estratégia ativa). Antes, uma sessão Spring Loaded só capturava BB e EMAs; agora captura ~35 features: RSI(14), EMA(9/21/50/100), SMA(20/50/200), MACD(line/signal/histogram), Bollinger(upper/mid/lower/%B), Stochastic(%K/%D), ATR(14), Donchian(upper/lower), ROC(12), Z-Score(20), Volume Ratio(20), Avg Volume(20), Median(14/20/50), MAD(14/20/50), Robust Z-Score(14/20/50). Alinhado com os indicadores do construtor de estratégias. Os indicadores originais da estratégia são preservados (sem sobrescrita).
*   **Estratégias Duplicadas (Admin):** Estratégias admin-only (Spring Loaded FTMO, Win First FTMO) apareciam duplicadas na listagem do Lab — uma vez como oficial (badge FTMO/Híbrido) e outra como "Personalizadas" (registro custom no DB). Corrigido filtrando registros custom que são proxies de estratégias oficiais (`rules.strategy_type` definido) no endpoint `GET /api/strategies/`.
*   **Paper Trading — Avaliação OR em Grupo Único:** Estratégias com todas as regras de saída em um único grupo (ex: Spring Loaded com TP, SL, Trailing Stop) não vendiam mesmo com `sell_logic="OR"`, porque `_evaluate_grouped()` usava `group_logic="AND"` (default) no grupo único, exigindo TODAS as condições ativas. Corrigido para usar `outer_logic` como lógica interna quando há apenas um grupo. Múltiplos grupos continuam usando cada `group_logic` individual.
*   **Spring Loaded — FutureWarning:** Silenciado `FutureWarning` do pandas em `squeeze.shift(lag).fillna(False)` que poluía os logs a cada poll do frontend (~5s). Substituído `.infer_objects(copy=False)` por `.astype(bool)`.

### 💎 Sistema Freemium (v6.0)

*   **3 Tiers de Acesso (Free / Pro / Desk):** Controle de acesso granular via códigos de convite. Cada código possui um `plan_tier` associado que é atribuído automaticamente ao usuário no registro. Quotas (sessões, rate limit) configuradas automaticamente via `apply_tier_quotas()`.

| Tier | Sessões | Grid Search | Multi-exchange | Testnet | Decision Logs Export | Rate Limit |
|------|---------|-------------|----------------|---------|---------------------|------------|
| **Free** | 1 | — | — | ✅ | — | 1x |
| **Pro** | 2 | ✅ | ✅ | ✅ | CSV + JSONL | 3x |
| **Desk** | 5 | ✅ | ✅ | ✅ | CSV + JSONL | 5x |

*   **Feature Gating (Backend):** FastAPI dependency `require_feature("feature_name")` bloqueia rotas protegidas (Grid Search, export de Decision Logs). Checks inline para testnet e multi-exchange. Admin (`role="admin"`) bypassa todos os gates — `has_feature()` sempre retorna `True`.
*   **Feature Gating (Frontend):** Hook `useTier()` espelha a config do backend. Componente `<UpgradeGate>` envolve seções restritas: se o tier não tem acesso, exibe badge do tier necessário e mensagem de upgrade. Suporte a modo `inline` para desabilitar botões com overlay.
*   **User Panel — Tier Info:** Seção no topo do painel mostra badge do tier atual (cores: verde=Free, azul=Pro, âmbar=Desk, roxo=Admin), número de sessões, e lista de features disponíveis/bloqueadas.
*   **Admin — Gestão de Tiers:** Coluna "Tier" na tabela de usuários e invite codes com badges coloridos. Botão "Tier" por usuário para upgrade/downgrade (auto-ajusta quotas). Select de tier na criação de invite codes.
*   **Sem Gateway de Pagamento:** Controle 100% manual via invite codes. O admin recebe pagamento externamente, cria um código com o tier desejado e envia ao cliente.
*   **Configuração Centralizada:** `backend/core/tier_config.py` é a single source of truth para quotas, features e gates. Frontend espelha em `useTier.ts`.
*   **i18n:** Namespace `Tier` com 12 chaves traduzidas em 6 idiomas (frontend) + `errors.tier` com 2 chaves (backend).

### 🌐 Landing Page, Termos Legais e Controle de Inatividade (v7.0)

#### 🏠 Landing Page Pública

*   **Nova página inicial:** A rota `/` exibe uma landing page pública responsiva — acessível sem login. O Dashboard foi movido para `/dashboard`. O logo no navbar redireciona para `/` (landing após logout).
*   **Seções da landing (fluxo narrativo, redesign v8.1):** HeroSection (linha de categoria "PLATAFORMA DE TRADING ALGORÍTMICO PARA CRIPTOMOEDAS" + headline "Crie, valide e opere estratégias de trading conversando com a IA" + sub apresentando "Aura, a IA do Gastor" e nomeando Binance/Bybit/OKX + linha "não é uma corretora, não é um grupo de sinais" para eliminar mal-entendidos + mockup de conversa com a Aura + equity curve + trust strip multi-exchange/multi-LLM/auditoria) → ProblemSection (3 dores ICP: backtest superficial, paper sem auditoria, prop firm às cegas) → **AuraSection** (protagonismo da assistente de IA — 4 capabilities com prompts reais, 19 tools, providers OpenAI/Anthropic/Google/Meta/Mistral/DeepSeek) → WorkflowSection (4 passos: Conversar → Validar → Simular → Decidir) → **MultiExchangeSection** (Binance/Bybit/OKX + bullets técnicos) → **DecisionLogsSection** (cada trade vira dado de treino, com mockup de log) → FTMOSection → PricingSection (3 tiers em comparação visual, Pro destacado como recomendado) → FAQSection (9 perguntas, +Aura/MCP) → FooterSection.
*   **Scroll reveal:** cada seção entra com fade-in suave via `useScrollReveal` hook (IntersectionObserver, threshold 10%).
*   **Rotas públicas:** `/`, `/login`, `/register`, `/terms` e `/glossary` — acessíveis sem login.
*   **Navbar adaptativo:** Links de navegação (Dashboard, Lab, Otimizador, etc.) visíveis apenas para usuários autenticados. Usuários não autenticados veem apenas as ações de login/registro.
*   **i18n completo:** namespace `Landing` com 187 chaves em 6 idiomas (pt-BR, en, es, zh, ja, ko) após o redesign v8.1.

#### 📋 Termos de Uso v2.0 (Documento Legal Completo)

*   **12 seções legais:** Aceitação · Definições · Cadastro · Uso da Plataforma · Propriedade Intelectual · Isenção de Responsabilidade Financeira · Privacidade · Comunicações · Suspensão e Encerramento · Legislação Aplicável · **Política de Inatividade** · Disposições Gerais.
*   **Seção 11 dinâmica:** O prazo exibido na Política de Inatividade é buscado em tempo real via `GET /api/user/inactivity-limit` e interpolado no texto. Atualiza automaticamente quando o admin altera o limite.
*   **Página pública** acessível em `/terms` sem autenticação, com dark/light mode e i18n em 6 idiomas.

#### 🕒 Controle de Inatividade de Usuários

*   **ActivityTrackingMiddleware** (`backend/core/middleware.py`): Middleware ASGI não-bloqueante que registra `last_active_at` a cada request autenticado usando `asyncio.create_task` para não impactar a latência das respostas. Ignora usuários soft-deleted.
*   **Soft-delete:** Usuários que atingem o limite de inatividade têm `is_active=False` e `deleted_at` preenchido. A conta pode ser reativada pelo admin sem perda de dados (estratégias, sessões, logs preservados).
*   **SystemConfig:** Nova tabela `system_config` (key-value) para configurações globais. `INACTIVITY_LIMIT_DAYS` (padrão: 90 dias) controla o limite de inatividade e é alterável pelo admin via painel sem rebuild ou redeploy.
*   **Aviso automático:** Task background `check_inactive_users()` roda diariamente às 10:00 UTC. Envia aviso via Telegram 1 dia antes do prazo. Realiza soft-delete automaticamente ao atingir o limite. Não duplica avisos no mesmo dia.
*   **Isenção por usuário:** Campo `inactivity_exempt` permite excluir usuários específicos (ex: admin, clientes VIP) da política de inatividade.
*   **API Admin:** `GET/POST /api/admin/system/inactivity-config` (ler/alterar limite global), `PATCH /api/admin/users/{id}/inactivity` (ativar/remover isenção), `POST /api/admin/users/{id}/send-inactivity-warning` (aviso manual via Telegram), `DELETE /api/admin/users/{id}` (soft-delete manual).
*   **Endpoint público:** `GET /api/user/inactivity-limit` — retorna o limite atual sem autenticação (consumido pelos Termos de Uso para exibição dinâmica).
*   **UI Admin:** Coluna "Última Atividade" com tempo relativo (agora / Xmin / Xh / Xd) na tabela de usuários, badge "Deletado" para contas soft-deleted, botões "Alertar" (aviso Telegram) e "Deletar" por linha, painel de configuração do limite de inatividade na aba "Configurações".

### 🔬 CI/CD, OpenAPI & Cobertura de Testes (v7.2)

*   **GitHub Actions CI:** Pipeline automático em todo push para `main`. Dois jobs paralelos: (1) backend — instala deps, roda `ruff` (lint) e `pytest` com cobertura; (2) frontend — `npm ci`, lint e `next build`. O relatório de cobertura é salvo como artefato do run (30 dias).
*   **129 testes passando, 45% de cobertura** do backend. Execução via SQLite in-memory, zero dependências externas. Destaques por módulo:
    *   `core/indicators.py` — **100%** (25 funções: EMA, SMA, RSI, MACD, Bollinger, Donchian, Z-Score, Stochastic, sinais de entrada/saída)
    *   `core/metrics.py` — **100%** (calculate\_trade\_metrics, calculate\_drawdown, validate\_ftmo)
    *   `core/backtest.py` — **93%** (BacktestEngine completo: run, simulate, PnL, fee, equity curve)
    *   10 implementações de estratégia — **100%** cada (RSI Reversal, Golden Cross, MACD, Bollinger, Donchian, Trend Following, Volume Breakout, EMA+RSI, MACD+RSI, Stochastic)
    *   `core/security.py`, `core/tier_config.py`, `core/rate_limit.py` — cobertura alta
    *   O teto natural é ~55–60%: módulos como `paper_trading/engine`, `notifications` e `tasks` requerem mocks de WebSocket/Telegram para cobertura adicional
*   **OpenAPI público para MCPs:** Schema OpenAPI 3.1 com metadados completos (versão, contato, licença, tags com descrição por módulo). Estratégia de exposição:
    *   **Schema JSON:** `GET /api/openapi.json` — público em produção, consumido por MCPs, Postman e Insomnia. Rotas `/api/admin/*` omitidas do schema público (`include_in_schema=False`).
    *   **Swagger UI:** `GET /api/docs` — disponível apenas em desenvolvimento (`ENVIRONMENT != production`). Desabilitado em produção para reduzir superfície de ataque.
    *   **ReDoc:** `GET /api/redoc` — idem, apenas em desenvolvimento.
    *   **No repo:** [`docs/openapi.json`](docs/openapi.json) — 53 endpoints públicos versionados (68 total incluindo admin).
*   **Script de export:** `python backend/scripts/export_openapi.py` regenera `docs/openapi.json` localmente sem precisar subir o servidor.

```bash
# Rodar testes com cobertura localmente
cd backend
DATABASE_URL="sqlite:///:memory:" JWT_SECRET_KEY="test-secret-key-32-bytes-minimum!!" \
ENCRYPTION_KEY="nSo9pQzaOxO8UR5HjnoPj8Tbgno7FGDj6I3a9T9nPss=" \
ENVIRONMENT="test" python -m pytest
# Relatório HTML em docs/coverage/index.html
```

### 🪵 Logs Estruturados & Rotação (v7.1)

*   **Zero `print()` em produção:** Todo o código de produção (`backend/core/` e `backend/api/routes/`) foi migrado de `print()` para o `StructuredLogger`. Cada evento emite JSON com `timestamp`, `level`, `message` e contexto estruturado (`session_id`, `exchange`, `error`, etc.), facilitando grep e filtragem.
*   **Rotação de logs automática:** Os 3 containers (db, backend, frontend) agora têm `logging.max-size` e `logging.max-file` configurados no `docker-compose.yml`. O backend mantém até 50 MB de histórico rotacionado (5 × 10 MB), persistindo entre restarts. Sem risco de disco cheio por logs crescentes.
*   **Acesso rápido:**

```bash
docker compose logs -f backend           # stream ao vivo
docker compose logs --since 1h backend  # última hora
docker compose logs --tail 200 backend  # últimas 200 linhas
```

### v4.0 Final Polish

Refatoração completa da camada visual e arquitetural do frontend:

### 🌍 Internacionalização Dinâmica (i18n) Completa
*   **Tradução de Erros da API:** Todas as mensagens de erro e validações do Pydantic nas rotas (Auth, Usuário, Trading, Admin) são traduzidas dinamicamente via `backend/locales/` cobrindo 6 idiomas (pt-BR, en, es, zh, ja, ko).
*   **Gestão Dinâmica do Frontend:** Componentes como Glossário e Descrições de Estratégias agora buscam seus metadados totalmente renderizados para o idioma nativo via `next-intl`.
*   **Localidade Isolada do Usuário:** O `locale` do painel é salvo individualmente e dita o idioma global da UI e de **Alertas do Telegram (Heartbeats)** enviados pela plataforma periodicamente.
*   **Painel e Trading Traduzidos:** Remoção de placeholders em português hardcoded antigos. Todo o Painel de Usuário, Gráficos Interativos, Detalhes de Sessão de Paper Trading e Construtor de Estratégias foram adequados ao i18n global de 6 idiomas.
*   **Telegram Customizável por Robô:** Cada nova sessão de Paper Trading agora permite a escolha de um idioma exato independente (ex: UI em Inglês recebendo Alertas Diários de Sinais/Balance em Turco ou Japonês).
*   **Arquitetura Modular:** Configuração centralizada em `frontend/src/config/locales.ts` (flags, labels) e imports dinâmicos no `LocaleContext`. Para adicionar um novo idioma: (1) criar o `.json` em `frontend/messages/` e `backend/locales/`, (2) registrar no `config/locales.ts` com código, flag e nome. O backend autodetecta os `.json` sem alteração de código.
*   **Sincronização de Traduções:** `python scripts/sync_locales.py` compara todos os locales com `pt-BR` e lista chaves faltantes — útil após adicionar novas strings.

### 🎨 UI & UX Refinado e Otimizado
*   **Tailwind CSS v4 Nativo:** Migração completa para a nova engine do Tailwind, com arquitetura limpa focada em CSS variables nativas, `bg-card`, `text-foreground`.
*   **Validação de Autenticação Polida:** Substituição completa das validações *tooltip* nativas do navegador com os idiomas operacionais incorretos em favor de States React gerenciados, garantindo uniformidade idiomática nos formulários de **Login** e **Registro**.
*   **Dark/Light Mode Perfeito:** Contraste harmonioso em modais, links da página (Termos de Uso renderizados impecavelmente via tags ricas), e legibilidade consistente.
*   **Performance:** CSS otimizado, sem `!important` desnecessários, com componentes padronizados focados em reusabilidade.

---

### ⚡ Instalação Rápida (Docker)
A maneira mais fácil de rodar o projeto completo (Frontend + Backend + Banco de Dados):

```bash
# Opção 1: Script padrão (recomendado — builda, sobe e abre o navegador)
./start_gastor.sh

# Opção 2: Manual
docker compose up --build
```
> 🚀 **Nota:** O build agora utiliza `uv` e multi-stage builds, resultando em imagens 70% menores e instalação muito mais rápida.

Acesse:
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

### ☢️ Limpeza Total (Reset Docker / Nuke Deploy)
Se precisar zerar tudo (containers, volumes e imagens) e recomeçar do zero, ou formatar a VPS para uma instalação nova:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh nuke
```
> ⚠️ **Atenção:** Isso remove TODOS os resíduos do Docker (incluindo o banco de dados e os usuários cadastrados) e faz um deploy limpo. É a forma mais garantida de aplicar atualizações estruturais profundas sem conflitos de cache, pois o banco de dados já subirá atualizado com as novas colunas. Para deploy normal sem perda de dados na VPS, use apenas `./scripts/deploy.sh`.

### 🛠️ Instalação Manual (Desenvolvimento)

#### Backend (API)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend (Interface)
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 Fontes de Dados

O Gastor suporta múltiplas fontes de dados com fallback automático. Escolha na sidebar qual utilizar:

| Fonte | Ícone | Descrição | Limitações |
|-------|-------|-----------|------------|
| **Automático** | 🔄 | Tenta todas as fontes até uma funcionar | - |
| **CCXT (Binance)** | 🟡 | Exchange Binance via CCXT - Melhor qualidade | Bloqueado em algumas regiões |
| **CCXT (BinanceUS)** | 🇺🇸 | Exchange BinanceUS - Funciona em mais regiões | Menos pares disponíveis |
| **CCXT (Bybit)** | 🟠 | Exchange Bybit via CCXT | Unified Account |
| **CCXT (OKX)** | 🔵 | Exchange OKX via CCXT | Requer passphrase na API |
| **CoinGecko** | 🦎 | Agregador gratuito sem restrições geográficas | 30 calls/min, dados menos granulares |
| **CryptoCompare** | 📊 | API gratuita robusta | 100k calls/mês |

**Cadeia de fallback automática:** Binance → BinanceUS → Bybit → OKX → CryptoCompare → CoinGecko.

> 💡 **Dica:** Use **Automático** para que o sistema escolha a melhor fonte disponível. Se estiver em uma região com restrições, o sistema tenta automaticamente as outras exchanges e agregadores.

---

## 🌍 O Desafio das Prop Firms (FTMO)

### O que são Prop Firms?
**Proprietary Trading Firms** (Mesas Proprietárias) são empresas que disponibilizam seu próprio capital para traders operarem. Em vez de arriscar seu dinheiro, você opera o dinheiro da empresa e fica com a maior parte do lucro (geralmente **80-90%**).

Para acessar esse capital, você precisa passar por um **Challenge** (teste) rigoroso que prova sua consistência e gestão de risco.

### Por que FTMO?
A **[FTMO](https://ftmo.com)** é líder global e amplamente considerada uma das prop firms mais sólidas e confiáveis do mercado.
- 🏢 **Reputação:** Paga seus traders consistentemente desde 2015 via transferência bancária ou cripto.
- ⚖️ **Regras Claras:** Sem "pegadinhas" ocultas. Limites de drawdown e perda diária bem definidos.
- 📈 **Escalabilidade:** Planos de crescimento (Scaling Plan) que aumentam o capital sob gestão.

### O Papel do GASTOR
O **Gastor** foi desenhado com o **FTMO Challenge** em mente. O sistema verifica automaticamente se suas estratégias passariam no teste, monitorando em tempo real:
- ✅ Se o lucro atinge a meta (+10%)
- ✅ Se o Drawdown respeita o limite (-10%)
- ✅ Se a perda diária não excede o permitido (-5%)

---

## 🔐 Autenticação e Segurança

O Gastor agora conta com um sistema completo de gerenciamento de identidade:

### Funcionalidades
- **Login/Registro:** Crie conta com Email/Senha ou **Google One Tap** (Requer código de convite).
- **Sistema de Convites:** O registro é restrito. Novos usuários precisam de um **Código de Convite** válido fornecido por um administrador.
- **Recuperação de Acesso:** Em caso de perda de senha, entre em contato via Telegram com o administrador para reset manual.
- **Gestão de Perfil:** Altere seu nome de usuário e senha em `/settings/profile`. A configuração de APIs externas (chaves de exchange e API key da Aura/LLM) foi centralizada em **Painel do Usuário → Integrações** (`/user/panel`), com sub-abas Exchanges e IA & Assistente.
- **Segurança:** Senhas criptografadas com `bcrypt` e sessões via **JWT** (JSON Web Tokens).
- **Proteção de Dados:** Cada usuário vê apenas suas próprias estratégias, sessões de paper trading e configurações.
- **Integração OAuth:** Login social com Google para acesso rápido e seguro. A `redirect_uri` é derivada automaticamente: em dev (`localhost`) usa `/api/auth/google/callback` (com redirect nginx), em produção usa `/auth/google/callback`.
- **Termos de Uso v3.0:** Documento legal completo com 13 seções, incluindo a nova **Seção 5 — Inteligência Artificial (Aura)** que cobre BYOK, transferência a provedores LLM, compromisso de não-treinamento com dados do usuário, riscos próprios da IA (alucinação, tool calls, indisponibilidade, custos), clientes MCP externos (Claude Desktop/Cursor/VS Code) e segurança do JWT. Seção 11 (Inatividade) dinâmica via `GET /api/user/inactivity-limit`. Consentimento explícito obrigatório no registro e login. Página pública `/terms` acessível sem autenticação.
- **Controle de Cotas:** Limites de uso (Rate Limit e Sessões) individualizados e gerenciáveis pelo admin.
- **Sistema Freemium (3 Tiers):** Free, Pro e Desk — cada tier define sessões, features (Grid Search, Testnet, Multi-exchange, Decision Logs Export) e rate limit. Tier atribuído via invite code no registro, com upgrade manual pelo admin.
- **Validade de Assinatura e Downgrade Automático:** Cada plano pago (Pro/Desk) pode ter um prazo definido (`subscription_days` no invite code; `plan_tier_expires_at` em `users`). Ao expirar, a tarefa em background `check_expired_subscriptions` (executa **diariamente às 08:00 UTC**) faz **downgrade automático para Free**, ajusta as quotas via `apply_tier_quotas()` e dispara um alerta no Telegram do admin. **Sem perda de dados:** estratégias, sessões, decision logs e chaves de API ficam intactos — apenas os limites diminuem. **Renovação:** o admin acessa o painel `/admin`, clica em "Tier" no usuário e preenche o novo tier + duração em dias no modal — pode ser feita antes ou depois da expiração. Para o usuário, o User Panel exibe a data de expiração em âmbar nos últimos 7 dias e em vermelho após expirada (ainda que com Free no DB se o cron já rodou).
- **Soft Delete de Invite Codes (auditoria):** Códigos de convite têm tratamento dual no botão "Excluir":
    - **Códigos nunca usados** (`uses_count = 0`): hard delete (DELETE FROM). Sem usuários associados, sem perda de auditoria.
    - **Códigos já usados** (`uses_count > 0`): **soft delete** — `revoked_at = now()` é gravado e `is_active` vai para `false`. A linha continua na tabela, preservando o link em `users.invited_by_code` para auditoria forense ("quem entrou com qual código, quando").
    - **Re-emissão**: o índice parcial `UNIQUE(code) WHERE revoked_at IS NULL` permite criar um novo código com a mesma string depois de revogar o antigo. Cada versão é uma row distinta com `id`, `created_at` e `subscription_days` próprios.
    - **Defesa em profundidade**: `register()` e `validate-invite-code` filtram explicitamente `revoked_at IS NULL` na query, mesmo com o índice parcial garantindo a unicidade.
    - **UI**: na tabela do admin, códigos revogados aparecem em opacity reduzida com badge "Revogado" e data de revogação. Botões Ativar/Revogar somem (não há ação possível além de auditoria). O botão muda de "Excluir" para "Revogar" quando o código já foi usado, com texto de confirmação distinto.

### 🛡️ Isolamento de Sessão & Paper Trading Persistente

O Gastor introduz um poderoso sistema de **Sessões Persistentes e Resilientes**:
- **Slots por Tier:** Cada usuário tem direito a rodar sessões simultâneas conforme seu tier (Free: 1, Pro: 2, Desk: 5).
- **Background Execution:** As sessões continuam rodando no servidor mesmo se você fechar o navegador ou deslogar.
- **State Restoration:** Ao logar novamente, o frontend recupera automaticamente o estado das suas sessões ativas.
- **Auto-Recovery:** Se o servidor reiniciar, todas as sessões ativas são restauradas automaticamente (engines + WebSocket).
- **Watchdog WebSocket:** Streams silenciosos por mais de 5 minutos são reconectados automaticamente.
- **Detecção de Sessões Órfãs:** A cada 5 minutos, o sistema verifica se há sessões "running" sem engine ativo e restaura automaticamente, alertando o admin via Telegram.

### 🛡️ Painel Administrativo (Master User)

O sistema possui um painel exclusivo para administração e governança da plataforma:

- **Gestão de Usuários:** 
  - Listagem completa com status em tempo real.
  - **Bloquear/Desbloquear:** Suspender acesso temporariamente.
  - **Reset de Senha:** Definir nova senha para usuários que perderam acesso.
- **Códigos de Convite:**
  - Criação de novos códigos com **tier associado** (Free/Pro/Desk).
  - Definição de limite de usos (ex: apenas 1 uso ou ilimitado).
  - Monitoramento de uso e desativação de códigos.
- **Gestão de Tiers:**
  - Coluna "Tier" com badges coloridos na tabela de usuários e invite codes.
  - Alterar tier de qualquer usuário (auto-ajusta quotas de sessões e rate limit).
- **Monitoramento de Recursos:** CPU, RAM, latência HTTP (média e P95), erros HTTP e uptime atualizados a cada 5s. Cards dedicados para sessões de paper trading ativas e traders operando.
- **Configuração Global:** Alteração dinâmica de parâmetros do sistema via painel — **Limite Máximo de Usuários** e **Limite de Inatividade** (dias) — sem necessidade de rebuild.
- **Controle de Inatividade:**
  - Coluna "Última Atividade" na tabela de usuários com tempo relativo.
  - Badge "Deletado" para contas soft-deleted (conta desativada, dados preservados).
  - Botões "Alertar" (envia aviso Telegram) e "Deletar" (soft-delete manual) por usuário.
  - Campo "Isento de Inatividade" para excluir usuários específicos da política (ex: VIPs).
  - Configuração do `INACTIVITY_LIMIT_DAYS` na aba Configurações (padrão: 90 dias).
- **Gestão de Cotas:** Controle granular de recursos por usuário:
  - **Rate Limit Multiplier:** Ajuste de limites de requisição por usuário (ex: VIPs têm 2x mais requests).
  - **Max Active Strategies:** Limite de sessões simultâneas de Paper Trading (Padrão: 5).
- **Notificações de Admin:** O administrador recebe alertas no Telegram sobre novos cadastros e eventos críticos do sistema.

### 🖥️ Planejamento de Capacidade (VPS KVM 2 - 8GB)

Baseado no perfil do servidor **KVM 2 (8GB RAM, 2 vCPU)**, aqui está a estimativa realista de capacidade rodando o stack completo via Docker (Frontend + Backend + Banco de Dados):

1. **Overhead do Sistema:**
   - Sistema Operacional + Docker Daemon: ~500MB
   - Banco de Dados (Postgres): ~300MB
   - Backend (API ociosa): ~200MB
   - Frontend (Next.js Server): ~200MB
   - **Total Reservado:** ~1.2 GB

2. **Memória Disponível para Sessões:** ~6.8 GB

3. **Capacidade Real (Paper Trading):**
   Considerando consumo médio de **70MB a 100MB** por sessão ativa (WebSocket + Estratégia em memória):

| Perfil de Uso | Limite Sugerido | O que isso significa? |
| :--- | :---: | :--- |
| **Sessões Isoladas** | **~65-70** | Total de robôs rodando simultaneamente no servidor. |
| **Usuários "Heavy"** | **~13** | Usuários rodando 5 estratégias (full slots) ao mesmo tempo. |
| **Usuários "Médios"** | **~30-35** | Usuários rodando 2 estratégias em média. |

> 🚀 **Veredito:** O plano **KVM 2 (8GB)** é excelente para iniciar. Ele suporta confortavelmente um grupo de **30 traders ativos** sem gargalos de memória. O limitador secundário será a CPU (2 cores) caso todos tentem processar backtests pesados no Otimizador simultaneamente.

---

## 📱 Navegação e Interface
 
 ```mermaid
 graph LR
     subgraph Main Navigation
     A["📈 Dashboard"] --> B["📊 Resultados"]
     B --> C["🧪 Laboratório"]
     C --> D["⚙️ Otimizador"]
     D --> E["🛠️ Construtor"]
     E --> F["🎮 Live Trading"]
     end

     subgraph Live Trading
     F --> F1["Paper Trading"]
     F --> F2["🧪 Testnet"]
     end

     subgraph User Menu
     F -.-> G["📚 Glossário"]
     F -.-> H["⚙️ Perfil & Config"]
     F -.-> I["👤 Painel do Usuário"]
     F -.-> J["📄 Termos de Uso"]
     end

     style A fill:#10b981,stroke:#059669,color:#fff
     style B fill:#f59e0b,stroke:#d97706,color:#fff
     style C fill:#8b5cf6,stroke:#7c3aed,color:#fff
     style D fill:#3b82f6,stroke:#2563eb,color:#fff
     style E fill:#ec4899,stroke:#db2777,color:#fff
     style F fill:#22c55e,stroke:#16a34a,color:#fff
     style F1 fill:#3b82f6,stroke:#2563eb,color:#fff
     style F2 fill:#ca8a04,stroke:#a16207,color:#fff
     style G fill:#14b8a6,stroke:#0d9488,color:#fff
     style H fill:#6366f1,stroke:#4f46e5,color:#fff
     style I fill:#6366f1,stroke:#4f46e5,color:#fff
     style J fill:#6366f1,stroke:#4f46e5,color:#fff
 ```

> 📱 **Responsivo:** O menu de navegação é idêntico em desktop e mobile. Todos os itens (Painel do Usuário, Glossário, Termos de Uso, Perfil) aparecem em ambas as versões.

> 🏠 **Landing Page:** A rota `/` é uma página pública de apresentação do produto (acessível sem login). O Dashboard fica em `/dashboard`. Links de navegação são exibidos apenas para usuários autenticados.

---

### 📈 Dashboard (Análise de Mercado)

Painel central para monitoramento de mercado e análise técnica em tempo real:

<!-- ![Dashboard Tab](image/dashboard.png) -->
> *[Imagem do Dashboard em breve]*

| Funcionalidade | Descrição |
|----------------|-----------|
| **Gráfico Interativo** | Candlestick Chart com zoom e pan suaves |
| **Indicadores Técnicos** | Médias Móveis (9/21), RSI (14) e Volume |
| **Múltiplos Timeframes** | De 1 minuto (Scalping) a 1 dia (Swing Trade) |
| **Seleção de Fonte** | Alterne entre Binance, CoinGecko ou Automático |
| **Resumo de Mercado** | Preço Atual, Variação 24h e RSI em destaque |
| **Atualizar / Resetar** | Após carregar dados, botões para recarregar ou limpar tudo |

> **💡 Dica:** O Dashboard é o ponto de partida para analisar o estado atual do mercado antes de rodar os backtests.


---

### 📊 Resultados (Dashboard de Performance)

Dashboard completo com métricas de trading e comparativo FTMO. Inclui botões de **Atualizar** (re-fetch dos dados) e **Resetar** (limpar métricas).

<!-- ![Results Dashboard](image/results.png) -->
> *[Imagem do Dashboard de Resultados em breve]*

**Comparativo FTMO Challenge:**

| Regra | Limite | Descrição |
|-------|--------|-----------|
| Meta de Lucro | **+10%** | Atingir 10% de lucro |
| Max Drawdown | **-10%** | Patrimônio não pode cair mais de 10% |
| Max Loss Diária | **-5%** | Perda máxima em um único dia |
| Dias de Trading | **4** | Mínimo de dias com operações |

---

### 🧪 Laboratório de Estratégias

11 estratégias pré-configuradas disponíveis para todos os usuários:

<!-- ![Strategies Lab](image/strategies.png) -->
> *[Imagem do Laboratório de Estratégias em breve]*

| Categoria | Estratégias |
|-----------|-------------|
| 📈 Tendência | Golden Cross, Trend Following |
| 🔄 Reversão | RSI Reversal |
| ⚡ Momentum | MACD Crossover |
| 🔗 Híbridas | EMA+RSI, MACD+RSI, **Win First** 🏆 |
| 🚀 Breakout | Donchian, Volume |
| 🎢 Outras | Stochastic RSI, Bollinger Bounce |

> **Admin-only:** As estratégias `Spring Loaded (FTMO)` e `Win First (FTMO)` são estratégias personalizadas do administrador — visíveis apenas no painel admin e editáveis no Construtor.

---

#### 🏆 Estratégia em Destaque: Win First

> **Campeã da Pesquisa Exaustiva** — Validada em **88.704 backtests** | 6 pares × 3 timeframes × 90 dias | Train/Test split anti-overfitting

| Métrica | Train (60d) | Test (30d) | Full (90d) |
|---------|:-----------:|:----------:|:----------:|
| **PnL** | +1.24% | +2.18% ✅ | **+3.80%** |
| **Win Rate** | 66.4% | 78.8% | **70%** |
| **Max Drawdown** | — | — | **-4.9%** |
| **Score** | — | — | **56.5/100** |

**Lógica:**
- **Compra:** RSI(14) < 30 quando EMA(21) > EMA(50) > EMA(100) — dip em tendência forte
- **Saída:** TP +1.5% / SL -2.0% + Trailing Stop (ativa em +1%, trail 0.5%)

> 💡 **Insight:** O WR *subiu* de 66% no train para 79% no test → não é overfitting. Todas as top 15 estratégias usam filtro de tendência.

> [!WARNING]
> **Win First × FTMO Challenge:** Esta estratégia **não passaria** no desafio FTMO.
> Com R:R de 0.75 (TP 1.5% / SL 2%), o PnL é insuficiente para atingir +10%.
> Para FTMO, a pesquisa v5b identificou estratégias de **breakout** como viáveis — veja a seção [Pesquisa FTMO Challenge](#-pesquisa-ftmo-challenge-research-v5b).
> **Uso ideal:** Capital próprio com foco em consistência e preservação de capital.

---

#### 🏆 Estratégia FTMO: Spring Loaded

> **Campeã do FTMO Challenge** — Identificada em **108.864 simulações** | Pass Rate 56% (10/18 cenários) | ~2–3 semanas para passagem

| Métrica | Valor |
|---------|-------|
| **Pass Rate FTMO** | 56% (10 de 18 cenários) |
| **Retorno Médio** | +4,0% |
| **Win Rate** | ~47% |
| **Risk:Reward** | ≈ 1:5 |
| **Max Drawdown** | -11,4% |

**Lógica:**
- **Compra:** BB Squeeze nas últimas 3 velas → BB Expand agora + EMA21 > EMA50
- **Saída:** TP +7% / SL -1.5% + Trailing Stop (ativa em +3%, trail 1.5%)

> 💡 **Disponibilidade:** Esta estratégia é exclusiva do administrador e aparece em "Minhas Estratégias" no painel admin. O Seed é automático a cada `docker compose up`.

---

**Funcionalidades Avançadas:**

| Recurso | Descrição |
|---------|----------|
| **Juros Compostos** | Reinveste lucros automaticamente |
| **Sizing por ATR** | Ajusta tamanho da posição pela volatilidade |
| **Sizing por RSI** | Posições maiores em oversold extremo |
| **Force Close** | Fecha posições abertas no fim do período |

---

### ⚙️ Otimizador de Estratégias

Grid Search automático para encontrar os melhores parâmetros:

| Funcionalidade | Descrição |
|----------------|-----------|
| **Grid Search** | Testa todas as combinações de parâmetros |
| **Otimização de Execução** | Testa Juros Compostos + Sizing Dinâmico |
| **Filtro de Mínimo de Pares** | Ignora estratégias com poucos trades (evita overfitting) |
| **Ranking Automático** | Ordena por PnL, Win Rate ou Drawdown |
| **Aviso de Significância** | Alerta quando campeã tem ≤3 pares |
| **Aplicar Campeã** | Um clique para usar a melhor configuração |

**Métricas calculadas:**
- Total PnL %
- Win Rate %
- Max Drawdown %
- Total de Pares (BUY+SELL completos)

> ⚠️ **Importante:** Resultados são reprodutíveis (seed fixo no sampling). Apenas trades completos são contados (sem force_close na avaliação).

---

### 🛠️ Construtor de Estratégias

Crie suas próprias estratégias personalizadas combinando regras e indicadores:

| Funcionalidade | Descrição |
|----------------|-----------|
| **18 Indicadores** | RSI, EMA, SMA, Bollinger, MACD, ATR, Z-Score, Stochastic e mais |
| **Grupos Aninhados** | Combine regras com lógica AND/OR em múltiplos grupos |
| **Preview em Tempo Real** | Visualize a regra em linguagem natural (ex: "RSI(14) < 30") |
| **Persistência** | Salve, carregue e gerencie suas estratégias personalizadas |
| **Validação de Escala** | Impede comparações sem sentido (ex: RSI vs Preço de Entrada) |

#### 🛡️ Gestão de Risco (Stop Loss / Take Profit)

Seção dedicada para definir critérios de saída baseados no PnL líquido (já descontando taxas de compra e venda):

| Funcionalidade | Descrição |
|----------------|-----------|
| **Stop Loss** | Vende automaticamente se prejuízo líquido exceder X% (ex: -3%) |
| **Take Profit** | Vende automaticamente se lucro líquido atingir X% (ex: +1%) |
| **OR com Regras** | SL/TP funcionam como **OR** com as regras manuais de venda |
| **Badges Visuais** | Indicadores 🛡️ SL e 🎯 TP aparecem na seção de Regras de Venda |

#### 📍 Indicadores de Posição (Sell Only)

Indicadores virtuais que dependem do preço de entrada da posição atual:

| Indicador | O que representa | % Ajuste |
|-----------|------------------|----------|
| **Preço de Entrada** | Preço exato da compra | Sim (ex: +2% = preço de entrada + 2%) |
| **Break-Even (+ Taxas)** | Preço mínimo para não ter prejuízo, incluindo taxas | Sim (ex: +1% = margem de segurança) |
| **PnL % da Posição** | Lucro/prejuízo líquido atual em % | Não (compara com constante %) |

#### 🔒 Validação de Escala

O sistema impede comparações que não fazem sentido entre indicadores de escalas diferentes:

| Escala | Indicadores | Só compara com |
|--------|-------------|----------------|
| **Preço** | Close, EMA, SMA, BB, ATR, Mediana, MAD, Entry Price, Entry Cost | Outros de preço |
| **Oscilador** | RSI, MACD, Stochastic %K, Z-Score | Outros osciladores |
| **Volume** | Volume, Média de Volume | Outros de volume |
| **Percentual** | PnL % | Sempre valor constante (%) |

**Exemplo de Estratégia Complexa:**
```
COMPRAR quando:
  (RSI(14) < 30 AND Preço < Bollinger_Lower)
  OR
  (MACD > Signal AND Volume > Volume_MA)

VENDER quando:
  (RSI(14) > 70)
  OR
  🛡️ Stop Loss: PnL < -3%
  🎯 Take Profit: PnL > +1%
```

---

### 📖 Glossário Interativo (Educação)

Uma enciclopédia completa integrada ao app para aprender trading do zero:

| Recurso | Descrição |
|---------|-----------|
| **Conceitos Básicos** | Explicações didáticas sobre Candles, Timeframes e Mercado |
| **Fórmulas Detalhadas** | Todas as equações matemáticas explicadas elemento por elemento |
| **Analogias** | Comparações do dia a dia para facilitar o entendimento (ex: RSI = corredor cansado) |
| **Categorias** | Médias Móveis, Osciladores, Volatilidade e Termos Gerais |

> 📚 **Objetivo:** Tornar o trading acessível para iniciantes, explicando não apenas "o que" é um indicador, mas "como" ele é calculado e "por que" ele funciona.

---

### ⚙️ Configurações de Taxas

Personalize as taxas de trading usadas nos backtests:

| Funcionalidade | Descrição |
|----------------|-----------|
| **Tabela de Taxas** | Visualize Exchange Fee + Slippage de cada moeda |
| **Editor Global** | Modifique a taxa de exchange (padrão: 0.10%) |
| **Editor por Moeda** | Ajuste o slippage individualmente por ativo |
| **Restaurar Padrões** | Volte aos valores conservadores pré-definidos |

> ⚠️ **Dica:** Taxas mais realistas geram backtests mais confiáveis. Moedas menos líquidas (DOGE, AVAX) têm maior slippage.

---

### 🎮 Live Trading — Paper & Testnet (Multi-Exchange)

Teste suas estratégias com preços reais de **Binance**, **Bybit** ou **OKX**. Dois modos disponíveis:

| Modo | Descrição | Ordens |
|------|-----------|--------|
| **Paper Trading** | Simulação interna com preços ao vivo | Apenas no banco de dados |
| **Testnet** | Envia ordens reais para a testnet da exchange | API Testnet/Demo (sem dinheiro real) |

#### Exchanges Suportadas

| Exchange | Testnet | Conta | Passphrase | WebSocket |
|----------|---------|-------|------------|-----------|
| **Binance** | `testnet.binance.vision` | Spot | N/A | `stream.binance.com` |
| **Bybit** | Bybit Testnet | Unified | N/A | `stream.bybit.com` |
| **OKX** | Demo Trading | Unified | Obrigatoria | `ws.okx.com` |

> **Unified Account:** Bybit e OKX utilizam contas unificadas. O sistema normaliza automaticamente o saldo (`fetch_balance` com `type: unified` para Bybit). OKX requer uma **passphrase** no cadastro da chave API, alem de API Key e Secret.

> **Precisao de Ordens (Lot Size):** Antes de cada ordem, o sistema consulta `market['precision']` via CCXT e trunca a quantidade para baixo (nunca arredonda para cima). Isso evita rejeicoes por excesso de casas decimais, que variam por exchange e por par.

| Funcionalidade | Descrição |
|----------------|-----------|
| **Multiplas Sessoes** | Rode ate 5 estrategias simultaneamente |
| **Precos ao Vivo** | WebSocket conectado a mainnet de cada exchange. Parser especifico por exchange (Binance: URL direta, Bybit/OKX: subscribe JSON pos-conexao). Watchdog anti-stale com reconexao automatica |
| **Calculo de Equity** | PnL considera saldo + valor da posicao aberta. O valor nao-realizado desconta o `entry_cost` (custo total da entrada incluindo taxa de compra), garantindo que o equity nunca seja superestimado. Veja a seção [Como o PnL é Calculado](#-como-o-pnl-é-calculado-fluxo-de-dinheiro) para detalhes |
| **Gatilhos Visuais** | Veja em tempo real quais indicadores estão ativos, com lógica AND/OR dinâmica por estratégia. Suporte a grupos de regras: `(A AND B) OR C`. Estratégias pré-definidas usam BUY=AND / SELL=OR; estratégias customizadas respeitam a lógica configurada no builder. Separadores visuais entre grupos com pills coloridos (AND azul, OR âmbar) |
| **Depositos/Saques** | Simule aportes e retiradas virtuais |
| **Notificacoes Telegram** | Receba alertas de trades no celular |
| **Reset/Delete Rapido** | Gerencie sessoes com feedback instantaneo |
| **Badges de Exchange** | Sessoes exibem badge colorido da exchange (Binance/Bybit/OKX) + badge TESTNET quando aplicavel |
| **Monitor de Saldo** | Consulte o saldo real de qualquer exchange no painel de chaves e ao iniciar sessoes |
| **Pre-flight Balance Check** | Antes de cada BUY testnet, o engine verifica o saldo real e ajusta a quantidade |
| **🧠 Aba Decisoes** | Log detalhado de cada BUY/SELL com snapshot de indicadores, regras ativas, latencia e exchange |
| **📉 FTMO Drawdown Tracking** | Max Drawdown Total (%) e Max Drawdown Diário (%) calculados em tempo real a cada candle. Usa high/low do candle para capturar pior cenário intra-candle. Reset diário à meia-noite BRT. Persistido no DB para sobreviver a restarts. Cards com cores: verde (<50% do limite), amarelo (50-80%), vermelho (≥80%) |
| **⚠️ Alertas FTMO** | Alerta Telegram opt-in quando drawdown atinge 80% dos limites FTMO (8% total ou 4% diário). Configurável no painel de notificações |

**Gerenciamento de Sessões:**
- **Nomear Sessão:** Dê um nome personalizado ao iniciar (ex: "Teste BTC Scalping") para fácil identificação.
- **Renomear:** Renomeie sessões ativas a qualquer momento clicando no ícone de lápis ✏️.

**Alocação de Capital:**

> 💡 O sistema utiliza **95% do saldo** para cada compra, reservando 5% para:
> - Taxas de trading (0.1% maker/taker)
> - Slippage em mercados voláteis
> - Margem de segurança para múltiplos trades


#### 💡 Como o PnL é Calculado (Fluxo de Dinheiro)

O cálculo de PnL no Gastor considera **todas as taxas** (compra e venda) e nunca superestima o lucro. A chave é entender o conceito de `entry_cost` — o custo total para abrir a posição.

**Exemplo numérico completo:**

| Etapa | Descrição | Valor |
|-------|-----------|------:|
| Saldo inicial | Capital disponível | $100.00 |
| Alocação (95%) | `amount_to_use` — quanto será gasto | $95.00 |
| Fee de compra (0.25%) | `fee_buy = 95 × 0.0025` | -$0.24 |
| Valor líquido de compra | `value = 95 - 0.24 = 94.76` (convertido em moedas) | $94.76 |
| Moedas compradas | `qty = 94.76 / 83.08` (preço de entrada) | 1.1405 |
| **entry_cost** | **= amount_to_use = $95.00** (custo total, inclui fee) | **$95.00** |
| Saldo após BUY | `100 - 95 = 5.00` (reserva de 5%) | $5.00 |

**Na venda (quando ocorre):**

| Etapa | Descrição | Valor |
|-------|-----------|------:|
| Valor bruto de venda | `gross = 1.1405 × 84.92` | $96.87 |
| Fee de venda (0.25%) | `fee_sell = 96.87 × 0.0025` | -$0.24 |
| Valor líquido recebido | `net_value = 96.87 - 0.24` | $96.63 |
| **PnL Realizado** | **`net_value - entry_cost = 96.63 - 95.00`** | **+$1.63** |

**PnL Não-Realizado (posição aberta):**

```
unrealized_pnl = (quantidade × preço_atual) - entry_cost
```

Exemplo: se o preço atual caiu para $82.73:
```
unrealized = (1.1405 × 82.73) - 95.00 = 94.37 - 95.00 = -$0.63
```

**Equity (patrimônio total):**

```
equity = saldo_atual + (quantidade × preço_atual)
pnl_total = equity - saldo_inicial
```

> **Por que o equity é a fonte de verdade?** Porque o `saldo_atual` já contabiliza todas as fees pagas. Ao somar o valor de mercado da posição aberta (`qty × preço`), obtemos o patrimônio real. O `pnl_total` é simplesmente `equity - saldo_inicial`.

> **Regra de consistência:** `PnL Realizado + PnL Não-Realizado ≈ PnL Total (equity)`. A diferença é apenas variação de preço em tempo real entre as consultas.

**Resumo das fórmulas:**

| Grandeza | Fórmula | Onde vive |
|----------|---------|-----------|
| `entry_cost` | `amount_to_use` (95% do saldo, inclui fee de compra) | `PaperPosition.entry_cost` |
| PnL Realizado | `(qty × preço_venda - fee_venda) - entry_cost` | `PaperTrade.pnl` (SELL) |
| PnL Não-Realizado | `(qty × preço_atual) - entry_cost` | Calculado on-the-fly pelo endpoint |
| Equity | `saldo_atual + (qty × preço_atual)` | `session.current_balance + position_value` |
| PnL Total | `equity - saldo_inicial` | Derivado |

**Como usar (Paper Trading):**

1. Vá para a aba "Live"
2. Selecione uma estratégia (pré-pronta ou custom)
3. **(Opcional)** Dê um nome para a sessão (ex: "Teste Sol Volatility") para facilitar a identificação
4. Clique em "Iniciar" e acompanhe a execução


#### 🧪 Como usar o Modo Testnet

O modo Testnet envia **ordens de mercado reais** para a testnet da exchange selecionada (Binance Testnet, Bybit Testnet ou OKX Demo Trading) — ideal para validar o fluxo completo de execução antes de operar com dinheiro real.

**Fluxo validado em produção:**

| Teste | Resultado |
|-------|-----------|
| Conectividade ao servidor testnet | ✅ Resposta em <50ms |
| Autenticação (fetch_balance) | ✅ Saldo USDT/SOL/BNB retornado |
| Ticker + Orderbook SOL/USDT | ✅ Dados ao vivo recebidos |
| BUY market order executada | ✅ `status=closed`, fill price real retornado |
| SELL market order executada | ✅ `status=closed`, ciclo BUY→SELL completo |
| Latência de execução medida | ✅ ~307ms (BUY) / ~312ms (SELL) |

> 💡 A latência de ~310ms é capturada automaticamente em `ws_latency_ms` e `signal_latency_ms` no log de cada decisão.

---

### 🧠 Aba Decisões (Trade Decision Logs)

Cada BUY e SELL executado — em Paper Trading, Testnet ou Backtest — gera automaticamente um log detalhado com o estado completo do mercado no momento da decisão.

| Dado capturado | Descrição |
|----------------|-----------|
| **Indicadores** | Snapshot enriquecido com ~35 indicadores (RSI, EMA, SMA, MACD, Bollinger, Stochastic, ATR, Donchian, ROC, Z-Score, Median, MAD, Robust Z-Score, Volume Ratio) — independente da estratégia ativa |
| **Candle** | OHLCV do candle que gerou o sinal |
| **Regras ativas** | Lista das condições que foram satisfeitas (ex: `RSI(14) < 30`) |
| **Motivo de saída** | `take_profit` · `stop_loss` · `trailing_stop` · `signal` · `manual` |
| **Contexto financeiro** | Preço de entrada/saída, quantidade, taxas, saldo antes/depois, PnL |
| **Latência** | Tempo do WebSocket ao trade (`ws_latency_ms`) e do sinal à execução (`signal_latency_ms`) |

O par BUY + SELL de uma operação compartilha um `trade_pair_id` (UUID), permitindo **exportar exemplos de treinamento para ML**: features do momento da entrada → label do resultado.

**Endpoints de export disponíveis:**
- `GET /api/decision-logs/export?format=csv&session_id=X` — CSV flat para análise em planilhas
- `GET /api/decision-logs/export?format=jsonl&paired=true&session_id=X` — JSONL com pares BUY+SELL completos para fine-tuning de modelos
- Filtro por exchange: `?exchange_name=bybit` — para análise comparativa entre exchanges

> 🔑 Todos os logs são isolados por usuário (JWT) e incluem o campo `exchange_name` para identificar qual exchange executou cada trade. Admins podem acessar logs de outros usuários via `?user_id=X`.

---

**Seed automático da chave no startup (admin):**

O `promote_admin.py` cria automaticamente a chave testnet para o admin no primeiro `docker compose up`, lendo as variáveis de ambiente e **criptografando com Fernet antes de salvar no banco**. A operação é idempotente — nunca duplica.

```bash
# No .env, adicione as chaves obtidas em testnet.binance.vision:
ADMIN_TESTNET_API_KEY=sua_api_key_aqui
ADMIN_TESTNET_API_SECRET=seu_api_secret_aqui
```

Saída esperada no startup:
```
  Chave Binance Testnet criada com sucesso (criptografada no banco).
```
Nos restarts seguintes:
```
  Chave testnet já existe: 'Binance Testnet (seed)' — sem alteração.
```

> ⚠️ **As chaves da Binance Testnet vencem em ~30 dias.** Quando isso ocorrer, as ordens falharão com `AuthenticationError`. Para renovar:
> 1. Acesse [testnet.binance.vision](https://testnet.binance.vision) → **Generate HMAC_SHA256 Key**
> 2. Atualize `ADMIN_TESTNET_API_KEY` e `ADMIN_TESTNET_API_SECRET` no `.env`
> 3. Delete a chave antiga em **Settings → Chaves API** (ou diretamente no banco)
> 4. Reinicie: `docker compose restart backend` — o seed criará uma nova entrada automaticamente

---

**Como adicionar a chave manualmente (usuários não-admin):**

1. Acesse [testnet.binance.vision](https://testnet.binance.vision)
2. Faça login com sua conta GitHub
3. Clique em **"Generate HMAC_SHA256 Key"**
4. Copie a **API Key** e o **Secret Key** (o Secret aparece **apenas uma vez**)

> ⚠️ As chaves da Testnet **não funcionam** na Binance real e vice-versa. São ambientes completamente separados.

**Cadastrar a chave no Gastor:**

1. Vá para **Settings → Chaves API**
2. Clique em "Adicionar Chave"
3. Selecione a **exchange** (Binance, Bybit ou OKX)
4. Preencha Label, API Key e Secret Key
5. Para **OKX**: preencha também a **Passphrase** (campo obrigatório)
6. Marque o checkbox de Testnet/Demo se aplicável
7. Salve

**Consultar saldo (qualquer exchange):**

1. Vá para **Settings → Chaves API**
2. Para cada chave, clique em **"Consultar Saldo"**
3. O saldo USDT disponível/total será exibido em tempo real (funciona para Binance, Bybit e OKX)
4. Use **"Atualizar"** para refrescar o saldo a qualquer momento

**Iniciar sessão Testnet:**

1. Vá para a aba **"Live"**
2. Clique em "Nova Sessão"
3. O toggle **"🧪 Testnet"** aparece automaticamente (se você tiver chaves cadastradas)
4. Selecione a chave testnet desejada — o saldo será consultado automaticamente
5. Se o saldo USDT for menor que o saldo inicial configurado, um aviso amarelo é exibido
6. Clique em **"🧪 Iniciar Testnet"**

**Verificando ordens executadas:**

- **Log do backend:** `[TESTNET] BUY SOL/USDT order placed: id=549577, fill=77.96`
- **Binance Testnet UI:** Acesse [testnet.binance.vision](https://testnet.binance.vision) → **Orders → Order History**

**Configurando Telegram (Receba alertas no celular):**

```bash
# 1. Crie um bot no @BotFather e copie o token

# 2. Obtenha seu Chat ID via @userinfobot

# 3. Adicione ao arquivo .env na raiz do projeto:
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_DEFAULT_CHAT_ID=seu_chat_id

# 4. Teste com:
cd backend && python test_telegram.py
```

**Notificações Aprimoradas (v2.0):**
- 🟢 **Trades de Compra:** Com estratégia, preço, quantidade e indicadores técnicos (contexto).
- 🔴 **Trades de Venda:** Com PnL realizado (Lucro/Prejuízo) e % de retorno.
- 🔄 **Resolução de Chat ID:** O sistema busca o `chat_id` na seguinte ordem: (1) enviado pelo frontend na criação da sessão, (2) consultado na tabela `TelegramConfig` do banco de dados, (3) campo `telegram_chat_id` do perfil do usuário. Na restauração de sessões após restart, sessões com `chat_id` vazio são preenchidas automaticamente via `TelegramConfig`.
- 💓 **Heartbeat (Relatório de Status):** Enviado a cada 6 horas BRT (00h, 06h, 12h, 18h) com:
    - Sessões Ativas
    - Saldo Global
    - Total de Trades (últimas 24h)
    - CPU e RAM do servidor.
- 🚀 **Sessão:** Alertas visuais de início e fim de operação.
- 💰 **Financeiro:** Confirmação de depósitos e saques.
- ⚠️ **Erros:** Alertas críticos com descrição do problema.
- 🕒 **Horários em BRT:** Todos os timestamps das mensagens usam horário de Brasília (UTC-3).
- 🎰 **Identificação por Slot:** Mensagens exibem "Slot 1" a "Slot 5" (e não o ID incremental do banco), evitando contadores confusos após deletar sessões.
- 📋 **Logging Completo:** Todas as notificações (envio, sucesso, falha, falha parcial) são registradas nos logs estruturados para auditoria e diagnóstico.

> 🎮 **Nota:** O Paper Trading simula ordens - nenhum dinheiro real é envolvido. Perfeito para validar estratégias antes de operar de verdade.

---

## ❓ Resolução de Problemas (FAQ)

### 1. Por que o horário do gráfico parece "atrasado"?
O sistema só processa **candles fechados** (completos). O gráfico exibe o intervalo de cada vela (ex: "21:00 – 22:00").
*   **Exemplo:** No gráfico de **1 hora (1h)**, se são **22:40**, a última vela fechada é **21:00 – 22:00**. A vela das 22:00 ainda está sendo formada e só será processada às 23:00.
*   Isso garante que trades sejam executados com dados completos, não parciais.

### 2. Por que minha estratégia mostra "Aguardando" nos gatilhos?
Estratégias robustas (como a **Spring Loaded**) exigem condições específicas de mercado para operar com segurança.
*   **Exemplo:** Se o mercado está muito volátil, o filtro de "Squeeze" (baixa volatilidade) não é atendido.
*   **Ação:** O sistema está funcionando corretamente; ele está apenas **filtrando** entradas ruins para proteger seu capital.

### 3. Erro "HTTP 404" ao conectar no Testnet?
Isso geralmente indica que a URL do WebSocket mudou ou a chave expirou.
*   O Gastor usa a URL atualizada: `wss://stream.testnet.binance.vision/ws`.
*   Verifique se suas chaves API na Binance Testnet não expiraram (elas duram ~30 dias).

---

## 🏗️ Arquitetura

```
gastor/
├── backend/                    # API FastAPI
│   ├── api/                    # Rotas (Endpoints)
│   ├── core/                   # Lógica de Negócio
│   │   ├── paper_trading/      # Módulo Paper/Testnet Trading
│   │   │   ├── engine.py       # Motor de execução (mode="paper"|"testnet")
│   │   │   ├── strategies.py   # Cálculo de triggers
│   │   │   └── signals.py      # Avaliação de sinais
│   │   ├── exchange/           # Abstração Multi-Exchange (Binance, Bybit, OKX)
│   │   │   ├── registry.py     # Config por exchange (URLs, fees, account type)
│   │   │   ├── client.py       # CCXT genérico + fetch_exchange_balance()
│   │   │   ├── order_manager.py# place_market_order() + lot size precision
│   │   │   └── symbols.py      # Normalização de símbolos (SOL/USDT ↔ WS/REST)
│   │   ├── exchange_ws.py      # WebSocket multi-exchange (kline streams)
│   │   ├── testnet/            # Aliases deprecated → exchange/
│   │   │   ├── client.py       # Delega para exchange/client.py
│   │   │   └── order_manager.py# Delega para exchange/order_manager.py
│   │   ├── strategies/         # Estratégias
│   │   │   ├── implementations/# 13 estratégias + Custom
│   │   │   │   ├── spring_loaded.py # BB Squeeze→Expand (admin)
│   │   │   │   ├── win_first.py     # RSI+EMA Uptrend (admin)
│   │   │   │   └── custom.py        # Construtor + Position Indicators
│   │   │   ├── base.py         # Classe base
│   │   │   └── factory.py      # Factory pattern
│   │   ├── indicators.py       # Indicadores técnicos
│   │   ├── decision_logger.py  # Snapshot de mercado por trade (ML dataset)
│   │   ├── rate_limit.py       # Proteção contra força bruta (Token Bucket)
│   │   ├── middleware.py       # ActivityTrackingMiddleware (last_active_at por request)
│   │   ├── logger.py           # Logger estruturado (JSON) para auditoria
│   │   ├── notifications.py    # Sistema de alertas
│   │   ├── telegram_templates.py # Templates de mensagens
│   │   ├── tier_config.py      # Config de tiers freemium (TIER_QUOTAS, require_feature)
│   │   └── backtest.py         # Motor de backtest
│   ├── scripts/                # Scripts utilitários Backend
│   │   ├── check_penetration.py # Script de Pentest (Rate Limit/Headers)
│   │   └── run_advanced_pentest.sh # Runner para ZAP/SQLMap (Docker)
│   ├── tests/                  # Testes Unitários/Integração Backend
│   └── main.py                 # Entry point + Middleware de Segurança (HSTS/CSP)
│
├── frontend/                   # Next.js Application
│   ├── src/
│   │   ├── app/                # Páginas (Next.js App Router)
│   │   │   ├── page.tsx        # Landing Page pública (Hero, Problem, Aura, Workflow, MultiExchange, DecisionLogs, FTMO, Pricing, FAQ)
│   │   │   ├── dashboard/      # Dashboard de mercado (movido de /)
│   │   │   ├── live/           # Live Trading (Paper + Testnet)
│   │   │   ├── strategies/builder/ # Construtor + Gestão de Risco
│   │   │   ├── admin/mcp/      # Painel admin de analytics MCP (v8.3)
│   │   │   └── docs/mcp/       # Documentação para clientes MCP externos (v8.3)
│   │   ├── features/live/      # Componentes da página Live
│   │   ├── lib/                # API Client e Utils
│   │   └── context/            # Global State
│   ├── public/                 # Assets (Imagens)
│   ├── nginx.conf              # Nginx config (SPA fallback + OAuth redirect)
│   └── Dockerfile              # Multi-stage build (Node → Nginx static)
│
├── research/                   # Scripts de Pesquisa (Jupyter/Python)
├── tests/                      # Testes de Regressão e Integração (Raiz)
├── scripts/                    # Scripts de Manutenção (Docker, Seeding)
├── deploy/                     # Configurações de Deploy (VPS)
│   ├── nginx/                  # Configs Nginx (HTTP + HTTPS)
│   └── setup_vps.sh            # Script de bootstrap da VPS
├── docs/                       # Documentação Adicional
├── docker-compose.prod.yml     # Override de produção
├── .env.production             # Template de variáveis de produção
├── start_gastor.sh             # Script de startup (build + open browser)
└── README.md                   # Documentação Principal
```

---

## 📚 Documentação Adicional

*   [🏗️ Arquitetura do Sistema](docs/architecture.md) — Diagramas C4 (contexto, containers, componentes), fluxo completo de trade, fluxo de autenticação, modelo ER e ADRs
*   [⚡ Benchmarks de Performance](docs/benchmarks.md) — Throughput de indicadores (até 79M candles/s), BacktestEngine, latência de API e capacidade da VPS
*   [🤖 MCP Integration & Aura](docs/mcp.md) — Servidor MCP em `/mcp`, tool catalog com tier gating, **Aura** (a assistente de IA interna), configuração LLM por usuário e clients externos (Claude Desktop, Cursor, VS Code)
*   [🛡️ Guia de Segurança](docs/SECURITY.md)
*   [❓ Perguntas Frequentes (FAQ)](docs/FAQ.md)
*   [🚀 Plano de Deploy VPS](vps.md)
*   [🤖 Instruções Claude Code](CLAUDE.md)

---

## 💰 Taxas Configuráveis

| Moeda | Exchange | Slippage | **Total** |
|-------|----------|----------|-----------|
| BTC/USDT | 0.10% | 0.10% | **0.20%** |
| ETH/USDT | 0.10% | 0.12% | **0.22%** |
| SOL/USDT | 0.10% | 0.15% | **0.25%** |
| DOGE/USDT | 0.10% | 0.20% | **0.30%** |
| AVAX/USDT | 0.10% | 0.25% | **0.35%** |

---

## 🧩 Adicionando Novas Estratégias

Crie uma nova classe em `backend/core/strategies/implementations/`:

```python
from ..base import BaseStrategy
import pandas as pd

class MinhaStrategy(BaseStrategy):
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores e gera sinais de compra/venda.
        Retorna DataFrame com colunas 'buy_signal' e 'sell_signal' (bool).
        """
        period = self.get_param("period", 14)
        # Sua lógica aqui
        df["buy_signal"] = False
        df["sell_signal"] = False
        return df
```

Depois registre em `factory.py`:
```python
STRATEGY_MAP["minha_estrategia"] = MinhaStrategy
```

---

## 🧪 Testes

### Testes de Regressão (287 assertions)

```bash
source venv/bin/activate && python tests/test_exit_criteria.py
```

| Bloco | O que testa | Assertions |
|-------|-------------|------------|
| **Fórmulas** | Break-even com 6 fee rates, PnL com/sem taxas, entry_price constante | ~15 |
| **Detecção** | pnl_pct no LHS/RHS, indicators em buy (ignora), params vazio | ~10 |
| **Stateful** | evaluate_sell_at_bar com TP, SL, AND lógica determinística | ~8 |
| **Backtest SL/TP** | 4 fee rates, TP apertado, SL apertado, condição impossível | ~100+ |
| **Regressão** | Todas as **10 estratégias pré-definidas** + alias | ~90+ |
| **Lógica Custom** | AND multi-regra, crossover, múltiplos sell groups (OR) | ~10 |
| **Edge Cases** | 10 candles, fee=0%, fee=5%, preços flat, 0 trades, operador == | ~15 |
| **Paper Trading** | Triggers com/sem posição, evaluate_signal, dados insuficientes | ~10 |
| **Consistência** | RSI native vs custom (idêntico), SL/TP gera mais trades | ~5 |

> 💡 **Nota:** Testes unitários granulares (pytest) serão reimplementados na **Fase 3 — Testes de Segurança** do roadmap.

---

## 🔒 Reprodutibilidade dos Resultados

O Gastor foi projetado para gerar **resultados consistentes** independente do dia que você rodar:

### 🛡️ Rigor na Configuração (Sem "Chutes")

O Backend opera com política de **Tolerância Zero** para configurações padrão implícitas. Isso garante reprodutibilidade total:
*   **Nada é assumido:** O Frontend DEVE enviar explicitamente `initial_balance`, `use_compound`, `include_fees` e `fee_rate` em TODAS as requisições.
*   **Validação Estrita:** Se faltar qualquer parâmetro, o sistema rejeita a operação (Erro 422), impedindo que simulações rodem com valores padrão incorretos.

### 💰 PnL Realizado (Money in the Pocket)
*   **Realized Only:** Todas as métricas de PnL (Lucro/Prejuízo) consideram APENAS trades **fechados**. Ganhos não realizados (posições abertas) não entram na conta final, simulando o saldo real disponível para saque.

### Garantias Implementadas

| Problema Evitado | Solução |
|------------------|---------|
| Amostragem aleatória diferente | `random.seed(42)` fixo no grid search |
| Posições abertas fechadas no preço atual | `force_close=False` na avaliação (só trades completos) |
| Win rate inflado por poucos trades | Filtro de "Mínimo de Pares" + aviso automático |
| Indicadores usando dados futuros | Todos usam `rolling()` e `shift(1)` (olham para trás) |

### O que NÃO causa data leak:

- **Indicadores** (RSI, EMA, Bollinger, MACD) - calculados com dados passados apenas
- **Estratégias** - usam `iloc[i-1]` para comparar com candle anterior
- **Separação OOT** - últimos 30 dias reservados e não usados no treino

> ⚠️ **Resultado diferente?** Se rodar em outro dia, os **dados novos** (candles recentes) podem mudar o resultado. Mas rodando no mesmo dia/período, o resultado será idêntico.

---

## 📦 Stack

| Categoria | Tecnologia |
|-----------|------------|
| Frontend | Next.js 16, React 19, TailwindCSS 4, Recharts, lightweight-charts |
| Backend | FastAPI, Pydantic, SQLAlchemy |
| Banco de Dados | PostgreSQL 15 |
| Exchange / Trading | CCXT (Binance, BinanceUS, Bybit, OKX — Testnet/Demo) |
| Dados | Pandas, CoinGecko API, CryptoCompare API |
| Infra Dev | Docker Compose, uv (fast Python packaging) |
| Infra Prod | Nginx, Let's Encrypt (Certbot), UFW, Hostinger KVM 2 |

---

## 🪙 Moedas Suportadas

`SOL/USDT` • `ETH/USDT` • `BTC/USDT` • `XRP/USDT` • `AVAX/USDT` • `DOGE/USDT`

---

## 🔬 Pesquisa de Estratégias (Research v3)

O Gastor inclui um motor de pesquisa exaustiva para descobrir estratégias viáveis com rigor estatístico.

### Metodologia

A pesquisa realiza uma varredura combinatória completa:

| Dimensão | Valores Testados |
|----------|------------------|
| **Sinais de Entrada** | 44 (RSI, Z-Score Robusto, Bollinger, MACD, Stochastic, drops, combinações, com/sem filtro de tendência) |
| **Take Profit** | +1.5%, +2%, +3%, +5% |
| **Stop Loss** | -1%, -1.5%, -2%, -3% + ATR dinâmico (×1.5, ×2, ×3) |
| **Trailing Stop** | Nenhum, Ativa 1%/Trail 0.5%, Ativa 2%/Trail 1%, Ativa 3%/Trail 1.5% |
| **Pares** | SOL, ETH, BTC, XRP, AVAX, DOGE (todos /USDT) |
| **Timeframes** | 15m, 1h, 4h |
| **Total** | **88.704 backtests** |

### Anti-Overfitting: Train/Test Split

Cada backtest é executado em 3 períodos:
- **Train (60 dias)** — Onde a estratégia é "descoberta"
- **Test (30 dias)** — Dados que a estratégia nunca viu (validação out-of-sample)
- **Full (90 dias)** — Visão consolidada

Apenas estratégias lucrativas em **ambos** períodos (train E test) são consideradas candidatas.

### Score de Robustez (0-100)

| Componente | Peso | Critério |
|------------|:----:|----------|
| PnL Full | 25% | Retorno total em 90 dias |
| PnL Test | 25% | Retorno nos 30 dias de validação |
| Consistência | 20% | % de datasets lucrativos no test |
| Profit Factor | 15% | Ganhos brutos / Perdas brutas |
| Drawdown | 15% | Máxima queda do equity |

### Principais Descobertas

1. **Filtro de tendência é obrigatório** — 100% das top 15 estratégias usam EMA alinhadas
2. **RSI supera Z-Score Robusto** — Z-Score isolado não superou RSI em nenhum cenário
3. **Trailing Stop é essencial** — Aparece em todas as top 4 estratégias
4. **Timeframes maiores = mais estáveis** — 4h teve 19% dos combos lucrativos vs 8% no 15m
5. **67 estratégias** sobreviveram ao filtro train + test

### Como Rodar

```bash
source venv/bin/activate
python research_scalping.py
```

> O script baixa dados automaticamente via CCXT (BinanceUS/Binance) e gera relatório completo no terminal.

---

## 🏆 Pesquisa FTMO Challenge (Research v5b)

O Gastor inclui pesquisa específica para o **FTMO Challenge** — o desafio de trading mais conhecido do mundo para acesso a mesas proprietárias (prop firms).

### 🎯 O que é o FTMO Challenge?

O FTMO Challenge é um processo de avaliação onde traders devem atingir uma meta de lucro respeitando regras de risco. Se aprovado, o trader recebe uma conta financiada de até $200.000 para operar, mantendo até **90% dos lucros**.

### 📋 Regras Oficiais (validadas em [ftmo.com](https://ftmo.com))

| Regra | Valor | Para $500 |
|-------|-------|-----------|
| **Meta de Lucro** | +10% do saldo inicial | $500 → **$550** |
| **Perda Máxima Total** | -10% do saldo inicial | Saldo mínimo: **$450** |
| **Perda Máxima Diária** | -5% do saldo inicial | Máx perda/dia: **$25** |
| **Dias Mínimos** | 4 dias de trading | ≥4 dias com posição aberta |
| **Prazo** | **Ilimitado** | Sem pressa, foque em consistência |

> [!IMPORTANT]
> **Detalhe crucial:** A perda máxima total e diária são calculadas sobre o **saldo inicial**, não sobre o saldo atual. Isso significa que um trader com $500 é eliminado quando o saldo cai para $450 — independentemente de quanto lucrou antes.

### 🔬 Metodologia v5b

A pesquisa realizou **108.864 simulações** com dados reais de 365 dias:

| Dimensão | Valores |
|----------|---------|
| **Sinais de Entrada** | 21 estratégias (RSI, Bollinger, MACD, Breakout, Squeeze, combos) |
| **Take Profit** | +1.5%, +2%, +3%, +4%, +5%, +7% |
| **Stop Loss** | -0.5%, -1%, -1.5%, -2% |
| **Trailing Stop** | Nenhum, T(1/0.5), T(2/1), T(3/1.5) |
| **Risk %** | 1%, 2%, 3% do capital por trade |
| **Pares** | SOL, ETH, BTC, XRP, AVAX, DOGE (todos /USDT) |
| **Timeframes** | 15m, 1h, 4h |
| **Total** | **108.864 backtests** |

**Características da simulação:**
- ✅ **Compound interest** — lucros reinvestidos
- ✅ **Position sizing dinâmico** — tamanho baseado no % de risco e SL
- ✅ **Daily drawdown tracking** — perda diária verificada barra a barra
- ✅ **Early stop** — para ao atingir meta OU estourar DD
- ✅ **Min 4 dias** — PASS só quando meta + dias mínimos atingidos

### 📊 Resultados Gerais

| Resultado | Quantidade | Proporção |
|-----------|:----------:|:---------:|
| 🟢 **PASS** (meta + 4 dias) | 17.568 | 16,1% |
| 🔴 FAIL DD (saldo < $450) | 49.530 | 45,5% |
| 🟠 FAIL Diário (perda > $25/dia) | 4.035 | 3,7% |
| ⏱️ TIMEOUT (365d sem resultado) | 37.731 | 34,7% |

> **16% das configurações testadas passam no FTMO** — significavelmente validado dado que nenhum viés de seleção foi aplicado (teste exaustivo).

### 🥇 Top 5 Estratégias que Passam no FTMO

| # | Sinal | Exit Config | Pass Rate | PnL Médio | WR |
|---|-------|-------------|:---------:|:---------:|:--:|
| 🥇 | **BB Squeeze→Expand + Up** | +7%/-1.5% T(3/1.5) R2% | **56% (10/18)** | +4,0% | 46,6% |
| 🥈 | **Breakout + StrongUp** | +3%/-2% T(1/0.5) R3% | **50% (9/18)** | +1,3% | 53,5% |
| 🥉 | **Breakout + Vol + Up** | +7%/-2% T(3/1.5) R2% | **50% (9/18)** | +1,5% | 46,9% |
| 4 | **🔥 Brkout+MACD↑+Vol+Up** | +7%/-2% T(2/1) R2% | **50% (9/18)** | +1,7% | 47,3% |
| 5 | **Price→EMA21 + StrongUp** | +7%/-2% T(3/1.5) R2% | **50% (9/18)** | +2,0% | 45,1% |

### 🏆 Estratégia Campeã: BB Squeeze→Expand + Up

**Lógica:** As Bollinger Bands se comprimem (squeeze = baixa volatilidade) e em seguida expandem violentamente = **explosão de volatilidade**. A entrada acontece quando essa expansão ocorre em **tendência de alta** (EMA 21 > EMA 50).

**Configuração de saída:** TP +7% / SL -1.5% / Trailing Stop (ativa +3%, trail 1.5%) / Risk 2%

#### ⏱️ Detalhamento por Par e Tempo para Passagem

| Status | Par | TF | Saldo Final | PnL | DD | Perda/dia | Trades | Dias Trading | Tempo Estimado |
|:------:|-----|:--:|:-----------:|:---:|:--:|:---------:|:------:|:------------:|:--------------:|
| 🟢 PASS | AVAX/USDT | 4h | $584 | **+16,9%** | 0,0% | $0 | 3 | 6 | **~1 semana** |
| 🟢 PASS | DOGE/USDT | 1h | $582 | **+16,5%** | -2,4% | $16 | 8 | 13 | **~2 semanas** |
| 🟢 PASS | ETH/USDT | 1h | $567 | **+13,4%** | -2,0% | $13 | 12 | 21 | **~3 semanas** |
| 🟢 PASS | XRP/USDT | 1h | $563 | **+12,6%** | 0,0% | $9 | 7 | 12 | **~2 semanas** |
| 🟢 PASS | SOL/USDT | 4h | $562 | **+12,3%** | -2,0% | $10 | 5 | 15 | **~3 semanas** |
| 🟢 PASS | DOGE/USDT | 4h | $558 | **+11,6%** | 0,0% | $9 | 3 | 7 | **~1 semana** |
| 🟢 PASS | XRP/USDT | 4h | $558 | **+11,5%** | -8,1% | $14 | 5 | 9 | **~2 semanas** |
| 🟢 PASS | SOL/USDT | 1h | $557 | **+11,5%** | -1,5% | $15 | 8 | 11 | **~2 semanas** |
| 🟢 PASS | XRP/USDT | 15m | $556 | **+11,2%** | -10,0% | $19 | 51 | 65 | **~2 meses** |
| 🟢 PASS | ETH/USDT | 15m | $552 | **+10,4%** | 0,0% | $11 | 4 | 6 | **~1 semana** |
| ⏱️ TO | BTC/USDT | 4h | $516 | +3,2% | -5,7% | $12 | 8 | 21 | > 12 meses |
| ⏱️ TO | AVAX/USDT | 1h | $485 | -3,0% | -5,1% | $18 | 28 | 42 | > 12 meses |
| ⏱️ TO | BTC/USDT | 1h | $473 | -5,3% | -5,8% | $19 | 31 | 90 | > 12 meses |
| ⏱️ TO | ETH/USDT | 4h | $464 | -7,2% | -9,1% | $19 | 11 | 23 | > 12 meses |
| 🔴 DD | AVAX/USDT | 15m | $450 | -10,0% | -10,0% | $21 | 30 | 28 | ❌ Eliminado |
| 🔴 DD | DOGE/USDT | 15m | $444 | -11,1% | -11,1% | $20 | 7 | 8 | ❌ Eliminado |
| 🔴 DD | BTC/USDT | 15m | $444 | -11,2% | -11,2% | $10 | 26 | 38 | ❌ Eliminado |
| 🔴 DD | SOL/USDT | 15m | $443 | -11,4% | -11,4% | $17 | 29 | 40 | ❌ Eliminado |

> [!TIP]
> **Tempo médio para passagem nos cenários bem-sucedidos: ~2-3 semanas.** Os melhores cenários (AVAX 4h, DOGE 4h) passam em apenas **1 semana** com 3 trades certeiros.

### 📈 Análise por Dimensão

#### Por Timeframe

| Timeframe | Pass Rate | Taxa de Falha | PnL Médio | Recomendação |
|:---------:|:---------:|:-------------:|:---------:|:------------:|
| **1h** | **20,9%** ⭐ | 43,7% | -2,4% | ✅ **Melhor custo-benefício** |
| 4h | 16,9% | 32,0% | -1,6% | ✅ Menor risco |
| 15m | 10,6% | 71,9% | -6,1% | ⚠️ Alto risco |

> **1 hora é o timeframe ideal** — melhor taxa de aprovação e, combinado com TFs maiores, oferece o equilíbrio entre frequência de sinais e qualidade.

#### Por Risk % (Position Sizing)

| Risk | Pass Rate | Taxa de Falha | PnL Médio |
|:----:|:---------:|:-------------:|:---------:|
| 1% | 13,4% | 45,0% | -3,5% |
| **2%** | **17,5%** ⭐ | 51,3% | -3,3% |
| **3%** | **17,5%** ⭐ | 51,3% | -3,3% |

> **2% de risco por trade é o sweet spot** — 3% não oferece vantagem adicional e 1% é conservador demais para atingir +10%.

#### Por Família de Sinal

| Família | Melhor Pass Rate | Tipo | Comentário |
|---------|:----------------:|:----:|------------|
| **BB Squeeze→Expand + Up** | 56% ⭐ | Breakout | Campeã absoluta |
| **Breakout + StrongUp** | 50% | Breakout | Consistente |
| **Breakout + Vol + Up** | 50% | Breakout | Com confirmação de volume |
| **🔥 Brkout+MACD↑+Vol+Up** | 50% | Multi | Forte confluência |
| **Price→EMA21 + StrongUp** | 50% | Pullback | Pullback para EMA |
| MACD Hist→+ / MACDxSig↑ | 44% | Momentum | Sólido mas não atinge 50% |
| BB Low + Up / ZR<-2 | 39% | Reversão | Risco elevado |
| RSI<30 + Up | 11% | Reversão | Poucas oportunidades |

> [!NOTE]
> **Padrão claro: estratégias de BREAKOUT dominam o FTMO.** As 5 melhores são todas baseadas em capturar explosões de volatilidade em tendência. Reversões (RSI, Z-Score) funcionam mal — o FTMO requer ganhos rápidos e expressivos, não recuperações graduais.

### 🧠 Conclusões Estratégicas

1. **Estratégias de breakout/squeeze são viáveis para o FTMO** — 56% de chance de passar com a config certa
2. **O timeframe 1h é ideal** — frequência suficiente sem noise excessivo
3. **Risk 2% com TP +7% e Trailing Stop** — configuração que maximiza a chance de passagem
4. **15 minutos é perigoso** — alta taxa de eliminação (72%), usar apenas como complemento
5. **BTC é o par mais difícil** — nenhum cenário passou em 1h/4h, tendência mais errática

### ⚠️ Limitações e Caveats

- **Backtesting ≠ Live**: Resultados simulados. Latência, slippage e condições de mercado reais podem diferir
- **Pass rate 56% ≠ garantia**: Significa 44% de chance de ser eliminado no período testado
- **Dados de 1 ano**: Performance pode variar em mercados bear/bull/lateral diferentes
- **Sem leverage extremo**: Simulação usa position sizing conservador (2-3% de risco)
- **Crypto only**: Resultados para pares USDT na Binance — FTMO opera também Forex, índices, etc.

### 🚀 Como Rodar a Pesquisa FTMO

```bash
source venv/bin/activate
python research_ftmo.py
```

> O script baixa 365 dias de dados via CCXT, executa 108.864 simulações e gera relatório completo no terminal. Tempo estimado: ~15 minutos.

---

## 🛡️ Auditoria e Reforço de Segurança (Fase 3)

A segurança da plataforma foi auditada e reforçada para o ambiente de produção, cobrindo código, infraestrutura e validação externa.

### 🔐 Implementações de Segurança
- **Rate Limiting**: Bloqueio de ataques de força bruta em endpoints de login/registro (10 tentativas/min). Identificação do IP real via `X-Forwarded-For` apenas quando `TRUST_PROXY_HEADERS=1` (prod atrás de Nginx). Store de buckets com GC automático e cap de 20k identificadores para evitar memory leak.
- **Security Headers**: HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy e CSP estrita por padrão (`default-src 'none'`, sem `unsafe-inline` nem `unsafe-eval`). Apenas as rotas do Swagger/Redoc/openapi.json recebem CSP relaxada com `cdn.jsdelivr.net`.
- **CORS Validation**: Em produção, `CORS_ORIGINS` é validado no startup — exige HTTPS absoluto, rejeita wildcards e falha o boot se a variável estiver vazia ou inválida.
- **OAuth CSRF Protection**: Google OAuth usa state tokens com validação server-side (TTL 10 min, one-time use, store com cap e GC). O callback exige que o state coincida com o emitido pelo backend.
- **Secrets em repouso**: Chaves de exchange sempre cifradas com Fernet (`ENCRYPTION_KEY`). Colunas legadas `binance_api_key`/`binance_api_secret` em texto puro foram removidas do modelo e do banco.
- **Estratégias ativas por usuário**: Endpoints `/api/strategies/active/*` exigem JWT e persistem estado isolado por `user_id` em disco (sem vazamento entre contas).
- **Logs de Auditoria**: Registro estruturado (JSON) de eventos de segurança (login success/fail) com IP de origem.
- **Docker Hardening**: Containers rodando com usuário não-root (UID 1000) e limites de recursos (CPU/RAM).
- **Gestão de Segredos**: Validação estrita de `JWT_SECRET_KEY` e `ENCRYPTION_KEY` em produção.
- **OpenAPI scope control**: Rotas `/api/admin/*` omitidas do schema público (`include_in_schema=False`). Swagger UI desabilitado em produção — apenas o schema JSON machine-readable permanece acessível (necessário para integração MCP).
- **Validação estrita de input (v7.3)**: Módulo central `backend/core/validators.py` com regex allowlists (coin, timeframe, strategy slug, locale, exchange, telegram chat_id, trade mode/side/outcome, ISO date). Todos os schemas Pydantic usam `Field(min_length/max_length/ge/le)` + `pattern` e `field_validator` para listas — ataques de payload oversized, injeção por campos livres e enumeração de slugs são bloqueados no parse antes de tocar a lógica.
- **Ownership checks granulares (v7.3)**: Endpoints por ID (`/api/live/session/{id}`, `/api/decision-logs/session/{id}`, `/api/decision-logs/{log_id}`) filtram por `user_id` na própria query e retornam **404 em vez de 403** para recursos de outros usuários — previne enumeração de IDs. `/api/optimizer/run` exige `current_user` e filtra `Strategy.owner_id` ao resolver slugs `custom_<id>`, impedindo grid search com regras de estratégias de outros usuários.
- **Handler global de exceções (v7.3)**: `RequestValidationError` e `Exception` têm handlers globais em `main.py`. Em produção, exceções não tratadas retornam `{"detail": "Internal server error"}` (stack trace apenas em log estruturado); mensagens de erro genéricas também substituíram vazamentos de `str(e)` em `/api/market/*`, `/api/strategies/{slug}/run` (error_loading_custom), `/api/optimizer/run` (error_fetching_data) e `/api/user/keys/{id}/balance`.

### 🕵️‍♂️ Testes e Validação
- **Pentest Automatizado**: Scripts customizados validaram a eficácia do Rate Limit e a presença dos Headers.
- **OWASP ZAP Scans**: Varredura sem vulnerabilidades de Alto Risco. Apenas alertas informativos de CSP.
- **SQLMap**: Testes de injeção confirmaram a robustez do ORM (SQLAlchemy).
- **Dependências**: Auditoria completa e atualização de pacotes vulneráveis (`cryptography`, `protobuf`, etc.).

> **Status:** ✅ **Aprovado para Live Trading**

---

## 🚀 Deploy em Produção (VPS)

O Gastor está em produção em **https://gastor.com.br**, hospedado em uma VPS Hostinger.

### Infraestrutura

| Componente | Detalhe |
|------------|---------|
| **VPS** | Hostinger KVM 2 — 2 vCPU, 8 GB RAM, Ubuntu 24.04 LTS |
| **Domínio** | `gastor.com.br` |
| **IP** | `72.60.8.246` |
| **HTTPS** | Let's Encrypt via Certbot (renovação automática) |
| **Proxy Reverso** | Nginx instalado no host (não em Docker) |
| **Containers** | Docker Compose com override de produção |
| **Healthchecks** | DB: `pg_isready` (30s). Backend: `GET /api/health` (30s). Auto-restart se unhealthy |
| **Firewall** | UFW — portas 22 (SSH), 80 (HTTP), 443 (HTTPS) |

### Arquitetura de Produção

```
Internet (443/80) → Nginx (host) → Terminação SSL
  ├─ /api/live/ws/*  → 127.0.0.1:8000  (backend — WebSocket upgrade)
  ├─ /api/*          → 127.0.0.1:8000  (backend — FastAPI)
  └─ /*              → 127.0.0.1:3080  (frontend — arquivos estáticos)

Containers Docker só fazem bind em 127.0.0.1 (inacessíveis externamente).
PostgreSQL não expõe porta nenhuma ao host.
```

### Resiliência em Produção

| Mecanismo | Descrição |
|-----------|-----------|
| **Docker Healthchecks** | PostgreSQL (`pg_isready`) e Backend (`GET /api/health`) verificados a cada 30s. Containers unhealthy são reiniciados automaticamente |
| **Watchdog WebSocket** | Streams sem dados por >5 min são reconectados automaticamente. Kline data sempre via mainnet (testnet WS é instável) |
| **Detecção de Sessões Órfãs** | A cada 5 min, sessões "running" sem engine ativo são detectadas, alertadas via Telegram e restauradas |
| **Restauração no Startup** | Todas as sessões ativas são restauradas automaticamente após restart do backend |
| **Fallback Testnet→Paper** | Se a Binance Testnet falhar (timeout/conexão), a sessão degrada para paper trading com alerta ao admin |
| **Pre-flight Balance Check** | Antes de cada BUY testnet, o saldo real USDT é consultado e a quantidade é ajustada para evitar rejeições por saldo insuficiente |
| **Tratamento de Saldo Insuficiente** | Se a Binance Testnet rejeitar por saldo insuficiente, o trade é pulado sem crashar a sessão |
| **Logging de Notificações** | Todas as notificações Telegram (trades, erros, alertas admin) registram sucesso/falha nos logs para rastreabilidade |

### Arquivos de Deploy

| Arquivo | Finalidade |
|---------|------------|
| `docker-compose.prod.yml` | Override de produção: portas restritas, sem volume mounts, variáveis de ambiente |
| `.env.production` | Template com todas as variáveis necessárias e instruções de geração |
| `scripts/deploy.sh` | Script de deploy automatizado (front, back, all, nuke, status, logs) |
| `deploy/nginx/gastor.conf` | Configuração Nginx HTTP (deploy inicial sem domínio) |
| `deploy/nginx/gastor-ssl.conf` | Configuração Nginx HTTPS (com domínio e SSL) |
| `deploy/setup_vps.sh` | Script de bootstrap da VPS (Docker, Nginx, UFW, etc.) |

### Como Fazer Deploy

#### 1. Setup inicial da VPS (primeira vez)

```bash
# No servidor (via SSH como root):
bash /opt/gastor/deploy/setup_vps.sh
```

O script instala Docker, Nginx, Certbot, configura o firewall e inicia os containers.

#### 2. Script de Deploy (`scripts/deploy.sh`)

O script automatiza todo o processo de deploy: empacota o projeto, envia para a VPS, preserva o `.env` de produção e faz o build dos containers.

```bash
# Subir tudo (frontend + backend)
./scripts/deploy.sh

# Apenas o frontend
./scripts/deploy.sh front

# Apenas o backend
./scripts/deploy.sh back

# Reset total: limpa Docker na VPS (inclusive DB!) e sobe do zero
./scripts/deploy.sh nuke

# Ver status dos containers na VPS
./scripts/deploy.sh status

# Acompanhar logs em tempo real (Ctrl+C para sair)
./scripts/deploy.sh logs
./scripts/deploy.sh logs backend    # logs de um serviço específico
```

| Comando | O que faz |
|---------|-----------|
| `(vazio)` ou `all` | Empacota, envia e faz build do frontend + backend |
| `front` | Empacota, envia e faz build apenas do frontend |
| `back` | Empacota, envia e faz build apenas do backend |
| `nuke` | Destrói todos os containers/volumes na VPS e sobe do zero (pede confirmação) |
| `status` | Mostra o estado dos containers na VPS via SSH |
| `logs` | Conecta aos logs em tempo real (aceita nome do serviço como segundo argumento) |

> ⚠️ **`nuke` destrói o banco de dados!** O comando pede confirmação (digitar "sim") antes de executar. Use apenas para recriar o ambiente do zero.

#### 3. Deploy manual (alternativa)

Se preferir executar manualmente:

```bash
# Na máquina local — compactar o projeto:
cd /home/silvano/Documentos/projetos
tar --exclude='node_modules' --exclude='venv' --exclude='.next' \
    --exclude='__pycache__' --exclude='.git' \
    -czf /tmp/gastor.tar.gz Gastor/

scp /tmp/gastor.tar.gz root@72.60.8.246:/opt/

# No servidor (via SSH):
ssh root@72.60.8.246
cd /opt
mv gastor gastor.old
tar xzf gastor.tar.gz && mv Gastor gastor && rm gastor.tar.gz
cp gastor.old/.env gastor/.env    # preservar secrets de produção
cd /opt/gastor
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### Administração da VPS

```bash
# Conectar via SSH
ssh root@72.60.8.246

# Todos os comandos abaixo executados em /opt/gastor:
cd /opt/gastor
```

#### Monitoramento

```bash
# Status dos containers
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Logs ao vivo (Ctrl+C para sair)
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f backend   # só backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f frontend  # só frontend

# Recursos do servidor
free -h         # memória
df -h           # disco
htop            # CPU e processos

# Uso de disco pelo Docker
docker system df
```

#### Operações

```bash
# Reiniciar um serviço
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart backend

# Parar tudo
docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# Rebuild e restart completo
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Acessar banco de dados diretamente
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec db psql -U gastor gastor_db

# Limpar imagens/containers antigos
docker system prune -f
```

#### Nginx e SSL

```bash
# Status do Nginx
systemctl status nginx

# Testar configuração
nginx -t

# Ver configuração ativa
cat /etc/nginx/sites-enabled/gastor

# Verificar certificado SSL
certbot certificates

# Testar renovação automática
certbot renew --dry-run

# Renovar manualmente (normalmente automático)
certbot renew
```

#### Firewall

```bash
# Ver regras ativas
ufw status

# Portas abertas: 22 (SSH), 80 (HTTP), 443 (HTTPS)
```

### Configuração do Domínio e HTTPS

Passos para configurar um novo domínio (já realizado para `gastor.com.br`):

1. **DNS**: Criar registro A apontando `gastor.com.br` → `72.60.8.246` no painel da Hostinger
2. **Nginx**: Atualizar `server_name` no arquivo de configuração:
   ```bash
   sed -i "s/server_name _;/server_name gastor.com.br;/" /etc/nginx/sites-enabled/gastor
   nginx -t && systemctl reload nginx
   ```
3. **Certificado SSL**: `certbot --nginx -d gastor.com.br`
4. **Variáveis de Ambiente**: Atualizar `.env`:
   ```
   NEXT_PUBLIC_API_URL=https://gastor.com.br
   CORS_ORIGINS=https://gastor.com.br
   GOOGLE_REDIRECT_URI=https://gastor.com.br/auth/google/callback
   ```
5. **Rebuild**: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d`
6. **Google OAuth**: Adicionar `https://gastor.com.br` nas origens autorizadas e `https://gastor.com.br/auth/google/callback` nos URIs de redirecionamento no [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### Variáveis de Ambiente de Produção

O arquivo `.env` na VPS contém todos os secrets. Use `.env.production` como referência:

| Variável | Descrição | Como Gerar |
|----------|-----------|------------|
| `POSTGRES_PASSWORD` | Senha do PostgreSQL | `openssl rand -base64 24` |
| `DATABASE_URL` | Connection string completa | `postgresql://gastor:<senha>@db:5432/gastor_db` |
| `JWT_SECRET_KEY` | Chave de assinatura JWT | `openssl rand -hex 32` |
| `ENCRYPTION_KEY` | Chave Fernet para criptografia | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `ENVIRONMENT` | Modo de execução | `production` (ativa validação de secrets no startup) |
| `NEXT_PUBLIC_API_URL` | URL da API para o frontend | `https://gastor.com.br` |
| `CORS_ORIGINS` | Origens aceitas pelo backend | `https://gastor.com.br` |
| `ADMIN_PASSWORD` | Senha do admin | Definir manualmente |
| `GOOGLE_CLIENT_ID` | OAuth Client ID | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | OAuth Client Secret | Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | Callback do OAuth | `https://gastor.com.br/auth/google/callback` |
| `TRUST_PROXY_HEADERS` | Lê `X-Forwarded-For` para rate limit | `1` em prod (atrás de Nginx). **Nunca ligar em dev ou backend exposto** |

> ⚠️ **Nunca commite o `.env` no repositório.** O arquivo `.env.production` é apenas um template com placeholders.

---

## 🛣️ Roadmap

O desenvolvimento do Gastor é contínuo. Fases concluídas e próximas etapas:

### ✅ Concluído

- [x] **Paper Trading** — Simulação com preços ao vivo (WebSocket Binance), Force Delete, Optimistic UI.
- [x] **Sistema de Autenticação** — Login/Registro, Google OAuth, JWT, isolamento de dados.
- [x] **Sistema de Convites** — Registro restrito via códigos gerados pelo admin.
- [x] **Painel Administrativo** — Gestão de usuários, monitoramento de recursos, notificações Telegram.
- [x] **Refinamentos de Sessão** — Persistência em background, reuso de slots, logout seguro.
- [x] **Refatoração do Core** — Estratégias unificadas (Single Source of Truth), componentes modulares.
- [x] **Gestão de Risco (SL/TP)** — Stop Loss e Take Profit baseados no PnL líquido, indicadores de posição (entry_price, entry_cost, pnl_pct), validação de escala entre indicadores, % de ajuste para break-even e preço de entrada.
- [x] **Pesquisa de Estratégias (v3)** — Varredura exaustiva de 88.704 backtests com train/test split, 44 sinais, 6 pares, 3 timeframes. Estratégia campeã (Win First) integrada ao sistema.
- [x] **Pesquisa FTMO Challenge (v5b)** — 108.864 simulações com regras oficiais FTMO validadas (DD no saldo inicial, min 4 dias, período ilimitado). Campeã: BB Squeeze→Expand com 56% de pass rate e ~2 semanas para passagem.
- [x] **Spring Loaded (Admin)** — Implementação completa da estratégia BB Squeeze→Expand + EMA uptrend como estratégia personalizada do admin. Inclui trailing stop stateful, gatilhos de paper trading, seed automático no startup Docker, e modo de edição de parâmetros no Construtor.
- [x] **Integração Binance Testnet (Fase 1)** — Market Orders reais enviadas para `testnet.binance.vision` sem dinheiro real. Modo Testnet no engine, WebSocket e data loader. Gerenciamento de chaves API com flag `is_testnet`. Sessões Testnet persistem e são restauradas no restart. Badge TESTNET na UI. Seed automático da chave admin no startup (`promote_admin.py`) com criptografia Fernet. Validado com testes de conectividade, autenticação, ticker, orderbook e ciclo BUY→SELL completo (~310ms de latência).
- [x] **Gerenciamento de Cotas (Admin)** — Implementação de limites de recursos por usuário (`rate_limit_multiplier` e `max_active_strategies`). UI dedicada no Painel Admin para ajuste granular de cotas. Middleware de Rate Limit atualizado para respeitar configurações dinâmicas.
- [x] **Compliance & Termos** — Página pública de Termos de Uso acessível sem login. Fluxos de autenticação (Google/Email) atualizados para exigir consentimento explícito aos termos.
- [x] **Trade Decision Logs (Fase 2)** — Log detalhado de cada BUY/SELL: snapshot completo de indicadores, candle OHLCV, regras ativas, motivo de saída, latência WebSocket e contexto financeiro. Suporte a Paper Trading, Testnet e Backtest. Export CSV e JSONL pareado (BUY+SELL com `trade_pair_id`) para fine-tuning de modelos ML. API `/api/decision-logs` com filtros, paginação e isolamento por usuário. Aba "🧠 Decisões" na UI de sessões ao vivo.
- [x] **Deploy VPS (Produção)** — Plataforma em produção em `https://gastor.com.br`. VPS Hostinger KVM 2 (Ubuntu 24.04), Docker Compose com override de produção, Nginx como proxy reverso, HTTPS via Let's Encrypt, firewall UFW. Scripts de deploy e administração documentados.
- [x] **Logging de Notificações Telegram** — Registro completo de sucesso/falha em todas as notificações Telegram (trades, erros, alertas admin, sessões, depósitos, saques). Detecção de falhas parciais em alertas multi-destinatário. Rastreabilidade total para diagnóstico de falhas de entrega.
- [x] **Testnet Balance Management** — Pre-flight balance check antes de cada BUY testnet: consulta saldo real USDT e ajusta quantidade para evitar rejeições. Detecção específica de `InsufficientBalanceError` (trade pulado sem crashar sessão). Monitor de saldo no painel de chaves ("Consultar Saldo"). Auto-fetch de saldo ao selecionar chave no formulário de nova sessão com aviso se saldo insuficiente. Endpoint `GET /api/user/keys/{id}/balance`.
- [x] **Modo Claro/Escuro (Theme Toggle)** — Toggle de tema no navbar (desktop e mobile) com ícones sol/lua. Implementado via CSS variable overrides do TailwindCSS v4: redefine `--color-slate-*` em `:root` (claro) e `.dark` (escuro), fazendo todas as classes Tailwind se adaptarem automaticamente. Charts (lightweight-charts e SVG) usam cores dinâmicas via `ThemeContext.chartColors`. Preferência persistida em `localStorage` (`gastor_theme`). Default: modo escuro (preserva visual atual). Transição suave de 150ms. Cores semânticas (emerald, red, blue, amber) usam `dark:` prefixes para contraste adequado em ambos os modos.
- [x] **Script de Deploy Automatizado** — `scripts/deploy.sh` automatiza todo o fluxo de deploy para VPS: empacota, envia via scp, preserva `.env`, e faz build dos containers. Comandos: `front`, `back`, `all`, `nuke` (reset total com confirmação), `status`, `logs`.
- [x] **Heartbeat Telegram Fix** — Correção do `send_admin_alert()` para usar fallback `ADMIN_TELEGRAM_CHAT_ID` quando `ADMIN_TELEGRAM_CONTACTS` não está configurado. Garante envio dos relatórios de heartbeat (6h/6h BRT).
- [x] **UI Polish & Architecture (v4.0)** — Migração para Tailwind v4, limpeza de configs legadas, padronização de botões, correção de contraste (Dark Mode) e refatoração semântica de componentes (Modais, Inputs).
- [x] **Backend i18n (Fase 4.3)** — Motor de internacionalização (i18n.t) integrado ao Core, FastAPI, Models e Middleware. Dependências dinâmicas resolvendo o idioma via Header e Banco de Dados (PostgreSQL). Erros de API (HTTPException) globalmente traduzidos e templates de notificações do Telegram (compras/vendas, heartbeats) enviadas no idioma nativo do usuário.
- [x] **Frontend Polish & Long-Form i18n (Fase 4.4)** — Refatoração com next-intl para componentes de textos ricos: Glossário traduzido (+20 verbetes teóricos em 6 idiomas com suporte a KaTeX), Termos de Uso (Legal Docs) localizados, revisão visual garantindo legibilidade Dark/Light mode no Tailwind v4 e responsividade de tabelas cross-languages. Build unificado testado em produção.
- [x] **Multi-Exchange (Bybit + OKX)** — Abstração completa da camada de exchange para suportar **Binance**, **Bybit** e **OKX**. Módulo `core/exchange/` com registry centralizado, client CCXT genérico (Unified Account para Bybit/OKX, passphrase para OKX), order manager com ajuste automático de lot size/precisão, e normalização de símbolos entre formatos. WebSocket multi-exchange (`exchange_ws.py`) com parsers específicos por exchange e factory pattern. Data loader com fallback chain expandida (Binance → BinanceUS → Bybit → OKX → CryptoCompare → CoinGecko). Decision Logs com campo `exchange_name` e filtro por exchange nos endpoints e exports. Frontend com seletor de exchange no cadastro de chaves, campo passphrase condicional (OKX), badges coloridos por exchange na listagem de sessões e detalhes, e monitor de saldo para qualquer exchange. Backward-compatible: todos os defaults são `"binance"`, aliases deprecated mantidos em `testnet/`. i18n completo em 6 idiomas (frontend + backend).
- [x] **PnL Entry Cost Fix** — Correção do cálculo de PnL para considerar o custo total da entrada (incluindo taxa de compra). Nova coluna `entry_cost` em `PaperPosition`. Fórmulas corrigidas: `pnl = net_sell - entry_cost` e `unrealized = (qty × price) - entry_cost`. Endpoint de detalhes calcula `unrealized_pnl` on-the-fly (nunca depende do valor defasado no DB). Engine recalcula no `_sync_state` ao restaurar sessões. Backward-compatible com fallback para posições antigas sem `entry_cost`.
- [x] **Migration Rollback Fix** — Correção crítica do sistema de migrations PostgreSQL: `conn.rollback()` após falhas evita transação em estado "aborted". Reordenação do `entrypoint.sh` para rodar migrations antes do `promote_admin.py`.
- [x] **Timestamp Timezone Consistency** — Colunas `executed_at`, `ws_receive_at`, `signal_detected_at` e `candle_open_at` no `TradeDecisionLog` agora usam `TIMESTAMPTZ` (consistente com `PaperTrade`).
- [x] **Telegram Chat ID Resolution** — Notificações de trade agora consultam `TelegramConfig` no banco de dados como fallback quando o frontend não envia o `chat_id`. Aplica o mesmo fallback na restauração de sessões após restart do backend.
- [x] **Data Loader Symbol Fix** — Corrigido bug de normalização de símbolos no roteamento para Bybit/OKX como fonte de dados OHLCV (`normalize_to_ccxt(symbol)` em vez de `normalize_to_ccxt(coin)`).
- [x] **Telegram HTML Parsing Fix** — Corrigido erro 400 do Telegram ("Unsupported start tag") que impedia notificações de SELL e de estratégias com operadores `<`/`>`/`<=` nos indicadores. Adicionado `html_escape()` em todos os valores dinâmicos do template e `_flatten_triggers()` para transformar o dict estruturado em formato plano legível.
- [x] **FTMO Drawdown Tracking** — Métricas de Max Drawdown Total (%) e Max Drawdown Diário (%) calculadas em tempo real a cada candle no engine. Usa candle high/low para capturar pior cenário intra-candle. Fórmula FTMO: `(peak - worst) / initial_balance × 100` (denominador = capital inicial). Reset diário à meia-noite BRT. Persistido no DB (6 colunas em `paper_sessions`) para sobreviver a restarts. Cards na UI com cores verde/amarelo/vermelho conforme proximidade dos limites (10% total, 5% diário). Alertas Telegram opt-in (toggle no painel de notificações, default OFF) quando DD ≥ 80% dos limites FTMO. i18n completo em 6 idiomas.
- [x] **Freemium Tiers (v6.0)** — Sistema de 3 tiers (Free/Pro/Desk) controlado por invite codes. Colunas `plan_tier` em `users` e `invite_codes`. Tier atribuído no registro e quotas configuradas automaticamente (`apply_tier_quotas()`). Feature gating backend via `require_feature()` (Grid Search, Decision Logs Export) e checks inline (testnet, multi-exchange). Frontend: hook `useTier()`, componente `<UpgradeGate>`, seção de tier no User Panel, gestão de tiers no Admin. Config centralizada em `tier_config.py`. Admin bypassa todos os gates. i18n em 6 idiomas.
- [x] **Landing Page Polish + Termos v2.1 (v7.1)** — Seção de pricing reformulada: badge "Recomendado" (verde) no plano Gratuito, fita diagonal "Apoie" nos planos pagos (azul/âmbar), highlight verde no card Free, copy suavizado nos tiers (sem "traders sérios"). Fix de consistência no FAQ ("Free" → "Gratuito"). Termos de Uso atualizados para v2.1: nova cláusula na Seção 4 explicando validade de planos, downgrade automático ao expirar (sem suspensão, sem perda de dados) e renovação via WhatsApp. i18n em 6 idiomas. Fix de deploy: `tsconfig.tsbuildinfo` adicionado ao `.dockerignore`; variáveis `DATABASE_URL`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL` e `GOOGLE_REDIRECT_URI` tornadas explícitas no `.env` de produção.
- [x] **Subscription Expiry (v6.2)** — Validade de assinatura atrelada ao tier. Coluna `plan_tier_expires_at` em `users` e `subscription_days` em `invite_codes`. Ao registrar com um código com duração definida, `expires_at = agora + dias`. Task diária às 08:00 UTC (`check_expired_subscriptions`) faz downgrade automático para Free e alerta admin via Telegram. Admin pode renovar/alterar tier com duração via botão "Tier" no painel (prompt solicita novo tier + dias). Campo "Dias (assinatura)" no formulário de criação de invite codes (desabilitado para Free). Data de expiração exibida no User Panel em âmbar (≤7 dias) ou vermelho (expirado). Coluna de expiração na tabela de usuários do Admin. i18n em 6 idiomas.
- [x] **SEO Foundations (v6.1)** — `public/sitemap.xml` (3 URLs públicas com priority/changefreq) e `public/robots.txt` (permite `/`, `/glossary`, `/terms`; bloqueia rotas autenticadas). `generateMetadata` em `layout.tsx` com title template, description, keywords de alta intenção ("backtesting crypto FTMO", "paper trading binance"), OG, Twitter card e canonical. Layouts de rota dedicados para `/glossary` e `/terms` com metadata específico. JSON-LD `WebApplication` (planos + preços) e `FAQPage` (7 Q&A para rich snippets nas SERPs) no root layout; `DefinedTermSet` no layout do glossário.
- [x] **Hero Dual-Card + No-Code Differentiator (v6.1)** — Hero reformulado com dois cards animados lado a lado: (1) Builder mockup — 3 regras (`RSI(14) < 30`, `EMA(9) > EMA(21)`, `Preço > BB inferior`) aparecem uma a uma com delays CSS progressivos, badge "Sem código" em destaque; (2) Equity curve animada com stats de backtest. Subtítulo atualizado em 6 idiomas para incluir "sem escrever uma linha de código". Diferencial no-code visível na primeira tela sem scroll.
- [x] **Landing Page Pública (v7.0)** — Rota `/` com narrativa completa em 7 seções: Hero (equity curve SVG animada, escopo cripto explícito), ProblemSection (3 dores reais do trader), WorkflowSection (5 passos SVG), FTMOSection (prop firm como um dos usos + explicação do que é FTMO), FeaturesSection, PricingSection (sem rate limit, preços em reais, CTAs WhatsApp por plano), FAQSection. Scroll reveal via IntersectionObserver. Rotas públicas: `/glossary` adicionada junto de `/terms`. ~90 chaves i18n no namespace `Landing` em 6 idiomas.
- [x] **Termos de Uso v2.0 (v7.0)** — Documento legal completo com 12 seções incluindo Política de Inatividade. Seção 11 dinâmica: prazo buscado em tempo real via `GET /api/user/inactivity-limit` e interpolado no texto. i18n em 6 idiomas.
- [x] **Controle de Inatividade (v7.0)** — `ActivityTrackingMiddleware` registra `last_active_at` por request autenticado (não-bloqueante). Soft-delete: usuários inativos ficam com `is_active=False` e `deleted_at` (dados preservados). `SystemConfig` key-value para `INACTIVITY_LIMIT_DAYS` (padrão: 90 dias) configurável pelo admin sem rebuild. Task diária às 10:00 UTC envia aviso Telegram 1 dia antes e soft-deleta ao atingir o limite. `inactivity_exempt` por usuário. API admin completa + endpoint público para Termos de Uso. UI admin: coluna "Última Atividade", badge "Deletado", botões "Alertar"/"Deletar", painel de configuração.
- [x] **OpenAPI & API Security Polish (v7.2)** — Schema OpenAPI público em `/api/openapi.json` (53 endpoints, rotas admin omitidas). Swagger UI desabilitado em produção (`ENVIRONMENT=production`), disponível em dev. Schema machine-readable pronto para integração MCP. Deploy script corrigido para não sobrescrever `.env` de produção (`--exclude='.env'` no tar). Variáveis de produção (`DATABASE_URL`, `ENVIRONMENT`, `CORS_ORIGINS`, `GOOGLE_REDIRECT_URI`) documentadas e explícitas no `.env`.
- [x] **Cobertura de Testes Expandida (v7.2)** — Suite ampliada de 17 para **129 testes** (45% de cobertura). Novos arquivos: `test_indicators.py` (100% em `core/indicators.py` — 25 funções), `test_metrics_and_tiers.py` (100% em `core/metrics.py`, tiers e segurança), `test_strategies_and_backtest.py` (10 estratégias em 100% + `BacktestEngine` em 93%). Todos rodando via SQLite in-memory sem dependências externas.
- [x] **Hardening de Input, Ownership e Exceções (v7.3)** — Módulo central `backend/core/validators.py` com regex allowlists; schemas Pydantic de `user`, `live`, `strategies`, `optimizer`, `admin`, `market` e `decision_logs` endurecidos com `Field(min_length/max_length/ge/le)` e `pattern`. Endpoints por ID (`/api/live/session/{id}`, `/api/decision-logs/session/{id}`, `/api/decision-logs/{log_id}`) passam a filtrar `user_id` na query e retornam **404** (anti-enumeração). `/api/optimizer/run` fecha ownership de `Strategy.custom_<id>` (antes rodava grid search com regras de outros usuários). Handlers globais de `RequestValidationError` e `Exception` em `main.py` mascaram stack trace em produção. Vazamentos de `str(e)` removidos de `/api/market/*`, `/api/strategies/{slug}/run`, `/api/optimizer/run` e `/api/user/keys/{id}/balance`. `backtest_failed` adicionado aos 6 locales. Senha mínima no reset admin: 6 → 8. Backend 130/130 testes; frontend lint/build OK.
- [x] **Arquitetura Formal + Benchmarks + Prometheus (v7.3)** — [`docs/architecture.md`](docs/architecture.md): diagramas C4 (contexto, containers, componentes), sequências de trade/auth/backtest, modelo ER e 6 ADRs. [`docs/benchmarks.md`](docs/benchmarks.md): throughput medido de indicadores (até 79M candles/s), BacktestEngine (~128k candles/s), latência por estratégia e capacidade da VPS. Prometheus: endpoint `/api/metrics/prometheus` com contadores, histogramas e gauges (`gastor_http_requests_total`, `gastor_http_request_duration_seconds`, `gastor_active_trading_sessions`, CPU/RAM). Script `scripts/benchmark.py` reproduzível.
- [x] **MCP Integration & Aura (v8.0)** — Servidor MCP baseado em FastMCP montado em `/mcp` dentro do backend FastAPI, com `MCPAuthMiddleware` que reusa o JWT da API principal. 19 ferramentas (após auditoria de v8.1) distribuídas em 9 módulos (`market`, `strategies`, `education`, `backtest`, `builder`, `optimizer`, `live`, `decision_logs`, `metrics`) com tier gating via `TOOL_TIER_MAP` (Free/Pro/Desk/Admin). Resources (`gastor://strategies/catalog`, `gastor://indicators`) e prompts pré-configurados (`build_strategy`, `analyze_strategy`, `market_overview`, `learn_indicator`). **Aura by Gastor** — a assistente de IA embutida em `/chat` com ponte OpenAI-compatible: gera function definitions a partir do `TOOL_TIER_MAP`, executa tool calls com validação de tier, renderiza cards expansíveis com ferramenta/args/resultado, suporta até 5 rodadas encadeadas. Configuração LLM por usuário em **Painel do Usuário → Integrações → IA & Assistente** (API key, base URL, modelo) — key criptografada com Fernet em `user_configs.llm_api_key_encrypted` e nunca retornada por `GET /api/chat/config` (apenas flag `has_api_key`). Suporte a qualquer endpoint OpenAI-compatible (OpenAI, Anthropic via LiteLLM, LocalAI, Ollama). Clients externos: Claude Desktop, Cursor, VS Code via configuração MCP padrão — habilitados em produção desde **v8.3** (Phase B). Controlado por `MCP_ENABLED` (`true` em dev e em prod). 36 testes dedicados. Documentação em [docs/mcp.md](docs/mcp.md) e em **/docs/mcp** (acessível pelo usuário final).
- [x] **Termos de Uso v3.0 — Cláusula de IA (v8.2)** — Reescrita dos Termos de Uso após v8.0/v8.1: 12 → 13 seções, nova **Seção 5 — Inteligência Artificial (Aura)** com 7 subseções cobrindo o funcionamento da Aura como camada de orquestração sobre LLMs externos, BYOK (chave criptografada com Fernet, faturamento direto pelo provedor), transferência de prompts ao provedor LLM (com aviso de revisão da política do provedor), **compromisso vinculante de não-treinamento de modelos com dados do usuário** (privacidade como cláusula contratual), riscos próprios de IA (alucinação, tool calls, indisponibilidade, custos imprevisíveis), conexão de clientes MCP externos (Claude Desktop, Cursor, VS Code) com responsabilidade do JWT, e Aura como opcional. Atualizações pontuais: novo item de risco (Seção 3) sobre sandboxes Bybit Testnet/OKX Demo Trading; Seção 6 (LGPD) explicita criptografia Fernet de chaves de exchange + LLM. Versão 2.1 → 3.0, data Março → Abril/2026. i18n em 6 idiomas.
- [x] **Landing Redesign + UX da Aura (v8.1)** — Landing reposicionada com a Aura como gancho principal e a Pro destacada como tier recomendado. Hero responde "o que é + para quem" em 5s: linha de categoria em caps ("PLATAFORMA DE TRADING ALGORÍTMICO PARA CRIPTOMOEDAS"), headline "Crie, valide e opere estratégias de trading conversando com a IA", sub abrindo com o ICP e apresentando "Aura, a IA do Gastor" antes de soltar o nome, e linha "não é uma corretora, não é um grupo de sinais" abaixo dos CTAs eliminando mal-entendidos clássicos de software de trading. Novas seções **AuraSection** (4 capabilities com prompts reais, providers OpenAI/Anthropic/Google/Meta/Mistral/DeepSeek), **MultiExchangeSection** (Binance/Bybit/OKX) e **DecisionLogsSection** (cada trade vira dado de treino, com mockup de log); WorkflowSection reduzido para 4 passos (Conversar → Validar → Simular → Decidir); Pricing redesenhado em comparação visual de 9 features × 3 tiers; FAQ +3 (Aura cobra à parte? Posso usar sem? O que é MCP?). Página `/chat` redesenhada — glyph SVG no lugar do emoji 🤖, painel `AuraCapabilities` agrupado por categoria com tier locks, sugestões filtradas pelo plano do usuário, callout primary (não amarelo) com CTA direto para `/user/panel`. Aba **Integrações** no User Panel centralizou chaves de exchange e API key da Aura/LLM (movidas de `/settings/profile`), com sub-abas Exchanges + IA & Assistente. Catálogo de tools auditado: 5 ghosts removidas (`market_sentiment`, `export_decision_logs`, `find_best_strategy`, `full_strategy_analysis`, `session_performance_report`), `get_trade_pair` adicionada; teste bidirecional impede regressão. Modelo do LLM virou input livre com `<datalist>` agnóstico de provedor. 187 chaves no namespace `Landing` em 6 idiomas (com `heroCategory` e `heroNotIs` adicionados no ajuste de clareza).
- [x] **MCP Hardening — Phase B (v8.3)** — Transformação do MCP de canal interno para feature de produção, em 8 commits sequenciais e auditáveis. **Tokens MCP escopados** (`aud="mcp"` + `jti` em `mcp_tokens`, expiração 90d, revogação granular) substituem o uso do JWT da sessão principal — defesa em profundidade nas duas direções. **Audit log** (`mcp_audit_log`) com snapshot completo de cada call, instrumentado em `execute_tool` (chat bridge) e em `require_mcp_tool_access` (clients externos). **Rate limit por categoria** (token-bucket in-process por (user, category) com refill linear; tools caras como `run_backtest` 10/min Pro, `run_grid_search` 5/min Pro). **Cost cap diário** (Free 20 / Pro 200 / Desk 1000 chamadas/dia, contagem do audit log; reset UTC). **Alerta Telegram no primeiro uso** de cada token (snapshot do `last_used_at` antes do bump; envia IP, UA, timestamp BRT). **IP allowlist** opcional por token (lista CSV de IPs/CIDR; tolera entradas malformadas). **Painel admin** em `/admin/mcp` com KPIs, rollups por tool/usuário/categoria/origem e audit log filtrado. **UI no User Panel** com criação/revogação de tokens, barra de uso diário e banner do JWT raw exibido apenas uma vez. **Página `/docs/mcp`** acessível ao usuário final com snippets de configuração para Claude Desktop / Cursor / VS Code. **MCP_ENABLED=true em produção** após o rollout completo. 207 testes passando, zero regressões.

### 🔜 Próximas Fases (em ordem)

| Fase | Descrição | Status |
|------|-----------|--------|
| **1.5. 📊 Better Risk Metrics** | Implementação do **Sortino Ratio** em toda a stack (Research + Backend + Optimizer). Penaliza apenas downside volatility, permitindo estratégias de alto upside. Valido para identificar bull runs. | ✅ Concluído |
| **2. 📝 Logs de Trading** | Snapshot completo de indicadores, candle, regras ativas, motivo de saída e latência por trade. Base proprietária para auditoria e fine-tuning de modelos ML. Export CSV e JSONL pareado (BUY+SELL) via API. | ✅ Concluído |
| **3. 🔒 Testes de Segurança** | Auditoria de segurança: rate limiting, proteção contra replay attacks em JWT, validação de inputs, testes de penetração OWASP, hardening de containers Docker. Dependências vulneráveis corrigidas. | ✅ Concluído |
| **4. 🌐 Internacionalização (i18n)** | Suporte multi-idioma completo: 🇧🇷 PT-BR (default), 🇺🇸 English, 🇪🇸 Español, 🇨🇳 中文, 🇯🇵 日本語, 🇰🇷 한국어. Migração do schema do banco para inglês. Timezone configurável por usuário. | ✅ Concluído |
| **5. 🔄 Multi-Exchange** | Suporte a Binance, Bybit e OKX — client CCXT genérico, WebSocket multi-exchange, lot size precision, Unified Accounts, Decision Logs multi-exchange. | ✅ Concluído |
| **6. 💎 Freemium Tiers + Landing + Inatividade** | Freemium (Free/Pro/Desk) via invite codes com feature gating. Landing page narrativa pública. Termos de Uso v2.0. Controle de inatividade com soft-delete e aviso Telegram. | ✅ Concluído |
| **6.1 🔍 SEO + Landing Polish** | `sitemap.xml`, `robots.txt`, `generateMetadata` por rota pública, JSON-LD schemas. Hero dual-card animado: builder mockup (regras aparecem uma a uma) + equity curve — diferencial "sem código" visível imediatamente. Subtítulo atualizado para incluir o no-code angle. | ✅ Concluído |
| **6.2 📅 Subscription Expiry** | Validade de assinatura por tier. `plan_tier_expires_at` em `users`, `subscription_days` em `invite_codes`. Downgrade automático diário, alerta Telegram ao admin, renovação via painel, exibição de expiração no User Panel. | ✅ Concluído |
| **8. 🤖 MCP Agêntico + Aura** | Interface MCP (Model Context Protocol) para interação agêntica com o Gastor. Servidor MCP em `/mcp` com **19 ferramentas reais** distribuídas em 9 categorias e 4 tiers (Free/Pro/Desk/Admin). **Aura by Gastor** — a assistente de IA interna em `/chat` com ponte OpenAI-compatible, agnóstica a provedor (OpenAI, Anthropic, Google, Meta, Mistral, DeepSeek). Config LLM por usuário centralizada em **Painel → Integrações → IA & Assistente**, criptografada com Fernet. Suporte a Claude Desktop, Cursor e VS Code via MCP. | ✅ Concluído |
| **8.1 🎨 Landing Redesign + UX da Aura** | Hero responde "o que é + para quem" em 5s (categoria em caps, headline "Crie, valide e opere estratégias de trading conversando com a IA", linha "não é uma corretora, não é um grupo de sinais"). AuraSection com 4 capabilities + mockup de conversa, MultiExchangeSection, DecisionLogsSection, Pricing em comparação visual (3 tiers, Pro destacado), FAQ +3 perguntas. `/chat` redesenhada — glyph SVG, painel de capabilities por categoria com tier locks, sugestões filtradas por tier. Aba "Integrações" no User Panel centralizando chaves de exchange e LLM. Catálogo de tools auditado (5 ghosts removidas, `get_trade_pair` adicionada, teste bidirecional). Modelo de LLM agnóstico por `<datalist>`. 187 chaves i18n no namespace `Landing` em 6 idiomas. | ✅ Concluído |
| **8.2 📋 Termos de Uso v3.0** | Reescrita dos Termos para refletir v8.0/v8.1: nova Seção 5 dedicada à Aura (BYOK, transferência ao provedor LLM, compromisso de não-treinamento, riscos da IA, clientes MCP externos), atualização da Seção 3 (sandboxes Bybit/OKX) e Seção 6 (criptografia Fernet de chaves de exchange + LLM). 12 → 13 seções, versão 2.1 → 3.0. i18n em 6 idiomas. | ✅ Concluído |
| **8.3 🔐 MCP Hardening — Phase B** | Hardening enterprise-grade do MCP em 8 camadas: tokens MCP-escopados (`aud="mcp"`, `jti`, 90d, revogação), audit log completo, rate limit por categoria, cost cap diário, alerta Telegram no primeiro uso, IP allowlist por token, painel admin de analytics, UI no User Panel + página `/docs/mcp` para clientes externos. `MCP_ENABLED=true` em produção. 207 testes. | ✅ Concluído |
| **9. 🚀 Live Trading** | Execução automática em conta real via API de qualquer exchange suportada (Binance, Bybit, OKX). Kill switch de emergência, limites de exposição e confirmação dupla via Telegram. Requer análise regulatória (CVM). | 🔜 Próximo Passo |

> ⚠️ **Filosofia:** Cada fase é pré-requisito da próxima. O hardening do MCP (v8.3) precede o Live Trading porque os mesmos controles de segurança — tokens escopados, audit log, rate limit, cost cap, alerta no primeiro uso, IP allowlist — vão valer dobrado quando houver dinheiro real fluindo pela mesma camada de tool calling.

### 🧭 Análise de Evolução — Por que MCP antes de Live Trading?

Três caminhos foram avaliados como evolução natural do Gastor:

| Critério | 🤖 MCP Agêntico | 🚀 Live Trading | 🏦 Novos Mercados (B3) |
|----------|:-:|:-:|:-:|
| **Infraestrutura pronta** | 🟡 ~40% (OpenAPI existe) | 🟢 ~85% (CCXT/engine) | 🔴 ~10% |
| **Barreira burocrática** | 🟢 Nenhuma | 🔴 Alta (CVM) | 🔴 Alta (custo de dados) |
| **Diferencial competitivo** | 🟢 Alto | 🟡 Médio | 🟡 Médio |
| **Monetização imediata** | 🟢 Rápida (tier feature) | 🔴 Lenta (regulação) | 🔴 Lenta (integrações) |
| **Risco técnico** | 🟢 Baixo | 🔴 Alto (dinheiro real) | 🟡 Médio |

**Decisão: MCP Agêntico (Fase 8)**

1. **Zero burocracia** — não mexe com dinheiro real nem com regulação da CVM
2. **Infra parcialmente pronta** — OpenAPI schema público com 53 endpoints já existe em `/api/openapi.json`
3. **Diferencial de mercado** — nenhuma plataforma de trading quantitativo para cripto oferece interação agêntica via MCP hoje
4. **Monetização natural** — encaixa como feature premium nos tiers Pro/Desk existentes
5. **Efeito cascata** — qualquer agente (Cursor, Claude Desktop, custom) pode operar o Gastor, multiplicando o alcance

> 💡 O Live Trading (Fase 9) continua planejado — e o MCP será o canal natural para configurar e monitorar operações reais.

### 🌐 Fase 4 — Internacionalização (i18n) — Sub-fases

| Sub-fase | Descrição | Escopo |
|----------|-----------|--------|
| **4.1 🏗️ Infraestrutura** | Setup do `next-intl` no App Router. Estrutura de arquivos de tradução (`messages/pt-BR.json`, `en.json`, etc.). Dropdown de idioma na navbar (desktop + mobile) com bandeira + código. Preferência salva em `localStorage` e no perfil do usuário. | Frontend ✅ |
| **4.2 🖥️ Tradução do Frontend** | Extração de todas as strings hardcoded para arquivos de tradução. Cobertura de todas as páginas: Dashboard, Laboratório, Otimizador, Construtor, Live Trading, Admin, Glossário, Settings, Termos de Uso, Login/Registro. | Frontend ✅ |
| **4.3 🗄️ Backend i18n** | Migração do schema do banco de dados para inglês (colunas e tabelas). Logs internos do servidor padronizados em inglês. Respostas de API (mensagens de erro user-facing) traduzidas por locale. Templates do Telegram traduzidos para o idioma do usuário. | Backend ✅ |
| **4.4 ✨ Polimento** | Timezone configurável por usuário no perfil (override do auto-detect do navegador). Backend armazena tudo em UTC, frontend converte para exibição. Formatação de números e datas por locale (`Intl`). Revisão de qualidade das traduções (zh, ja, ko). | Full Stack ✅ |

### 💡 Backlog (Sem Prioridade Definida)

- [ ] **Machine Learning Avançado** — Integração com modelos Deep Learning (LSTMs) para predição de sinais.
- [ ] **Novos Mercados (B3, NYSE)** — Expansão para mercados tradicionais. Requer integração com brokers (XP, Clear), dados de mercado pagos e adequação a horários de pregão/settlement T+2.

---

## 📄 Licença

Copyright (c) 2026 Gastor Analytics. All rights reserved.

Este projeto é **proprietário e confidencial**. O uso, cópia, modificação ou distribuição não autorizada deste software é estritamente proibida.
