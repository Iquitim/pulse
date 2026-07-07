export function renderOllamaDiagnostic(data) {
  const ramEl = document.getElementById('diag-ram-val');
  const cpuEl = document.getElementById('diag-cpu-val');
  const gpuEl = document.getElementById('diag-gpu-val');
  const diskEl = document.getElementById('diag-disk-val');
  const tierEl = document.getElementById('diag-tier-val');
  const recNameEl = document.getElementById('diag-rec-model-name');
  const recReasonEl = document.getElementById('diag-rec-reason');
  const modelsContainer = document.getElementById('diag-models-list');

  if (ramEl) ramEl.textContent = `${data.ram_gb} GB`;
  if (cpuEl) cpuEl.textContent = `${data.cpu_cores} núcleos lógicos`;
  
  if (gpuEl) {
    if (data.apple_silicon) {
      gpuEl.innerHTML = `<span style="color: var(--color-success); font-weight: bold;">🍎 Apple Silicon (M-Series GPU)</span>`;
    } else if (data.gpu) {
      gpuEl.innerHTML = `<span style="color: var(--color-success); font-weight: bold;">🟢 NVIDIA ${data.gpu.name} (${data.gpu.vram_gb}GB VRAM)</span>`;
    } else {
      gpuEl.textContent = 'Apenas CPU (Sem aceleração dedicada)';
    }
  }

  if (diskEl) {
    const isDiskOk = data.disk_free_gb >= 5;
    diskEl.innerHTML = `<span style="color: ${isDiskOk ? 'var(--color-success)' : 'var(--color-danger)'}; font-weight: bold;">${data.disk_free_gb} GB livres</span>`;
  }

  if (tierEl) {
    const tierColors = {
      Critico: 'var(--color-danger)',
      Low: 'var(--color-warning)',
      Mid: 'var(--color-accent)',
      High: 'var(--color-ai)',
      Ultra: 'var(--color-success)'
    };
    tierEl.innerHTML = `<span style="color: ${tierColors[data.tier] || 'var(--text-primary)'};">${data.tier.toUpperCase()}</span> · <span style="font-weight: normal; font-size: 0.7rem; color: var(--text-secondary);">${data.reason}</span>`;
  }

  if (recNameEl) recNameEl.textContent = data.recommended_model;
  if (recReasonEl) recReasonEl.textContent = data.recommended_reason;

  if (modelsContainer) {
    modelsContainer.innerHTML = '';
    data.models.forEach(m => {
      const row = document.createElement('div');
      row.className = 'model-row-item';
      
      const badgeClass = m.status === 'excellent' ? 'perf-excellent' : (m.status === 'good' ? 'perf-good' : (m.status === 'slow' ? 'perf-slow' : 'perf-unsupported'));
      
      row.innerHTML = `
        <div>
          <strong style="color: var(--text-primary); font-size: 0.8rem;">${m.name}</strong>
          <span style="font-size: 0.65rem; color: var(--text-muted); margin-left: 0.25rem;">(${m.size})</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span style="font-size: 0.7rem; color: var(--text-secondary);">${m.speed_label}</span>
          <span class="perf-badge ${badgeClass}">${m.status_label}</span>
        </div>
      `;
      modelsContainer.appendChild(row);
    });
  }
}

export function updateOllamaInstallProgress(percentage, bytesStr, statusMsg, isError = false) {
  const progressBar = document.getElementById('ollama-install-progress-bar');
  const percentText = document.getElementById('ollama-install-progress-percent');
  const bytesText = document.getElementById('ollama-install-progress-bytes');
  const statusConsole = document.getElementById('ollama-install-status-console');
  const retryBtn = document.getElementById('btn-retry-ollama-install');
  
  if (progressBar) progressBar.style.width = `${percentage}%`;
  if (percentText) percentText.textContent = `${percentage}%`;
  if (bytesText) bytesText.textContent = bytesStr;
  
  if (statusConsole) {
    if (isError) {
      statusConsole.innerHTML = `<span style="color: var(--color-danger); font-weight: bold;">Erro: ${statusMsg}</span>`;
      if (retryBtn) retryBtn.classList.remove('hidden');
    } else {
      statusConsole.innerHTML = statusMsg;
      if (retryBtn) retryBtn.classList.add('hidden');
    }
  }
}

export function renderOllamaLocalModels(modelsList) {
  const container = document.getElementById('ollama-local-models-list');
  if (!container) return;
  container.innerHTML = '';
  
  if (!modelsList || modelsList.length === 0) {
    container.innerHTML = `
      <div style="color: var(--text-muted); font-size: 0.75rem; text-align: center; padding: 1rem;">
        Nenhum modelo baixado neste servidor ainda.
      </div>
    `;
    return;
  }
  
  modelsList.forEach(m => {
    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.justifyContent = 'space-between';
    row.style.alignItems = 'center';
    row.style.padding = '0.45rem 0.6rem';
    row.style.borderBottom = '1px solid var(--border-color)';
    row.style.fontSize = '0.75rem';
    row.style.color = 'var(--text-primary)';
    row.style.background = 'var(--bg-surface-elevated)';
    row.style.borderRadius = 'var(--radius-sm)';
    row.style.marginBottom = '0.35rem';
    
    row.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <span style="color: var(--color-success);">●</span>
        <strong>${m}</strong>
      </div>
      <button class="btn-use-model-shortcut" data-model="${m}" style="color: var(--color-accent); font-size: 0.7rem; font-weight: bold; background: none; border: none; cursor: pointer; padding: 0;">Usar no editor</button>
    `;
    container.appendChild(row);
  });
}
