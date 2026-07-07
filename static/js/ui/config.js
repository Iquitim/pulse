import { state } from '../state.js';
import { renderCalendar } from './calendar.js';

export function renderConnectedAccounts() {
  const container = document.getElementById('connected-accounts-list');
  if (!container) return;
  container.innerHTML = '';
  
  if (state.connectedAccounts.length === 0) {
    container.innerHTML = '<div style="color: var(--text-muted); font-size: 0.75rem; text-align: center; padding: 1rem;">Nenhuma conta vinculada ainda.</div>';
    return;
  }
  
  state.connectedAccounts.forEach(acc => {
    const div = document.createElement('div');
    div.className = 'queue-item';
    div.style.display = 'flex';
    div.style.justifyContent = 'space-between';
    div.style.alignItems = 'center';
    
    const platformName = acc.platform.charAt(0).toUpperCase() + acc.platform.slice(1);
    
    div.innerHTML = `
      <div>
        <strong style="color: var(--color-ai); font-size: 0.8rem;">${platformName}</strong>
        <span style="color: var(--text-muted); margin: 0 0.25rem;">·</span>
        <span style="font-size: 0.8rem; font-weight: 500;">${acc.account_handle}</span>
      </div>
      <button class="btn-text-action btn-disconnect-account" data-id="${acc.id}" style="color: var(--color-failed); font-weight: 600;">Desconectar</button>
    `;
    container.appendChild(div);
  });
}

