import { state } from '../state.js';
import * as api from '../api.js';
import * as ui from '../ui.js';

export function setupAuthEvents() {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const pass = document.getElementById('login-password').value.trim();
      api.loginUser(email, pass);
    });
  }

  const changePasswordForm = document.getElementById('change-password-form');
  if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const currentPass = document.getElementById('change-current-password').value;
      const newPass = document.getElementById('change-new-password').value;
      const confirmPass = document.getElementById('change-confirm-password').value;
      
      const errorDiv = document.getElementById("auth-error");
      const errorMsg = document.getElementById("auth-error-msg");
      
      if (newPass !== confirmPass) {
        if (errorDiv && errorMsg) {
          errorDiv.classList.remove("hidden");
          errorMsg.textContent = "As novas senhas não coincidem.";
        }
        return;
      }
      
      if (newPass.length < 6) {
        if (errorDiv && errorMsg) {
          errorDiv.classList.remove("hidden");
          errorMsg.textContent = "A nova senha deve ter pelo menos 6 caracteres.";
        }
        return;
      }
      
      api.changePassword(currentPass, newPass);
    });
  }

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('register-email').value.trim();
      const pass = document.getElementById('register-password').value.trim();
      const invite = document.getElementById('register-invite').value.trim();
      api.registerUser(email, pass, invite);
    });
  }

  const goToRegister = document.getElementById('go-to-register');
  const goToLogin = document.getElementById('go-to-login');
  if (goToRegister && goToLogin) {
    goToRegister.addEventListener('click', (e) => {
      e.preventDefault();
      document.getElementById('login-form').classList.add('hidden');
      document.getElementById('register-form').classList.remove('hidden');
      document.getElementById('auth-title').textContent = "Registrar no Pulse";
      document.getElementById('auth-error').classList.add('hidden');
    });

    goToLogin.addEventListener('click', (e) => {
      e.preventDefault();
      document.getElementById('register-form').classList.add('hidden');
      document.getElementById('login-form').classList.remove('hidden');
      document.getElementById('auth-title').textContent = "Entrar no Pulse";
      document.getElementById('auth-error').classList.add('hidden');
    });
  }

  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', api.logout);
  }

  // Change Password Modal handlers
  const changePasswordModal = document.getElementById('change-password-modal');
  const btnOpenChangePasswordModal = document.getElementById('btn-open-change-password-modal');
  const btnClosePasswordModal = document.getElementById('btn-close-password-modal');
  const userChangePasswordForm = document.getElementById('user-change-password-form');
  
  if (btnOpenChangePasswordModal && changePasswordModal) {
    btnOpenChangePasswordModal.addEventListener('click', () => {
      if (userChangePasswordForm) userChangePasswordForm.reset();
      changePasswordModal.classList.remove('hidden');
    });
  }
  
  if (btnClosePasswordModal && changePasswordModal) {
    btnClosePasswordModal.addEventListener('click', () => {
      changePasswordModal.classList.add('hidden');
    });
  }
  
  if (changePasswordModal) {
    changePasswordModal.addEventListener('click', (e) => {
      if (e.target === changePasswordModal) {
        changePasswordModal.classList.add('hidden');
      }
    });
  }
  
  if (userChangePasswordForm) {
    userChangePasswordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const currentPass = document.getElementById('user-current-password').value;
      const newPass = document.getElementById('user-new-password').value;
      const confirmPass = document.getElementById('user-confirm-password').value;
      
      if (newPass !== confirmPass) {
        ui.showToast('A nova senha e a confirmação não coincidem.', 'erro');
        return;
      }
      
      const success = await api.changePasswordSelf(currentPass, newPass);
      if (success) {
        userChangePasswordForm.reset();
        changePasswordModal.classList.add('hidden');
      }
    });
  }

  // --- Landing Page Event Listeners ---
  const btnLandingLogin = document.getElementById('btn-landing-login');
  const btnLandingRegister = document.getElementById('btn-landing-register');
  const btnHeroStart = document.getElementById('btn-hero-start');
  const btnHeroPlans = document.getElementById('btn-hero-plans');
  const landingThemeToggle = document.getElementById('landing-theme-toggle');
  
  if (btnLandingLogin) {
    btnLandingLogin.addEventListener('click', () => {
      document.getElementById('landing-page')?.classList.add('hidden');
      document.getElementById('auth-container')?.classList.remove('hidden');
      document.getElementById('login-form')?.classList.remove('hidden');
      document.getElementById('register-form')?.classList.add('hidden');
      document.getElementById('change-password-form')?.classList.add('hidden');
      document.getElementById('auth-title').textContent = "Entrar no Pulse";
      document.getElementById('auth-error')?.classList.add('hidden');
    });
  }

  if (btnLandingRegister) {
    btnLandingRegister.addEventListener('click', () => {
      document.getElementById('landing-page')?.classList.add('hidden');
      document.getElementById('auth-container')?.classList.remove('hidden');
      document.getElementById('login-form')?.classList.add('hidden');
      document.getElementById('register-form')?.classList.remove('hidden');
      document.getElementById('change-password-form')?.classList.add('hidden');
      document.getElementById('auth-title').textContent = "Criar Conta";
      document.getElementById('auth-error')?.classList.add('hidden');
    });
  }

  if (btnHeroStart) {
    btnHeroStart.addEventListener('click', () => {
      document.getElementById('landing-page')?.classList.add('hidden');
      document.getElementById('auth-container')?.classList.remove('hidden');
      document.getElementById('login-form')?.classList.add('hidden');
      document.getElementById('register-form')?.classList.remove('hidden');
      document.getElementById('change-password-form')?.classList.add('hidden');
      document.getElementById('auth-title').textContent = "Criar Conta";
      document.getElementById('auth-error')?.classList.add('hidden');
    });
  }

  if (btnHeroPlans) {
    btnHeroPlans.addEventListener('click', () => {
      document.getElementById('pricing-section')?.scrollIntoView({ behavior: 'smooth' });
    });
  }

  document.querySelectorAll('.btn-price-action').forEach(btn => {
    btn.addEventListener('click', () => {
      const tier = btn.getAttribute('data-tier');
      document.getElementById('landing-page')?.classList.add('hidden');
      document.getElementById('auth-container')?.classList.remove('hidden');
      document.getElementById('login-form')?.classList.add('hidden');
      document.getElementById('register-form')?.classList.remove('hidden');
      document.getElementById('change-password-form')?.classList.add('hidden');
      document.getElementById('auth-title').textContent = "Criar Conta";
      document.getElementById('auth-error')?.classList.add('hidden');
      
      const inviteInput = document.getElementById('register-invite');
      if (inviteInput && state.publicSettings.require_invite_code) {
        inviteInput.placeholder = `INSIRA O CONVITE DO PERFIL ${tier.toUpperCase()}`;
        inviteInput.focus();
      } else {
        document.getElementById('register-email')?.focus();
      }
    });
  });

  if (landingThemeToggle) {
    landingThemeToggle.addEventListener('click', () => {
      const isLight = document.documentElement.classList.toggle('light-theme');
      localStorage.setItem('pulse_theme', isLight ? 'light' : 'dark');
    });
  }
}
