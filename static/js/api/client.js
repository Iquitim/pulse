import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';

// Helper custom fetch to automatically append headers and verify JWT sessions
export async function request(url, options = {}) {
  options.headers = options.headers || {};
  if (state.token) {
    options.headers['Authorization'] = `Bearer ${state.token}`;
  }
  
  const res = await fetch(url, options);
  if (res.status === 401) {
    logout();
    throw new Error('Sessão expirada. Faça login novamente.');
  }
  return res;
}

export function logout() {
  localStorage.removeItem("pulse_token");
  state.token = null;
  state.user = null;
  state.connectedAccounts = [];
  state.inviteCodes = [];
  state.usersList = [];
  state.calendarItems = [];
  state.activeCalendarItemId = null;
  
  // Update view classes
  document.getElementById("landing-page")?.classList.remove("hidden");
  document.getElementById("auth-container")?.classList.add("hidden");
  document.querySelector(".app-container")?.classList.add("hidden");
  
  // Reset fields
  const loginEmail = document.getElementById("login-email");
  const loginPass = document.getElementById("login-password");
  if (loginEmail) loginEmail.value = "";
  if (loginPass) loginPass.value = "";
  
  addConsoleLog('Sessão encerrada.', 'system');
}

export async function fetchPublicSettings() {
  try {
    const res = await fetch('/api/public-settings');
    if (!res.ok) {
      throw new Error('Não foi possível obter as configurações públicas.');
    }
    const data = await res.json();
    state.publicSettings = data;
    
    // Toggle public register option in UI
    const registerCta = document.getElementById('btn-landing-register');
    const heroRegisterCta = document.getElementById('btn-hero-start');
    if (registerCta) {
      if (data.allow_public_registration) {
        registerCta.classList.remove('hidden');
        if (heroRegisterCta) heroRegisterCta.textContent = 'Iniciar Agora';
      } else {
        registerCta.classList.add('hidden');
        if (heroRegisterCta) heroRegisterCta.textContent = 'Entrar no Painel';
      }
    }
    
    // Show/hide invite code field on register form
    const registerInviteField = document.getElementById('register-invite-field');
    const registerInviteInput = document.getElementById('register-invite-code');
    if (registerInviteField && registerInviteInput) {
      if (data.require_invite_code) {
        registerInviteField.classList.remove('hidden');
        registerInviteInput.required = true;
      } else {
        registerInviteField.classList.add('hidden');
        registerInviteInput.required = false;
      }
    }
  } catch (error) {
    addConsoleLog(`Erro ao obter configurações públicas: ${error.message}`, 'erro');
  }
}
