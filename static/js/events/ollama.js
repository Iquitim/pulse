import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

let installInterval = null;
let activeDiagData = null;
let modelsHost = 'http://localhost:11434';
let pullInterval = null;

export function setupOllamaEvents() {
  // --- Ollama Installer Event Listeners ---
  const btnOpenOllamaInstaller = document.getElementById('btn-open-ollama-installer');
  if (btnOpenOllamaInstaller) {
    btnOpenOllamaInstaller.addEventListener('click', async () => {
      const modal = document.getElementById('ollama-installer-modal');
      if (!modal) return;
      
      // Reset screens
      document.getElementById('ollama-install-screen-diagnostic').classList.remove('hidden');
      document.getElementById('ollama-install-screen-progress').classList.add('hidden');
      
      modal.classList.remove('hidden');

      // Fetch and render diagnostics
      try {
        const diag = await api.fetchHardwareDiagnostic();
        activeDiagData = diag;
        ui.renderOllamaDiagnostic(diag);
      } catch (err) {
        ui.showToast(err.message, 'erro');
      }
    });
  }

  const btnCloseOllamaInstaller = document.getElementById('btn-close-ollama-installer');
  const btnCancelOllamaInstall = document.getElementById('btn-cancel-ollama-install');
  const cancelAndClose = () => {
    if (installInterval) {
      clearInterval(installInterval);
      installInterval = null;
    }
    document.getElementById('ollama-installer-modal')?.classList.add('hidden');
  };

  if (btnCloseOllamaInstaller) btnCloseOllamaInstaller.addEventListener('click', cancelAndClose);
  if (btnCancelOllamaInstall) btnCancelOllamaInstall.addEventListener('click', cancelAndClose);

  const btnProceedOllamaInstall = document.getElementById('btn-proceed-ollama-install');
  if (btnProceedOllamaInstall) {
    btnProceedOllamaInstall.addEventListener('click', async () => {
      document.getElementById('ollama-install-screen-diagnostic').classList.add('hidden');
      document.getElementById('ollama-install-screen-progress').classList.remove('hidden');

      try {
        ui.updateOllamaInstallProgress(0, 'Conectando...', 'Iniciando download...');
        await api.installOllama();
        
        // Start polling installer progress
        installInterval = setInterval(async () => {
          try {
            const progress = await api.fetchInstallProgress();
            
            if (progress.status === 'downloading') {
              const mbDownloaded = (progress.downloaded_bytes / (1024 * 1024)).toFixed(1);
              const mbTotal = (progress.total_bytes / (1024 * 1024)).toFixed(1);
              ui.updateOllamaInstallProgress(
                progress.percentage,
                `${mbDownloaded} / ${mbTotal} MB`,
                `Baixando arquivos portáteis... (${progress.percentage}%)`
              );
            } else if (progress.status === 'extracting') {
              ui.updateOllamaInstallProgress(90, 'Descompactando...', 'Extraindo pacote portátil no workspace...');
            } else if (progress.status === 'completed') {
              clearInterval(installInterval);
              installInterval = null;
              ui.updateOllamaInstallProgress(100, 'Extraído', 'Configurando e inicializando serviço local...');
              
              // Start the server subprocess
              const defaultModel = activeDiagData ? activeDiagData.recommended_model : 'phi3:3.8b';
              const startRes = await api.startOllama(defaultModel);
              
              ui.updateOllamaInstallProgress(100, 'Completo', `<span style="color: var(--color-success); font-weight: bold;">Ollama embutido ativo e ativado com modelo ${defaultModel}!</span>`);
              
              ui.showToast('Ollama instalado e ativo com sucesso!', 'sucesso');
              await api.fetchLLMServers();
              
              // Close after 2.5s
              setTimeout(cancelAndClose, 2500);
            } else if (progress.status === 'failed') {
              clearInterval(installInterval);
              installInterval = null;
              ui.updateOllamaInstallProgress(0, 'Erro', progress.error || 'Falha ao instalar o Ollama.', true);
            }
          } catch (err) {
            clearInterval(installInterval);
            installInterval = null;
            ui.updateOllamaInstallProgress(0, 'Erro', err.message, true);
          }
        }, 1000);

      } catch (err) {
        ui.updateOllamaInstallProgress(0, 'Erro', err.message, true);
      }
    });
  }

  const btnRetryOllamaInstall = document.getElementById('btn-retry-ollama-install');
  if (btnRetryOllamaInstall) {
    btnRetryOllamaInstall.addEventListener('click', () => {
      btnProceedOllamaInstall?.click();
    });
  }

  // --- Ollama Models Management Event Listeners ---
  const llmServersList = document.getElementById('llm-servers-list');
  // Delegate click for "Modelos 📦" button in servers list
  if (llmServersList) {
    llmServersList.addEventListener('click', async (e) => {
      if (e.target.classList.contains('btn-manage-models')) {
        const serverId = e.target.getAttribute('data-id');
        let rawUrl = e.target.getAttribute('data-url') || 'http://localhost:11434';
        
        // Strip /v1 to talk natively to Ollama client
        if (rawUrl.endsWith('/v1/')) rawUrl = rawUrl.slice(0, -4);
        else if (rawUrl.endsWith('/v1')) rawUrl = rawUrl.slice(0, -3);
        
        modelsHost = rawUrl;
        
        const modal = document.getElementById('ollama-models-modal');
        if (!modal) return;

        document.getElementById('ollama-models-host').textContent = modelsHost;
        document.getElementById('ollama-pull-progress-container').classList.add('hidden');
        document.getElementById('ollama-custom-model-group').classList.add('hidden');
        document.getElementById('ollama-model-library-select').value = 'phi3:3.8b';
        
        modal.classList.remove('hidden');

        // Fetch models
        try {
          ui.renderOllamaLocalModels([]);
          const res = await api.fetchOllamaModels(modelsHost);
          ui.renderOllamaLocalModels(res.models);
        } catch (err) {
          ui.showToast(err.message, 'erro');
        }
      }
    });
  }

  const btnCloseOllamaModels = document.getElementById('btn-close-ollama-models');
  if (btnCloseOllamaModels) {
    btnCloseOllamaModels.addEventListener('click', () => {
      if (pullInterval) {
        clearInterval(pullInterval);
        pullInterval = null;
      }
      document.getElementById('ollama-models-modal')?.classList.add('hidden');
    });
  }

  // Preset model dropdown change
  const librarySelect = document.getElementById('ollama-model-library-select');
  const customModelGroup = document.getElementById('ollama-custom-model-group');
  if (librarySelect && customModelGroup) {
    librarySelect.addEventListener('change', (e) => {
      if (e.target.value === 'custom') {
        customModelGroup.classList.remove('hidden');
      } else {
        customModelGroup.classList.add('hidden');
      }
    });
  }

  // Pull model form submit
  const pullForm = document.getElementById('ollama-pull-model-form');
  if (pullForm) {
    pullForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const selectVal = librarySelect.value;
      const modelName = selectVal === 'custom' 
        ? document.getElementById('ollama-custom-model-input').value.trim()
        : selectVal;

      if (!modelName) {
        ui.showToast('Por favor, informe o Model ID.', 'erro');
        return;
      }

      const progressContainer = document.getElementById('ollama-pull-progress-container');
      const statusText = document.getElementById('ollama-pull-status-text');
      const percentText = document.getElementById('ollama-pull-percent-text');
      const progressBar = document.getElementById('ollama-pull-progress-bar');

      try {
        if (progressContainer) progressContainer.classList.remove('hidden');
        if (statusText) statusText.textContent = `Iniciando pull de ${modelName}...`;
        if (percentText) percentText.textContent = '0%';
        if (progressBar) progressBar.style.width = '0%';

        await api.pullModel(modelsHost, modelName);

        // Start progress polling
        if (pullInterval) clearInterval(pullInterval);
        pullInterval = setInterval(async () => {
          try {
            const res = await api.fetchPullProgress(modelsHost, modelName);
            if (statusText) statusText.textContent = res.status;
            if (percentText) percentText.textContent = `${res.percentage}%`;
            if (progressBar) progressBar.style.width = `${res.percentage}%`;

            if (res.done) {
              clearInterval(pullInterval);
              pullInterval = null;
              
              if (res.error) {
                ui.showToast(`Erro ao baixar modelo: ${res.error}`, 'erro');
                if (statusText) statusText.innerHTML = `<span style="color: var(--color-failed);">Download Falhou: ${res.error}</span>`;
              } else {
                ui.showToast(`Modelo ${modelName} baixado com sucesso!`, 'sucesso');
                // Refresh models list
                const listRes = await api.fetchOllamaModels(modelsHost);
                ui.renderOllamaLocalModels(listRes.models);
                setTimeout(() => {
                  progressContainer.classList.add('hidden');
                }, 2000);
              }
            }
          } catch (err) {
            clearInterval(pullInterval);
            pullInterval = null;
            ui.showToast(err.message, 'erro');
          }
        }, 1000);

      } catch (err) {
        ui.showToast(err.message, 'erro');
      }
    });
  }

  // Dynamic delegation for model shortcuts inside modal
  const localModelsList = document.getElementById('ollama-local-models-list');
  if (localModelsList) {
    localModelsList.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-use-model-shortcut')) {
        const modelName = e.target.getAttribute('data-model');
        const modelInput = document.getElementById('llm_model');
        if (modelInput) {
          modelInput.value = modelName;
          ui.showToast(`Modelo ${modelName} selecionado no formulário!`, 'sucesso');
        }
        document.getElementById('ollama-models-modal')?.classList.add('hidden');
      }
    });
  }
  
  // Quick Action Buttons for Ollama in LLM Server List Header
  const btnQuickOllamaInstaller = document.getElementById('btn-quick-ollama-installer');
  if (btnQuickOllamaInstaller) {
    btnQuickOllamaInstaller.addEventListener('click', () => {
      document.getElementById('btn-open-ollama-installer')?.click();
    });
  }

  const btnQuickOllamaModels = document.getElementById('btn-quick-ollama-models');
  if (btnQuickOllamaModels) {
    btnQuickOllamaModels.addEventListener('click', async () => {
      let rawUrl = 'http://localhost:11434';
      const providerSelect = document.getElementById('llm_provider');
      const urlInput = document.getElementById('llm_base_url');
      if (providerSelect && providerSelect.value === 'ollama' && urlInput && urlInput.value) {
        rawUrl = urlInput.value.trim();
      }
      
      if (rawUrl.endsWith('/v1/')) rawUrl = rawUrl.slice(0, -4);
      else if (rawUrl.endsWith('/v1')) rawUrl = rawUrl.slice(0, -3);
      
      modelsHost = rawUrl;
      
      const modal = document.getElementById('ollama-models-modal');
      if (!modal) return;

      document.getElementById('ollama-models-host').textContent = modelsHost;
      document.getElementById('ollama-pull-progress-container').classList.add('hidden');
      document.getElementById('ollama-custom-model-group').classList.add('hidden');
      document.getElementById('ollama-model-library-select').value = 'phi3:3.8b';
      
      modal.classList.remove('hidden');

      try {
        ui.renderOllamaLocalModels([]);
        const res = await api.fetchOllamaModels(modelsHost);
        ui.renderOllamaLocalModels(res.models);
      } catch (err) {
        ui.showToast(`Não foi possível conectar ao Ollama em ${modelsHost}. Certifique-se de que o serviço está ativo.`, 'erro');
      }
    });
  }
}
