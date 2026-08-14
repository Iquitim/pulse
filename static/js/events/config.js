import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';
import { addConsoleLog } from '../logger.js';
import { setupConfigSocialEvents } from './config_social.js';
import { setupConfigLLMEvents } from './config_llm.js';

export function setupConfigEvents() {
  // Delegate sub-feature event bindings
  setupConfigSocialEvents();
  setupConfigLLMEvents();

  // Theme Toggle Button
  const btnThemeToggle = document.getElementById('btn-theme-toggle');
  if (btnThemeToggle) {
    btnThemeToggle.addEventListener('click', () => {
      const isLight = document.documentElement.classList.toggle('light-theme');
      localStorage.setItem('pulse_theme', isLight ? 'light' : 'dark');
      addConsoleLog(`Tema alterado para modo ${isLight ? 'claro' : 'escuro'}.`, 'system');
    });
  }

  // Add Theme
  const btnAddTheme = document.getElementById('btn-add-theme');
  const newThemeInput = document.getElementById('new-theme-input');
  if (btnAddTheme && newThemeInput) {
    btnAddTheme.addEventListener('click', () => {
      const value = newThemeInput.value.trim();
      if (value && !state.appConfig.themes.includes(value)) {
        state.appConfig.themes.push(value);
        ui.renderThemes();
        newThemeInput.value = '';
        ui.updateMetrics();
      }
    });
    
    newThemeInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        btnAddTheme.click();
      }
    });
  }

  // Remove Theme delegator
  const themesContainer = document.getElementById('themes-container');
  if (themesContainer) {
    themesContainer.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-remove')) {
        const index = parseInt(e.target.getAttribute('data-index'), 10);
        state.appConfig.themes.splice(index, 1);
        ui.renderThemes();
        ui.updateMetrics();
      }
    });
  }

  // Interval hours slider
  const intervalHoursInput = document.getElementById('interval_hours');
  const intervalDisplay = document.getElementById('interval-display');
  if (intervalHoursInput && intervalDisplay) {
    intervalHoursInput.addEventListener('input', (e) => {
      const val = e.target.value;
      intervalDisplay.textContent = `A cada ${val} ${val === '1' ? 'hora' : 'horas'}`;
      ui.updateFrequencyEstimateText(val);
      ui.syncPresetButtons(val);
      ui.updateQueueList();
    });
    intervalHoursInput.addEventListener('change', () => {
      api.saveConfig();
    });
  }

  // Preset buttons
  document.querySelectorAll('.btn-preset').forEach(btn => {
    btn.addEventListener('click', () => {
      const val = btn.getAttribute('data-value');
      const intervalHoursInput = document.getElementById('interval_hours');
      const intervalDisplay = document.getElementById('interval-display');
      if (intervalHoursInput) intervalHoursInput.value = val;
      if (intervalDisplay) intervalDisplay.textContent = `A cada ${val} ${val === '1' ? 'hora' : 'horas'}`;
      ui.updateFrequencyEstimateText(val);
      ui.syncPresetButtons(val);
      ui.updateQueueList();
      api.saveConfig();
    });
  });

  // Prompt template restore
  const btnRestorePrompt = document.getElementById('btn-restore-prompt');
  const systemPromptInput = document.getElementById('system_prompt');
  if (btnRestorePrompt && systemPromptInput) {
    btnRestorePrompt.addEventListener('click', () => {
      systemPromptInput.value = `Você é o Pulse, um assistente editorial inteligente que escreve posts curtos para redes sociais (como o Bluesky).

Você deve escrever incorporando a Persona fornecida.

Tarefa:
Escreva um post para o Bluesky sobre: {theme}

Tom do post:
{tone}

Regras Gerais de Escrita:
* Máximo de 280 caracteres.
* Sem hashtags.
* Sem aspas no início/fim.
* Sem introduções ou explicações ("aqui está um post...", "olá pessoal").
* Sem threads.
* Sem prometer resultados milagrosos.
* Sem inventar dados ou notícias.
* Sem exagero publicitário.
* No máximo 1 emoji, apenas se for natural.
* Use português brasileiro.
* Escreva de forma curta, fluida e com personalidade.

Estilo desejado:
* Uma reflexão curta.
* Uma observação prática.
* Um aprendizado de bastidor.
* Uma provocação leve.
* Uma pergunta que convide conversa.
* Uma frase que pareça escrita por uma pessoa real, não por uma marca.

Retorne apenas o post final, pronto para ser publicado.`;
      addConsoleLog('Instruções do sistema restauradas para o padrão original.', 'info');
    });
  }

  // Persona template restore
  const btnRestorePersona = document.getElementById('btn-restore-persona');
  const personaDescriptionInput = document.getElementById('persona_description');
  if (btnRestorePersona && personaDescriptionInput) {
    btnRestorePersona.addEventListener('click', () => {
      personaDescriptionInput.value = `Nome: Persona de Exemplo
Voz e Atitude:
* Especialista na sua área de atuação (ex: tecnologia, marketing, design).
* Gosta de falar sobre tópicos práticos do dia a dia, compartilhando aprendizados reais.
* Prefere um tom honesto, simples e útil, sem promessas milagrosas.
* Evita clichês corporativos, autoridade forçada ou linguagem artificial.
* Fala de forma natural, como uma pessoa real conversando com um colega.`;
      addConsoleLog('Persona do usuário restaurada para a biografia padrão.', 'info');
    });
  }

  // Config form submissions
  const configForm = document.getElementById('config-form');
  if (configForm) {
    configForm.addEventListener('submit', api.saveConfig);
  }

  const btnPostNow = document.getElementById('btn-post-now');
  if (btnPostNow) {
    btnPostNow.addEventListener('click', api.triggerPostNow);
  }

  const btnRefreshMetrics = document.getElementById('btn-refresh-metrics');
  if (btnRefreshMetrics) {
    btnRefreshMetrics.addEventListener('click', api.triggerRefreshMetrics);
  }

  // Logs terminal buttons
  const btnCopyLogs = document.getElementById('btn-copy-logs');
  const btnClearLogs = document.getElementById('btn-clear-logs');
  const consoleOutput = document.getElementById('console-output');
  if (btnCopyLogs && consoleOutput) {
    btnCopyLogs.addEventListener('click', () => {
      const logTexts = [];
      consoleOutput.querySelectorAll('.terminal-line').forEach(line => {
        logTexts.push(line.textContent.trim());
      });
      navigator.clipboard.writeText(logTexts.join('\n'));
      addConsoleLog('Logs copiados para a área de transferência.', 'system');
    });
  }
  
  if (btnClearLogs && consoleOutput) {
    btnClearLogs.addEventListener('click', () => {
      consoleOutput.innerHTML = '';
      addConsoleLog('Console de logs esvaziado.', 'system');
    });
  }

  // Tab navigation triggers
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const tabId = btn.getAttribute('data-tab');
      ui.switchTab(tabId);
    });
  });

  // Quick navigation from header status badges to config tab
  ['status-gemini', 'status-bsky', 'status-twitter', 'status-threads'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.style.cursor = 'pointer';
      el.addEventListener('click', () => ui.switchTab('config'));
    }
  });

  // Instructions Sidebar Navigation
  document.querySelectorAll('.doc-menu-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      
      document.querySelectorAll('.doc-menu-btn').forEach(b => {
        b.classList.remove('active');
        b.style.color = 'var(--text-secondary)';
      });
      btn.classList.add('active');
      btn.style.color = 'var(--text-primary)';

      document.getElementById(targetId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}
