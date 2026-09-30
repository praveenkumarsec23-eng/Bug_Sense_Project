/* ==========================================================================
   BugSense — Profile Page
   Connected to FastAPI Backend
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  const API_URL = `${window.BUGSENSE_CONFIG.API_BASE}/api/profile`;


  /* ---------------------------------------------------------------------
     1. Element references
     --------------------------------------------------------------------- */

  const editProfileForm =
    document.getElementById('editProfileForm');

  const editFullName =
    document.getElementById('editFullName');

  const editEmail =
    document.getElementById('editEmail');

  const editRole =
    document.getElementById('editRole');
  const editPrimarySkills =
  document.getElementById('editPrimarySkills');

const editSpecialization =
  document.getElementById('editSpecialization');

const editExperience =
  document.getElementById('editExperience');
  const cancelEditProfileBtn =
    document.getElementById('cancelEditProfileBtn');

  const saveProfileBtn =
    document.getElementById('saveProfileBtn');


  // Main profile information
  const profileDisplayName =
    document.getElementById('profileDisplayName');

  const profileDisplayRole =
    document.getElementById('profileDisplayRole');

  const infoFullName =
    document.getElementById('infoFullName');

  const infoEmail =
    document.getElementById('infoEmail');

  const infoRole =
    document.getElementById('infoRole');

  const infoLastUpdated =
    document.getElementById('infoLastUpdated');
  const infoPrimarySkills =
  document.getElementById('infoPrimarySkills');

const infoSpecialization =
  document.getElementById('infoSpecialization');

const infoExperience =
  document.getElementById('infoExperience');

const infoMemberSince =
  document.getElementById('infoMemberSince');

  // Topbar information
  const topbarProfileName =
    document.getElementById('topbarProfileName');

  const topbarAvatarInitials =
    document.getElementById('topbarAvatarInitials');

  const profileAvatarInitials =
    document.getElementById('profileAvatarInitials');


  // Profile loading state
  const profileContent =
    document.getElementById('profileContent');

  const profileLoader =
    document.getElementById('profileLoader');


  /* ---------------------------------------------------------------------
     2. Bootstrap modal
     --------------------------------------------------------------------- */

  const editProfileModalEl =
    document.getElementById('editProfileModal');

  const editProfileModal =
    bootstrap.Modal.getOrCreateInstance(
      editProfileModalEl
    );


  /* ---------------------------------------------------------------------
     3. Toast
     --------------------------------------------------------------------- */

  const toastEl =
    document.getElementById('profileToast');

  const toastMessage =
    document.getElementById('profileToastMessage');

  const toastIcon =
    document.getElementById('profileToastIcon');

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
     5. Generate initials
     --------------------------------------------------------------------- */

  function getInitials(name) {

    if (!name) {
      return 'U';
    }

    const parts =
      name
        .trim()
        .split(/\s+/);

    if (parts.length === 1) {

      return parts[0]
        .charAt(0)
        .toUpperCase();
    }

    return (
      parts[0].charAt(0) +
      parts[parts.length - 1].charAt(0)
    ).toUpperCase();
  }


  /* ---------------------------------------------------------------------
     6. Profile loading / reveal state
     --------------------------------------------------------------------- */

  function revealProfile() {

    if (!profileContent) {
      return;
    }

    requestAnimationFrame(() => {

      requestAnimationFrame(() => {

        profileContent.classList.remove(
          'profile-data-loading',
          'profile-data-error'
        );

        profileContent.classList.add(
          'profile-data-ready'
        );

      });

    });
  }


  function showProfileError(
    message = 'Unable to load your profile.'
  ) {

    if (
      !profileContent ||
      !profileLoader
    ) {
      return;
    }

    profileContent.classList.remove(
      'profile-data-loading',
      'profile-data-ready'
    );

    profileContent.classList.add(
      'profile-data-error'
    );

    /*
     * textContent is used for the backend/error message
     * so server text is never injected as HTML.
     */
    profileLoader.innerHTML = `
      <span class="profile-loader__error-icon">
        <i class="bi bi-exclamation-triangle"></i>
      </span>

      <div class="profile-loader__text">
        <strong>Profile unavailable</strong>
        <span id="profileLoaderErrorMessage"></span>
      </div>
    `;

    const errorMessage =
      document.getElementById(
        'profileLoaderErrorMessage'
      );

    if (errorMessage) {
      errorMessage.textContent =
        message;
    }
  }


  /* ---------------------------------------------------------------------
   7. Update profile information on page
   --------------------------------------------------------------------- */

