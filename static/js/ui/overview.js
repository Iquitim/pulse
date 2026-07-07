import { state } from '../state.js';

export function updateMetrics() {
  const totalThemes = state.appConfig.themes.length;
  const metricThemesCount = document.getElementById('metric-themes-count');
  if (metricThemesCount) metricThemesCount.textContent = totalThemes;
  
  const themesCountBadge = document.getElementById('themes-count-badge');
  if (themesCountBadge) themesCountBadge.textContent = `${totalThemes} ${totalThemes === 1 ? 'tema' : 'temas'}`;
  
  const statusText = state.appConfig.is_active ? 'Ativo' : 'Inativo';
  const statusEl = document.getElementById('metric-status');
  if (statusEl) {
    statusEl.textContent = statusText;
    statusEl.className = `metric-value ${state.appConfig.is_active ? 'color-accent' : 'text-muted'}`;
  }
  
  const successPosts = state.postHistory.filter(p => p.status === 'success');
  const totalPosts = state.postHistory.filter(p => p.status === 'success' || p.status === 'failed');
  
  const successRateEl = document.getElementById('metric-success-rate');
  if (successRateEl) {
    if (totalPosts.length === 0) {
      successRateEl.textContent = '100%';
    } else {
      const percentage = Math.round((successPosts.length / totalPosts.length) * 100);
      successRateEl.textContent = `${percentage}%`;
    }
  }
  
  const now = new Date();
  const oneDayAgo = now.getTime() - 24 * 3600 * 1000;
  const postsToday = successPosts.filter(p => {
    const pDate = new Date(p.timestamp);
    return pDate.getTime() > oneDayAgo;
  }).length;
  
  const metricPostedToday = document.getElementById('metric-posted-today');
  if (metricPostedToday) metricPostedToday.textContent = postsToday;
  
  let totalLikes = 0;
  let totalReposts = 0;
  let totalReplies = 0;
  
  successPosts.forEach(p => {
    totalLikes += (p.likes || 0);
    totalReposts += (p.reposts || 0);
    totalReplies += (p.replies || 0);
  });
  
  const totalInteractions = totalLikes + totalReposts + totalReplies;
  
  const totalInteractionsEl = document.getElementById('metric-total-interactions');
  const interactionsDescEl = document.getElementById('metric-interactions-desc');
  
  if (totalInteractionsEl) totalInteractionsEl.textContent = totalInteractions;
  if (interactionsDescEl) {
    interactionsDescEl.textContent = `${totalLikes} ${totalLikes === 1 ? 'curtida' : 'curtidas'} · ${totalReposts} repost${totalReposts === 1 ? '' : 's'} · ${totalReplies} ${totalReplies === 1 ? 'resposta' : 'respostas'}`;
  }
}

export function updateQueueList() {
  const queueList = document.getElementById('queue-list');
  if (!queueList) return;
  queueList.innerHTML = '';
  
  const isActive = document.getElementById('is_active')?.checked;
  const isApprovalRequired = document.getElementById('requires_approval')?.checked;
  const intervalHoursInput = document.getElementById('interval_hours');
  const intervalHours = intervalHoursInput ? parseInt(intervalHoursInput.value, 10) : 6;
  
  if (!isActive) {
    queueList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.725rem; text-align: center; padding: 0.8rem 0;">Agendador inativo. Fila vazia.</div>';
    return;
  }
  
  let nextRun = state.nextPostTime ? new Date(state.nextPostTime) : new Date(new Date().getTime() + intervalHours * 3600000);
  
  for (let i = 0; i < 3; i++) {
    const itemTime = new Date(nextRun.getTime() + i * intervalHours * 3600000);
    const timeStr = itemTime.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    
    let predictedTheme = 'Aleatório';
    if (state.appConfig.themes.length > 0) {
      predictedTheme = state.appConfig.themes[i % state.appConfig.themes.length];
    }
    
    const queueItem = document.createElement('div');
    const itemType = isApprovalRequired ? 'draft' : (i === 0 ? 'active' : 'pending');
    queueItem.className = `queue-item ${itemType === 'active' ? 'active' : (itemType === 'draft' ? 'draft' : '')}`;
    queueItem.innerHTML = `
      <div>
        <span class="queue-time">${timeStr}</span>
        <span style="color: var(--text-muted); margin: 0 0.25rem;">·</span>
        <span class="queue-theme">${predictedTheme}</span>
      </div>
      <span class="queue-status">${isApprovalRequired ? 'Gerará Rascunho' : (i === 0 ? 'Aguardando' : 'Agendado')}</span>
    `;
    queueList.appendChild(queueItem);
  }
}

export function renderAuditLogs() {
  const tbody = document.getElementById('user-activities-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
 
  if (!state.auditLogs || state.auditLogs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-muted); padding: 12px;">Nenhuma atividade recente encontrada.</td></tr>';
    return;
  }
 
  state.auditLogs.forEach(log => {
    const tr = document.createElement('tr');
    
    let formattedDate = log.timestamp;
    try {
      const dt = new Date(log.timestamp);
      formattedDate = dt.toLocaleString('pt-BR');
    } catch (e) {}
 
    tr.innerHTML = `
      <td style="color: var(--text-muted); font-size: 0.75rem; white-space: nowrap; padding: 6px 12px;">${formattedDate}</td>
      <td style="font-weight: 600; color: var(--color-accent); font-size: 0.75rem; padding: 6px 12px;">${log.action}</td>
      <td style="color: var(--text-secondary); font-size: 0.75rem; padding: 6px 12px;">${log.details || ''}</td>
    `;
    tbody.appendChild(tr);
  });
}
