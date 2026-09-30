/* ==========================================================================
   BugSense — Shared Authentication Guard
   Used by protected frontend pages.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', async () => {

  const token = localStorage.getItem('bugsense_token');

  /* ---------------------------------------------------------------------
     1. If no token exists, return user to login page
     --------------------------------------------------------------------- */

  if (!token) {
    window.location.href = 'index.html';
    return;
  }


  /* ---------------------------------------------------------------------
     2. Verify token with backend
     --------------------------------------------------------------------- */

  try {

    const response = await fetch(
     `${window.BUGSENSE_CONFIG.API_BASE}/api/auth/me`,
      {
        method: 'GET',

        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    if (!response.ok) {

      clearAuthData();

      window.location.href = 'index.html';

      return;
    }

    const user = await response.json();


    /* -------------------------------------------------------------------
       3. Keep latest user data in localStorage
       ------------------------------------------------------------------- */

    localStorage.setItem(
      'bugsense_user_id',
      user.id
    );

    localStorage.setItem(
      'bugsense_user_name',
      user.name
    );

    localStorage.setItem(
      'bugsense_user_email',
      user.email
    );


    /* -------------------------------------------------------------------
       4. Update user name in topbar automatically
       ------------------------------------------------------------------- */

    const profileNameElements = document.querySelectorAll(
      '.dash-profile__name, .dash-profile__info small'
    );

    profileNameElements.forEach((element) => {
      element.textContent = user.name;
    });


    /* -------------------------------------------------------------------
       5. Update avatar initials automatically
       ------------------------------------------------------------------- */

    const avatarElements = document.querySelectorAll(
      '.dash-avatar, .dash-profile__avatar'
    );

    const initials = getInitials(user.name);

    avatarElements.forEach((element) => {
      element.textContent = initials;
    });

  } catch (error) {

    console.error(
      'Authentication check failed:',
      error
    );

    clearAuthData();

    window.location.href = 'index.html';
  }


  /* ---------------------------------------------------------------------
     6. Logout handlers
     --------------------------------------------------------------------- */

  const logoutLinks = document.querySelectorAll(
    'a[href="index.html"].dash-nav__link--logout, a[href="index.html"].dash-dropdown__item'
  );

  logoutLinks.forEach((logoutLink) => {

    logoutLink.addEventListener('click', () => {

      clearAuthData();

    });

  });

});


/* ==========================================================================
   CLEAR AUTH DATA
   ========================================================================== */

function clearAuthData() {

  localStorage.removeItem('bugsense_token');
  localStorage.removeItem('bugsense_user_id');
  localStorage.removeItem('bugsense_user_name');
  localStorage.removeItem('bugsense_user_email');

}


/* ==========================================================================
   GET USER INITIALS
   ========================================================================== */

function getInitials(name) {

  if (!name) {
    return 'U';
  }

  const parts = name
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