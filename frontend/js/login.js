/* ==========================================================================
   BugSense — Login / Register page logic
   Login + Register connected to FastAPI backend
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  /* ---------------------------------------------------------------------
     1. Tab switching (Login <-> Register)
     --------------------------------------------------------------------- */

  const tabLoginBtn = document.getElementById('tabLoginBtn');
  const tabRegisterBtn = document.getElementById('tabRegisterBtn');
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const goToRegister = document.getElementById('goToRegister');
  const goToLogin = document.getElementById('goToLogin');

  function showLogin() {
    loginForm.classList.add('active');
    registerForm.classList.remove('active');

    tabLoginBtn.classList.add('active');
    tabRegisterBtn.classList.remove('active');

    tabLoginBtn.setAttribute('aria-selected', 'true');
    tabRegisterBtn.setAttribute('aria-selected', 'false');
  }

  function showRegister() {
    registerForm.classList.add('active');
    loginForm.classList.remove('active');

    tabRegisterBtn.classList.add('active');
    tabLoginBtn.classList.remove('active');

    tabRegisterBtn.setAttribute('aria-selected', 'true');
    tabLoginBtn.setAttribute('aria-selected', 'false');
  }

  tabLoginBtn.addEventListener('click', showLogin);
  tabRegisterBtn.addEventListener('click', showRegister);

  if (goToRegister) {
    goToRegister.addEventListener('click', showRegister);
  }

  if (goToLogin) {
    goToLogin.addEventListener('click', showLogin);
  }


  /* ---------------------------------------------------------------------
     2. Password visibility toggles
     --------------------------------------------------------------------- */

  document.querySelectorAll('.password-toggle').forEach((btn) => {

    btn.addEventListener('click', () => {

      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      const icon = btn.querySelector('i');

      if (!input || !icon) {
        return;
      }

      const isHidden = input.type === 'password';

      input.type = isHidden ? 'text' : 'password';

      icon.classList.toggle('bi-eye', !isHidden);
      icon.classList.toggle('bi-eye-slash', isHidden);

      btn.setAttribute(
        'aria-label',
        isHidden ? 'Hide password' : 'Show password'
      );
    });
  });


  /* ---------------------------------------------------------------------
     3. Password strength meter
     --------------------------------------------------------------------- */

  const registerPassword = document.getElementById('registerPassword');
  const strengthMeter = document.getElementById('strengthMeter');
  const strengthLabel = document.getElementById('strengthLabel');

  function scorePassword(value) {

    let score = 0;

    if (value.length >= 8) {
      score++;
    }

    if (/[A-Z]/.test(value) && /[0-9]/.test(value)) {
      score++;
    }

    if (/[^A-Za-z0-9]/.test(value) && value.length >= 10) {
      score++;
    }

    return score;
  }

  if (registerPassword && strengthMeter && strengthLabel) {

    registerPassword.addEventListener('input', () => {

      const value = registerPassword.value;

      const score =
        value.length === 0
          ? 0
          : scorePassword(value) || 1;

      strengthMeter.setAttribute(
        'data-level',
        score
      );

      const labels = {
        0: 'Signal weak',
        1: 'Signal weak',
        2: 'Signal medium',
        3: 'Signal strong'
      };

      strengthLabel.textContent = labels[score];
    });
  }


  /* ---------------------------------------------------------------------
     4. Confirm password validation
     --------------------------------------------------------------------- */

  const confirmPassword =
    document.getElementById('registerConfirmPassword');

  function validatePasswordMatch() {

    if (!confirmPassword || !registerPassword) {
      return;
    }

    if (
      confirmPassword.value !==
      registerPassword.value
    ) {

      confirmPassword.setCustomValidity(
        'Passwords do not match'
      );

    } else {

      confirmPassword.setCustomValidity('');

    }
  }

  if (registerPassword && confirmPassword) {

    registerPassword.addEventListener(
      'input',
      validatePasswordMatch
    );

    confirmPassword.addEventListener(
      'input',
      validatePasswordMatch
    );
  }


  /* ---------------------------------------------------------------------
     5. Toast helper
     --------------------------------------------------------------------- */

  const toastEl =
    document.getElementById('authToast');

  const toastMessage =
    document.getElementById('toastMessage');

  const toastIcon =
    document.getElementById('toastIcon');

  let bsToast = null;

  if (toastEl && typeof bootstrap !== 'undefined') {

    bsToast = new bootstrap.Toast(
      toastEl,
      {
        delay: 3200
      }
    );
  }

  function showToast(
    message,
    type = 'success'
  ) {

    if (
      !toastEl ||
      !toastMessage ||
      !toastIcon ||
      !bsToast
    ) {

      console.log(message);
      return;
    }

    toastMessage.textContent = message;

    toastEl.classList.toggle(
      'toast--error',
      type === 'error'
    );

    toastIcon.className =
      type === 'error'
        ? 'bi bi-x-circle-fill'
        : 'bi bi-check-circle-fill';

    bsToast.show();
  }


  /* ---------------------------------------------------------------------
     6. LOGIN
     --------------------------------------------------------------------- */

  loginForm.addEventListener(
    'submit',
    async (event) => {

      event.preventDefault();
      event.stopPropagation();

      if (!loginForm.checkValidity()) {

        loginForm.classList.add(
          'was-validated'
        );

        return;
      }

      loginForm.classList.remove(
        'was-validated'
      );

      const email =
        document
          .getElementById('loginEmail')
          .value
          .trim();

      const password =
        document
          .getElementById('loginPassword')
          .value;

      try {

        const response = await fetch(
          `${window.BUGSENSE_CONFIG.API_BASE}/api/auth/login`,
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json'
            },

            body: JSON.stringify({
              email: email,
              password: password
            })
          }
        );

        const data =
          await response.json();

        if (!response.ok) {

          showToast(
            data.detail ||
              'Invalid email or password.',
            'error'
          );

          return;
        }


        /* ---------------------------------------------------------------
           Store authentication data
           --------------------------------------------------------------- */

        localStorage.setItem(
          'bugsense_token',
          data.access_token
        );

        localStorage.setItem(
          'bugsense_user_id',
          String(data.user_id)
        );

        localStorage.setItem(
          'bugsense_user_name',
          data.name
        );

        localStorage.setItem(
          'bugsense_user_email',
          data.email
        );


       

        /* ---------------------------------------------------------------
           Redirect immediately to Dashboard
           --------------------------------------------------------------- */

        window.location.replace(
          'dashboard.html'
        );

      } catch (error) {

        console.error(
          'BugSense login error:',
          error
        );

        showToast(
          'Unable to connect to the BugSense backend. Make sure FastAPI is running.',
          'error'
        );
      }
    }
  );


  /* ---------------------------------------------------------------------
     7. REGISTER
     --------------------------------------------------------------------- */

  registerForm.addEventListener(
    'submit',
    async (event) => {

      event.preventDefault();
      event.stopPropagation();

      validatePasswordMatch();

      if (!registerForm.checkValidity()) {

        registerForm.classList.add(
          'was-validated'
        );

        return;
      }

      registerForm.classList.remove(
        'was-validated'
      );

      const name =
        document
          .getElementById('registerName')
          .value
          .trim();

      const email =
        document
          .getElementById('registerEmail')
          .value
          .trim();

      const password =
        document
          .getElementById('registerPassword')
          .value;


      try {

        const response = await fetch(
          `${window.BUGSENSE_CONFIG.API_BASE}/api/auth/register`,
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json'
            },

            body: JSON.stringify({
              name: name,
              email: email,
              password: password
            })
          }
        );

        const data =
          await response.json();


        if (!response.ok) {

          showToast(
            data.detail ||
              'Registration failed.',
            'error'
          );

          return;
        }


        showToast(
          'Account created successfully. You can now log in.',
          'success'
        );


        registerForm.reset();


        if (
          strengthMeter &&
          strengthLabel
        ) {

          strengthMeter.setAttribute(
            'data-level',
            '0'
          );

          strengthLabel.textContent =
            'Signal weak';
        }


        /* ---------------------------------------------------------------
           Switch back to Login after registration
           --------------------------------------------------------------- */

        setTimeout(() => {

          showLogin();

          const loginEmail =
            document.getElementById(
              'loginEmail'
            );

          if (loginEmail) {
            loginEmail.value = email;
          }

        }, 900);

      } catch (error) {

        console.error(
          'BugSense registration error:',
          error
        );

        showToast(
          'Unable to connect to the BugSense backend. Make sure FastAPI is running.',
          'error'
        );
      }
    }
  );


  /* ---------------------------------------------------------------------
     8. Diagnostic console animation
     --------------------------------------------------------------------- */

  const scanStatusText =
    document.getElementById(
      'scanStatusText'
    );

  const scanMessages = [
    'Analyzing traceback…',
    'Cross-referencing stack frames…',
    'Bug isolated at line 15 — NoneType error',
    'Generating fix recommendation…'
  ];

  let scanIndex = 0;

  if (scanStatusText) {

    setInterval(() => {

      scanIndex =
        (scanIndex + 1) %
        scanMessages.length;

      scanStatusText.textContent =
        scanMessages[scanIndex];

    }, 2600);
  }

});