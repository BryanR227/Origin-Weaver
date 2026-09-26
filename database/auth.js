// auth.js — wires the sign in / sign up dialog to the backend auth API.
// Add <script src="auth.js"></script> in index.html, after chat.js.

(function () {
  // Change this if your backend runs somewhere other than localhost:3001.
  const API_BASE = 'http://localhost:3001/api/auth';

  const TOKEN_KEY = 'ow_token';
  const USER_KEY = 'ow_user';

  const accountButton = document.getElementById('accountButton');
  const authDialog = document.getElementById('authDialog');
  const closeAuthButton = document.getElementById('closeAuthButton');
  const authForm = document.getElementById('authForm');
  const authTitle = document.getElementById('authTitle');
  const authSubmit = document.getElementById('authSubmit');
  const authStatus = document.getElementById('authStatus');
  const authEmail = document.getElementById('authEmail');
  const authPassword = document.getElementById('authPassword');
  const authConfirmField = document.getElementById('authConfirmField');
  const authConfirmPassword = document.getElementById('authConfirmPassword');
  const modeButtons = document.querySelectorAll('[data-auth-mode]');

  let mode = 'signin'; // 'signin' | 'signup'

  function getStoredUser() {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function saveSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function setStatus(message, isError) {
    if (!authStatus) return;
    authStatus.textContent = message || '';
    authStatus.classList.toggle('auth-status--error', Boolean(isError));
  }

  function updateAccountButton() {
    const user = getStoredUser();
    if (user) {
      accountButton.textContent = user.email;
      accountButton.dataset.loggedIn = 'true';
    } else {
      accountButton.textContent = 'Sign in / Sign up';
      accountButton.dataset.loggedIn = 'false';
    }
  }

  function setMode(newMode) {
    mode = newMode;
    modeButtons.forEach((btn) => {
      const active = btn.dataset.authMode === mode;
      btn.setAttribute('aria-pressed', String(active));
    });

    if (mode === 'signup') {
      authTitle.textContent = 'Create your account';
      authSubmit.textContent = 'Sign up';
      authConfirmField.hidden = false;
      authConfirmPassword.setAttribute('required', 'required');
      authPassword.setAttribute('autocomplete', 'new-password');
    } else {
      authTitle.textContent = 'Welcome back';
      authSubmit.textContent = 'Sign in';
      authConfirmField.hidden = true;
      authConfirmPassword.removeAttribute('required');
      authPassword.setAttribute('autocomplete', 'current-password');
    }
    setStatus('');
  }

  function openDialog() {
    setStatus('');
    authForm.reset();
    authDialog.showModal();
    authEmail.focus();
  }

  function closeDialog() {
    authDialog.close();
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus('');

    const email = authEmail.value.trim();
    const password = authPassword.value;

    if (mode === 'signup') {
      const confirmPassword = authConfirmPassword.value;
      if (password !== confirmPassword) {
        setStatus('Passwords do not match.', true);
        return;
      }
    }

    authSubmit.disabled = true;
    authSubmit.textContent = mode === 'signup' ? 'Signing up…' : 'Signing in…';

    try {
      const endpoint = mode === 'signup' ? 'signup' : 'login';
      const response = await fetch(`${API_BASE}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setStatus(data.error || 'Something went wrong. Please try again.', true);
        return;
      }

      saveSession(data.token, data.user);
      updateAccountButton();
      setStatus('Success!', false);
      setTimeout(closeDialog, 500);
    } catch (err) {
      console.error('Auth request failed:', err);
      setStatus('Could not reach the server. Is the backend running?', true);
    } finally {
      authSubmit.disabled = false;
      authSubmit.textContent = mode === 'signup' ? 'Sign up' : 'Sign in';
    }
  }

  function handleAccountButtonClick() {
    const user = getStoredUser();
    if (user) {
      // Already signed in -> sign out.
      clearSession();
      updateAccountButton();
      setStatus('');
    } else {
      openDialog();
    }
  }

  accountButton.addEventListener('click', handleAccountButtonClick);
  closeAuthButton.addEventListener('click', closeDialog);
  authForm.addEventListener('submit', handleSubmit);
  modeButtons.forEach((btn) => {
    btn.addEventListener('click', () => setMode(btn.dataset.authMode));
  });

  // Close the dialog on backdrop click.
  authDialog.addEventListener('click', (event) => {
    const rect = authDialog.getBoundingClientRect();
    const inDialog =
      event.clientX >= rect.left &&
      event.clientX <= rect.right &&
      event.clientY >= rect.top &&
      event.clientY <= rect.bottom;
    if (!inDialog) closeDialog();
  });

  setMode('signin');
  updateAccountButton();
})();