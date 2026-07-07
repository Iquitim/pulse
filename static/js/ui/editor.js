import { state } from '../state.js';

export function updateCalendarActiveIndicator() {
  const indicator = document.getElementById('calendar-active-indicator');
  if (indicator) {
    if (state.activeCalendarItemId) {
      indicator.classList.remove('hidden');
      indicator.title = "A publicação gerada será associada a este agendamento do calendário.";
    } else {
      indicator.classList.add('hidden');
    }
  }
}

export function updateDraftActiveIndicator() {
  const indicator = document.getElementById('draft-active-indicator');
  if (indicator) {
    if (state.activeDraftId) {
      indicator.classList.remove('hidden');
      indicator.title = "A publicação gerada substituirá o rascunho original.";
    } else {
      indicator.classList.add('hidden');
    }
  }
}

export function renderQualityAnalysis(analysis) {
  const loading = document.getElementById("quality-loading");
  const container = document.getElementById("quality-analysis-container");
  
  if (loading) loading.classList.add("hidden");
  if (!container) return;
  
  container.classList.remove("hidden");
  
  // Set overall score
  const overallScoreEl = document.getElementById("quality-overall-score");
  if (overallScoreEl) {
    overallScoreEl.textContent = analysis.score_geral || 0;
    const score = analysis.score_geral || 0;
    if (score >= 80) {
      overallScoreEl.style.borderColor = "var(--color-success)";
      overallScoreEl.style.color = "var(--color-success)";
    } else if (score >= 50) {
      overallScoreEl.style.borderColor = "var(--color-accent)";
      overallScoreEl.style.color = "var(--color-accent)";
    } else {
      overallScoreEl.style.borderColor = "var(--color-danger)";
      overallScoreEl.style.color = "var(--color-danger)";
    }
  }
  
  // Set overall label
  const overallLabelEl = document.getElementById("quality-overall-label");
  if (overallLabelEl) {
    const score = analysis.score_geral || 0;
    if (score >= 80) {
      overallLabelEl.textContent = "Excelente Qualidade";
      overallLabelEl.style.color = "var(--color-success)";
    } else if (score >= 60) {
      overallLabelEl.textContent = "Boa Qualidade";
      overallLabelEl.style.color = "var(--text-primary)";
    } else if (score >= 40) {
      overallLabelEl.textContent = "Qualidade Aceitável";
      overallLabelEl.style.color = "var(--text-secondary)";
    } else {
      overallLabelEl.textContent = "Qualidade Ruim";
      overallLabelEl.style.color = "var(--color-danger)";
    }
  }
  
  // Helper to update criteria progress
  const updateCriteria = (id, value, isLowBetter = false) => {
    const scoreEl = document.getElementById(`score-${id}`);
    const progressEl = document.getElementById(`progress-${id}`);
    if (scoreEl) scoreEl.textContent = `${value}%`;
    if (progressEl) {
      progressEl.style.width = `${value}%`;
      if (isLowBetter) {
        if (value < 30) {
          progressEl.style.backgroundColor = "var(--color-success)";
        } else if (value < 60) {
          progressEl.style.backgroundColor = "var(--color-warning)";
        } else {
          progressEl.style.backgroundColor = "var(--color-danger)";
        }
      } else {
        if (value >= 80) {
          progressEl.style.backgroundColor = "var(--color-success)";
        } else if (value >= 50) {
          progressEl.style.backgroundColor = "var(--color-accent)";
        } else {
          progressEl.style.backgroundColor = "var(--color-danger)";
        }
      }
    }
  };
  
  updateCriteria("clareza", analysis.clareza || 0);
  updateCriteria("gancho", analysis.gancho || 0);
  updateCriteria("especificidade", analysis.especificidade || 0);
  updateCriteria("generico", analysis.generico || 0, true);
  
  // Suggestions
  const suggestionsEl = document.getElementById("quality-suggestions");
  if (suggestionsEl) {
    suggestionsEl.innerHTML = "";
    const suggestions = analysis.sugestoes || [];
    if (suggestions.length === 0) {
      suggestionsEl.innerHTML = "<li style='list-style-type: none; margin-left: -1rem; color: var(--color-success); font-weight: 500;'>✨ Nenhuma sugestão! O post está perfeito.</li>";
    } else {
      suggestions.forEach(sug => {
        const li = document.createElement("li");
        li.textContent = sug;
        suggestionsEl.appendChild(li);
      });
    }
  }
}
