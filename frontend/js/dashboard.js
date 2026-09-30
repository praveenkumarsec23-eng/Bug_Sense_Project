/* ==========================================================================
   BugSense — Dashboard
   Loads real dashboard data from FastAPI.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', async () => {

  /* ---------------------------------------------------------------------
     Mobile sidebar toggle
     --------------------------------------------------------------------- */

  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  const openBtn = document.getElementById('sidebarToggle');
  const closeBtn = document.getElementById('sidebarClose');

  function openSidebar() {
    sidebar?.classList.add('is-open');
    backdrop?.classList.add('is-open');
    openBtn?.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    sidebar?.classList.remove('is-open');
    backdrop?.classList.remove('is-open');
    openBtn?.setAttribute('aria-expanded', 'false');
  }

  openBtn?.addEventListener('click', openSidebar);
  closeBtn?.addEventListener('click', closeSidebar);
  backdrop?.addEventListener('click', closeSidebar);

  window.addEventListener('resize', () => {
    if (window.innerWidth >= 992) {
      closeSidebar();
    }
  });


  /* ---------------------------------------------------------------------
     Sidebar active link
     --------------------------------------------------------------------- */

  const navLinks = document.querySelectorAll(
    '.dash-nav__link:not(.dash-nav__link--logout)'
  );

  const currentPage =
    window.location.pathname.split('/').pop() || 'dashboard.html';

  navLinks.forEach((link) => {

    const linkPage = link.getAttribute('href');

    link.classList.toggle(
      'active',
      linkPage === currentPage
    );

  });


  /* ---------------------------------------------------------------------
     Cached user interface
     --------------------------------------------------------------------- */

  updateCachedUserUI();


  /* ---------------------------------------------------------------------
     Load Dashboard data
     --------------------------------------------------------------------- */

  if (currentPage === 'dashboard.html') {
    await loadDashboard();
  }

});


/* ==========================================================================
   LOAD DASHBOARD
   ========================================================================== */

