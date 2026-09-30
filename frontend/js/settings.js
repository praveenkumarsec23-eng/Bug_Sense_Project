/* ==========================================================================
   BugSense — Settings Page
   Connected to FastAPI Backend
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  const API_URL =
  `${window.BUGSENSE_CONFIG.API_BASE}/api/settings`;


  /* ---------------------------------------------------------------------
     1. Settings fields
     --------------------------------------------------------------------- */

  const SELECT_FIELDS = [
    'generalLanguage',
    'generalTimezone',
    'generalDateFormat',
    'appearanceTheme'
  ];


  const CHECKBOX_FIELDS = [
    'generalAutoSave',

    'appearanceCompactMode',
    'appearanceAnimations',

    'notifAnalysisCompleted',
    'notifNewKnowledge',
    'notifBugAlerts',
    'notifSystemNotifications',

    'privacySaveHistory',
    'privacyStoreResolved',
    'privacyUsageAnalytics',

    'aiSuggestions',
    'aiHistoricalRetrieval',
    'aiRootCause',
    'aiFixRecommendations'
  ];


  /* ---------------------------------------------------------------------
     2. Main element references
     --------------------------------------------------------------------- */

  const settingsForm =
    document.getElementById(
      'settingsForm'
    );

  const resetSettingsBtn =
    document.getElementById(
      'resetSettingsBtn'
    );

  const saveSettingsBtn =
    document.getElementById(
      'saveSettingsBtn'
    );


  // Loading / real content
  const settingsContent =
    document.getElementById(
      'settingsContent'
    );

  const settingsLoader =
    document.getElementById(
      'settingsLoader'
    );


  /* ---------------------------------------------------------------------
     3. Toast
     --------------------------------------------------------------------- */

  const toastEl =
    document.getElementById(
      'settingsToast'
    );

  const toastMessage =
    document.getElementById(
      'settingsToastMessage'
    );

  const toastIcon =
    document.getElementById(
      'settingsToastIcon'
    );


  const bsToast =
    new bootstrap.Toast(
      toastEl,
      {
        delay: 3000
      }
    );


  function showToast(
    message,
    type = 'success'
  ) {

    toastMessage.textContent =
      message;

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
     4. Get JWT token
     --------------------------------------------------------------------- */

  function getToken() {

    return localStorage.getItem(
      'bugsense_token'
    );
  }


  /* ---------------------------------------------------------------------
     5. Handle unauthorized response
     --------------------------------------------------------------------- */

  function handleUnauthorized() {

    localStorage.removeItem(
      'bugsense_token'
    );

    localStorage.removeItem(
      'bugsense_user_id'
    );

    localStorage.removeItem(
      'bugsense_user_name'
    );

    localStorage.removeItem(
      'bugsense_user_email'
    );

    window.location.href =
      'index.html';
  }


  /* ---------------------------------------------------------------------
     6. Loading / reveal states
     --------------------------------------------------------------------- */

  function revealSettings() {

    if (!settingsContent) {
      return;
    }


    /*
     * Wait until the browser has painted
     * all backend values into the controls.
     */
    requestAnimationFrame(() => {

      requestAnimationFrame(() => {

        settingsContent.classList.remove(
          'settings-data-loading',
          'settings-data-error'
        );

        settingsContent.classList.add(
          'settings-data-ready'
        );

      });

    });
  }


  function showSettingsError(
    message =
      'Unable to load your settings.'
  ) {

    if (
      !settingsContent ||
      !settingsLoader
    ) {
      return;
    }


    settingsContent.classList.remove(
      'settings-data-loading',
      'settings-data-ready'
    );

    settingsContent.classList.add(
      'settings-data-error'
    );


    /*
     * Build only the fixed UI using HTML.
     * Dynamic error text is added with
     * textContent for safety.
     */
    settingsLoader.innerHTML = `
      <span class="settings-loader__error-icon">
        <i class="bi bi-exclamation-triangle"></i>
      </span>

      <div class="settings-loader__text">
        <strong>Settings unavailable</strong>
        <span id="settingsLoaderErrorMessage"></span>
      </div>
    `;


    const errorMessage =
      document.getElementById(
        'settingsLoaderErrorMessage'
      );


    if (errorMessage) {

      errorMessage.textContent =
        message;
    }
  }


  /* ---------------------------------------------------------------------
     7. Frontend field -> Backend field mapping
     --------------------------------------------------------------------- */

  const FIELD_MAP = {

    generalLanguage:
      'general_language',

    generalTimezone:
      'general_timezone',

    generalDateFormat:
      'general_date_format',

    generalAutoSave:
      'general_auto_save',


    appearanceTheme:
      'appearance_theme',

    appearanceCompactMode:
      'appearance_compact_mode',

    appearanceAnimations:
      'appearance_animations',


    notifAnalysisCompleted:
      'notif_analysis_completed',

    notifNewKnowledge:
      'notif_new_knowledge',

    notifBugAlerts:
      'notif_bug_alerts',

    notifSystemNotifications:
      'notif_system_notifications',


    privacySaveHistory:
      'privacy_save_history',

    privacyStoreResolved:
      'privacy_store_resolved',

    privacyUsageAnalytics:
      'privacy_usage_analytics',


    aiSuggestions:
      'ai_suggestions',

    aiHistoricalRetrieval:
      'ai_historical_retrieval',

    aiRootCause:
      'ai_root_cause',

    aiFixRecommendations:
      'ai_fix_recommendations'
  };


  /* ---------------------------------------------------------------------
     8. Apply backend settings to form
     --------------------------------------------------------------------- */

  function applySettingsToForm(
    settings
  ) {

    if (!settings) {
      return;
    }


    SELECT_FIELDS.forEach(
      (frontendId) => {

        const element =
          document.getElementById(
            frontendId
          );

        const backendField =
          FIELD_MAP[frontendId];


        if (
          element &&
          settings[backendField] !==
            undefined &&
          settings[backendField] !==
            null
        ) {

          element.value =
            settings[backendField];
        }
      }
    );


    CHECKBOX_FIELDS.forEach(
      (frontendId) => {

        const element =
          document.getElementById(
            frontendId
          );

        const backendField =
          FIELD_MAP[frontendId];


        if (
          element &&
          settings[backendField] !==
            undefined &&
          settings[backendField] !==
            null
        ) {

          element.checked =
            Boolean(
              settings[backendField]
            );
        }
      }
    );
  }


  /* ---------------------------------------------------------------------
     9. Collect settings from form
     --------------------------------------------------------------------- */

  function collectSettingsFromForm() {

    const settings = {};


    SELECT_FIELDS.forEach(
      (frontendId) => {

        const element =
          document.getElementById(
            frontendId
          );

        if (!element) {
          return;
        }


        const backendField =
          FIELD_MAP[frontendId];

        settings[backendField] =
          element.value;
      }
    );


    CHECKBOX_FIELDS.forEach(
      (frontendId) => {

        const element =
          document.getElementById(
            frontendId
          );

        if (!element) {
          return;
        }


        const backendField =
          FIELD_MAP[frontendId];

        settings[backendField] =
          element.checked;
      }
    );


    return settings;
  }


  /* ---------------------------------------------------------------------
     10. Safely read JSON response
     --------------------------------------------------------------------- */

  async function readJsonResponse(
    response
  ) {

    try {

      return await response.json();

    } catch {

      return null;
    }
  }


  /* ---------------------------------------------------------------------
     11. LOAD SETTINGS
     GET /api/settings
     --------------------------------------------------------------------- */

  async function loadSettings() {

    const token =
      getToken();


    if (!token) {

      handleUnauthorized();

      return;
    }


    try {

      const response =
        await fetch(
          API_URL,
          {
            method: 'GET',

            headers: {

              'Authorization':
                `Bearer ${token}`
            }
          }
        );


      if (response.status === 401) {

        handleUnauthorized();

        return;
      }


      const data =
        await readJsonResponse(
          response
        );


      if (!response.ok) {

        throw new Error(
          data?.detail ||
          'Unable to load settings.'
        );
      }


      if (!data) {

        throw new Error(
          'Invalid settings response.'
        );
      }


      /*
       * Populate every control while
       * settings-real-content is hidden.
       */
      applySettingsToForm(
        data
      );


      /*
       * Only reveal after every saved
       * backend preference has been applied.
       */
      revealSettings();


   

    } catch (error) {

      console.error(
        'Settings load error:',
        error
      );


      /*
       * Do NOT reveal browser/default
       * values when backend loading fails.
       */
      showSettingsError(
        error?.message ||
        'Unable to connect to the BugSense backend.'
      );
    }
  }


  /* ---------------------------------------------------------------------
     12. SAVE SETTINGS
     PUT /api/settings
     --------------------------------------------------------------------- */

  settingsForm.addEventListener(
    'submit',
    async (event) => {

      event.preventDefault();


      const token =
        getToken();


      if (!token) {

        handleUnauthorized();

        return;
      }


      const currentSettings =
        collectSettingsFromForm();


      const originalButtonContent =
        saveSettingsBtn.innerHTML;


      saveSettingsBtn.disabled =
        true;


      saveSettingsBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';


      try {

        const response =
          await fetch(
            API_URL,
            {
              method: 'PUT',

              headers: {

                'Content-Type':
                  'application/json',

                'Authorization':
                  `Bearer ${token}`
              },


              body: JSON.stringify(
                currentSettings
              )
            }
          );


        if (
          response.status === 401
        ) {

          handleUnauthorized();

          return;
        }


        const data =
          await readJsonResponse(
            response
          );


        if (!response.ok) {

          showToast(
            data?.detail ||
            'Unable to save settings.',
            'error'
          );

          return;
        }


        if (!data) {

          showToast(
            'Invalid response from the backend.',
            'error'
          );

          return;
        }


        /*
         * Always use backend response as
         * the final source of truth.
         */
        applySettingsToForm(
          data
        );


        showToast(
          'Settings saved successfully.',
          'success'
        );



      } catch (error) {

        console.error(
          'Settings save error:',
          error
        );


        showToast(
          'Unable to connect to the BugSense backend.',
          'error'
        );


      } finally {

        saveSettingsBtn.disabled =
          false;


        saveSettingsBtn.innerHTML =
          originalButtonContent;
      }
    }
  );


  /* ---------------------------------------------------------------------
     13. RESET SETTINGS
     POST /api/settings/reset
     --------------------------------------------------------------------- */

  resetSettingsBtn.addEventListener(
    'click',
    async () => {

      const token =
        getToken();


      if (!token) {

        handleUnauthorized();

        return;
      }


      const originalButtonContent =
        resetSettingsBtn.innerHTML;


      resetSettingsBtn.disabled =
        true;


      resetSettingsBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2"></span>Resetting...';


      try {

        const response =
          await fetch(
            `${API_URL}/reset`,
            {
              method: 'POST',

              headers: {

                'Authorization':
                  `Bearer ${token}`
              }
            }
          );


        if (
          response.status === 401
        ) {

          handleUnauthorized();

          return;
        }


        const data =
          await readJsonResponse(
            response
          );


        if (!response.ok) {

          showToast(
            data?.detail ||
            'Unable to reset settings.',
            'error'
          );

          return;
        }


        if (!data) {

          showToast(
            'Invalid response from the backend.',
            'error'
          );

          return;
        }


        /*
         * Reset UI using the actual
         * backend reset response.
         */
        applySettingsToForm(
          data
        );


        showToast(
          'Settings restored to default.',
          'success'
        );



      } catch (error) {

        console.error(
          'Settings reset error:',
          error
        );


        showToast(
          'Unable to connect to the BugSense backend.',
          'error'
        );


      } finally {

        resetSettingsBtn.disabled =
          false;


        resetSettingsBtn.innerHTML =
          originalButtonContent;
      }
    }
  );


  /* ---------------------------------------------------------------------
     14. Initial load
     --------------------------------------------------------------------- */

  loadSettings();

});