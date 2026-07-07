import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request } from './client.js';
import * as ui from '../ui.js';

export async function fetchInviteCodes() {
  try {
    const res = await request('/api/admin/invite-codes');
    if (!res.ok) throw new Error('Erro ao buscar convites');
    state.inviteCodes = await res.json();
    ui.renderInviteCodes();
  } catch (error) {
    addConsoleLog(`Erro ao obter convites: ${error.message}`, 'erro');
  }
}

export async function createInviteCode(code, tier, uses) {
  try {
    const res = await request('/api/admin/invite-codes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, plan_tier: tier, max_uses: uses })
    });
    if (!res.ok) {
      const result = await res.json();
      throw new Error(result.detail || 'Erro ao gerar convite.');
    }
    addConsoleLog(`Código de convite ${code} gerado com sucesso.`, 'sucesso');
    document.getElementById("invite-code-input").value = "";
    await fetchInviteCodes();
  } catch (error) {
    addConsoleLog(`Erro ao criar convite: ${error.message}`, 'erro');
  }
}

export async function revokeInviteCode(id) {
  try {
    const res = await request(`/api/admin/invite-codes/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Erro ao revogar convite');
    addConsoleLog('Código de convite revogado.', 'sucesso');
    await fetchInviteCodes();
  } catch (error) {
    addConsoleLog(`Erro ao revogar convite: ${error.message}`, 'erro');
  }
}

export async function fetchUsersList() {
  try {
    const res = await request('/api/admin/users');
    if (!res.ok) throw new Error('Erro ao buscar usuários');
    state.usersList = await res.json();
    ui.renderUsersList();
  } catch (error) {
    addConsoleLog(`Erro ao obter usuários: ${error.message}`, 'erro');
  }
}

export async function toggleUserStatus(id, active) {
  try {
    const res = await request(`/api/admin/users/${id}?status_active=${active}`, {
      method: 'PATCH'
    });
    if (!res.ok) {
      const result = await res.json();
      throw new Error(result.detail || 'Erro ao alternar status do usuário');
    }
    addConsoleLog('Status do usuário atualizado.', 'sucesso');
    await fetchUsersList();
  } catch (error) {
    addConsoleLog(`Erro ao alternar status do usuário: ${error.message}`, 'erro');
  }
}

export async function fetchAuditLogs() {
  try {
    const res = await request('/api/audit-logs');
    if (!res.ok) throw new Error('Falha ao buscar logs de auditoria');
    state.auditLogs = await res.json();
    ui.renderAuditLogs();
  } catch (error) {
    addConsoleLog(`Erro ao carregar logs de auditoria: ${error.message}`, 'erro');
  }
}

export async function fetchUserAuditLogs(userId) {
  try {
    const res = await request(`/api/admin/users/${userId}/audit-logs`);
    if (!res.ok) throw new Error('Falha ao buscar logs do usuário');
    return await res.json();
  } catch (error) {
    addConsoleLog(`Erro ao carregar logs do usuário: ${error.message}`, 'erro');
    return [];
  }
}

export async function deleteUser(userId) {
  try {
    const res = await request(`/api/admin/users/${userId}`, {
      method: 'DELETE'
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao excluir usuário');
    addConsoleLog('Usuário excluído com sucesso.', 'sucesso');
    await fetchUsersList();
  } catch (error) {
    addConsoleLog(`Erro ao excluir usuário: ${error.message}`, 'erro');
  }
}

export async function updateUserPlan(userId, planTier) {
  try {
    const res = await request(`/api/admin/users/${userId}/plan`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan_tier: planTier })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao atualizar plano');
    addConsoleLog('Plano do usuário atualizado com sucesso.', 'sucesso');
    await fetchUsersList();
  } catch (error) {
    addConsoleLog(`Erro ao atualizar plano: ${error.message}`, 'erro');
  }
}

export async function fetchTierConfigs() {
  try {
    const res = await request('/api/admin/tier-configs');
    if (!res.ok) throw new Error('Falha ao buscar configurações de planos');
    return await res.json();
  } catch (error) {
    addConsoleLog(`Erro ao carregar configurações de planos: ${error.message}`, 'erro');
    return [];
  }
}

export async function updateTierConfig(tierName, maxThemes, maxAccounts, maxCalendarItems, dailyPostLimit) {
  try {
    const res = await request(`/api/admin/tier-configs/${tierName}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        max_themes: parseInt(maxThemes),
        max_accounts: parseInt(maxAccounts),
        max_calendar_items: parseInt(maxCalendarItems),
        daily_post_limit: parseInt(dailyPostLimit)
      })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao atualizar limites do plano');
    addConsoleLog(`Limites do plano ${tierName} atualizados com sucesso.`, 'sucesso');
  } catch (error) {
    addConsoleLog(`Erro ao atualizar limites: ${error.message}`, 'erro');
  }
}

export async function fetchGlobalSettings() {
  try {
    const res = await request('/api/admin/global-settings');
    if (!res.ok) throw new Error('Falha ao buscar configurações globais');
    return await res.json();
  } catch (error) {
    addConsoleLog(`Erro ao carregar configurações globais: ${error.message}`, 'erro');
    return null;
  }
}

export async function updateGlobalSettings(settings) {
  try {
    const res = await request('/api/admin/global-settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao atualizar configurações globais');
    addConsoleLog('Configurações globais atualizadas com sucesso.', 'sucesso');
    return true;
  } catch (error) {
    addConsoleLog(`Erro ao salvar configurações globais: ${error.message}`, 'erro');
    return false;
  }
}
