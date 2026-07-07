import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';
import { addConsoleLog } from '../logger.js';

function fillLLMServerForm(server) {
  document.getElementById('llm_server_id').value = server.id;
  document.getElementById('llm_server_name').value = server.name;
  document.getElementById('llm_provider').value = server.provider;
  document.getElementById('llm_model').value = server.model;
  document.getElementById('llm_base_url').value = server.base_url || '';
  document.getElementById('llm_api_key').value = server.api_key || '';
  
  // Trigger provider change event to toggle url/api fields visibility
  document.getElementById('llm_provider').dispatchEvent(new Event('change'));
  
  document.getElementById('llm-server-form-title').textContent = 'Editar Servidor';
  document.getElementById('btn-cancel-llm-edit').classList.remove('hidden');
}

function resetLLMServerForm() {
  const serverId = document.getElementById('llm_server_id');
  const serverForm = document.getElementById('llm-server-form');
  const provider = document.getElementById('llm_provider');
  const model = document.getElementById('llm_model');
  const baseUrl = document.getElementById('llm_base_url');
  const apiKey = document.getElementById('llm_api_key');
  const formTitle = document.getElementById('llm-server-form-title');
  const cancelBtn = document.getElementById('btn-cancel-llm-edit');
  
  if (serverId) serverId.value = '';
  if (serverForm) serverForm.reset();
  
  if (provider) provider.value = 'ollama';
  if (model) model.value = 'llama3';
  if (baseUrl) baseUrl.value = 'http://localhost:11434/v1';
  if (apiKey) apiKey.value = '';
  
  if (provider) provider.dispatchEvent(new Event('change'));
  
  if (formTitle) formTitle.textContent = 'Adicionar Servidor';
  if (cancelBtn) cancelBtn.classList.add('hidden');
}

