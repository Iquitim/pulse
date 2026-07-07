import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

export function setupEditorEvents() {
  const draftTextarea = document.getElementById('draft-text');
  const btnPublishDraft = document.getElementById('btn-publish-draft');
  const previewContent = document.getElementById('preview-content');

  if (draftTextarea) {
    draftTextarea.addEventListener('input', (e) => {
      const text = e.target.value;
      const len = text.length;
      ui.updateCharCounter(len);
      if (btnPublishDraft) btnPublishDraft.disabled = (len === 0);
      if (previewContent) previewContent.textContent = text || 'Digite ou gere algo no editor acima...';
    });
  }
  
  const btnCopyDraft = document.getElementById('btn-copy-draft');
  if (btnCopyDraft && draftTextarea) {
    btnCopyDraft.addEventListener('click', () => {
      const txt = draftTextarea.value;
      if (txt) {
        navigator.clipboard.writeText(txt);
        import('../logger.js').then(logger => {
          logger.addConsoleLog('Texto do rascunho copiado.', 'system');
        });
      }
    });
  }
  
  const btnGenerateDraft = document.getElementById('btn-generate-draft');
  if (btnGenerateDraft) {
    btnGenerateDraft.addEventListener('click', () => api.generateDraft());
  }

  const btnUnlinkIdea = document.getElementById('btn-unlink-idea');
  if (btnUnlinkIdea) {
    btnUnlinkIdea.addEventListener('click', (e) => {
      e.stopPropagation();
      state.currentIdeaText = null;
      document.getElementById('idea-active-indicator')?.classList.add('hidden');
      
      // Remove temporary option from theme select
      const themeSelect = document.getElementById('draft-theme-select');
      if (themeSelect) {
        const ideaOption = themeSelect.querySelector('option[value="idea_convert"]');
        if (ideaOption) {
          ideaOption.remove();
        }
        themeSelect.value = 'random';
      }
      
      import('../logger.js').then(logger => {
        logger.addConsoleLog('Ideia desvinculada do editor.', 'system');
      });
    });
  }

  const btnUnlinkDraft = document.getElementById('btn-unlink-draft');
  if (btnUnlinkDraft) {
    btnUnlinkDraft.addEventListener('click', (e) => {
      e.stopPropagation();
      state.activeDraftId = null;
      ui.updateDraftActiveIndicator();
      import('../logger.js').then(logger => {
        logger.addConsoleLog('Rascunho desvinculado do editor.', 'system');
      });
    });
  }
  
  if (btnPublishDraft) {
    btnPublishDraft.addEventListener('click', api.publishDraft);
  }

  document.getElementById('helper-improve')?.addEventListener('click', () => api.runAIHelper('improve'));
  document.getElementById('helper-shorten')?.addEventListener('click', () => api.runAIHelper('shorten'));
  document.getElementById('helper-technical')?.addEventListener('click', () => api.runAIHelper('technical'));
  document.getElementById('helper-funny')?.addEventListener('click', () => api.runAIHelper('funny'));

  const btnAnalyzeQuality = document.getElementById('btn-analyze-quality');
  if (btnAnalyzeQuality) {
    btnAnalyzeQuality.addEventListener('click', async () => {
      const draftTextarea = document.getElementById('draft-text');
      if (!draftTextarea || !draftTextarea.value.trim()) {
        ui.showToast('Escreva ou gere um post primeiro para poder avaliar.', 'erro');
        return;
      }
      
      const toneVal = state.appConfig.tone || 'informativo';
      await api.analyzePostQuality(draftTextarea.value.trim(), toneVal);
    });
  }
}
