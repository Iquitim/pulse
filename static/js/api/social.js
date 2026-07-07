import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request } from './client.js';
import * as ui from '../ui.js';

export async function fetchConnectedAccounts() {
  try {
    const res = await request('/api/social-accounts');
    if (!res.ok) throw new Error('Erro ao buscar contas conectadas');
    state.connectedAccounts = await res.json();
    ui.renderConnectedAccounts();
  } catch (error) {
    addConsoleLog(`Erro ao obter contas conectadas: ${error.message}`, 'erro');
  }
}

export async function connectAccount(platform, accountHandle, credentials) {
  const errorDiv = document.getElementById("social-connect-error");
  const errorMsg = document.getElementById("social-connect-error-msg");
  if (errorDiv) errorDiv.classList.add("hidden");
  
  try {
    const res = await request('/api/social-accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform,
        account_handle: accountHandle,
        credentials
      })
    });
    const result = await res.json();
    
    if (!res.ok) {
      throw new Error(result.detail || 'Não foi possível vincular a conta.');
    }
    
    addConsoleLog(`Conta ${accountHandle} vinculada no ${platform} com sucesso!`, 'sucesso');
    
    // Reset inputs
    document.getElementById("social-handle-input").value = "";
    if (platform === "bluesky") {
      document.getElementById("bsky-username-input").value = "";
      document.getElementById("bsky-password-input").value = "";
    } else if (platform === "twitter") {
      const keyInput = document.getElementById("twitter-key-input");
      const secretInput = document.getElementById("twitter-secret-input");
      if (keyInput) keyInput.value = "";
      if (secretInput) secretInput.value = "";
    } else if (platform === "threads") {
      // Threads uses no input fields to reset
    }
    
    await fetchConnectedAccounts();
    await fetchStatus();
  } catch (error) {
    if (errorDiv && errorMsg) {
      errorDiv.classList.remove("hidden");
      errorMsg.textContent = error.message;
    }
    addConsoleLog(`Falha ao vincular rede social: ${error.message}`, 'erro');
  }
}

export async function disconnectAccount(id) {
  try {
    const res = await request(`/api/social-accounts/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Não foi possível remover a conta');
    addConsoleLog('Rede social desconectada.', 'sucesso');
    await fetchConnectedAccounts();
    await fetchStatus();
  } catch (error) {
    addConsoleLog(`Erro ao desconectar conta: ${error.message}`, 'erro');
  }
}

export async function fetchStatus() {
  try {
    const res = await request('/api/status');
    if (!res.ok) throw new Error('Falha ao buscar status do sistema');
    
    const statusData = await res.json();
    
    state.connectionStatus = {
      gemini: statusData.gemini.connected ? 'online' : 'offline',
      gemini_msg: statusData.gemini.connected ? `Ativo (${statusData.gemini.name})` : 'Não configurado',
      bsky: statusData.bsky.connected ? 'online' : 'offline',
      bsky_msg: statusData.bsky.connected ? `Conectado (@${statusData.bsky.handle})` : 'Desconectado',
      twitter: statusData.twitter.connected ? 'online' : 'offline',
      twitter_msg: statusData.twitter.connected ? `Conectado (@${statusData.twitter.handle})` : 'Desconectado',
      scheduler: statusData.scheduler.active ? 'online' : 'offline',
      scheduler_msg: statusData.scheduler.active ? 'Scheduler: Ativo' : 'Scheduler: Inativo'
    };
    
    if (statusData.scheduler.next_run) {
      state.nextPostTime = new Date(statusData.scheduler.next_run).getTime();
    } else {
      state.nextPostTime = null;
    }
    
    ui.updateConnectionBadge('status-gemini', state.connectionStatus.gemini, `IA: ${state.connectionStatus.gemini_msg}`);
    ui.updateConnectionBadge('status-bsky', state.connectionStatus.bsky, `Bluesky: ${state.connectionStatus.bsky_msg}`);
    ui.updateConnectionBadge('status-twitter', state.connectionStatus.twitter, `Twitter: ${state.connectionStatus.twitter_msg}`);
    
    const previewHandle = document.getElementById('preview-handle');
    if (previewHandle) {
      if (statusData.bsky.connected && statusData.bsky.handle) {
        previewHandle.textContent = `@${statusData.bsky.handle}`;
      } else {
        previewHandle.textContent = '@usuario.bsky.social';
      }
    }
    
    ui.updateMetrics();
    ui.updateQueueList();
  } catch (error) {
    ui.updateConnectionBadge('status-gemini', 'offline', 'IA: Erro de API');
    ui.updateConnectionBadge('status-bsky', 'offline', 'Bluesky: Erro de API');
    ui.updateConnectionBadge('status-twitter', 'offline', 'Twitter: Erro de API');
    addConsoleLog(`Falha na sincronização de status: ${error.message}`, 'erro');
  }
}
