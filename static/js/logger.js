// Logging utilities for the admin panel console
export function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const item = document.createElement('div');
  item.className = `toast-item toast-${type}`;
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  if (type === 'error') icon = '❌';
  if (type === 'warning') icon = '⚠️';

  item.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <span class="toast-message">${message}</span>
  `;

  container.appendChild(item);

  setTimeout(() => {
    item.classList.add('toast-fade-out');
    item.style.opacity = '0';
    item.style.transform = 'translateY(-15px) scale(0.95)';
    setTimeout(() => {
      item.remove();
      const checkContainer = document.querySelector('.toast-container');
      if (checkContainer && checkContainer.children.length === 0) {
        checkContainer.remove();
      }
    }, 200);
  }, 4000);
}

export function addConsoleLog(message, type = 'system') {
  const consoleOutput = document.getElementById('console-output');
  if (!consoleOutput) return;
  
  const line = document.createElement('div');
  line.className = 'terminal-line';
  
  const now = new Date();
  const timeStr = now.toTimeString().split(' ')[0];
  
  line.innerHTML = `
    <span class="log-time">[${timeStr}]</span>
    <span class="log-tag tag-${type}">${type}</span>
    <span class="log-msg ${type === 'sucesso' ? 'success-msg' : (type === 'erro' ? 'error-msg' : '')}">${message}</span>
  `;
  consoleOutput.appendChild(line);
  
  // Auto-scroll terminal container
  const terminalWrapper = consoleOutput.parentElement;
  if (terminalWrapper) {
    terminalWrapper.scrollTop = terminalWrapper.scrollHeight;
  }

  // Trigger Toast Notification automatically
  if (type === 'sucesso') {
    showToast(message, 'success');
  } else if (type === 'erro') {
    showToast(message, 'error');
  } else if (type === 'alerta') {
    showToast(message, 'warning');
  }
}

