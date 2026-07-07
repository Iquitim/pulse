import { showToast } from '../logger.js';

export function updateConnectionBadge(elementId, status, label) {
  const element = document.getElementById(elementId);
  if (!element) return;
  element.className = `api-badge badge-${status}`;
  element.querySelector('span:last-child').textContent = label;
}

export function formatCountdown(ms) {
  if (ms <= 0) return '00:00:00';
  const totalSecs = Math.floor(ms / 1000);
  const hours = Math.floor(totalSecs / 3600);
  const minutes = Math.floor((totalSecs % 3600) / 60);
  const seconds = totalSecs % 60;
  const pad = (num) => String(num).padStart(2, '0');
  return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

export function updateFrequencyEstimateText(hours) {
  const frequencyEstimate = document.getElementById('frequency-estimate');
  if (!frequencyEstimate) return;
  const val = parseInt(hours, 10);
  if (val === 1) {
    frequencyEstimate.textContent = 'O Pulse publicará cerca de 24 posts por dia.';
  } else if (val === 2) {
    frequencyEstimate.textContent = 'O Pulse publicará cerca de 12 posts por dia.';
  } else {
    const times = Math.round(24 / val);
    frequencyEstimate.textContent = `O Pulse publicará cerca de ${times} ${times === 1 ? 'post' : 'posts'} por dia.`;
  }
}

export function updateCharCounter(length) {
  const draftCharCounter = document.getElementById('draft-char-counter');
  if (!draftCharCounter) return;
  draftCharCounter.textContent = `${length}/280`;
  
  if (length <= 240) {
    draftCharCounter.className = 'char-badge limit-green';
  } else if (length > 240 && length <= 260) {
    draftCharCounter.className = 'char-badge limit-yellow';
  } else {
    draftCharCounter.className = 'char-badge limit-red';
  }
}

export function syncPresetButtons(val) {
  document.querySelectorAll('.btn-preset').forEach(btn => {
    if (parseInt(btn.getAttribute('data-value'), 10) === parseInt(val, 10)) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

export function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  document.querySelectorAll('.tab-panel').forEach(panel => {
    if (panel.id === `tab-${tabId}`) {
      panel.classList.add('active');
    } else {
      panel.classList.remove('active');
    }
  });

  localStorage.setItem('pulse_active_tab', tabId);
}

export function syncVisualSelector(selectId, groupClass) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const cards = document.querySelectorAll(`.${groupClass} .channel-option-card`);
  cards.forEach(card => {
    if (card.getAttribute('data-value') === select.value) {
      card.classList.add('active');
    } else {
      card.classList.remove('active');
    }
  });
}

export { showToast };