function formatProfileDate(value) {

  if (!value) {
    return '—';
  }

  let normalizedValue = value;

  // Backend timestamps are UTC.
  // Add Z if timezone information is not included.
  if (
    typeof normalizedValue === 'string' &&
    !normalizedValue.endsWith('Z') &&
    !/[+-]\d{2}:\d{2}$/.test(normalizedValue)
  ) {
    normalizedValue += 'Z';
  }

  const date = new Date(normalizedValue);

  if (Number.isNaN(date.getTime())) {
    return '—';
  }

  return date.toLocaleString(
    undefined,
    {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }
  );
}


function updateProfileUI(user) {

  const userName =
    user?.name || 'User';

  const userEmail =
    user?.email || '—';

  const userRole =
    user?.role || '—';

  const primarySkills =
    user?.primary_skills || '—';

  const specialization =
    user?.specialization || '—';

  const experience =
    user?.experience || '—';


  // Main profile information
  if (profileDisplayName) {
    profileDisplayName.textContent =
      userName;
  }

  if (profileDisplayRole) {
    profileDisplayRole.textContent =
      userRole;
  }

  if (infoFullName) {
    infoFullName.textContent =
      userName;
  }

  if (infoEmail) {
    infoEmail.textContent =
      userEmail;
  }

  if (infoRole) {
    infoRole.textContent =
      userRole;
  }


  // Professional information
  if (infoPrimarySkills) {
    infoPrimarySkills.textContent =
      primarySkills;
  }

  if (infoSpecialization) {
    infoSpecialization.textContent =
      specialization;
  }

  if (infoExperience) {
    infoExperience.textContent =
      experience;
  }


  // Member Since
  if (infoMemberSince) {

    if (user?.created_at) {

      const createdDate =
        new Date(user.created_at);

      infoMemberSince.textContent =
        Number.isNaN(createdDate.getTime())
          ? '—'
          : String(createdDate.getFullYear());

    } else {

      infoMemberSince.textContent =
        '—';
    }
  }


  // Last Updated
  if (infoLastUpdated) {
    infoLastUpdated.textContent =
      formatProfileDate(user?.updated_at);
  }


  // Topbar
  if (topbarProfileName) {
    topbarProfileName.textContent =
      userName;
  }


  // Avatar initials
  const initials =
    getInitials(userName);

  if (topbarAvatarInitials) {
    topbarAvatarInitials.textContent =
      initials;
  }

  if (profileAvatarInitials) {
    profileAvatarInitials.textContent =
      initials;
  }


  // Store latest user information locally
  if (
    user?.id !== undefined &&
    user?.id !== null
  ) {

    localStorage.setItem(
      'bugsense_user_id',
      String(user.id)
    );
  }

  localStorage.setItem(
    'bugsense_user_name',
    userName
  );

  localStorage.setItem(
    'bugsense_user_email',
    userEmail
  );
}
  /* ---------------------------------------------------------------------
     8. Load profile from backend
     GET /api/profile
     --------------------------------------------------------------------- */

  async function loadProfile() {

    const token =
      getToken();

    if (!token) {

      window.location.href =
        'index.html';

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


      // Invalid or expired login
      if (response.status === 401) {

        localStorage.removeItem(
          'bugsense_token'
        );

        window.location.href =
          'index.html';

        return;
      }


      let data = null;

      try {

        data =
          await response.json();

      } catch {

        data = null;
      }


      if (!response.ok) {

        throw new Error(
          data?.detail ||
          'Unable to load profile.'
        );
      }


      /*
       * Fill the hidden page using
       * the real backend response.
       */
      updateProfileUI(data);

      
      /*
       * Initial backend load is complete.
       * We do not invent a "last updated"
       * value if the API does not provide one.
       */
      if (
        infoLastUpdated &&
        !infoLastUpdated.textContent.trim()
      ) {

        infoLastUpdated.textContent =
          '—';
      }


      /*
       * Reveal only after all real
       * backend data has been rendered.
       */
      revealProfile();


     


    } catch (error) {

      console.error(
        'Profile load error:',
        error
      );

      /*
       * Do not reveal placeholder/demo
       * content when the API fails.
       */
      showProfileError(
        error?.message ||
        'Unable to connect to the BugSense backend.'
      );
    }
  }


  /* ---------------------------------------------------------------------
   9. Populate edit modal
   --------------------------------------------------------------------- */

