import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request } from './client.js';
import * as ui from '../ui.js';
import { fetchCalendarItems } from './calendar.js';
import { fetchStatus } from './social.js';

export async function fetchHistory() {
  try {
    const res = await request('/api/history');
    if (!res.ok) throw new Error('Falha ao buscar histórico');
    
    state.postHistory = await res.json();
    ui.renderHistory();
  } catch (error) {
    addConsoleLog(`Erro ao carregar histórico: ${error.message}`, 'erro');
  }
}

export async function triggerPostNow() {
  const btnPostNow = document.getElementById('btn-post-now');
  if (!btnPostNow || btnPostNow.disabled) return;
  
  btnPostNow.disabled = true;
  btnPostNow.querySelector('span').textContent = 'Gerando & Publicando...';
  
  const draftThemeSelect = document.getElementById('draft-theme-select');
  const selectedTheme = draftThemeSelect ? draftThemeSelect.value : 'random';
  const draftChannelSelect = document.getElementById('draft-channel');
  const channel = draftChannelSelect ? draftChannelSelect.value : 'bluesky';
  
  const requestBody = {
    channel: channel
  };
  if (selectedTheme !== 'random') {
    requestBody.theme = selectedTheme;
  }
  if (state.activeCalendarItemId) {
    requestBody.calendar_item_id = state.activeCalendarItemId;
  }
  
  addConsoleLog(`Gerando conteúdo inteligente via LangChain (Tema: ${selectedTheme === 'random' ? 'Aleatório' : selectedTheme})...`, 'ai');
  
  try {
    const res = await request('/api/post-now', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    const result = await res.json();
    
    if (!res.ok) {
      throw new Error(result.detail || result.error || 'Erro desconhecido na postagem');
    }
    
    addConsoleLog(`Sucesso! Post publicado. Tema: [${result.theme}]`, 'sucesso');
    addConsoleLog(`Conteúdo: "${result.content}"`, 'info');
    
    // Reset active calendar item
    state.activeCalendarItemId = null;
    ui.updateCalendarActiveIndicator();
    
    await fetchHistory();
    await fetchStatus();
    await fetchCalendarItems();
  } catch (error) {
    addConsoleLog(`Falha na postagem manual imediata: ${error.message}`, 'erro');
  } finally {
    btnPostNow.disabled = false;
    btnPostNow.querySelector('span').textContent = 'Gerar & Postar Agora (Sem Revisão)';
  }
}

export async function runAIHelper(instruction) {
  const draftTextarea = document.getElementById('draft-text');
  if (!draftTextarea) return;
  const currentText = draftTextarea.value.trim();
  if (!currentText && (instruction === 'improve' || instruction === 'shorten')) {
    addConsoleLog('Digite um rascunho no editor primeiro para solicitar melhorias.', 'erro');
    return;
  }
  
  const helperButtons = document.querySelectorAll('.btn-helper');
  helperButtons.forEach(btn => btn.disabled = true);
  addConsoleLog(`Processando auxílio da IA (${instruction})...`, 'ai');
  
  const draftThemeSelect = document.getElementById('draft-theme-select');
  
  let requestBody = {};
  if (instruction === 'improve') {
    requestBody = {
      theme: state.currentDraftTheme || 'Geral',
      system_prompt: `Melhore a escrita do seguinte post, tornando-o mais cativante e mantendo o limite de 280 caracteres. Retorne apenas o texto final melhorado:\n\n"${currentText}"`
    };
  } else if (instruction === 'shorten') {
    requestBody = {
      theme: state.currentDraftTheme || 'Geral',
      system_prompt: `Encurte o seguinte texto de forma direta e objetiva, respeitando o limite de 280 caracteres. Retorne apenas o texto final:\n\n"${currentText}"`
    };
  } else if (instruction === 'technical') {
    const selectedTheme = draftThemeSelect ? draftThemeSelect.value : 'random';
    requestBody = {
      system_prompt: "Você é um especialista altamente técnico e profissional. Escreva um post curto (máximo de 280 caracteres) e formal sobre o tema fornecido. Não use hashtags."
    };
    if (selectedTheme !== 'random') requestBody.theme = selectedTheme;
  } else if (instruction === 'funny') {
    const selectedTheme = draftThemeSelect ? draftThemeSelect.value : 'random';
    requestBody = {
      system_prompt: "Você é um criador de conteúdo descontraído, divertido e leve. Escreva um post curto (máximo de 280 caracteres), engraçado e informal sobre o tema fornecido. Não use hashtags."
    };
    if (selectedTheme !== 'random') requestBody.theme = selectedTheme;
  }
  
  try {
    const res = await request('/api/generate-draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro no processamento da IA');
    
    draftTextarea.value = result.content;
    if (result.theme && instruction !== 'improve' && instruction !== 'shorten') {
      state.currentDraftTheme = result.theme;
    }
    
    ui.updateCharCounter(result.content.length);
    const btnPublishDraft = document.getElementById('btn-publish-draft');
    if (btnPublishDraft) btnPublishDraft.disabled = false;
    
    const previewContent = document.getElementById('preview-content');
    if (previewContent) previewContent.textContent = result.content;
    
    addConsoleLog('Rascunho processado pela IA com sucesso!', 'sucesso');
  } catch (error) {
    addConsoleLog(`Falha no assistente de IA: ${error.message}`, 'erro');
  } finally {
    helperButtons.forEach(btn => btn.disabled = false);
  }
}

export async function generateDraft(ideaText = null) {
  if (ideaText && typeof ideaText !== 'string') {
    ideaText = null;
  }

  if (ideaText) {
    state.currentIdeaText = ideaText;
    const indicator = document.getElementById('idea-active-indicator');
    if (indicator) indicator.classList.remove('hidden');

    // Add temporary option to theme select
    const themeSelect = document.getElementById('draft-theme-select');
    if (themeSelect) {
      let ideaOption = themeSelect.querySelector('option[value="idea_convert"]');
      if (!ideaOption) {
        ideaOption = document.createElement('option');
        ideaOption.value = 'idea_convert';
        ideaOption.textContent = '💡 Ideia do Usuário';
        themeSelect.appendChild(ideaOption);
      }
      themeSelect.value = 'idea_convert';
    }
  } else if (state.currentIdeaText) {
    ideaText = state.currentIdeaText;
  }

  const btnGenerateDraft = document.getElementById('btn-generate-draft');
  if (!btnGenerateDraft) return;
  btnGenerateDraft.disabled = true;
  btnGenerateDraft.querySelector('span').textContent = 'Gerando...';
  
  const draftThemeSelect = document.getElementById('draft-theme-select');
  const selectedTheme = draftThemeSelect ? draftThemeSelect.value : 'random';
  
  let themeToSend = selectedTheme;
  if (selectedTheme === 'random') {
    if (state.appConfig.themes && state.appConfig.themes.length > 0) {
      themeToSend = state.appConfig.themes[Math.floor(Math.random() * state.appConfig.themes.length)];
    }
  }
  
  const systemPromptInput = document.getElementById('system_prompt');
  const requestBody = {
    system_prompt: systemPromptInput?.value || ''
  };
  
  if (themeToSend && themeToSend !== 'random') {
    requestBody.theme = themeToSend === 'idea_convert' ? 'Ideia do Usuário' : themeToSend;
  }
  if (ideaText) {
    requestBody.idea_text = ideaText;
  }
  
  let activeAiName = 'IA';
  if (state.connectionStatus && state.connectionStatus.gemini === 'online' && state.connectionStatus.gemini_msg) {
    const match = state.connectionStatus.gemini_msg.match(/\(([^)]+)\)/);
    if (match && match[1]) {
      activeAiName = match[1];
    }
  }
  addConsoleLog(`Solicitando rascunho de post ao servidor de IA (${activeAiName}) (Tema: ${selectedTheme === 'random' ? `Aleatório → ${themeToSend}` : selectedTheme})...`, 'ai');
  
  try {
    const res = await request('/api/generate-draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    
    const result = await res.json();
    if (!res.ok) {
      let errMsg = 'Erro ao gerar rascunho';
      if (result && result.detail) {
        if (typeof result.detail === 'string') {
          errMsg = result.detail;
        } else if (Array.isArray(result.detail)) {
          errMsg = result.detail.map(d => `${d.loc ? d.loc.join('.') : 'erro'}: ${d.msg || 'inválido'}`).join(', ');
        } else {
          errMsg = JSON.stringify(result.detail);
        }
      }
      throw new Error(errMsg);
    }
    
    const draftTextarea = document.getElementById('draft-text');
    if (draftTextarea) draftTextarea.value = result.content;
    state.currentDraftTheme = result.theme;
    
    ui.updateCharCounter(result.content.length);
    const btnPublishDraft = document.getElementById('btn-publish-draft');
    if (btnPublishDraft) btnPublishDraft.disabled = false;
    
    const previewContent = document.getElementById('preview-content');
    if (previewContent) previewContent.textContent = result.content;
    
    addConsoleLog(`Rascunho gerado com sucesso! Tema: [${state.currentDraftTheme}]`, 'sucesso');
  } catch (error) {
    addConsoleLog(`Erro ao gerar rascunho: ${error.message}`, 'erro');
    ui.showToast(`Erro ao gerar rascunho: ${error.message}`, 'erro');
  } finally {
    btnGenerateDraft.disabled = false;
    btnGenerateDraft.querySelector('span').textContent = 'Gerar Rascunho';
  }
}

export async function publishDraft() {
  const btnPublishDraft = document.getElementById('btn-publish-draft');
  if (!btnPublishDraft) return;
  btnPublishDraft.disabled = true;
  btnPublishDraft.querySelector('span').textContent = 'Publicando...';
  addConsoleLog('Enviando rascunho para a fila de publicação...', 'system');
  
  try {
    const draftTextarea = document.getElementById('draft-text');
    const content = draftTextarea ? draftTextarea.value : '';
    
    const draftChannelSelect = document.getElementById('draft-channel');
    const channel = draftChannelSelect ? draftChannelSelect.value : 'bluesky';
    
    const requestBody = {
      content: content,
      theme: state.currentDraftTheme,
      channel: channel
    };
    if (state.activeCalendarItemId) {
      requestBody.calendar_item_id = state.activeCalendarItemId;
    }
    if (state.activeDraftId) {
      requestBody.draft_id = state.activeDraftId;
    }

    const res = await request('/api/post-draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao publicar rascunho');
    
    addConsoleLog('Post publicado com sucesso!', 'sucesso');
    
    if (draftTextarea) draftTextarea.value = '';
    ui.updateCharCounter(0);
    btnPublishDraft.disabled = true;
    const previewContent = document.getElementById('preview-content');
    if (previewContent) previewContent.textContent = 'Digite ou gere algo no editor acima...';
    
    // Reset active calendar item and draft
    state.activeCalendarItemId = null;
    ui.updateCalendarActiveIndicator();
    state.activeDraftId = null;
    ui.updateDraftActiveIndicator();
    
    await fetchHistory();
    await fetchStatus();
    await fetchCalendarItems();
  } catch (error) {
    addConsoleLog(`Erro ao publicar post: ${error.message}`, 'erro');
    btnPublishDraft.disabled = false;
  } finally {
    btnPublishDraft.querySelector('span').textContent = 'Publicar Rascunho';
  }
}

export async function approvePost(post, target) {
  target.disabled = true;
  target.textContent = 'Postando...';
  addConsoleLog(`Aprovando rascunho de post agendado. Tema: [${post.theme}]`, 'system');
  
  try {
    const res = await request('/api/post-draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: post.content,
        theme: post.theme || 'Geral',
        draft_id: post.id
      })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao publicar');
    
    addConsoleLog('Post aprovado e publicado com sucesso!', 'sucesso');
    
    post.status = 'success';
    await fetchHistory();
    await fetchStatus();
  } catch (error) {
    addConsoleLog(`Falha ao aprovar e publicar: ${error.message}`, 'erro');
    target.disabled = false;
    target.textContent = 'Postar';
  }
}

export async function triggerRefreshMetrics() {
  const btnRefreshMetrics = document.getElementById('btn-refresh-metrics');
  if (!btnRefreshMetrics || btnRefreshMetrics.disabled) return;
  
  btnRefreshMetrics.disabled = true;
  const originalHtml = btnRefreshMetrics.innerHTML;
  btnRefreshMetrics.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="svg-inline" style="animation: spin 1s linear infinite; width: 13px; height: 13px;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
    <span>Atualizando...</span>
  `;
  
  addConsoleLog('Consultando APIs sociais para sincronizar métricas de engajamento...', 'system');
  
  try {
    const res = await request('/api/refresh-metrics', { method: 'POST' });
    const result = await res.json();
    
    if (!res.ok) {
      throw new Error(result.detail || 'Erro ao consultar APIs externas');
    }
    
    await fetchHistory();
    addConsoleLog(result.message || 'Métricas atualizadas com sucesso!', 'sucesso');
  } catch (error) {
    addConsoleLog(`Falha ao atualizar métricas: ${error.message}`, 'erro');
  } finally {
    btnRefreshMetrics.disabled = false;
    btnRefreshMetrics.innerHTML = originalHtml;
  }
}
