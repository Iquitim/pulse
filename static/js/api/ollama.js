import { request } from './client.js';

// Helper to format FastAPI errors (including validation 422 lists)
async function handleResponseError(res, defaultMsg) {
  try {
    const err = await res.json();
    if (err && err.detail) {
      if (typeof err.detail === 'string') {
        return err.detail;
      } else if (Array.isArray(err.detail)) {
        return err.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
      } else {
        return JSON.stringify(err.detail);
      }
    }
  } catch (e) {
    // Ignore and fall back to defaultMsg
  }
  return defaultMsg;
}

export async function fetchHardwareDiagnostic() {
  const res = await request('/api/ollama/diagnostic');
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao executar diagnóstico de hardware'));
  }
  return await res.json();
}

export async function fetchOllamaStatus() {
  const res = await request('/api/ollama/status');
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao buscar status do Ollama'));
  }
  return await res.json();
}

export async function installOllama() {
  const res = await request('/api/ollama/install', { method: 'POST' });
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao iniciar instalação do Ollama'));
  }
  return await res.json();
}

export async function fetchInstallProgress() {
  const res = await request('/api/ollama/install-progress');
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao obter progresso de instalação'));
  }
  return await res.json();
}

export async function startOllama(model = null) {
  const res = await request('/api/ollama/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model })
  });
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao iniciar Ollama'));
  }
  return await res.json();
}

export async function stopOllama() {
  const res = await request('/api/ollama/stop', { method: 'POST' });
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao parar Ollama'));
  }
  return await res.json();
}

export async function fetchOllamaModels(host) {
  const hostParam = encodeURIComponent(host);
  const res = await request(`/api/ollama/models?host=${hostParam}`);
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao listar modelos do Ollama'));
  }
  return await res.json();
}

export async function pullModel(host, model) {
  const res = await request('/api/ollama/pull', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ host, model })
  });
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao iniciar download do modelo'));
  }
  return await res.json();
}

export async function fetchPullProgress(host, model) {
  const hostParam = encodeURIComponent(host);
  const modelParam = encodeURIComponent(model);
  const res = await request(`/api/ollama/pull-progress?host=${hostParam}&model=${modelParam}`);
  if (!res.ok) {
    throw new Error(await handleResponseError(res, 'Falha ao buscar progresso do modelo'));
  }
  return await res.json();
}
