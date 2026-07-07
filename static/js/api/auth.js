import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request, logout } from './client.js';
import * as ui from '../ui.js';

// Circular imports are resolved by importing from direct modules
import { fetchConfig } from './config.js';
import { fetchStatus, fetchConnectedAccounts } from './social.js';
import { fetchHistory } from './posts.js';
import { fetchCalendarItems } from './calendar.js';
import { fetchIdeas } from './ideas.js';
import { fetchUsersList, fetchInviteCodes, fetchAuditLogs } from './admin.js';

export async function loginUser(email, password) {
  const errorDiv = document.getElementById("auth-error");
  const errorMsg = document.getElementById("auth-error-msg");
  if (errorDiv) errorDiv.classList.add("hidden");

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const result = await res.json();
    
    if (!res.ok) {
      throw new Error(result.detail || 'E-mail ou senha inválidos.');
    }
    
    if (result.user.must_change_password) {
      state.token = result.access_token;
      localStorage.setItem("pulse_token", result.access_token);
      state.user = result.user;
      
      document.getElementById("login-form")?.classList.add("hidden");
      document.getElementById("register-form")?.classList.add("hidden");
      document.getElementById("change-password-form")?.classList.remove("hidden");
      document.getElementById("auth-title").textContent = "Alteração de Senha";
      document.getElementById("auth-subtitle").textContent = "Você deve alterar sua senha temporária no primeiro login.";
      document.getElementById("auth-error")?.classList.add("hidden");
      addConsoleLog("Alteração de senha obrigatória pendente.", "alerta");
      return;
    }

    state.token = result.access_token;
    localStorage.setItem("pulse_token", result.access_token);
    state.user = result.user;
    
    // UI toggle
    document.getElementById("landing-page")?.classList.add("hidden");
    document.getElementById("auth-container")?.classList.add("hidden");
    document.querySelector(".app-container")?.classList.remove("hidden");
    
    // Render email badge
    const headerUser = document.getElementById("header-user-email");
    if (headerUser) headerUser.textContent = state.user.email;
    
    // Toggle Admin navigation tab visibility
    const navAdminBtn = document.getElementById("nav-admin-btn");
    if (navAdminBtn) {
      if (state.user.role === 'admin') {
        navAdminBtn.classList.remove("hidden");
      } else {
        navAdminBtn.classList.add("hidden");
      }
    }
    
    let planLabel = 'Pessoal';
    if (state.user.plan_tier === 'pro') planLabel = 'Entusiasta';
    else if (state.user.plan_tier === 'desk') planLabel = 'Coletivo';
    addConsoleLog(`Autenticado como ${state.user.email}. Nível de Uso: [${planLabel}]`, 'sucesso');
    
    // Bootstrap data fetching
    await fetchConfig();
    await fetchStatus();
    await fetchHistory();
    await fetchConnectedAccounts();
    await fetchCalendarItems();
    await fetchIdeas();
    
    // Lazy load metrics or import on demand
    const ideasModule = await import('./ideas.js');
    await ideasModule.fetchMetricsInsights();
    
    if (state.user.role === 'admin') {
      await fetchUsersList();
      await fetchInviteCodes();
    }
  } catch (error) {
    if (errorDiv && errorMsg) {
      errorDiv.classList.remove("hidden");
      errorMsg.textContent = error.message;
    }
    addConsoleLog(`Falha ao realizar login: ${error.message}`, 'erro');
  }
}

export async function registerUser(email, password, inviteCode) {
  const errorDiv = document.getElementById("auth-error");
  const errorMsg = document.getElementById("auth-error-msg");
  if (errorDiv) errorDiv.classList.add("hidden");

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, invite_code: inviteCode || null })
    });
    const result = await res.json();
    
    if (!res.ok) {
      throw new Error(result.detail || 'Erro ao registrar usuário.');
    }
    
    addConsoleLog('Registro concluído com sucesso. Iniciando login automático...', 'sucesso');
    await loginUser(email, password);
  } catch (error) {
    if (errorDiv && errorMsg) {
      errorDiv.classList.remove("hidden");
      errorMsg.textContent = error.message;
    }
    addConsoleLog(`Falha ao registrar usuário: ${error.message}`, 'erro');
  }
}

