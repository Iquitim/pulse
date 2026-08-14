import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

export function fillLLMServerForm(server) {
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

export function resetLLMServerForm() {
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

export function setupConfigLLMEvents() {
  // Initialize LLM server form defaults
  resetLLMServerForm();

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
}