async function loadDashboard() {

  const token =
    localStorage.getItem('bugsense_token');

  if (!token) {
    window.location.href = 'index.html';
    return;
  }


  try {

    const response = await fetch(
      `${window.BUGSENSE_CONFIG.API_BASE}/api/dashboard`,
      {
        method: 'GET',

        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );


    if (response.status === 401) {

      clearDashboardAuth();

      window.location.href = 'index.html';

      return;
    }


    if (!response.ok) {

      throw new Error(
        `Dashboard request failed: ${response.status}`
      );

    }


    const data = await response.json();

    const summary =
      data.summary || {};


    updateSummaryCards(
      summary
    );


    updateSeverityOverview(
      data.severity || {},
      summary.total_bugs ?? 0
    );


    updateCategories(
      data.categories || []
    );


    updateRecentBugs(
      data.recent_bugs || []
    );


    updateRecentActivity(
      data.recent_activity || []
    );


    updateKnowledgeBase(
      data.knowledge_base || {}
    );


    revealDashboard();


  } catch (error) {

    console.error(
      'Failed to load dashboard:',
      error
    );

    showDashboardError();

  }

}


/* ==========================================================================
   CACHED USER UI
   ========================================================================== */

function updateCachedUserUI() {

  const cachedName =
    (localStorage.getItem('bugsense_user_name') || '')
      .trim();

  const displayName =
    cachedName || 'User';

  const firstName =
    displayName.split(/\s+/)[0];


  const initials =
    displayName
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join('') || 'U';


  const welcomeHeading =
    document.querySelector('.dash-welcome h2');

  const profileName =
    document.querySelector('.dash-profile__name');

  const avatar =
    document.querySelector('.dash-avatar');


  if (welcomeHeading) {
    welcomeHeading.textContent =
      `Welcome back, ${firstName}`;
  }


  if (profileName) {
    profileName.textContent =
      displayName;
  }


  if (avatar) {
    avatar.textContent =
      initials;
  }

}


/* ==========================================================================
   REVEAL DASHBOARD
   ========================================================================== */

function revealDashboard() {

  const dashboardContent =
    document.getElementById('dashboardContent');

  if (!dashboardContent) {
    return;
  }


  requestAnimationFrame(() => {

    requestAnimationFrame(() => {

      dashboardContent.classList.remove(
        'dashboard-data-loading',
        'dashboard-data-error'
      );

      dashboardContent.classList.add(
        'dashboard-data-ready'
      );

    });

  });

}


/* ==========================================================================
   DASHBOARD LOAD ERROR
   ========================================================================== */

function showDashboardError() {

  const dashboardContent =
    document.getElementById('dashboardContent');

  const dashboardLoader =
    document.getElementById('dashboardLoader');


  if (!dashboardContent || !dashboardLoader) {
    return;
  }


  dashboardContent.classList.remove(
    'dashboard-data-loading',
    'dashboard-data-ready'
  );

  dashboardContent.classList.add(
    'dashboard-data-error'
  );


  dashboardLoader.innerHTML = `
    <div class="dashboard-loader__error-icon">
      <i class="bi bi-exclamation-triangle"></i>
    </div>

    <div class="dashboard-loader__text">
      <strong>Unable to load dashboard</strong>
      <span>
        Check that the BugSense backend is running,
        then refresh this page.
      </span>
    </div>
  `;

}

/* ==========================================================================
   SUMMARY CARDS
   ========================================================================== */

function updateSummaryCards(summary) {

  if (!summary) {
    return;
  }


  const values =
    document.querySelectorAll(
      '.dash-stats .stat-card__value'
    );


  if (values.length >= 4) {

    values[0].textContent =
      summary.total_bugs ?? 0;

    values[1].textContent =
      summary.open_bugs ?? 0;

    values[2].textContent =
      summary.resolved_bugs ?? 0;

    values[3].textContent =
      summary.critical_bugs ?? 0;

  }


  const trends =
    document.querySelectorAll(
      '.dash-stats .stat-card__trend'
    );

  trends.forEach((trend) => {

    trend.innerHTML =
      '<i class="bi bi-dash"></i> Live data';

    trend.className =
      'stat-card__trend stat-card__trend--flat';

  });

}


/* ==========================================================================
   SEVERITY OVERVIEW
   ========================================================================== */

function updateSeverityOverview(
  severity,
  totalBugs
) {

  if (!severity) {
    return;
  }


  const severityItems =
    document.querySelectorAll(
      '.severity-list li'
    );


  const levels = [
    'critical',
    'high',
    'medium',
    'low'
  ];


  severityItems.forEach(
    (item, index) => {

      const level =
        levels[index];

      if (!level) {
        return;
      }


      const count =
        severity[level] ?? 0;


      const countElement =
        item.querySelector(
          '.severity-list__count'
        );


      if (countElement) {

        countElement.textContent =
          count;

      }


      const progressBar =
        item.querySelector(
          '.dash-bar__fill'
        );


      if (progressBar) {

        let percentage = 0;

        if (totalBugs > 0) {

          percentage =
            Math.round(
              (count / totalBugs) * 100
            );

        }

        progressBar.style.width =
          `${percentage}%`;

      }

    }
  );

}


/* ==========================================================================
   BUG CATEGORIES
   ========================================================================== */

function updateCategories(categories) {

  const categoryList =
    document.querySelector(
      '.category-list'
    );


  if (!categoryList) {
    return;
  }


  categoryList.innerHTML = '';


  if (
    !categories ||
    categories.length === 0
  ) {

    categoryList.innerHTML = `
      <li>
        <span class="category-list__icon">
          <i class="bi bi-inbox"></i>
        </span>

        <span class="category-list__name">
          No bug categories yet
        </span>

        <span class="category-list__count">
          0
        </span>
      </li>
    `;

    return;
  }


  categories.forEach((item) => {

    const li =
      document.createElement('li');


    const icon =
      getCategoryIcon(
        item.category
      );


    li.innerHTML = `
      <span class="category-list__icon">
        <i class="bi ${icon}"></i>
      </span>

      <span class="category-list__name">
        ${escapeHTML(item.category)}
      </span>

      <span class="category-list__count">
        ${item.count ?? 0}
      </span>
    `;


    categoryList.appendChild(li);

  });

}


/* ==========================================================================
   RECENT BUG ANALYSES
   ========================================================================== */

function updateRecentBugs(bugs) {

  const tableBody =
    document.querySelector(
      '.dash-table tbody'
    );


  if (!tableBody) {
    return;
  }


  tableBody.innerHTML = '';


  const sampleTag =
    document.querySelector(
      '.dash-table-panel .panel__tag'
    );


  if (sampleTag) {

    sampleTag.textContent =
      'Live data';

  }


  if (
    !bugs ||
    bugs.length === 0
  ) {

    tableBody.innerHTML = `
      <tr>
        <td
          colspan="7"
          class="text-center py-4"
        >
          No bug analyses yet.
          Analyze your first bug to see it here.
        </td>
      </tr>
    `;

    return;
  }


  bugs.forEach((bug) => {

    const row =
      document.createElement('tr');


    const severity =
      (bug.severity || 'low')
        .toLowerCase();


    const status =
      (bug.status || 'open')
        .toLowerCase();


    row.innerHTML = `
      <td>
        <span class="mono">
          ${escapeHTML(bug.bug_id)}
        </span>
      </td>

      <td>
        ${escapeHTML(bug.title)}
      </td>

      <td>
        ${escapeHTML(
          bug.category ||
          'Uncategorized'
        )}
      </td>

      <td>
        <span
          class="badge-severity badge-severity--${getSeverityClass(severity)}"
        >
          ${capitalize(severity)}
        </span>
      </td>

      <td>
        <span
          class="badge-status badge-status--${getStatusClass(status)}"
        >
          <i
            class="status-dot ${getStatusDotClass(status)}"
          ></i>

          ${capitalize(status)}
        </span>
      </td>

      <td>
        ${formatDate(bug.date)}
      </td>

      <td class="text-end">
        <a
          href="analysis-result.html?id=${bug.id}"
          class="dash-view-btn"
        >
          <i class="bi bi-eye"></i>
          View
        </a>
      </td>
    `;


    tableBody.appendChild(row);

  });

}


/* ==========================================================================
   RECENT ACTIVITY
   ========================================================================== */

function updateRecentActivity(activities) {

  const activityList =
    document.querySelector(
      '.activity-list'
    );


  if (!activityList) {
    return;
  }


  activityList.innerHTML = '';


  if (
    !activities ||
    activities.length === 0
  ) {

    activityList.innerHTML = `
      <li>
        <span class="activity-list__icon">
          <i class="bi bi-clock-history"></i>
        </span>

        <div>
          <p>No recent activity</p>
          <small>
            Bug activity will appear here.
          </small>
        </div>
      </li>
    `;

    return;
  }


  activities.forEach((activity) => {

    const li =
      document.createElement('li');


    li.innerHTML = `
      <span class="activity-list__icon">
        <i class="bi bi-bug-fill"></i>
      </span>

      <div>
        <p>
          ${escapeHTML(activity.message)}
        </p>

        <small>
          ${timeAgo(activity.created_at)}
        </small>
      </div>
    `;


    activityList.appendChild(li);

  });

}


/* ==========================================================================
   KNOWLEDGE BASE SUMMARY
   ========================================================================== */

function updateKnowledgeBase(
  knowledgeBase
) {

  if (!knowledgeBase) {
    return;
  }


  const values =
    document.querySelectorAll(
      '.dash-kb-panel__value'
    );


  if (values.length >= 3) {

    values[0].textContent =
      knowledgeBase.historical_bugs ?? 0;

    values[1].textContent =
      knowledgeBase.resolved_issues ?? 0;

    values[2].textContent =
      knowledgeBase.similar_bug_searches ?? 0;

  }

}


/* ==========================================================================
   CATEGORY ICON
   ========================================================================== */

function getCategoryIcon(category) {

  const value =
    (category || '')
      .toLowerCase();


  if (value.includes('database')) {
    return 'bi-server';
  }

  if (value.includes('runtime')) {
    return 'bi-cpu';
  }

  if (value.includes('security')) {
    return 'bi-shield-lock';
  }

  if (value.includes('performance')) {
    return 'bi-speedometer';
  }

  if (value.includes('syntax')) {
    return 'bi-code-slash';
  }

  if (value.includes('logic')) {
    return 'bi-diagram-3';
  }

  return 'bi-bug';

}


/* ==========================================================================
   SEVERITY CLASS
   ========================================================================== */

function getSeverityClass(severity) {

  const allowed = [
    'critical',
    'high',
    'medium',
    'low'
  ];


  return allowed.includes(severity)
    ? severity
    : 'low';

}


/* ==========================================================================
   STATUS CLASS
   ========================================================================== */

function getStatusClass(status) {

  if (status === 'resolved') {
    return 'resolved';
  }

  if (
    status === 'analyzing' ||
    status === 'analyzed'
  ) {
    return 'analyzing';
  }

  return 'open';

}


/* ==========================================================================
   STATUS DOT
   ========================================================================== */

function getStatusDotClass(status) {

  if (status === 'resolved') {
    return 'status-dot--green';
  }

  if (
    status === 'analyzing' ||
    status === 'analyzed'
  ) {
    return 'status-dot--accent';
  }

  return 'status-dot--amber';

}


/* ==========================================================================
   FORMAT DATE
   ========================================================================== */

function formatDate(dateValue) {

  if (!dateValue) {
    return '-';
  }


  const date =
    new Date(dateValue);


  if (Number.isNaN(
    date.getTime()
  )) {

    return '-';

  }


  return date.toLocaleDateString(
    'en-US',
    {
      month: 'short',
      day: '2-digit',
      year: 'numeric'
    }
  );

}


/* ==========================================================================
   TIME AGO
   ========================================================================== */

function timeAgo(dateValue) {

  if (!dateValue) {
    return '';
  }


  const date =
    new Date(dateValue);


  const seconds =
    Math.floor(
      (Date.now() - date.getTime()) / 1000
    );


  if (seconds < 60) {
    return 'Just now';
  }


  const minutes =
    Math.floor(seconds / 60);


  if (minutes < 60) {

    return `${minutes} minute${
      minutes === 1 ? '' : 's'
    } ago`;

  }


  const hours =
    Math.floor(minutes / 60);


  if (hours < 24) {

    return `${hours} hour${
      hours === 1 ? '' : 's'
    } ago`;

  }


  const days =
    Math.floor(hours / 24);


  return `${days} day${
    days === 1 ? '' : 's'
  } ago`;

}


/* ==========================================================================
   CAPITALIZE
   ========================================================================== */

function capitalize(value) {

  if (!value) {
    return '';
  }


  return (
    value.charAt(0).toUpperCase() +
    value.slice(1)
  );

}


/* ==========================================================================
   ESCAPE HTML
   ========================================================================== */

function escapeHTML(value) {

  if (value === null ||
      value === undefined) {

    return '';

  }


  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

}


/* ==========================================================================
   CLEAR AUTH DATA
   ========================================================================== */

function clearDashboardAuth() {

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

}