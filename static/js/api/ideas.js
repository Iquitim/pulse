import { state } from '../state.js';
import { addConsoleLog } from '../logger.js';
import { request } from './client.js';
import * as ui from '../ui.js';

export async function fetchIdeas() {
  try {
    const res = await request('/api/ideas');
    if (!res.ok) throw new Error('Falha ao buscar banco de ideias');
    const data = await res.json();
    state.ideas = data;
    ui.renderIdeas();
    return data;
  } catch (error) {
    addConsoleLog(`Erro ao carregar ideias: ${error.message}`, 'erro');
    return [];
  }
}

export async function createIdea(title, description, channel = 'bluesky') {
  try {
    const res = await request('/api/ideas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description, channel })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao criar ideia');
    addConsoleLog(`Ideia capturada com sucesso para ${channel}: ${title}`, 'sucesso');
    await fetchIdeas();
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao salvar ideia: ${error.message}`, 'erro');
    throw error;
  }
}

export async function updateIdeaStatus(ideaId, status) {
  try {
    const res = await request(`/api/ideas/${ideaId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao atualizar status da ideia');
    await fetchIdeas();
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao atualizar ideia: ${error.message}`, 'erro');
    throw error;
  }
}

export async function deleteIdea(ideaId) {
  try {
    const res = await request(`/api/ideas/${ideaId}`, {
      method: 'DELETE'
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao excluir ideia');
    addConsoleLog('Ideia excluída com sucesso.', 'sucesso');
    await fetchIdeas();
  } catch (error) {
    addConsoleLog(`Erro ao excluir ideia: ${error.message}`, 'erro');
  }
}

export async function analyzePostQuality(content, tone) {
  const loading = document.getElementById("quality-loading");
  const container = document.getElementById("quality-analysis-container");
  if (loading) loading.classList.remove("hidden");
  if (container) container.classList.add("hidden");

  try {
    const res = await request('/api/analyze-quality', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, tone })
    });
    const result = await res.json();
    if (!res.ok) throw new Error(result.detail || 'Erro ao analisar qualidade do post');
    
    state.qualityAnalysis = result;
    ui.renderQualityAnalysis(result);
    addConsoleLog('Análise de qualidade do post gerada com sucesso pela IA.', 'sucesso');
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao avaliar qualidade do post: ${error.message}`, 'erro');
    if (loading) loading.classList.add("hidden");
    throw error;
  }
}

export async function fetchMetricsInsights() {
  const loading = document.getElementById("insights-loading");
  const content = document.getElementById("insights-content");
  if (loading) loading.classList.remove("hidden");
  if (content) content.classList.add("hidden");

  try {
    const res = await request('/api/metrics/insights');
    if (!res.ok) throw new Error('Falha ao obter insights de métricas');
    const result = await res.json();
    
    state.metricsInsights = result;
    ui.renderMetricsInsights(result);
    addConsoleLog('Insights de métricas e sugestões atualizados.', 'sucesso');
    return result;
  } catch (error) {
    addConsoleLog(`Erro ao gerar insights: ${error.message}`, 'erro');
    if (loading) loading.classList.add("hidden");
    if (content) content.classList.remove("hidden");
  } finally {
    if (loading) loading.classList.add("hidden");
  }
}
