import * as ui from '../ui.js';

export function setupTutorialEvents() {
  // --- Bluesky Tutorial Redirection to Instructions ---
  const btnBskyTutorial = document.getElementById('btn-bsky-tutorial');
  if (btnBskyTutorial) {
    btnBskyTutorial.addEventListener('click', (e) => {
      e.preventDefault();
      ui.switchTab('instructions');
      
      // Highlight the correct menu button in instructions tab
      document.querySelectorAll('.doc-menu-btn').forEach(btn => {
        if (btn.getAttribute('data-target') === 'section-bluesky') {
          btn.classList.add('active');
          btn.style.color = 'var(--text-primary)';
        } else {
          btn.classList.remove('active');
          btn.style.color = 'var(--text-secondary)';
        }
      });
      
      setTimeout(() => {
        document.getElementById('section-bluesky')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    });
  }

  const btnCloseBskyTutorial = document.getElementById('btn-close-bsky-tutorial');
  if (btnCloseBskyTutorial) {
    btnCloseBskyTutorial.addEventListener('click', ui.closeBskyTutorial);
  }

  let tutorialStep = 1;
  const btnBskyNext = document.getElementById('btn-bsky-next');
  const btnBskyPrev = document.getElementById('btn-bsky-prev');

  if (btnBskyNext) {
    btnBskyNext.addEventListener('click', () => {
      if (tutorialStep < 4) {
        tutorialStep++;
        ui.updateBskyTutorialStep(tutorialStep);
      } else {
        ui.closeBskyTutorial();
      }
    });
  }

  if (btnBskyPrev) {
    btnBskyPrev.addEventListener('click', () => {
      if (tutorialStep > 1) {
        tutorialStep--;
        ui.updateBskyTutorialStep(tutorialStep);
      }
    });
  }
}
