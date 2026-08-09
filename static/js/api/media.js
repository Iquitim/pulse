// API client methods for Media Asset Gallery
import { request } from './client.js';

export async function uploadMediaAPI(file) {
  const formData = new FormData();
  formData.append('file', file);

  const token = localStorage.getItem('pulse_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch('/api/media/upload', {
    method: 'POST',
    headers: headers,
    body: formData
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Erro ao fazer upload da mídia');
  }
  return await response.json();
}

export async function getUserMediaAPI() {
  const res = await request('/api/media', { method: 'GET' });
  if (!res.ok) throw new Error('Falha ao obter mídias');
  return await res.json();
}

export async function deleteMediaAPI(mediaId) {
  const res = await request(`/api/media/${mediaId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Falha ao excluir mídia');
  return await res.json();
}

export async function attachMediaToCalendarItemAPI(calendarItemId, mediaId) {
  const res = await request(`/api/calendar/${calendarItemId}/media`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ media_id: mediaId })
  });
  if (!res.ok) throw new Error('Falha ao anexar mídia ao item');
  return await res.json();
}

