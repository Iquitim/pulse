import { state } from '../state.js';
import { updateMetrics, updateQueueList } from './overview.js';

export function renderHistory() {
  const historyLoading = document.getElementById('history-loading');
  const historyEmpty = document.getElementById('history-empty');
  const historyTableContainer = document.getElementById('history-table-container');
  const historyTbody = document.getElementById('history-tbody');
  
  if (historyLoading) historyLoading.classList.add('hidden');
  
  if (state.postHistory.length === 0) {
    if (historyEmpty) historyEmpty.classList.remove('hidden');
    if (historyTableContainer) historyTableContainer.classList.add('hidden');
    updateMetrics();
    updateQueueList();
    return;
  }
  
  if (historyEmpty) historyEmpty.classList.add('hidden');
  if (historyTableContainer) historyTableContainer.classList.remove('hidden');
  if (!historyTbody) return;
  
  historyTbody.innerHTML = '';
  state.postHistory.forEach((post, index) => {
    const tr = document.createElement('tr');
    
    const date = new Date(post.timestamp);
    const dateStr = date.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    
    let statusText = 'Publicado';
    let statusClass = 'success';
    if (post.status === 'failed') {
      statusText = 'Erro';
      statusClass = 'failed';
    } else if (post.status === 'draft') {
      statusText = 'Rascunho';
      statusClass = 'draft';
    }
    
    let actionsHtml = `
      <button class="btn-text-action btn-view-post" data-index="${index}" style="margin-right: 0.35rem;">Ver</button>
    `;
    if (post.status === 'draft') {
      actionsHtml += `
        <button class="btn-text-action btn-approve-post" data-index="${index}" style="color: var(--color-success); font-weight:600; margin-right: 0.35rem;">Postar</button>
        <button class="btn-text-action btn-edit-post" data-index="${index}" style="color: var(--color-accent);">Editar</button>
      `;
    } else if (post.status === 'success') {
      actionsHtml += `
        <button class="btn-text-action btn-reuse-post" data-index="${index}" style="color: var(--color-ai);">Reutilizar</button>
      `;
    }
    
    let metricsHtml = '<span style="color: var(--text-muted);">--</span>';
    if (post.status === 'success') {
      metricsHtml = `
        <div class="metrics-badges" style="display: flex; gap: 0.4rem; font-size: 0.725rem;">
          <span title="Curtidas" style="color: #F43F5E; display: inline-flex; align-items: center; gap: 0.15rem;">❤️ ${post.likes || 0}</span>
          <span title="Reposts" style="color: #10B981; display: inline-flex; align-items: center; gap: 0.15rem;">🔁 ${post.reposts || 0}</span>
          <span title="Respostas" style="color: #3B82F6; display: inline-flex; align-items: center; gap: 0.15rem;">💬 ${post.replies || 0}</span>
        </div>
      `;
    }

    let scoreBadge = '';
    if (post.quality_score !== undefined && post.quality_score !== null) {
      let scoreColor = 'var(--text-muted)';
      if (post.quality_score >= 80) scoreColor = 'var(--color-success)';
      else if (post.quality_score >= 50) scoreColor = 'var(--color-accent)';
      else scoreColor = 'var(--color-danger)';
      scoreBadge = `<span style="font-size: 0.7rem; font-weight: 700; color: ${scoreColor}; margin-left: 0.35rem; border: 1px solid currentColor; border-radius: 4px; padding: 0.05rem 0.2rem;" title="Score Geral de Qualidade IA">${post.quality_score}</span>`;
    }

    tr.innerHTML = `
      <td class="td-date">${dateStr}</td>
      <td><span class="theme-badge">${post.theme || 'N/A'}</span></td>
      <td><div style="display: flex; align-items: center;"><span class="status-pill ${statusClass}">${statusText}</span>${scoreBadge}</div></td>
      <td>${metricsHtml}</td>
      <td><div class="excerpt-text" title="${post.content || ''}">${post.content || post.error || 'N/A'}</div></td>
      <td class="actions-cell">${actionsHtml}</td>
    `;
    
    historyTbody.appendChild(tr);
  });
  
  updateMetrics();
  updateQueueList();
}