editProfileModalEl.addEventListener(
  'show.bs.modal',
  () => {

    // Personal information
    editFullName.value =
      infoFullName.textContent.trim();

    editEmail.value =
      infoEmail.textContent.trim();

    editRole.value =
      infoRole.textContent.trim();


    // Professional information
    editPrimarySkills.value =
      infoPrimarySkills.textContent.trim() === '—'
        ? ''
        : infoPrimarySkills.textContent.trim();

    editSpecialization.value =
      infoSpecialization.textContent.trim() === '—'
        ? ''
        : infoSpecialization.textContent.trim();

    editExperience.value =
      infoExperience.textContent.trim() === '—'
        ? ''
        : infoExperience.textContent.trim();


    // Reset validation state
    editProfileForm.classList.remove(
      'was-validated'
    );


    [
      editFullName,
      editEmail,
      editRole,
      editPrimarySkills,
      editSpecialization,
      editExperience

    ].forEach((field) => {

      field.classList.remove(
        'is-invalid'
      );

    });
  }
);
  /* ---------------------------------------------------------------------
     10. Cancel edit
     --------------------------------------------------------------------- */

  cancelEditProfileBtn.addEventListener(
    'click',
    () => {

      editProfileForm.classList.remove(
        'was-validated'
      );


      [
        editFullName,
        editEmail,
        editRole

      ].forEach((field) => {

        field.classList.remove(
          'is-invalid'
        );

      });
    }
  );


  /* ---------------------------------------------------------------------
     11. Email validation
     --------------------------------------------------------------------- */

  function isValidEmail(value) {

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      .test(value);
  }


  /* ---------------------------------------------------------------------
     12. Form validation
     --------------------------------------------------------------------- */

  function validateForm() {

    let isValid = true;


    // Name
    if (!editFullName.value.trim()) {

      editFullName.classList.add(
        'is-invalid'
      );

      isValid = false;

    } else {

      editFullName.classList.remove(
        'is-invalid'
      );
    }


    // Email
    if (
      !editEmail.value.trim() ||
      !isValidEmail(
        editEmail.value.trim()
      )
    ) {

      editEmail.classList.add(
        'is-invalid'
      );

      isValid = false;

    } else {

      editEmail.classList.remove(
        'is-invalid'
      );
    }


    // Role
    if (!editRole.value.trim()) {

      editRole.classList.add(
        'is-invalid'
      );

      isValid = false;

    } else {

      editRole.classList.remove(
        'is-invalid'
      );
    }


    return isValid;
  }


  /* ---------------------------------------------------------------------
   13. UPDATE PROFILE
   PUT /api/profile
   --------------------------------------------------------------------- */

editProfileForm.addEventListener(
  'submit',
  async (event) => {

    event.preventDefault();
    event.stopPropagation();


    editProfileForm.classList.add(
      'was-validated'
    );


    if (!validateForm()) {
      return;
    }


    const token =
      getToken();


    if (!token) {

      window.location.href =
        'index.html';

      return;
    }


    // Personal information
    const newName =
      editFullName
        .value
        .trim();

    const newEmail =
      editEmail
        .value
        .trim();

    const newRole =
      editRole
        .value
        .trim();


    // Professional information
    const newPrimarySkills =
      editPrimarySkills
        .value
        .trim();

    const newSpecialization =
      editSpecialization
        .value
        .trim();

    const newExperience =
      editExperience
        .value
        .trim();


    /* ---------------------------------------------------------------
       Disable button while saving
       --------------------------------------------------------------- */

    const originalButtonContent =
      saveProfileBtn.innerHTML;

    saveProfileBtn.disabled =
      true;

    saveProfileBtn.innerHTML =
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

            body: JSON.stringify({
              name: newName,
              email: newEmail,
              role: newRole,
              primary_skills:
                newPrimarySkills || null,
              specialization:
                newSpecialization || null,
              experience:
                newExperience || null
            })
          }
        );


      if (response.status === 401) {

        localStorage.removeItem(
          'bugsense_token'
        );

        window.location.href =
          'index.html';

        return;
      }


      let data = null;

      try {

        data =
          await response.json();

      } catch {

        data = null;
      }


      if (!response.ok) {

        showToast(
          data?.detail ||
          'Unable to update profile.',
          'error'
        );

        return;
      }


      /* -------------------------------------------------------------
         Update UI using actual backend response
         ------------------------------------------------------------- */

      updateProfileUI(data);


      editProfileModal.hide();


      showToast(
        'Profile updated successfully.',
        'success'
      );




    } catch (error) {

      console.error(
        'Profile update error:',
        error
      );


      showToast(
        'Unable to connect to the BugSense backend.',
        'error'
      );


    } finally {

      saveProfileBtn.disabled =
        false;

      saveProfileBtn.innerHTML =
        originalButtonContent;
    }
  }
);
  /* ---------------------------------------------------------------------
     14. Load real profile when page opens
     --------------------------------------------------------------------- */

  loadProfile();

});