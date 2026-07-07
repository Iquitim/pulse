// Shared global state for the application
export const state = {
  token: localStorage.getItem("pulse_token") || null,
  user: null, // { email, role, plan_tier }
  llmServers: [],
  connectedAccounts: [],
  inviteCodes: [],
  usersList: [],
  appConfig: {
    themes: [],
    tone: 'informativo',
    interval_hours: 6,
    is_active: false,
    system_prompt: '',
    persona_description: '',
    requires_approval: false
  },
  connectionStatus: {
    gemini: 'loading',
    bsky: 'loading',
    scheduler: 'loading',
    scheduler_msg: 'Verificando...'
  },
  postHistory: [],
  auditLogs: [],
  countdownInterval: null,
  nextPostTime: null,
  currentDraftTheme: 'Geral',
  calendarItems: [],
  activeCalendarItemId: null,
  activeDraftId: null,
  calendarYear: new Date().getFullYear(),
  publicSettings: {
    allow_public_registration: true,
    require_invite_code: false
  },
  ideas: [],
  activeLibrarySubTab: 'history',
  currentIdeaText: null,
  qualityAnalysis: null,
  metricsInsights: null,
  ollamaStatus: { status: 'loading', type: 'none', embedded_installed: false },
  ollamaDiagnostic: null,
  ollamaPullProgress: {}
};