export function renderInviteCodes() {
  const tbody = document.getElementById('invite-codes-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  
  if (state.inviteCodes.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">Nenhum convite gerado.</td></tr>';
    return;
  }
  
  state.inviteCodes.forEach(code => {
    const tr = document.createElement('tr');
    const actionsHtml = code.revoked ? '<span style="color: var(--text-muted);">--</span>' : `<button class="btn-text-action btn-revoke-invite" data-id="${code.id}" style="color: var(--color-failed); font-weight: 600;">Revogar</button>`;
    
    tr.innerHTML = `
      <td style="font-family: monospace; font-weight: 600; color: var(--color-ai);">${code.code}</td>
      <td style="text-transform: uppercase;">${code.plan_tier}</td>
      <td>${code.uses_count}/${code.max_uses}</td>
      <td>${actionsHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

export function renderUsersList() {
  const tbody = document.getElementById('users-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  
  if (state.usersList.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">Nenhum usuário cadastrado.</td></tr>';
    return;
  }
  
  state.usersList.forEach(user => {
    const tr = document.createElement('tr');
    const isSelf = (state.user && state.user.email === user.email);
    
    const statusText = user.is_active ? 'Ativo' : 'Inativo';
    const statusColor = user.is_active ? 'var(--color-success)' : 'var(--color-danger, #EF4444)';
    
    let actionsHtml = '';
    let planCellHtml = '';
    
    let planLabel = 'Pessoal';
    if (user.plan_tier === 'pro') planLabel = 'Entusiasta';
    else if (user.plan_tier === 'desk') planLabel = 'Coletivo';

    if (isSelf) {
      planCellHtml = `<span style="text-transform: uppercase; font-weight: 600; color: var(--color-accent);">${planLabel}</span>`;
      actionsHtml = '<span style="color: var(--text-muted); font-size: 0.8rem;">Você (Admin)</span>';
    } else {
      planCellHtml = `
        <select class="change-user-plan clean-select compact" data-id="${user.id}" style="font-size: 0.75rem; padding: 2px 4px; border-radius: 4px; border: 1px solid var(--border-color); background-color: var(--bg-surface-elevated); color: var(--text-primary); cursor: pointer;">
          <option value="free" ${user.plan_tier === 'free' ? 'selected' : ''}>Pessoal</option>
          <option value="pro" ${user.plan_tier === 'pro' ? 'selected' : ''}>Entusiasta</option>
          <option value="desk" ${user.plan_tier === 'desk' ? 'selected' : ''}>Coletivo</option>
        </select>
      `;
      
      const btnText = user.is_active ? 'Bloquear' : 'Ativar';
      const btnColor = user.is_active ? 'var(--color-danger, #EF4444)' : 'var(--color-success)';
      actionsHtml = `
        <div style="display: flex; gap: 10px; align-items: center;">
          <button class="btn-text-action btn-toggle-user" data-id="${user.id}" data-active="${!user.is_active}" style="color: ${btnColor}; font-weight: 600;">${btnText}</button>
          <button class="btn-text-action btn-view-user-logs" data-id="${user.id}" data-email="${user.email}" style="color: var(--color-accent); font-weight: 600;">Logs 📋</button>
          <button class="btn-text-action btn-delete-user" data-id="${user.id}" style="color: var(--color-danger, #EF4444); font-weight: 600;">Excluir 🗑️</button>
        </div>
      `;
    }
    
    tr.innerHTML = `
      <td style="font-weight: 500; padding: 8px 12px;">${user.email}</td>
      <td style="padding: 8px 12px;">${planCellHtml}</td>
      <td style="color: ${statusColor}; font-weight: 600; padding: 8px 12px;">${statusText}</td>
      <td style="padding: 8px 12px;">${actionsHtml}</td>
    `;
    tbody.appendChild(tr);
  });
}

export function renderLLMServers() {
  const container = document.getElementById('llm-servers-list');
  if (!container) return;
  container.innerHTML = '';
  
  if (!state.llmServers || state.llmServers.length === 0) {
    container.innerHTML = `
      <div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; padding: 2rem; border: 1px dashed var(--border-color); border-radius: var(--radius-md);">
        Nenhum servidor configurado ainda. Use o formulário ao lado para adicionar o seu primeiro servidor de IA!
      </div>
    `;
    return;
  }
  
  state.llmServers.forEach(server => {
    const isActive = server.is_active;
    const card = document.createElement('div');
    card.className = `queue-item`;
    card.style.border = isActive ? '2px solid var(--color-success)' : '1px solid var(--border-color)';
    card.style.padding = '1rem';
    card.style.borderRadius = 'var(--radius-md)';
    card.style.display = 'flex';
    card.style.justifyContent = 'space-between';
    card.style.alignItems = 'center';
    card.style.background = isActive ? 'rgba(16, 185, 129, 0.04)' : 'var(--bg-surface-elevated)';
    card.style.transition = 'all 0.2s var(--ease-out)';
    
    // Add hover effects
    card.addEventListener('mouseenter', () => {
      card.style.transform = 'translateY(-2px)';
      card.style.boxShadow = 'var(--shadow-md)';
      if (!isActive) {
        card.style.borderColor = 'var(--border-focus)';
      }
    });
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'none';
      card.style.boxShadow = 'none';
      if (!isActive) {
        card.style.borderColor = 'var(--border-color)';
      }
    });
    
    const providerName = server.provider === 'openai_compatible' ? 'OpenAI / Compatível' : (server.provider === 'ollama' ? 'Ollama' : 'Gemini');
    const badgeHtml = isActive 
      ? `<span style="background-color: var(--color-success); color: white; font-size: 0.65rem; font-weight: 600; padding: 0.15rem 0.45rem; border-radius: 20px; display: inline-flex; align-items: center; gap: 0.25rem;">● Ativo</span>` 
      : '';
      
    card.innerHTML = `
      <div style="flex-grow: 1; padding-right: 1rem; min-width: 0;">
        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
          <strong style="font-size: 0.9rem; color: var(--text-primary);">${server.name}</strong>
          ${badgeHtml}
        </div>
        <div style="font-size: 0.725rem; color: var(--text-muted); margin-top: 0.35rem; line-height: 1.4;">
          <span style="color: var(--color-ai); font-weight: 600;">${providerName}</span> 
          · Modelo: <code style="background: var(--bg-surface); padding: 0.05rem 0.25rem; border-radius: 3px;">${server.model}</code>
          ${server.base_url ? `· Endpoint: <code style="background: var(--bg-surface); padding: 0.05rem 0.25rem; border-radius: 3px; word-break: break-all;">${server.base_url}</code>` : ''}
        </div>
      </div>
      <div style="display: flex; gap: 0.75rem; align-items: center; flex-shrink: 0;">
        ${server.provider === 'ollama' ? `<button class="btn-text-action btn-manage-models" data-id="${server.id}" data-url="${server.base_url}" style="color: var(--color-ai); font-weight: 600; font-size: 0.75rem;">Modelos 📦</button>` : ''}
        ${!isActive ? `<button class="btn-text-action btn-activate-server" data-id="${server.id}" style="color: var(--color-success); font-weight: 600; font-size: 0.75rem;">Ativar</button>` : ''}
        <button class="btn-text-action btn-edit-server" data-id="${server.id}" style="color: var(--color-accent); font-weight: 600; font-size: 0.75rem;">Editar</button>
        <button class="btn-text-action btn-delete-server" data-id="${server.id}" style="color: var(--color-failed); font-weight: 600; font-size: 0.75rem;">Excluir</button>
      </div>
    `;
    
    container.appendChild(card);
  });
}

export function toggleSchedulingModeUI(mode) {
  const recurrentView = document.getElementById('calendar-recurrent-view');
  const customView = document.getElementById('calendar-custom-view');
  const btnOpenCalendarForm = document.getElementById('btn-open-calendar-form');
  
  if (mode === 'personalizado') {
    if (recurrentView) recurrentView.classList.add('hidden');
    if (customView) customView.classList.remove('hidden');
    if (btnOpenCalendarForm) btnOpenCalendarForm.classList.remove('hidden');
    renderCalendar();
  } else {
    if (recurrentView) recurrentView.classList.remove('hidden');
    if (customView) customView.classList.add('hidden');
    if (btnOpenCalendarForm) btnOpenCalendarForm.classList.add('hidden');
  }
}

export function renderThemes() {
  const themesContainer = document.getElementById('themes-container');
  const draftThemeSelect = document.getElementById('draft-theme-select');
  const themesCountBadge = document.getElementById('themes-count-badge');
  if (!themesContainer) return;
  
  themesContainer.innerHTML = '';
  const previousSelection = draftThemeSelect ? draftThemeSelect.value : 'random';
  if (draftThemeSelect) {
    draftThemeSelect.innerHTML = '<option value="random">🎲 Aleatório (Sorteado)</option>';
  }

  if (state.appConfig.themes.length === 0) {
    themesContainer.innerHTML = '<span style="color: var(--text-muted); font-size: 0.75rem;">Nenhum tema configurado.</span>';
    if (themesCountBadge) themesCountBadge.textContent = '0 temas';
    return;
  }
  
  const totalThemes = state.appConfig.themes.length;
  if (themesCountBadge) {
    themesCountBadge.textContent = `${totalThemes} ${totalThemes === 1 ? 'tema' : 'temas'}`;
  }

  state.appConfig.themes.forEach((theme, index) => {
    const chip = document.createElement('div');
    chip.className = 'theme-chip';
    chip.innerHTML = `
      <span>${theme}</span>
      <button type="button" class="btn-remove" data-index="${index}">&times;</button>
    `;
    themesContainer.appendChild(chip);
    
    if (draftThemeSelect) {
      const option = document.createElement('option');
      option.value = theme;
      option.textContent = theme;
      draftThemeSelect.appendChild(option);
    }
  });
  
  if (draftThemeSelect && (previousSelection === 'random' || state.appConfig.themes.includes(previousSelection))) {
    draftThemeSelect.value = previousSelection;
  }
}

export function openUserLogsModal(userEmail, logs) {
  const modal = document.getElementById('user-logs-modal');
  const title = document.getElementById('user-logs-modal-title');
  const tbody = document.getElementById('modal-user-activities-tbody');
  
  if (!modal || !tbody) return;
  
  if (title) title.textContent = `Logs de Auditoria: ${userEmail}`;
  tbody.innerHTML = '';
  
  if (logs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: var(--text-muted); padding: 12px;">Nenhum log de auditoria encontrado para este usuário.</td></tr>';
  } else {
    logs.forEach(log => {
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
  
  modal.classList.remove('hidden');
}