export function renderIdeas() {
  const loading = document.getElementById('ideas-loading');
  const empty = document.getElementById('ideas-empty');
  const list = document.getElementById('ideas-list');
  
  if (loading) loading.classList.add('hidden');
  
  if (!state.ideas || state.ideas.length === 0) {
    if (empty) empty.classList.remove('hidden');
    if (list) list.innerHTML = '';
    return;
  }
  
  if (empty) empty.classList.add('hidden');
  if (!list) return;
  
  list.innerHTML = '';
  state.ideas.forEach(idea => {
    const card = document.createElement('div');
    card.className = 'idea-card';
    card.style = `
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 0.85rem;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      transition: all var(--transition-fast);
    `;
    
    card.onmouseover = () => { card.style.borderColor = 'var(--color-accent)'; };
    card.onmouseout = () => { card.style.borderColor = 'var(--border-color)'; };
    
    const date = new Date(idea.created_at);
    const dateStr = date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    
    const isConverted = idea.status === 'converted';
    const statusLabel = isConverted ? 'Convertido' : 'Pendente';
    const statusBg = isConverted ? 'var(--color-success-bg)' : 'var(--color-warning-bg)';
    const statusColor = isConverted ? 'var(--color-success)' : 'var(--color-warning)';
    
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: start; gap: 0.5rem;">
        <h4 style="margin: 0; font-size: 0.85rem; font-weight: 600; color: var(--text-primary);">${idea.title}</h4>
        <div style="display: flex; gap: 0.35rem; align-items: center;">
          <span style="font-size: 0.65rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 4px; background: var(--bg-main); color: var(--text-secondary); text-transform: capitalize; border: 1px solid var(--border-color);">
            ${idea.channel || 'bluesky'}
          </span>
          <span style="font-size: 0.65rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 10px; background: ${statusBg}; color: ${statusColor}; white-space: nowrap;">
            ${statusLabel}
          </span>
        </div>
      </div>
      <p style="margin: 0; font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4; white-space: pre-wrap;">${idea.description}</p>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem; font-size: 0.7rem; color: var(--text-muted);">
        <span>${dateStr}</span>
        <div style="display: flex; gap: 0.5rem;">
          <button type="button" class="btn-text-action btn-convert-idea" data-id="${idea.id}" data-desc="${encodeURIComponent(idea.description)}" data-channel="${idea.channel || 'bluesky'}" style="color: var(--color-accent); font-weight: 600;">
            ${isConverted ? 'Re-criar Post' : 'Criar Post'}
          </button>
          <button type="button" class="btn-text-action btn-delete-idea" data-id="${idea.id}" style="color: var(--color-danger);">
            Excluir
          </button>
        </div>
      </div>
    `;
    
    list.appendChild(card);
  });
}

export function renderMetricsInsights(insights) {
  const textEl = document.getElementById("insights-text");
  const containerEl = document.getElementById("insights-suggestions-container");
  const listEl = document.getElementById("insights-suggestions-list");
  
  if (textEl) {
    textEl.textContent = insights.insight_text || "Nenhum insight disponível.";
  }
  
  const suggestions = insights.sugestoes || [];
  if (suggestions.length === 0) {
    if (containerEl) containerEl.classList.add("hidden");
    if (listEl) listEl.innerHTML = "";
    return;
  }
  
  if (containerEl) containerEl.classList.remove("hidden");
  if (!listEl) return;
  
  listEl.innerHTML = "";
  suggestions.forEach((sug, idx) => {
    const card = document.createElement("div");
    card.className = "insight-suggestion-card";
    card.style = `
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 0.75rem;
      cursor: pointer;
      font-size: 0.75rem;
      line-height: 1.35;
      color: var(--text-secondary);
      transition: all var(--transition-fast);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.5rem;
    `;
    
    card.onmouseover = () => { 
      card.style.borderColor = 'var(--color-accent)'; 
      card.style.backgroundColor = 'var(--bg-surface-elevated)';
    };
    card.onmouseout = () => { 
      card.style.borderColor = 'var(--border-color)'; 
      card.style.backgroundColor = 'var(--bg-surface)';
    };
    
    card.innerHTML = `
      <div style="font-style: italic; color: var(--text-primary);">"${sug}"</div>
      <div style="text-align: right; font-weight: 600; color: var(--color-accent); font-size: 0.7rem; display: flex; align-items: center; justify-content: flex-end; gap: 0.25rem; margin-top: 0.25rem;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="svg-inline" style="width: 11px; height: 11px;"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
        <span>Usar Sugestão</span>
      </div>
    `;
    
    card.addEventListener("click", () => {
      // Convert suggestion: navigate to Editor, set text, trigger generator
      const draftTextarea = document.getElementById("draft-text");
      if (draftTextarea) {
        const tabBtn = document.querySelector('[data-tab="editor"]');
        if (tabBtn) tabBtn.click();
        
        import('../api.js').then(api => {
          api.generateDraft(sug);
        });
      }
    });
    
    listEl.appendChild(card);
  });
}
