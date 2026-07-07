import { state } from './state.js';
import { addConsoleLog } from './logger.js';
import * as ui from './ui.js';
import * as api from './api.js';

import { setupAuthEvents } from './events/auth.js';
import { setupEditorEvents } from './events/editor.js';
import { setupLibraryEvents } from './events/library.js';
import { setupCalendarEvents } from './events/calendar.js';
import { setupConfigEvents } from './events/config.js';
import { setupAdminEvents } from './events/admin.js';
import { setupOllamaEvents } from './events/ollama.js';
import { setupTutorialEvents } from './events/tutorial.js';

// --- Background Timer & Countdown ---
function startTimerCountdown() {
  const countdownTimer = document.getElementById('countdown-timer');
  const countdownSubtext = document.getElementById('countdown-subtext');
  if (!countdownTimer || !countdownSubtext) return;
  
  if (state.countdownInterval) clearInterval(state.countdownInterval);
  
  state.countdownInterval = setInterval(() => {
    // Only check if user is logged in
    if (!state.token) return;

    if (!state.appConfig.is_active || !state.nextPostTime) {
      countdownTimer.textContent = '--:--:--';
      countdownSubtext.textContent = 'Agendador pausado ou inativo.';
      return;
    }
    
    const now = new Date().getTime();
    const diff = state.nextPostTime - now;
    
    if (diff <= 0) {
      countdownTimer.textContent = '00:00:00';
      countdownSubtext.textContent = 'Executando ciclo automático...';
      setTimeout(api.fetchStatus, 3000);
    } else {
      countdownTimer.textContent = ui.formatCountdown(diff);
      const nextDate = new Date(state.nextPostTime);
      countdownSubtext.textContent = `Próxima postagem estimada em: ${nextDate.toLocaleTimeString()}`;
    }
  }, 1000);
}

function setupEventListeners() {
  setupAuthEvents();
  setupEditorEvents();
  setupLibraryEvents();
  setupCalendarEvents();
  setupConfigEvents();
  setupAdminEvents();
  setupOllamaEvents();
  setupTutorialEvents();

  // Sync the visual selectors for the editor and idea capture screens initially
  ui.syncVisualSelector('draft-channel', 'draft-channel-selector');
  ui.syncVisualSelector('idea-channel', 'idea-channel-selector');
}

function applyPublicSettingsUI() {
  const settings = state.publicSettings || { allow_public_registration: true, require_invite_code: false };
  
  const btnLandingRegister = document.getElementById('btn-landing-register');
  const btnHeroStart = document.getElementById('btn-hero-start');
  const switchToRegisterContainer = document.getElementById('switch-to-register-container');
  const registerInviteGroup = document.getElementById('register-invite-group');
  const registerInviteInput = document.getElementById('register-invite');
  const goToRegisterLink = document.getElementById('go-to-register');
  
  if (!settings.allow_public_registration) {
    if (btnLandingRegister) btnLandingRegister.classList.add('hidden');
    if (switchToRegisterContainer) switchToRegisterContainer.classList.add('hidden');
    if (btnHeroStart) {
      btnHeroStart.textContent = "Acessar Painel";
      btnHeroStart.addEventListener('click', (e) => {
        e.stopImmediatePropagation();
        document.getElementById('landing-page')?.classList.add('hidden');
        document.getElementById('auth-container')?.classList.remove('hidden');
        document.getElementById('login-form')?.classList.remove('hidden');
        document.getElementById('register-form')?.classList.add('hidden');
        document.getElementById('change-password-form')?.classList.add('hidden');
        document.getElementById('auth-title').textContent = "Entrar no Pulse";
        document.getElementById('auth-error')?.classList.add('hidden');
      });
    }
  } else {
    if (btnLandingRegister) btnLandingRegister.classList.remove('hidden');
    if (switchToRegisterContainer) switchToRegisterContainer.classList.remove('hidden');
    
    if (settings.require_invite_code) {
      if (registerInviteGroup) registerInviteGroup.classList.remove('hidden');
      if (registerInviteInput) {
        registerInviteInput.required = true;
        registerInviteInput.placeholder = "PULSE-XXXX-XXXX";
      }
      if (goToRegisterLink) goToRegisterLink.textContent = "Registrar com convite";
    } else {
      if (registerInviteGroup) registerInviteGroup.classList.add('hidden');
      if (registerInviteInput) {
        registerInviteInput.required = false;
        registerInviteInput.placeholder = "";
      }
      if (goToRegisterLink) goToRegisterLink.textContent = "Criar uma conta";
    }
  }
}

async function checkOllamaBannerStatus() {
  if (!state.token) return;
  try {
    const statusData = await api.fetchOllamaStatus();
    state.ollamaStatus = statusData;
    
    const banner = document.getElementById('ollama-installer-banner');
    if (banner) {
      if (statusData.status === 'not_installed' || statusData.status === 'stopped') {
        banner.classList.remove('hidden');
      } else {
        banner.classList.add('hidden');
      }
    }
  } catch (err) {
    console.error('Erro ao verificar status do Ollama para banner:', err);
  }
}

// --- Initialization ---
async function init() {
  setupEventListeners();

  // Restore saved theme on startup
  const savedTheme = localStorage.getItem('pulse_theme') || 'dark';
  if (savedTheme === 'light') {
    document.documentElement.classList.add('light-theme');
  } else {
    document.documentElement.classList.remove('light-theme');
  }

  // Buscar configurações públicas no boot (registro aberto, convites)
  await api.fetchPublicSettings();
  applyPublicSettingsUI();

  // If token is present, try validating session
  if (state.token) {
    await api.fetchMe();
    await checkOllamaBannerStatus();
  } else {
    api.logout();
  }

  // Status check intervals (5s) for authenticated sessions
  setInterval(() => {
    if (state.token) {
      api.fetchStatus();
      checkOllamaBannerStatus();
    }
  }, 5000);
  
  // Run scheduler countdown ticker
  startTimerCountdown();
  
  addConsoleLog('Painel do Pulse carregado.', 'system');
}

// Boot up
window.addEventListener('DOMContentLoaded', init);