export async function changePassword(currentPassword, newPassword) {
  const errorDiv = document.getElementById("auth-error");
  const errorMsg = document.getElementById("auth-error-msg");
  if (errorDiv) errorDiv.classList.add("hidden");
  
  try {
    const res = await request('/api/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });
    const result = await res.json();
    if (!res.ok) {
      throw new Error(result.detail || 'Erro ao alterar senha.');
    }
    
    addConsoleLog('Senha alterada com sucesso! Acessando painel...', 'sucesso');
    
    // Reset inputs
    document.getElementById("change-current-password").value = "";
    document.getElementById("change-new-password").value = "";
    document.getElementById("change-confirm-password").value = "";
    
    // Hide change password form and show dashboard
    document.getElementById("landing-page")?.classList.add("hidden");
    document.getElementById("auth-container")?.classList.add("hidden");
    document.getElementById("change-password-form")?.classList.add("hidden");
    document.querySelector(".app-container")?.classList.remove("hidden");
    
    // Reload state securely
    await fetchMe();
  } catch (error) {
    if (errorDiv && errorMsg) {
      errorDiv.classList.remove("hidden");
      errorMsg.textContent = error.message;
    }
    addConsoleLog(`Falha ao alterar senha obrigatória: ${error.message}`, 'erro');
  }
}

export async function changePasswordSelf(currentPassword, newPassword) {
  try {
    const res = await request('/api/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });
    const result = await res.json();
    if (!res.ok) {
      throw new Error(result.detail || 'Erro ao alterar senha.');
    }
    
    addConsoleLog('Senha alterada com sucesso!', 'sucesso');
    ui.showToast('Senha alterada com sucesso!', 'sucesso');
    return true;
  } catch (error) {
    addConsoleLog(`Falha ao alterar senha: ${error.message}`, 'erro');
    ui.showToast(error.message, 'erro');
    return false;
  }
}

export async function fetchMe() {
  try {
    const res = await request('/api/auth/me');
    if (!res.ok) throw new Error('Não autenticado');
    state.user = await res.json();
    
    if (state.user.must_change_password) {
      document.getElementById("auth-container")?.classList.remove("hidden");
      document.querySelector(".app-container")?.classList.add("hidden");
      document.getElementById("login-form")?.classList.add("hidden");
      document.getElementById("register-form")?.classList.add("hidden");
      document.getElementById("change-password-form")?.classList.remove("hidden");
      document.getElementById("auth-title").textContent = "Alteração de Senha";
      document.getElementById("auth-subtitle").textContent = "Você deve alterar sua senha temporária no primeiro login.";
      addConsoleLog("Alteração de senha obrigatória pendente.", "alerta");
      return;
    }
    
    // Setup header
    const headerUser = document.getElementById("header-user-email");
    if (headerUser) headerUser.textContent = state.user.email;
    
    const navAdminBtn = document.getElementById("nav-admin-btn");
    if (navAdminBtn) {
      if (state.user.role === 'admin') {
        navAdminBtn.classList.remove("hidden");
      } else {
        navAdminBtn.classList.add("hidden");
      }
    }
    
    document.getElementById("landing-page")?.classList.add("hidden");
    document.getElementById("auth-container")?.classList.add("hidden");
    document.querySelector(".app-container")?.classList.remove("hidden");
    
    // Fetch core contents
    await fetchConfig();
    await fetchStatus();
    await fetchHistory();
    await fetchConnectedAccounts();
    await fetchCalendarItems();
    await fetchAuditLogs();
    await fetchIdeas();
    
    // Lazy load insights
    const ideasModule = await import('./ideas.js');
    await ideasModule.fetchMetricsInsights();
    
    if (state.user.role === 'admin') {
      await fetchUsersList();
      await fetchInviteCodes();
    }
  } catch (error) {
    logout();
  }
}
