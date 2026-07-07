import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

export function setupLibraryEvents() {
  const historyTbody = document.getElementById('history-tbody');
  const previewHandle = document.getElementById('preview-handle');
  const modalTheme = document.getElementById('modal-theme');
  const modalDate = document.getElementById('modal-date');
  const modalStatus = document.getElementById('modal-status');
  const modalAuthorHandle = document.getElementById('modal-author-handle');
  const modalContent = document.getElementById('modal-content');
  const modalErrorBox = document.getElementById('modal-error-box');
  const modalErrorMessage = document.getElementById('modal-error-message');
  const postModal = document.getElementById('post-modal');
  const btnPublishDraft = document.getElementById('btn-publish-draft');
  const previewContent = document.getElementById('preview-content');

  if (historyTbody) {
    historyTbody.addEventListener('click', async (e) => {
      const target = e.target;
      const index = parseInt(target.getAttribute('data-index'), 10);
      const post = state.postHistory[index];
      if (!post) return;
      
      if (target.classList.contains('btn-view-post')) {
        if (modalTheme) modalTheme.textContent = post.theme || 'N/A';
        if (modalDate) modalDate.textContent = new Date(post.timestamp).toLocaleString('pt-BR');
        
        let statusText = 'Publicado';
        if (post.status === 'failed') statusText = 'Erro';
        else if (post.status === 'draft') statusText = 'Rascunho';
        
        if (modalStatus) {
          modalStatus.textContent = statusText;
          modalStatus.className = `status-pill ${post.status === 'success' ? 'success' : (post.status === 'failed' ? 'failed' : 'draft')}`;
        }
        
        if (modalAuthorHandle) modalAuthorHandle.textContent = previewHandle?.textContent || '@usuario.bsky.social';
        if (modalContent) modalContent.textContent = post.content || 'Nenhum conteúdo gerado devido a uma falha.';
        
        if (post.status === 'failed' && post.error) {
          if (modalErrorBox) modalErrorBox.classList.remove('hidden');
          if (modalErrorMessage) modalErrorMessage.textContent = post.error;
        } else {
          if (modalErrorBox) modalErrorBox.classList.add('hidden');
        }
        
        const modalMetricsContainer = document.getElementById('modal-metrics-container');
        const modalLikes = document.getElementById('modal-likes');
        const modalReposts = document.getElementById('modal-reposts');
        const modalReplies = document.getElementById('modal-replies');
        if (post.status === 'success') {
          if (modalLikes) modalLikes.textContent = `❤️ ${post.likes || 0}`;
          if (modalReposts) modalReposts.textContent = `🔁 ${post.reposts || 0}`;
          if (modalReplies) modalReplies.textContent = `💬 ${post.replies || 0}`;
          if (modalMetricsContainer) modalMetricsContainer.classList.remove('hidden');
        } else {
          if (modalMetricsContainer) modalMetricsContainer.classList.add('hidden');
        }
        
        if (postModal) postModal.classList.remove('hidden');
        
      } else if (target.classList.contains('btn-edit-post') || target.classList.contains('btn-reuse-post')) {
        const draftTextarea = document.getElementById('draft-text');
        if (draftTextarea) {
          draftTextarea.value = post.content || '';
          state.currentDraftTheme = post.theme || 'Geral';
          
          if (target.classList.contains('btn-edit-post')) {
            state.activeDraftId = post.id;
          } else {
            state.activeDraftId = null;
          }
          ui.updateDraftActiveIndicator();
          
          const draftThemeSelect = document.getElementById('draft-theme-select');
          if (draftThemeSelect && state.appConfig.themes.includes(state.currentDraftTheme)) {
            draftThemeSelect.value = state.currentDraftTheme;
          }
          
          ui.updateCharCounter(draftTextarea.value.length);
          if (btnPublishDraft) btnPublishDraft.disabled = (draftTextarea.value.length === 0);
          if (previewContent) previewContent.textContent = draftTextarea.value || 'Digite ou gere algo no editor acima...';
        }
        
        import('../logger.js').then(logger => {
          logger.addConsoleLog('Post carregado no editor de rascunhos.', 'system');
        });
        ui.switchTab('editor');
        
      } else if (target.classList.contains('btn-approve-post')) {
        await api.approvePost(post, target);
      }
    });
  }

  // Modals closing handlers
  const btnCloseModal = document.getElementById('btn-close-modal');
  if (btnCloseModal && postModal) {
    btnCloseModal.addEventListener('click', () => {
      postModal.classList.add('hidden');
    });
  }
  
  if (postModal) {
    postModal.addEventListener('click', (e) => {
      if (e.target === postModal) {
        postModal.classList.add('hidden');
      }
    });
  }

  // --- Ideas Sub-tab navigation ---
  document.querySelectorAll('.sub-tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const subtab = btn.getAttribute('data-subtab');
      state.activeLibrarySubTab = subtab;
      
      // Update buttons active class
      document.querySelectorAll('.sub-tab-btn').forEach(b => {
        b.classList.remove('active');
        b.style.borderBottomColor = 'transparent';
        b.style.color = 'var(--text-secondary)';
      });
      btn.classList.add('active');
      btn.style.borderBottomColor = 'var(--color-accent)';
      btn.style.color = 'var(--text-primary)';
      
      // Update panels active class
      document.querySelectorAll('.sub-tab-panel-content').forEach(p => p.classList.add('hidden'));
      const activePanel = document.getElementById(`subpanel-${subtab}`);
      if (activePanel) activePanel.classList.remove('hidden');
      
      if (subtab === 'ideas') {
        api.fetchIdeas();
      }
    });
  });

  // --- Create New Idea Form ---
  const formNewIdea = document.getElementById('form-new-idea');
  if (formNewIdea) {
    formNewIdea.addEventListener('submit', async (e) => {
      e.preventDefault();
      const titleInput = document.getElementById('idea-title');
      const descInput = document.getElementById('idea-description');
      if (!titleInput || !descInput) return;
      
      const title = titleInput.value.trim();
      const desc = descInput.value.trim();
      const channelSelect = document.getElementById('idea-channel');
      const channel = channelSelect ? channelSelect.value : 'bluesky';
      
      try {
        await api.createIdea(title, desc, channel);
        titleInput.value = '';
        descInput.value = '';
        ui.showToast('Ideia salva com sucesso!', 'sucesso');
      } catch (err) {
        ui.showToast('Erro ao salvar ideia.', 'erro');
      }
    });
  }

  // --- Ideas list events delegation ---
  const ideasList = document.getElementById('ideas-list');
  if (ideasList) {
    ideasList.addEventListener('click', async (e) => {
      const target = e.target;
      if (target.classList.contains('btn-delete-idea')) {
        const id = parseInt(target.getAttribute('data-id'), 10);
        if (confirm('Deseja realmente excluir esta ideia?')) {
          await api.deleteIdea(id);
          ui.showToast('Ideia excluída.', 'sucesso');
        }
      } else if (target.classList.contains('btn-convert-idea')) {
        const id = parseInt(target.getAttribute('data-id'), 10);
        const desc = decodeURIComponent(target.getAttribute('data-desc'));
        
        // Mark as converted in backend
        try {
          await api.updateIdeaStatus(id, 'converted');
        } catch (err) {
          console.error('Erro ao marcar ideia como convertida:', err);
        }
        
        const channel = target.getAttribute('data-channel') || 'bluesky';
        const select = document.getElementById('draft-channel');
        if (select) {
          select.value = channel;
          ui.syncVisualSelector('draft-channel', 'draft-channel-selector');
        }

        // Set the active tab in navigation
        const editorTabBtn = document.querySelector('.tab-btn[data-tab="editor"]');
        if (editorTabBtn) {
          editorTabBtn.click();
        }
        
        // Trigger generator with this idea
        setTimeout(() => {
          api.generateDraft(desc);
        }, 100);
      }
    });
  }

  // --- Refresh Insights ---
  const btnRefreshInsights = document.getElementById('btn-refresh-insights');
  if (btnRefreshInsights) {
    btnRefreshInsights.addEventListener('click', async () => {
      await api.fetchMetricsInsights();
      ui.showToast('Insights recalculados com sucesso!', 'sucesso');
    });
  }
}
