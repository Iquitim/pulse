import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

export function setupConfigSocialEvents() {
  const platformSelect = document.getElementById('social-platform-select');
  if (platformSelect) {
    platformSelect.addEventListener('change', (e) => {
      const selected = e.target.value;
      document.querySelectorAll('.credentials-fields').forEach(group => {
        group.classList.add('hidden');
      });
      document.getElementById(`credentials-group-${selected}`)?.classList.remove('hidden');
      
      const submitBtn = document.getElementById('btn-submit-social-connect');
      if (submitBtn) {
        if (selected === 'twitter') {
          const connType = document.getElementById('twitter-conn-type')?.value || 'oauth2';
          if (connType === 'oauth2') {
            submitBtn.classList.add('hidden');
          } else {
            submitBtn.classList.remove('hidden');
          }
        } else if (selected === 'threads') {
          const connType = document.getElementById('threads-conn-type')?.value || 'oauth2';
          if (connType === 'oauth2') {
            submitBtn.classList.add('hidden');
          } else {
            submitBtn.classList.remove('hidden');
          }
        } else {
          submitBtn.classList.remove('hidden');
        }
      }
    });

    // Sincronizar o seletor visual de plataforma inicialmente
    ui.syncVisualSelector('social-platform-select', 'social-platform-selector');
  }

  // Click handler para o seletor visual de plataforma nas configurações de conexão
  document.querySelectorAll('.social-platform-selector .channel-option-card').forEach(card => {
    card.addEventListener('click', () => {
      const val = card.getAttribute('data-value');
      const select = document.getElementById('social-platform-select');
      if (select) {
        select.value = val;
        ui.syncVisualSelector('social-platform-select', 'social-platform-selector');
        select.dispatchEvent(new Event('change'));
      }
    });
  });

  const twitterConnType = document.getElementById('twitter-conn-type');
  if (twitterConnType) {
    twitterConnType.addEventListener('change', (e) => {
      const selected = e.target.value;
      document.querySelectorAll('.twitter-sub-fields').forEach(group => {
        group.classList.add('hidden');
      });
      document.getElementById(`twitter-sub-${selected}`)?.classList.remove('hidden');
      
      const submitBtn = document.getElementById('btn-submit-social-connect');
      if (submitBtn) {
        if (selected === 'oauth2') {
          submitBtn.classList.add('hidden');
        } else {
          submitBtn.classList.remove('hidden');
        }
      }
    });
  }

  const threadsConnType = document.getElementById('threads-conn-type');
  if (threadsConnType) {
    threadsConnType.addEventListener('change', (e) => {
      const selected = e.target.value;
      document.querySelectorAll('.threads-sub-fields').forEach(group => {
        group.classList.add('hidden');
      });
      document.getElementById(`threads-sub-${selected}`)?.classList.remove('hidden');
      
      const submitBtn = document.getElementById('btn-submit-social-connect');
      if (submitBtn) {
        if (selected === 'oauth2') {
          submitBtn.classList.add('hidden');
        } else {
          submitBtn.classList.remove('hidden');
        }
      }
    });
  }

  const btnConnectTwitter = document.getElementById('btn-connect-twitter');
  if (btnConnectTwitter) {
    btnConnectTwitter.addEventListener('click', () => {
      const handleInput = document.getElementById('social-handle-input');
      const handle = handleInput ? handleInput.value.trim() : '';
      if (!handle) {
        alert('Por favor, insira o Handle / Identificador da sua conta antes de iniciar a autorização.');
        if (handleInput) handleInput.focus();
        return;
      }
      
      const width = 600;
      const height = 750;
      const left = (window.innerWidth - width) / 2;
      const top = (window.innerHeight - height) / 2;
      const url = `/api/social/twitter/login?handle=${encodeURIComponent(handle)}&token=${encodeURIComponent(state.token)}`;
      
      const twitterPopup = window.open(
        url,
        'twitter-oauth',
        `width=${width},height=${height},left=${left},top=${top},status=no,resizable=yes,scrollbars=yes`
      );
      
      if (!twitterPopup) {
        alert('Pop-up bloqueado pelo navegador. Por favor, ative os pop-ups para esta página e tente novamente.');
      }
    });
  }

  const btnConnectThreads = document.getElementById('btn-connect-threads');
  if (btnConnectThreads) {
    btnConnectThreads.addEventListener('click', () => {
      const handleInput = document.getElementById('social-handle-input');
      const handle = handleInput ? handleInput.value.trim() : '';
      
      const width = 600;
      const height = 750;
      const left = (window.innerWidth - width) / 2;
      const top = (window.innerHeight - height) / 2;
      const url = `/api/social/threads/login?handle=${encodeURIComponent(handle)}&token=${encodeURIComponent(state.token)}`;
      
      const threadsPopup = window.open(
        url,
        'threads-oauth',
        `width=${width},height=${height},left=${left},top=${top},status=no,resizable=yes,scrollbars=yes`
      );
      
      if (!threadsPopup) {
        alert('Pop-up bloqueado pelo navegador. Por favor, ative os pop-ups para esta página e tente novamente.');
      }
    });
  }

  // Escuta mensagens do popup de autenticação do Twitter e Threads
  window.addEventListener('message', (event) => {
    if (event.origin !== window.location.origin) return;
    
    if (event.data === 'twitter_connected') {
      import('../logger.js').then(logger => {
        logger.addConsoleLog('Conta do Twitter / X conectada com sucesso via OAuth 2.0!', 'success');
      });
      api.fetchConnectedAccounts();
      api.fetchStatus();
      const handleInput = document.getElementById('social-handle-input');
      if (handleInput) handleInput.value = '';
    } else if (event.data === 'threads_connected') {
      import('../logger.js').then(logger => {
        logger.addConsoleLog('Conta do Threads conectada com sucesso via OAuth 2.0!', 'success');
      });
      api.fetchConnectedAccounts();
      api.fetchStatus();
      const handleInput = document.getElementById('social-handle-input');
      if (handleInput) handleInput.value = '';
    } else if (event.data && event.data.error) {
      import('../logger.js').then(logger => {
        logger.addConsoleLog(`Falha na autorização OAuth: ${event.data.error}`, 'error');
      });
    }
  });

  const socialConnectForm = document.getElementById('social-connect-form');
  if (socialConnectForm) {
    socialConnectForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const platform = platformSelect.value;
      const accountHandle = document.getElementById('social-handle-input').value.trim();
      
      let credentials = {};
      if (platform === "bluesky") {
        credentials = {
          handle: document.getElementById('bsky-username-input').value.trim(),
          password: document.getElementById('bsky-password-input').value.trim()
        };
      } else if (platform === "twitter") {
        const connType = document.getElementById('twitter-conn-type')?.value;
        if (connType === 'oauth2') return; // Handled by popup
        
        credentials = {
          api_key: document.getElementById('twitter-key-input')?.value.trim() || '',
          api_secret: document.getElementById('twitter-secret-input')?.value.trim() || '',
          access_token: document.getElementById('twitter-token-input')?.value.trim() || '',
          access_token_secret: document.getElementById('twitter-token-secret-input')?.value.trim() || ''
        };
      } else if (platform === "threads") {
        const connType = document.getElementById('threads-conn-type')?.value || 'oauth2';
        if (connType === 'oauth2') return; // Handled by popup

        credentials = {
          access_token: document.getElementById('threads-token-input')?.value.trim() || '',
          user_id: document.getElementById('threads-userid-input')?.value.trim() || undefined
        };
      }
      
      api.connectAccount(platform, accountHandle, credentials);
    });
  }

  const connectedAccountsList = document.getElementById('connected-accounts-list');
  if (connectedAccountsList) {
    connectedAccountsList.addEventListener('click', (e) => {
      if (e.target.classList.contains('btn-disconnect-account')) {
        const id = parseInt(e.target.getAttribute('data-id'), 10);
        if (confirm('Deseja realmente desconectar esta rede social?')) {
          api.disconnectAccount(id);
        }
      }
    });
  }
}
