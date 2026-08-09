// API client methods for Media Asset Gallery
import { apiRequest } from './client.js';

export async function uploadMediaAPI(file) {
  const formData = new FormData();
  formData.append('file', file);

  const token = localStorage.getItem('token');
  const response = await fetch('/api/media/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || 'Erro ao fazer upload da mídia');
  }
  return await response.json();
}

export async function getUserMediaAPI() {
  return await apiRequest('/api/media', { method: 'GET' });
}

export async function deleteMediaAPI(mediaId) {
  return await apiRequest(`/api/media/${mediaId}`, { method: 'DELETE' });
}

export async function attachMediaToCalendarItemAPI(calendarItemId, mediaId) {
  return await apiRequest(`/api/calendar/${calendarItemId}/media`, {
    method: 'POST',
    body: JSON.stringify({ media_id: mediaId })
  });
}
