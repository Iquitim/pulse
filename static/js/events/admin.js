import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

let tierConfigsCache = [];

async function loadTierConfigUI() {
  if (state.user && state.user.role === 'admin') {
    tierConfigsCache = await api.fetchTierConfigs();
    updateTierFormFields();
  }
}

async function loadGlobalSettingsUI() {
  if (state.user && state.user.role === 'admin') {
    const settings = await api.fetchGlobalSettings();
    if (settings) {
      const clientIdInput = document.getElementById('global-twitter-client-id');
      const clientSecretInput = document.getElementById('global-twitter-client-secret');
      
      if (clientIdInput) clientIdInput.value = settings.twitter_client_id || '';
      if (clientSecretInput) {
        if (settings.twitter_client_secret_configured) {
          clientSecretInput.value = '__UNCHANGED__';
          clientSecretInput.placeholder = '•••••••••••••••• (Configurado)';
        } else {
          clientSecretInput.value = '';
          clientSecretInput.placeholder = 'Client Secret OAuth 2.0';
        }
      }
    }
  }
}

function updateTierFormFields() {
  const configTierSelect = document.getElementById('config-tier-select');
  const tierMaxThemes = document.getElementById('tier-max-themes');
  const tierMaxAccounts = document.getElementById('tier-max-accounts');
  const tierMaxCalendar = document.getElementById('tier-max-calendar');
  const tierDailyLimit = document.getElementById('tier-daily-limit');

  if (!configTierSelect) return;
  const selectedTier = configTierSelect.value;
  const configObj = tierConfigsCache.find(c => c.tier_name === selectedTier);
  if (configObj) {
    if (tierMaxThemes) tierMaxThemes.value = configObj.max_themes;
    if (tierMaxAccounts) tierMaxAccounts.value = configObj.max_accounts;
    if (tierMaxCalendar) tierMaxCalendar.value = configObj.max_calendar_items;
    if (tierDailyLimit) tierDailyLimit.value = configObj.daily_post_limit;
  }
}

export function setupAdminEvents() {
  const inviteCodeForm = document.getElementById('invite-code-form');
  if (inviteCodeForm) {
    inviteCodeForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const code = document.getElementById('invite-code-input').value.trim().toUpperCase();
      const tier = document.getElementById('invite-tier-select').value;
      const uses = parseInt(document.getElementById('invite-uses-input').value, 10);
      api.createInviteCode(code, tier, uses);
    });
  }

  const inviteCodesTbody = document.getElementById('invite-codes-tbody');
  if (inviteCodesTbody) {
    inviteCodesTbody.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-revoke-invite')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        if (confirm('Deseja realmente revogar este código de convite?')) {
          api.revokeInviteCode(id);
        }
      }
    });
  }

  const usersTbody = document.getElementById('users-tbody');
  if (usersTbody) {
    usersTbody.addEventListener('click', async (e) => {
      if (e.target.classList.contains('btn-toggle-user')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        const active = e.target.getAttribute('data-active') === 'true';
        const actionStr = active ? 'ativar' : 'bloquear';
        if (confirm(`Deseja realmente ${actionStr} este usuário?`)) {
          await api.toggleUserStatus(id, active);
        }
      } else if (e.target.classList.contains('btn-delete-user')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        if (confirm('Deseja realmente excluir permanentemente este usuário? Todos os seus dados e conexões serão removidos.')) {
          await api.deleteUser(id);
        }
      } else if (e.target.classList.contains('btn-view-user-logs')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        const email = e.target.getAttribute('data-email');
        const logs = await api.fetchUserAuditLogs(id);
        ui.openUserLogsModal(email, logs);
      }
    });

    usersTbody.addEventListener('change', async (e) => {
      if (e.target.classList.contains('change-user-plan')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        const newPlan = e.target.value;
        if (confirm(`Deseja alterar o plano deste usuário para ${newPlan.toUpperCase()}?`)) {
          await api.updateUserPlan(id, newPlan);
        } else {
          ui.renderUsersList();
        }
      }
    });
  }

  // --- Admin User Logs Modal Close Handlers ---
  const btnCloseUserLogsModal = document.getElementById('btn-close-user-logs-modal');
  const userLogsModal = document.getElementById('user-logs-modal');
  if (btnCloseUserLogsModal && userLogsModal) {
    btnCloseUserLogsModal.addEventListener('click', () => {
      userLogsModal.classList.add('hidden');
    });
    userLogsModal.addEventListener('click', (e) => {
      if (e.target === userLogsModal) {
        userLogsModal.classList.add('hidden');
      }
    });
  }

  // --- Tier Config Event Listeners ---
  const configTierSelect = document.getElementById('config-tier-select');
  const tierConfigForm = document.getElementById('tier-config-form');

  if (configTierSelect) {
    configTierSelect.addEventListener('change', updateTierFormFields);
  }

  if (tierConfigForm) {
    tierConfigForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const selectedTier = configTierSelect.value;
      const tierMaxThemes = document.getElementById('tier-max-themes');
      const tierMaxAccounts = document.getElementById('tier-max-accounts');
      const tierMaxCalendar = document.getElementById('tier-max-calendar');
      const tierDailyLimit = document.getElementById('tier-daily-limit');
      
      await api.updateTierConfig(
        selectedTier,
        tierMaxThemes.value,
        tierMaxAccounts.value,
        tierMaxCalendar.value,
        tierDailyLimit.value
      );
      tierConfigsCache = await api.fetchTierConfigs();
    });
  }

  const globalSettingsForm = document.getElementById('global-settings-form');
  if (globalSettingsForm) {
    globalSettingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const twitter_client_id = document.getElementById('global-twitter-client-id').value.trim();
      const twitter_client_secret = document.getElementById('global-twitter-client-secret').value.trim();
      
      const success = await api.updateGlobalSettings({
        twitter_client_id,
        twitter_client_secret
      });
      
      if (success) {
        await loadGlobalSettingsUI();
      }
    });
  }

  // Tab navigation triggers
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const tabId = btn.getAttribute('data-tab');
      if (tabId === 'admin') {
        await loadTierConfigUI();
        await loadGlobalSettingsUI();
        await api.fetchUsersList();
        await api.fetchInviteCodes();
      }
    });
  });
}
