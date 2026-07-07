let currentBskyStep = 1;

export function updateBskyTutorialStep(step) {
  currentBskyStep = step;
  // Hide all steps
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`bsky-step-${i}`);
    if (el) el.classList.add('hidden');
  }
  // Show active step
  const activeEl = document.getElementById(`bsky-step-${step}`);
  if (activeEl) activeEl.classList.remove('hidden');

  // Update dots
  const dots = document.querySelectorAll('#bsky-tutorial-modal .step-dot');
  dots.forEach(dot => {
    const s = parseInt(dot.getAttribute('data-step'));
    if (s === step) {
      dot.classList.add('active');
      dot.style.background = 'var(--color-ai)';
    } else {
      dot.classList.remove('active');
      dot.style.background = 'var(--border-color)';
    }
  });

  // Toggle button states
  const prevBtn = document.getElementById('btn-bsky-prev');
  const nextBtn = document.getElementById('btn-bsky-next');
  if (prevBtn) {
    prevBtn.disabled = step === 1;
    prevBtn.style.opacity = step === 1 ? '0.5' : '1';
  }
  if (nextBtn) {
    nextBtn.textContent = step === 4 ? 'Concluir' : 'Próximo';
  }
}

export function openBskyTutorial() {
  const modal = document.getElementById('bsky-tutorial-modal');
  if (!modal) return;
  updateBskyTutorialStep(1);
  modal.classList.remove('hidden');
}

export function closeBskyTutorial() {
  const modal = document.getElementById('bsky-tutorial-modal');
  if (modal) modal.classList.add('hidden');
}