export function setupConfigEvents() {
  // Initialize LLM server form defaults
  resetLLMServerForm();

  // --- Connected Social Networks Event Listeners ---
  const platformSelect = document.getElementById('social-platform-select');
  if (platformSelect) {
    platformSelect.addEventListener('change', (e) => {
      const selected = e.target.value;
      document.querySelectorAll('.credentials-fields').forEach(group => {
        group.classList.add('hidden');
      });
      document.getElementById(`credentials-group-${selected}`)?.classList.remove('hidden');
      
      const submitBtn = document.getElementById('btn-submit-social-connect');
      if (submitBtn) {
        if (selected === 'twitter') {
          const connType = document.getElementById('twitter-conn-type')?.value || 'oauth2';
          if (connType === 'oauth2') {
            submitBtn.classList.add('hidden');
          } else {
            submitBtn.classList.remove('hidden');
          }
        } else {
          submitBtn.classList.remove('hidden');
        }
      }
    });

    // Sincronizar o seletor visual de plataforma inicialmente
    ui.syncVisualSelector('social-platform-select', 'social-platform-selector');
  }

  // Click handler para o seletor visual de plataforma nas configurações de conexão
  document.querySelectorAll('.social-platform-selector .channel-option-card').forEach(card => {
    card.addEventListener('click', () => {
      const val = card.getAttribute('data-value');
      const select = document.getElementById('social-platform-select');
      if (select) {
        select.value = val;
        ui.syncVisualSelector('social-platform-select', 'social-platform-selector');
        select.dispatchEvent(new Event('change'));
      }
    });
  });

  const twitterConnType = document.getElementById('twitter-conn-type');
  if (twitterConnType) {
    twitterConnType.addEventListener('change', (e) => {
      const selected = e.target.value;
      document.querySelectorAll('.twitter-sub-fields').forEach(group => {
        group.classList.add('hidden');
      });
      document.getElementById(`twitter-sub-${selected}`)?.classList.remove('hidden');
      
      const submitBtn = document.getElementById('btn-submit-social-connect');
      if (submitBtn) {
        if (selected === 'oauth2') {
          submitBtn.classList.add('hidden');
        } else {
          submitBtn.classList.remove('hidden');
        }
      }
    });
  }

  const btnConnectTwitter = document.getElementById('btn-connect-twitter');
  if (btnConnectTwitter) {
    btnConnectTwitter.addEventListener('click', () => {
      const handleInput = document.getElementById('social-handle-input');
      const handle = handleInput ? handleInput.value.trim() : '';
      if (!handle) {
        alert('Por favor, insira o Handle / Identificador da sua conta antes de iniciar a autorização.');
        if (handleInput) handleInput.focus();
        return;
      }
      
      const width = 600;
      const height = 750;
      const left = (window.innerWidth - width) / 2;
      const top = (window.innerHeight - height) / 2;
      const url = `/api/social/twitter/login?handle=${encodeURIComponent(handle)}&token=${encodeURIComponent(state.token)}`;
      
      const twitterPopup = window.open(
        url,
        'twitter-oauth',
        `width=${width},height=${height},left=${left},top=${top},status=no,resizable=yes,scrollbars=yes`
      );
      
      if (!twitterPopup) {
        alert('Pop-up bloqueado pelo navegador. Por favor, ative os pop-ups para esta página e tente novamente.');
      }
    });
  }

  // Escuta mensagens do popup de autenticação do Twitter
  window.addEventListener('message', (event) => {
    if (event.origin !== window.location.origin) return;
    
    if (event.data === 'twitter_connected') {
      import('../logger.js').then(logger => {
        logger.addConsoleLog('Conta do Twitter / X conectada com sucesso via OAuth 2.0!', 'success');
      });
      api.loadSocialAccounts();
      const handleInput = document.getElementById('social-handle-input');
      if (handleInput) handleInput.value = '';
    } else if (event.data && event.data.error) {
      import('../logger.js').then(logger => {
        logger.addConsoleLog(`Falha ao conectar Twitter / X: ${event.data.error}`, 'error');
      });
    }
  });

  const socialConnectForm = document.getElementById('social-connect-form');
  if (socialConnectForm) {
    socialConnectForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const platform = platformSelect.value;
      const accountHandle = document.getElementById('social-handle-input').value.trim();
      
      let credentials = {};
      if (platform === "bluesky") {
        credentials = {
          handle: document.getElementById('bsky-username-input').value.trim(),
          password: document.getElementById('bsky-password-input').value.trim()
        };
      } else if (platform === "twitter") {
        const connType = document.getElementById('twitter-conn-type').value;
        if (connType === 'oauth2') return; // Handled by popup
        
        credentials = {
          api_key: document.getElementById('twitter-key-input').value.trim(),
          api_secret: document.getElementById('twitter-secret-input').value.trim(),
          access_token: document.getElementById('twitter-token-input').value.trim(),
          access_token_secret: document.getElementById('twitter-token-secret-input').value.trim()
        };
      } else if (platform === "threads") {
        credentials = {};
      }
      
      api.connectAccount(platform, accountHandle, credentials);
    });
  }

  const connectedAccountsList = document.getElementById('connected-accounts-list');
  if (connectedAccountsList) {
    connectedAccountsList.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-disconnect-account')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        if (confirm('Deseja realmente desconectar esta rede social?')) {
          api.disconnectAccount(id);
        }
      }
    });
  }

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
* Escreva de forma corta, fluida e com personalidade.

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

  // LLM Provider UI Toggle Event
  const llmProvider = document.getElementById('llm_provider');
  if (llmProvider) {
    llmProvider.addEventListener('change', (e) => {
      const val = e.target.value;
      const baseUrlGroup = document.getElementById('llm-base-url-group');
      const apiKeyGroup = document.getElementById('llm-api-key-group');
      
      if (val === 'gemini') {
        if (baseUrlGroup) baseUrlGroup.classList.add('hidden');
        if (apiKeyGroup) apiKeyGroup.classList.remove('hidden');
      } else if (val === 'ollama') {
        if (baseUrlGroup) baseUrlGroup.classList.remove('hidden');
        if (apiKeyGroup) apiKeyGroup.classList.add('hidden');
      } else if (val === 'openai_compatible') {
        if (baseUrlGroup) baseUrlGroup.classList.remove('hidden');
        if (apiKeyGroup) apiKeyGroup.classList.remove('hidden');
      }
    });
  }

  // LLM Server Form Submissions (Create / Edit)
  const llmServerForm = document.getElementById('llm-server-form');
  if (llmServerForm) {
    llmServerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const serverId = document.getElementById('llm_server_id').value;
      const name = document.getElementById('llm_server_name').value.trim();
      const provider = document.getElementById('llm_provider').value;
      const model = document.getElementById('llm_model').value.trim();
      const baseUrl = document.getElementById('llm_base_url').value.trim();
      const apiKey = document.getElementById('llm_api_key').value.trim();
      
      const serverData = {
        name,
        provider,
        model,
        base_url: baseUrl || null,
        api_key: apiKey || null
      };
      
      const saveBtn = document.getElementById('btn-save-llm-server');
      if (saveBtn) saveBtn.disabled = true;
      
      try {
        if (serverId) {
          await api.updateLLMServer(serverId, serverData);
        } else {
          await api.createLLMServer(serverData);
        }
        resetLLMServerForm();
        ui.showToast('Configuração de servidor salva com sucesso!', 'sucesso');
      } catch (error) {
        ui.showToast(`Erro ao salvar servidor: ${error.message}`, 'erro');
      } finally {
        if (saveBtn) saveBtn.disabled = false;
      }
    });
  }

  // Cancel edit button
  const btnCancelLlmEdit = document.getElementById('btn-cancel-llm-edit');
  if (btnCancelLlmEdit) {
    btnCancelLlmEdit.addEventListener('click', resetLLMServerForm);
  }

  // Event delegation for LLM Servers List actions (Activate / Edit / Delete)
  const llmServersList = document.getElementById('llm-servers-list');
  if (llmServersList) {
    llmServersList.addEventListener('click', async (e) => {
      const target = e.target;
      const id = target.getAttribute('data-id');
      if (!id) return;
      
      if (target.classList.contains('btn-activate-server')) {
        target.disabled = true;
        try {
          await api.activateLLMServer(id);
          ui.showToast('Servidor LLM ativado!', 'sucesso');
        } catch (error) {
          ui.showToast(`Erro ao ativar servidor: ${error.message}`, 'erro');
        } finally {
          target.disabled = false;
        }
      } else if (target.classList.contains('btn-edit-server')) {
        const server = state.llmServers.find(s => s.id == id);
        if (server) {
          fillLLMServerForm(server);
        }
      } else if (target.classList.contains('btn-delete-server')) {
        if (confirm('Deseja realmente excluir este servidor LLM?')) {
          target.disabled = true;
          try {
            await api.deleteLLMServer(id);
            ui.showToast('Servidor LLM excluído com sucesso!', 'sucesso');
            const currentEditId = document.getElementById('llm_server_id').value;
            if (currentEditId == id) {
              resetLLMServerForm();
            }
          } catch (error) {
            ui.showToast(`Erro ao excluir servidor: ${error.message}`, 'erro');
          } finally {
            target.disabled = false;
          }
        }
      }
    });
  }

  // LLM Connection Test Event for Server Form
  const btnTestLlmServer = document.getElementById('btn-test-llm-server');
  if (btnTestLlmServer) {
    btnTestLlmServer.addEventListener('click', async () => {
      const serverId = document.getElementById('llm_server_id').value || null;
      const provider = document.getElementById('llm_provider')?.value;
      const model = document.getElementById('llm_model')?.value.trim();
      const baseUrl = document.getElementById('llm_base_url')?.value.trim();
      const apiKey = document.getElementById('llm_api_key')?.value.trim();
      
      if (!model) {
        ui.showToast('Por favor, informe o Modelo antes de testar a conexão.', 'erro');
        return;
      }
      
      btnTestLlmServer.disabled = true;
      const originalText = btnTestLlmServer.textContent;
      btnTestLlmServer.textContent = 'Testando... ⚡';
      
      try {
        const res = await api.testLLMConnection(provider, model, baseUrl, apiKey, serverId);
        ui.showToast(res.message || 'Conexão estabelecida com sucesso!', 'sucesso');
      } catch (error) {
        ui.showToast(`Erro na conexão: ${error.message}`, 'erro');
      } finally {
        btnTestLlmServer.disabled = false;
        btnTestLlmServer.textContent = originalText;
      }
    });
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

  // --- Instructions Sidebar Navigation ---
  document.querySelectorAll('.doc-menu-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      
      // Update sidebar active state
      document.querySelectorAll('.doc-menu-btn').forEach(b => {
        b.classList.remove('active');
        b.style.color = 'var(--text-secondary)';
      });
      btn.classList.add('active');
      btn.style.color = 'var(--text-primary)';

      // Scroll to target section
      document.getElementById(targetId)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}
