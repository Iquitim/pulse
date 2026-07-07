import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request } from './client.js';
import * as ui from '../ui.js';
import { fetchStatus } from './social.js';

export async function fetchConfig() {
  try {
    const res = await request('/api/config');
    if (!res.ok) throw new Error('Falha ao buscar configurações');
    
    state.appConfig = await res.json();
    
    const isActiveInput = document.getElementById('is_active');
    const requiresApprovalInput = document.getElementById('requires_approval');
    const toneSelect = document.getElementById('tone');
    const intervalHoursInput = document.getElementById('interval_hours');
    const intervalDisplay = document.getElementById('interval-display');
    const systemPromptInput = document.getElementById('system_prompt');
    const personaDescriptionInput = document.getElementById('persona_description');
    const schedulingModeSelect = document.getElementById('scheduling_mode');
    if (isActiveInput) isActiveInput.checked = state.appConfig.is_active;
    if (requiresApprovalInput) requiresApprovalInput.checked = state.appConfig.requires_approval || false;
    if (toneSelect) toneSelect.value = state.appConfig.tone;
    if (intervalHoursInput) intervalHoursInput.value = state.appConfig.interval_hours;
    if (intervalDisplay) intervalDisplay.textContent = `A cada ${state.appConfig.interval_hours} ${state.appConfig.interval_hours === 1 ? 'hora' : 'horas'}`;
    
    if (schedulingModeSelect) {
      schedulingModeSelect.value = state.appConfig.scheduling_mode || 'recorrente';
      ui.toggleSchedulingModeUI(state.appConfig.scheduling_mode || 'recorrente');
    }
    
    const recurrentChannelInput = document.getElementById('recurrent-channel');
    if (recurrentChannelInput) {
      recurrentChannelInput.value = state.appConfig.channel || 'bluesky';
      syncVisualSelector('recurrent-channel', 'recurrent-channel-selector');
    }
    
    ui.updateFrequencyEstimateText(state.appConfig.interval_hours);
    ui.syncPresetButtons(state.appConfig.interval_hours);
    
    if (systemPromptInput) systemPromptInput.value = state.appConfig.system_prompt || '';
    if (personaDescriptionInput) personaDescriptionInput.value = state.appConfig.persona_description || '';
    
    ui.renderThemes();
    await fetchLLMServers();
    addConsoleLog('Configurações carregadas com sucesso.', 'info');
  } catch (error) {
    addConsoleLog(`Erro ao carregar configurações: ${error.message}`, 'erro');
  }
}

export async function saveConfig(e) {
  if (e && typeof e.preventDefault === 'function') e.preventDefault();
  
  const button = document.getElementById('btn-save-config');
  const isFormSubmit = e && e.type === 'submit';
  
  if (button && isFormSubmit) {
    button.disabled = true;
    button.textContent = 'Salvando...';
  }
  
  try {
    const toneSelect = document.getElementById('tone');
    const intervalHoursInput = document.getElementById('interval_hours');
    const isActiveInput = document.getElementById('is_active');
    const systemPromptInput = document.getElementById('system_prompt');
    const personaDescriptionInput = document.getElementById('persona_description');
    const requiresApprovalInput = document.getElementById('requires_approval');
    const schedulingModeSelect = document.getElementById('scheduling_mode');
    
    const llmProviderSelect = document.getElementById('llm_provider');
    const llmModelInput = document.getElementById('llm_model');
    const llmBaseUrlInput = document.getElementById('llm_base_url');
    const llmApiKeyInput = document.getElementById('llm_api_key');
    
    const configToSave = {
      themes: state.appConfig.themes,
      tone: toneSelect?.value || 'informativo',
      interval_hours: intervalHoursInput ? parseInt(intervalHoursInput.value, 10) : 6,
      is_active: isActiveInput ? isActiveInput.checked : false,
      system_prompt: systemPromptInput?.value || '',
      persona_description: personaDescriptionInput?.value || '',
      requires_approval: requiresApprovalInput ? requiresApprovalInput.checked : false,
      scheduling_mode: schedulingModeSelect?.value || 'recorrente',
      llm_provider: llmProviderSelect?.value || 'gemini',
      llm_model: llmModelInput?.value || 'gemini-2.5-flash-lite',
      llm_base_url: llmBaseUrlInput?.value || null,
      llm_api_key: llmApiKeyInput?.value || null,
      channel: document.getElementById('recurrent-channel')?.value || 'bluesky'
    };
    
    const res = await request('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configToSave)
    });
    
    if (!res.ok) throw new Error('Falha ao salvar configurações no servidor');
    
    state.appConfig = await res.json();
    addConsoleLog('Configurações salvas e aplicadas com sucesso!', 'sucesso');
    
    if (schedulingModeSelect) {
      ui.toggleSchedulingModeUI(state.appConfig.scheduling_mode || 'recorrente');
    }
    
    ui.renderThemes();
    await fetchStatus();
  } catch (error) {
    addConsoleLog(`Erro ao salvar configurações: ${error.message}`, 'erro');
  } finally {
    if (button && isFormSubmit) {
      button.disabled = false;
      button.textContent = 'Salvar Configurações';
    }
  }
}

export async function testLLMConnection(provider, model, baseUrl, apiKey, id = null) {
  try {
    const res = await request('/api/llm-servers/test-connection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider: provider,
        model: model,
        base_url: baseUrl || null,
        api_key: apiKey || null,
        id: id
      })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao testar LLM');
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao testar conexão do LLM: ${error.message}`, 'erro');
    throw error;
  }
}

export async function fetchLLMServers() {
  try {
    const res = await request('/api/llm-servers');
    if (!res.ok) throw new Error('Falha ao buscar servidores LLM');
    state.llmServers = await res.json();
    ui.renderLLMServers();
  } catch (error) {
    addConsoleLog(`Erro ao carregar servidores LLM: ${error.message}`, 'erro');
  }
}

export async function createLLMServer(serverData) {
  try {
    const res = await request('/api/llm-servers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(serverData)
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao criar servidor LLM');
    addConsoleLog(`Servidor LLM "${serverData.name}" criado com sucesso!`, 'sucesso');
    await fetchLLMServers();
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao criar servidor LLM: ${error.message}`, 'erro');
    throw error;
  }
}

export async function updateLLMServer(serverId, serverData) {
  try {
    const res = await request(`/api/llm-servers/${serverId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(serverData)
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao atualizar servidor LLM');
    addConsoleLog(`Servidor LLM "${serverData.name}" atualizado com sucesso!`, 'sucesso');
    await fetchLLMServers();
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao atualizar servidor LLM: ${error.message}`, 'erro');
    throw error;
  }
}

export async function deleteLLMServer(serverId) {
  try {
    const res = await request(`/api/llm-servers/${serverId}`, {
      method: 'DELETE'
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao excluir servidor LLM');
    addConsoleLog('Servidor LLM excluído com sucesso!', 'sucesso');
    await fetchLLMServers();
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao excluir servidor LLM: ${error.message}`, 'erro');
    throw error;
  }
}

export async function activateLLMServer(serverId) {
  try {
    const res = await request(`/api/llm-servers/${serverId}/activate`, {
      method: 'POST'
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao ativar servidor LLM');
    addConsoleLog(`Servidor LLM "${result.name}" ativado com sucesso!`, 'sucesso');
    await fetchLLMServers();
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao ativar servidor LLM: ${error.message}`, 'erro');
    throw error;
  }
}

function syncVisualSelector(selectId, groupClass) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const cards = document.querySelectorAll(`.${groupClass} .channel-option-card`);
  cards.forEach(card => {
    if (card.getAttribute('data-value') === select.value) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });
}

