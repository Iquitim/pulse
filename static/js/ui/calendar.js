import { state } from '../state.js';
import { syncVisualSelector } from './common.js';

export function openCalendarFormForDate(year, month, day) {
  const calendarItemForm = document.getElementById('calendar-item-form');
  const calendarFormModal = document.getElementById('calendar-form-modal');
  const calendarFormTitle = document.getElementById('calendar-form-title');
  const calendarFormSubmitText = document.getElementById('calendar-form-submit-text');
  
  if (calendarItemForm) {
    calendarItemForm.reset();
    syncVisualSelector('calendar-channel', 'calendar-channel-selector');
    const manualSwitch = document.getElementById('calendar-is-manual');
    if (manualSwitch) {
      manualSwitch.checked = false;
      manualSwitch.dispatchEvent(new Event('change'));
    }
  }
  document.getElementById('calendar-item-id').value = '';
  if (calendarFormTitle) calendarFormTitle.textContent = "Agendar Nova Postagem";
  if (calendarFormSubmitText) calendarFormSubmitText.textContent = "Salvar Agendamento";
  
  const displayDateInput = document.getElementById('calendar-date-display');
  const timeInput = document.getElementById('calendar-scheduled-time');
  if (displayDateInput && timeInput) {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const min = String(now.getMinutes()).padStart(2, '0');
    const mm = String(month).padStart(2, '0');
    const dd = String(day).padStart(2, '0');
    displayDateInput.value = `${year}-${mm}-${dd}`;
    displayDateInput.disabled = true;
    displayDateInput.style.opacity = "0.7";
    displayDateInput.style.cursor = "not-allowed";
    timeInput.value = `${hh}:${min}`;
  }
  
  if (calendarFormModal) calendarFormModal.classList.remove('hidden');
}

export function renderCalendar() {
  const year = state.calendarYear || new Date().getFullYear();
  const yearDisplay = document.getElementById('calendar-year-display');
  if (yearDisplay) yearDisplay.textContent = year;

  // Get today's date at midnight for comparison
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // Render header weekdays (Seg to Dom repeated 6 times = 42 columns)
  const headerRow = document.getElementById('calendar-header-weekdays');
  if (headerRow) {
    headerRow.innerHTML = '';
    
    // First cell (sticky) is the top-left corner label
    const thMonth = document.createElement('th');
    thMonth.className = 'month-header-cell';
    thMonth.style.height = '40px';
    thMonth.textContent = 'Mês';
    headerRow.appendChild(thMonth);
    
    const weekDays = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
    for (let i = 0; i < 42; i++) {
      const th = document.createElement('th');
      th.className = 'weekday-header-cell';
      th.textContent = weekDays[i % 7];
      headerRow.appendChild(th);
    }
  }

  const tbody = document.getElementById('calendar-board-tbody');
  if (!tbody) return;
  tbody.innerHTML = '';

  const monthNames = [
    'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
  ];

  for (let m = 0; m < 12; m++) {
    const tr = document.createElement('tr');
    
    // Month label cell (sticky left)
    const tdMonth = document.createElement('td');
    tdMonth.className = 'month-header-cell';
    tdMonth.textContent = monthNames[m];
    tr.appendChild(tdMonth);
    
    // Calculate start offset (0 = Mon, 1 = Tue, ..., 6 = Sun)
    const firstDay = new Date(year, m, 1);
    const startOffset = (firstDay.getDay() + 6) % 7;
    const daysInMonth = new Date(year, m + 1, 0).getDate();
    
    for (let col = 0; col < 42; col++) {
      const td = document.createElement('td');
      
      if (col < startOffset || col >= startOffset + daysInMonth) {
        td.className = 'calendar-board-cell cell-disabled';
      } else {
        const dayNum = col - startOffset + 1;
        const cellDate = new Date(year, m, dayNum);
        
        td.className = 'calendar-board-cell';
        if (cellDate < today) {
          td.classList.add('cell-past');
        }
        
        td.setAttribute('data-year', year);
        td.setAttribute('data-month', m + 1);
        td.setAttribute('data-day', dayNum);
        
        // Corner day label
        const dayLabel = document.createElement('div');
        dayLabel.className = 'cell-day-number';
        dayLabel.textContent = dayNum;
        td.appendChild(dayLabel);
        
        // Filter events on this specific date in local timezone parts
        const cellEvents = state.calendarItems.filter(item => {
          const itemDate = new Date(item.scheduled_date);
          return itemDate.getFullYear() === year &&
                 itemDate.getMonth() === m &&
                 itemDate.getDate() === dayNum;
        });
        
        // Sort cell events by time
        cellEvents.sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date));
        
        // Render events
        if (cellEvents.length > 0) {
          const notesContainer = document.createElement('div');
          notesContainer.className = 'cell-notes-container';
          
          cellEvents.forEach(item => {
            const itemDate = new Date(item.scheduled_date);
            const timeStr = itemDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            
            const note = document.createElement('div');
            note.className = `calendar-sticky-note ${item.channel}`;
            note.setAttribute('data-id', item.id);
            
            let statusDotClass = `status-${item.status}`;
            
            let actionBtnHtml = '';
            if (item.status === 'planejado') {
              actionBtnHtml = `
                <button type="button" class="btn-sticky-action btn-produce-calendar" data-id="${item.id}" title="Produzir Rascunho">✍️</button>
              `;
            }
            
            note.innerHTML = `
              <div class="sticky-time">
                <span>${timeStr}</span>
                <span class="sticky-status-dot ${statusDotClass}" title="${item.status}"></span>
              </div>
              <div class="sticky-theme" title="${item.theme}">${item.theme}</div>
              <div class="sticky-actions">
                ${actionBtnHtml}
                <button type="button" class="btn-sticky-action btn-edit-calendar" data-id="${item.id}" title="Editar">⚙️</button>
                <button type="button" class="btn-sticky-action btn-delete-calendar" data-id="${item.id}" title="Excluir">❌</button>
              </div>
            `;
            
            notesContainer.appendChild(note);
          });
          td.appendChild(notesContainer);
        }
      }
      
      tr.appendChild(td);
    }
    
    tbody.appendChild(tr);
  }
}
