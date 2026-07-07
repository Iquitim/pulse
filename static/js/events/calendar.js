import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

export function setupCalendarEvents() {
  const btnOpenCalendarForm = document.getElementById('btn-open-calendar-form');
  const btnCloseCalendarForm = document.getElementById('btn-close-calendar-form');
  const calendarFormModal = document.getElementById('calendar-form-modal');
  const calendarItemForm = document.getElementById('calendar-item-form');
  const calendarFormTitle = document.getElementById('calendar-form-title');
  const calendarFormSubmitText = document.getElementById('calendar-form-submit-text');
  
  const manualSwitch = document.getElementById('calendar-is-manual');
  const manualTextarea = document.getElementById('calendar-manual-content');
  const manualCharCounter = document.getElementById('calendar-manual-char-counter');

  const toggleCalendarManualMode = (isManual) => {
    const aiGroup = document.getElementById('calendar-ai-group');
    const manualGroup = document.getElementById('calendar-manual-group');
    const themeInput = document.getElementById('calendar-theme');
    const subtitle = document.getElementById('calendar-mode-subtitle');
    
    if (isManual) {
      if (aiGroup) aiGroup.classList.add('hidden');
      if (manualGroup) manualGroup.classList.remove('hidden');
      if (themeInput) {
        themeInput.required = false;
        themeInput.removeAttribute('required');
      }
      if (manualTextarea) {
        manualTextarea.required = true;
        manualTextarea.setAttribute('required', 'required');
      }
      if (subtitle) subtitle.textContent = "Disparar post escrito manualmente (sem IA)";
    } else {
      if (aiGroup) aiGroup.classList.remove('hidden');
      if (manualGroup) manualGroup.classList.add('hidden');
      if (themeInput) {
        themeInput.required = true;
        themeInput.setAttribute('required', 'required');
      }
      if (manualTextarea) {
        manualTextarea.required = false;
        manualTextarea.removeAttribute('required');
      }
      if (subtitle) subtitle.textContent = "Gerar post automaticamente por IA";
    }
  };

  if (manualSwitch) {
    manualSwitch.addEventListener('change', (e) => {
      toggleCalendarManualMode(e.target.checked);
    });
  }

  if (manualTextarea && manualCharCounter) {
    manualTextarea.addEventListener('input', (e) => {
      const len = e.target.value.length;
      manualCharCounter.textContent = `${len}/280`;
      if (len <= 240) {
        manualCharCounter.className = 'char-badge limit-green';
      } else if (len > 240 && len <= 260) {
        manualCharCounter.className = 'char-badge limit-yellow';
      } else {
        manualCharCounter.className = 'char-badge limit-red';
      }
    });
  }

  if (btnOpenCalendarForm && calendarFormModal) {
    btnOpenCalendarForm.addEventListener('click', () => {
      // Reset form
      if (calendarItemForm) {
        calendarItemForm.reset();
        ui.syncVisualSelector('calendar-channel', 'calendar-channel-selector');
      }
      document.getElementById('calendar-item-id').value = '';
      if (calendarFormTitle) calendarFormTitle.textContent = "Agendar Nova Postagem";
      if (calendarFormSubmitText) calendarFormSubmitText.textContent = "Salvar Agendamento";

      if (manualSwitch) {
        manualSwitch.checked = false;
        toggleCalendarManualMode(false);
      }
      if (manualTextarea) {
        manualTextarea.value = '';
      }
      if (manualCharCounter) {
        manualCharCounter.textContent = '0/280';
        manualCharCounter.className = 'char-badge limit-green';
      }
      
      const displayDateInput = document.getElementById('calendar-date-display');
      const timeInput = document.getElementById('calendar-scheduled-time');
      if (displayDateInput && timeInput) {
        const now = new Date();
        now.setHours(now.getHours() + 1);
        now.setMinutes(0);
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        const hh = String(now.getHours()).padStart(2, '0');
        const min = String(now.getMinutes()).padStart(2, '0');
        displayDateInput.value = `${yyyy}-${mm}-${dd}`;
        displayDateInput.disabled = false;
        displayDateInput.style.opacity = "1";
        displayDateInput.style.cursor = "default";
        timeInput.value = `${hh}:${min}`;
      }
      
      calendarFormModal.classList.remove('hidden');
    });
  }
  
  if (btnCloseCalendarForm && calendarFormModal) {
    btnCloseCalendarForm.addEventListener('click', () => {
      calendarFormModal.classList.add('hidden');
    });
    
    calendarFormModal.addEventListener('click', (e) => {
      if (e.target === calendarFormModal) {
        calendarFormModal.classList.add('hidden');
      }
    });
  }
  
  if (calendarItemForm) {
    calendarItemForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const id = document.getElementById('calendar-item-id').value;
      const channel = document.getElementById('calendar-channel').value;
      const dateVal = document.getElementById('calendar-date-display').value;
      const timeVal = document.getElementById('calendar-scheduled-time').value;
      const isManual = !!manualSwitch?.checked;
      const theme = isManual ? "Uso Manual" : document.getElementById('calendar-theme').value.trim();
      const objective = isManual ? "" : document.getElementById('calendar-objective').value.trim();
      const cta = isManual ? "" : document.getElementById('calendar-cta').value.trim();
      const manualContent = isManual ? manualTextarea.value.trim() : "";
      
      const localDate = new Date(`${dateVal}T${timeVal}`);
      const isoDate = localDate.toISOString();
      
      let success = false;
      if (id) {
        success = await api.updateCalendarItem(id, theme, isoDate, objective, cta, channel, isManual, manualContent);
      } else {
        success = await api.createCalendarItem(theme, isoDate, objective, cta, channel, isManual, manualContent);
      }
      
      if (success) {
        calendarFormModal.classList.add('hidden');
        calendarItemForm.reset();
      }
    });
  }
  
  const calendarTimeline = document.getElementById('calendar-timeline');
  if (calendarTimeline) {
    calendarTimeline.addEventListener('click', async (e) => {
      const target = e.target;

      // Check for cell clicks to schedule new post
      const cell = target.closest('.calendar-board-cell');
      const isStickyNoteClick = target.closest('.calendar-sticky-note');

      if (cell && !cell.classList.contains('cell-disabled') && !isStickyNoteClick) {
        const year = parseInt(cell.getAttribute('data-year'), 10);
        const month = parseInt(cell.getAttribute('data-month'), 10);
        const day = parseInt(cell.getAttribute('data-day'), 10);
        ui.openCalendarFormForDate(year, month, day);
        return;
      }

      // If they clicked a sticky note (or something inside it), resolve the item id
      const idAttr = target.getAttribute('data-id') || target.closest('.calendar-sticky-note')?.getAttribute('data-id');
      if (!idAttr) return;
      const id = parseInt(idAttr, 10);
      const item = state.calendarItems.find(i => i.id === id);
      if (!item) return;

      if (target.classList.contains('btn-delete-calendar')) {
        if (confirm('Deseja realmente excluir este agendamento do calendário?')) {
          await api.deleteCalendarItem(id);
        }
      } else if (target.classList.contains('btn-edit-calendar') || target.classList.contains('calendar-sticky-note') || target.closest('.calendar-sticky-note')) {
        // Guard to avoid collision with deletion or production click targets
        if (target.classList.contains('btn-delete-calendar') || target.classList.contains('btn-produce-calendar')) return;

        document.getElementById('calendar-item-id').value = item.id;
        document.getElementById('calendar-channel').value = item.channel;
        ui.syncVisualSelector('calendar-channel', 'calendar-channel-selector');
        document.getElementById('calendar-theme').value = item.is_manual ? '' : item.theme;
        document.getElementById('calendar-objective').value = item.is_manual ? '' : (item.objective || '');
        document.getElementById('calendar-cta').value = item.is_manual ? '' : (item.cta || '');
        
        if (manualSwitch) {
          manualSwitch.checked = !!item.is_manual;
        }
        if (manualTextarea) {
          manualTextarea.value = item.is_manual ? (item.manual_content || '') : '';
        }
        if (manualCharCounter) {
          const len = manualTextarea ? manualTextarea.value.length : 0;
          manualCharCounter.textContent = `${len}/280`;
          if (len <= 240) {
            manualCharCounter.className = 'char-badge limit-green';
          } else if (len > 240 && len <= 260) {
            manualCharCounter.className = 'char-badge limit-yellow';
          } else {
            manualCharCounter.className = 'char-badge limit-red';
          }
        }
        toggleCalendarManualMode(!!item.is_manual);
        
        const localDate = new Date(item.scheduled_date);
        const yyyy = localDate.getFullYear();
        const mm = String(localDate.getMonth() + 1).padStart(2, '0');
        const dd = String(localDate.getDate()).padStart(2, '0');
        const hh = String(localDate.getHours()).padStart(2, '0');
        const min = String(localDate.getMinutes()).padStart(2, '0');
        
        const displayDateInput = document.getElementById('calendar-date-display');
        const timeInput = document.getElementById('calendar-scheduled-time');
        
        if (displayDateInput) {
          displayDateInput.value = `${yyyy}-${mm}-${dd}`;
          displayDateInput.disabled = true;
          displayDateInput.style.opacity = "0.7";
          displayDateInput.style.cursor = "not-allowed";
        }
        if (timeInput) timeInput.value = `${hh}:${min}`;
        
        if (calendarFormTitle) calendarFormTitle.textContent = "Editar Agendamento";
        if (calendarFormSubmitText) calendarFormSubmitText.textContent = "Atualizar Agendamento";
        if (calendarFormModal) calendarFormModal.classList.remove('hidden');
        
      } else if (target.classList.contains('btn-produce-calendar')) {
        const draftTextarea = document.getElementById('draft-text');
        if (draftTextarea) {
          draftTextarea.value = item.is_manual ? (item.manual_content || "") : ""; 
          state.currentDraftTheme = item.theme;
          
          const draftThemeSelect = document.getElementById('draft-theme-select');
          if (draftThemeSelect) {
            let exists = false;
            for (let option of draftThemeSelect.options) {
              if (option.value === item.theme) {
                exists = true;
                break;
              }
            }
            if (exists) {
              draftThemeSelect.value = item.theme;
            } else {
              const opt = document.createElement('option');
              opt.value = item.theme;
              opt.textContent = item.is_manual ? `✍️ ${item.theme}` : `📅 ${item.theme}`;
              draftThemeSelect.appendChild(opt);
              draftThemeSelect.value = item.theme;
            }
          }
          
          const draftChannelSelect = document.getElementById('draft-channel');
          if (draftChannelSelect && item.channel) {
            draftChannelSelect.value = item.channel;
            ui.syncVisualSelector('draft-channel', 'draft-channel-selector');
          }
          
          ui.updateCharCounter(draftTextarea.value.length);
          const btnPublishDraft = document.getElementById('btn-publish-draft');
          if (btnPublishDraft) btnPublishDraft.disabled = (draftTextarea.value.length === 0);
          const previewContent = document.getElementById('preview-content');
          if (previewContent) previewContent.textContent = draftTextarea.value || 'Digite ou gere algo no editor acima...';

          import('../logger.js').then(logger => {
            const msg = item.is_manual 
              ? `Conteúdo do post manual carregado no editor.` 
              : `Tema "${item.theme}" carregado a partir do calendário. Clique em 'Gerar Rascunho' para gerar o post com IA.`;
            logger.addConsoleLog(msg, 'system');
          });
        }
        
        state.activeCalendarItemId = item.id;
        ui.updateCalendarActiveIndicator();
        ui.switchTab('editor');
      }
    });
  }

  const schedulingModeSelect = document.getElementById('scheduling_mode');
  if (schedulingModeSelect) {
    schedulingModeSelect.addEventListener('change', (e) => {
      ui.toggleSchedulingModeUI(e.target.value);
      api.saveConfig();
    });
  }

  // Click handler for visual channel selector in Recurrent config
  document.querySelectorAll('.recurrent-channel-selector .channel-option-card').forEach(card => {
    card.addEventListener('click', () => {
      const val = card.getAttribute('data-value');
      const select = document.getElementById('recurrent-channel');
      if (select) {
        select.value = val;
        ui.syncVisualSelector('recurrent-channel', 'recurrent-channel-selector');
        api.saveConfig();
      }
    });
  });

  // Click handler for visual channel selector in Calendar form modal
  document.querySelectorAll('.calendar-channel-selector .channel-option-card').forEach(card => {
    card.addEventListener('click', () => {
      const val = card.getAttribute('data-value');
      const select = document.getElementById('calendar-channel');
      if (select) {
        select.value = val;
        ui.syncVisualSelector('calendar-channel', 'calendar-channel-selector');
      }
    });
  });

  // Click handler for visual channel selector in Editor tab
  document.querySelectorAll('.draft-channel-selector .channel-option-card').forEach(card => {
    card.addEventListener('click', () => {
      const val = card.getAttribute('data-value');
      const select = document.getElementById('draft-channel');
      if (select) {
        select.value = val;
        ui.syncVisualSelector('draft-channel', 'draft-channel-selector');
      }
    });
  });

  // Click handler for visual channel selector in Idea form
  document.querySelectorAll('.idea-channel-selector .channel-option-card').forEach(card => {
    card.addEventListener('click', () => {
      const val = card.getAttribute('data-value');
      const select = document.getElementById('idea-channel');
      if (select) {
        select.value = val;
        ui.syncVisualSelector('idea-channel', 'idea-channel-selector');
      }
    });
  });

  // Prev/Next Year buttons
  const btnPrevYear = document.getElementById('btn-prev-year');
  const btnNextYear = document.getElementById('btn-next-year');
  if (btnPrevYear) {
    btnPrevYear.addEventListener('click', () => {
      state.calendarYear = (state.calendarYear || new Date().getFullYear()) - 1;
      ui.renderCalendar();
      import('../logger.js').then(logger => {
        logger.addConsoleLog(`Exibindo calendário do ano ${state.calendarYear}.`, 'system');
      });
    });
  }
  if (btnNextYear) {
    btnNextYear.addEventListener('click', () => {
      state.calendarYear = (state.calendarYear || new Date().getFullYear()) + 1;
      ui.renderCalendar();
      import('../logger.js').then(logger => {
        logger.addConsoleLog(`Exibindo calendário do ano ${state.calendarYear}.`, 'system');
      });
    });
  }
}
