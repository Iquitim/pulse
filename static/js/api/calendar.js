import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request } from './client.js';
import * as ui from '../ui.js';

export async function fetchCalendarItems() {
  try {
    const res = await request('/api/calendar');
    if (!res.ok) throw new Error('Falha ao buscar itens do calendário');
    state.calendarItems = await res.json();
    ui.renderCalendar();
  } catch (error) {
    addConsoleLog(`Erro ao carregar calendário: ${error.message}`, 'erro');
  }
}

export async function createCalendarItem(theme, scheduledDate, objective, cta, channel, isManual = false, manualContent = null) {
  try {
    const res = await request('/api/calendar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        theme,
        scheduled_date: scheduledDate,
        objective,
        cta,
        channel,
        is_manual: isManual,
        manual_content: manualContent
      })
    });
    if (!res.ok) {
      const result = await res.json();
      throw new Error(result.detail || 'Erro ao agendar item.');
    }
    addConsoleLog('Item adicionado ao calendário editorial com sucesso.', 'sucesso');
    await fetchCalendarItems();
    return true;
  } catch (error) {
    addConsoleLog(`Erro ao criar agendamento: ${error.message}`, 'erro');
    return false;
  }
}

export async function updateCalendarItem(id, theme, scheduledDate, objective, cta, channel, isManual = false, manualContent = null) {
  try {
    const res = await request(`/api/calendar/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        theme,
        scheduled_date: scheduledDate,
        objective,
        cta,
        channel,
        is_manual: isManual,
        manual_content: manualContent
      })
    });
    if (!res.ok) {
      const result = await res.json();
      throw new Error(result.detail || 'Erro ao atualizar item.');
    }
    addConsoleLog('Agendamento atualizado com sucesso.', 'sucesso');
    await fetchCalendarItems();
    return true;
  } catch (error) {
    addConsoleLog(`Erro ao atualizar agendamento: ${error.message}`, 'erro');
    return false;
  }
}

export async function deleteCalendarItem(id) {
  try {
    const res = await request(`/api/calendar/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Falha ao remover item do calendário');
    addConsoleLog('Agendamento excluído.', 'sucesso');
    await fetchCalendarItems();
  } catch (error) {
    addConsoleLog(`Erro ao excluir agendamento: ${error.message}`, 'erro');
  }
}
