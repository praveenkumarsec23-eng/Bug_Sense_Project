document.addEventListener('DOMContentLoaded', async () => {

  const API_BASE = window.BUGSENSE_CONFIG.API_BASE;
  const PAGE_SIZE = 8;

  let allBugs = [];
  let currentPage = 1;

  // =====================================================
  // ELEMENT REFERENCES
  // =====================================================

  const searchInput =
    document.getElementById('searchInput');

  const filterSeverity =
    document.getElementById('filterSeverity');

  const filterStatus =
    document.getElementById('filterStatus');

  const filterCategory =
    document.getElementById('filterCategory');

  const filterLanguage =
    document.getElementById('filterLanguage');

  const clearFiltersBtn =
    document.getElementById('clearFiltersBtn');

  const emptyClearFiltersBtn =
    document.getElementById('emptyClearFiltersBtn');

  const resultCount =
    document.getElementById('resultCount');

  const bugTableBody =
    document.getElementById('bugTableBody');

  const bugTable =
    document.getElementById('bugTable');

  const historyEmpty =
    document.getElementById('historyEmpty');

  const historyPagination =
    document.getElementById('historyPagination');
  
  const recentlyResolvedList =
  document.getElementById('recentlyResolvedList');

  // =====================================================
// HISTORY PAGE LOADING STATE
// =====================================================

const historyContent =
  document.getElementById('historyContent');

const historyLoader =
  document.getElementById('historyLoader');


function revealHistory() {

  if (!historyContent) {
    return;
  }

  requestAnimationFrame(() => {

    requestAnimationFrame(() => {

      historyContent.classList.remove(
        'history-data-loading',
        'history-data-error'
      );

      historyContent.classList.add(
        'history-data-ready'
      );

    });

  });
}


function showHistoryError() {

  if (!historyContent || !historyLoader) {
    return;
  }

  historyContent.classList.remove(
    'history-data-loading',
    'history-data-ready'
  );

  historyContent.classList.add(
    'history-data-error'
  );

  historyLoader.innerHTML = `
    <span class="history-loader__error-icon">
      <i class="bi bi-exclamation-triangle"></i>
    </span>

    <div class="history-loader__text">
      <strong>Could not load bug history</strong>
      <span>Please refresh the page and try again.</span>
    </div>
  `;
}
  // =====================================================
  // MODAL
  // =====================================================

  const bugDetailsModalEl =
    document.getElementById('bugDetailsModal');

  const bugDetailsModal =
    bugDetailsModalEl
      ? new bootstrap.Modal(bugDetailsModalEl)
      : null;

  const modalBugId =
    document.getElementById('modalBugId');

  const modalBugTitle =
    document.getElementById('modalBugTitle');

  const modalBugSeverity =
    document.getElementById('modalBugSeverity');

  const modalBugStatus =
    document.getElementById('modalBugStatus');

  const modalBugDate =
    document.getElementById('modalBugDate');

  const modalBugDescription =
    document.getElementById('modalBugDescription');

  const modalBugError =
    document.getElementById('modalBugError');

  const modalViewFullAnalysis =
    document.getElementById('modalViewFullAnalysis');

  // =====================================================
  // HELPERS
  // =====================================================

  function formatDate(dateString) {

    if (!dateString) {
      return 'Not available';
    }

    const date =
      new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return dateString;
    }

    return date.toLocaleDateString(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
      }
    );
  }

  function normalizeSeverity(severity) {

    return (
      severity ||
      'unknown'
    ).toLowerCase();
  }

  function normalizeStatus(status) {

    const value =
      (
        status ||
        ''
      ).toLowerCase();

    if (value === 'resolved') {
      return 'resolved';
    }

    if (
      value === 'analyzed' ||
      value === 'analyzing'
    ) {
      return 'analyzing';
    }

    return 'open';
  }

  function getStatusLabel(status) {

    const value =
      (
        status ||
        ''
      ).toLowerCase();

    if (value === 'resolved') {
      return 'Resolved';
    }

    if (value === 'analyzed') {
      return 'Analyzed';
    }

    if (value === 'analyzing') {
      return 'Analyzing';
    }

    return status || 'Open';
  }

  function getStatusDotClass(status) {

    const normalized =
      normalizeStatus(status);

    if (normalized === 'resolved') {
      return 'status-dot--green';
    }

    if (normalized === 'analyzing') {
      return 'status-dot--accent';
    }

    return 'status-dot--amber';
  }

  function getCategory(bug) {

    return (
      bug.bug_type ||
      'Uncategorized'
    );
  }

  // =====================================================
  // LOAD BUG HISTORY
  // =====================================================

 async function loadBugHistory() {

  const token =
    localStorage.getItem(
      'bugsense_token'
    );

  if (!token) {

    window.location.href =
      'index.html';

    return;
  }

  try {

    const response =
      await fetch(
        `${API_BASE}/api/bugs/history`,
        {
          method: 'GET',

          headers: {
            'Authorization':
              `Bearer ${token}`
          }
        }
      );

    // Invalid / expired login
    if (response.status === 401) {

      localStorage.removeItem(
        'bugsense_token'
      );

      window.location.href =
        'index.html';

      return;
    }

    let data = {};

    try {

      data =
        await response.json();

    } catch (jsonError) {

      throw new Error(
        'Invalid response received from the server.'
      );
    }

    if (!response.ok) {

      throw new Error(
        data.detail ||
        'Unable to load bug history.'
      );
    }

    // Store real backend bugs
    allBugs =
      Array.isArray(data.bugs)
        ? data.bugs
        : [];

    currentPage = 1;

    // Populate everything while page is still hidden
    updateSummaryCards();

    renderRecentlyResolved();

    render();

    // Reveal only after all real data is rendered
    revealHistory();

  } catch (error) {

    console.error(
      'Failed to load bug history:',
      error
    );

    /*
     * Do not reveal an empty/fake history page
     * when the backend request fails.
     */
    showHistoryError();
  }
}

  // =====================================================
  // SUMMARY CARDS
  // =====================================================

  function updateSummaryCards() {

    const cards =
      document.querySelectorAll(
        '.dash-stats .stat-card__value'
      );

    if (cards.length < 4) {
      return;
    }

    const total =
      allBugs.length;

    const open =
      allBugs.filter(
        bug =>
          normalizeStatus(
            bug.status
          ) !== 'resolved'
      ).length;

    const resolved =
      allBugs.filter(
        bug =>
          normalizeStatus(
            bug.status
          ) === 'resolved'
      ).length;

    const critical =
      allBugs.filter(
        bug =>
          normalizeSeverity(
            bug.severity
          ) === 'critical'
      ).length;

    cards[0].textContent =
      total;

    cards[1].textContent =
      open;

    cards[2].textContent =
      resolved;

    cards[3].textContent =
      critical;
  }

  // =====================================================
// RECENTLY RESOLVED
// =====================================================

function renderRecentlyResolved() {

  if (!recentlyResolvedList) {
    return;
  }

  const resolvedBugs =
    allBugs
      .filter(
        bug =>
          normalizeStatus(
            bug.status
          ) === 'resolved'
      )
      .slice(0, 4);

  if (resolvedBugs.length === 0) {

    recentlyResolvedList.innerHTML = `
      <li>
        <span class="recently-resolved__icon">
          <i class="bi bi-hourglass-split"></i>
        </span>

        <div class="recently-resolved__info">
          <p>No resolved bugs available yet.</p>
          <small>
            Resolved bugs will appear here automatically.
          </small>
        </div>
      </li>
    `;

    return;
  }

  recentlyResolvedList.innerHTML =
    resolvedBugs
      .map(
        bug => `
          <li>
            <span class="recently-resolved__icon">
              <i class="bi bi-check-circle-fill"></i>
            </span>

            <div class="recently-resolved__info">
              <p>
                <span class="mono">
                  ${bug.bug_id || `BUG-${bug.id}`}
                </span>
                — ${bug.title || 'Untitled Bug'}
              </p>

              <small>
                ${formatDate(bug.created_at)}
              </small>
            </div>
          </li>
        `
      )
      .join('');
}

  // =====================================================
  // FILTERING
  // =====================================================

  function getFilteredBugs() {

    const query =
      searchInput.value
        .trim()
        .toLowerCase();

    const severity =
      filterSeverity.value
        .toLowerCase();

    const status =
      filterStatus.value
        .toLowerCase();

    const category =
      filterCategory.value
        .toLowerCase();

    const language =
      filterLanguage.value
        .toLowerCase();

    return allBugs.filter(
      bug => {

        const searchableFields = [
          bug.bug_id,
          bug.title,
          bug.language,
          bug.severity,
          bug.status,
          bug.bug_type
        ];

        const matchesQuery =
          !query ||
          searchableFields.some(
            field =>
              String(
                field || ''
              )
                .toLowerCase()
                .includes(query)
          );

        const matchesSeverity =
          severity === 'all' ||
          normalizeSeverity(
            bug.severity
          ) === severity;

        const matchesStatus =
          status === 'all' ||
          normalizeStatus(
            bug.status
          ) === status;

        const matchesCategory =
          category === 'all' ||
          getCategory(bug)
            .toLowerCase() ===
          category;

        const matchesLanguage =
          language === 'all' ||
          (
            bug.language ||
            ''
          ).toLowerCase() ===
          language;

        return (
          matchesQuery &&
          matchesSeverity &&
          matchesStatus &&
          matchesCategory &&
          matchesLanguage
        );
      }
    );
  }

  // =====================================================
  // TABLE ROW
  // =====================================================

  function renderRow(bug) {

    const severity =
      normalizeSeverity(
        bug.severity
      );

    const status =
      normalizeStatus(
        bug.status
      );

    const statusLabel =
      getStatusLabel(
        bug.status
      );

    const statusDot =
      getStatusDotClass(
        bug.status
      );

    const category =
      getCategory(bug);

    return `
      <tr
        data-bug-id="${bug.id}"
        class="history-row"
        tabindex="0"
      >

        <td>
          <span class="mono">
            ${bug.bug_id || `BUG-${bug.id}`}
          </span>
        </td>

        <td>
          ${bug.title || 'Untitled Bug'}
        </td>

        <td>
          ${category}
        </td>

        <td>
          ${bug.language || 'Unknown'}
        </td>

        <td>
          <span
            class="badge-severity badge-severity--${severity}"
          >
            ${bug.severity || 'Unknown'}
          </span>
        </td>

        <td>
          <span
            class="badge-status badge-status--${status}"
          >
            <i
              class="status-dot ${statusDot}"
            ></i>
            ${statusLabel}
          </span>
        </td>

        <td>
          ${formatDate(
            bug.created_at
          )}
        </td>

        <td class="text-end">

          <button
            type="button"
            class="dash-view-btn history-detail-btn"
            data-bug-id="${bug.id}"
          >
            <i class="bi bi-info-circle"></i>
            Details
          </button>

          <a
            href="analysis-result.html?id=${bug.id}"
            class="dash-view-btn history-view-btn"
          >
            <i class="bi bi-eye"></i>
            View Analysis
          </a>

        </td>

      </tr>
    `;
  }

  // =====================================================
  // PAGINATION
  // =====================================================

  function renderPagination(
    totalItems
  ) {

    const totalPages =
      Math.max(
        1,
        Math.ceil(
          totalItems /
          PAGE_SIZE
        )
      );

    if (
      currentPage >
      totalPages
    ) {
      currentPage =
        totalPages;
    }

    if (
      totalItems === 0
    ) {

      historyPagination.innerHTML =
        '';

      return;
    }

    let html = `
      <button
        type="button"
        class="history-pagination__btn"
        data-page="prev"
        ${currentPage === 1 ? 'disabled' : ''}
      >
        <i class="bi bi-chevron-left"></i>
        Previous
      </button>
    `;

    for (
      let page = 1;
      page <= totalPages;
      page += 1
    ) {

      html += `
        <button
          type="button"
          class="history-pagination__btn ${page === currentPage ? 'active' : ''}"
          data-page="${page}"
        >
          ${page}
        </button>
      `;
    }

    html += `
      <button
        type="button"
        class="history-pagination__btn"
        data-page="next"
        ${currentPage === totalPages ? 'disabled' : ''}
      >
        Next
        <i class="bi bi-chevron-right"></i>
      </button>
    `;

    historyPagination.innerHTML =
      html;
  }

  // =====================================================
  // MAIN RENDER
  // =====================================================

  function render() {

    const filtered =
      getFilteredBugs();

    const totalPages =
      Math.max(
        1,
        Math.ceil(
          filtered.length /
          PAGE_SIZE
        )
      );

    if (
      currentPage >
      totalPages
    ) {
      currentPage =
        totalPages;
    }

    if (
      filtered.length === 0
    ) {

      bugTable.hidden =
        true;

      historyEmpty.hidden =
        false;

      historyPagination.innerHTML =
        '';

      resultCount.textContent =
        `Showing 0 of ${allBugs.length} bugs`;

      return;
    }

    bugTable.hidden =
      false;

    historyEmpty.hidden =
      true;

    const start =
      (
        currentPage -
        1
      ) * PAGE_SIZE;

    const pageItems =
      filtered.slice(
        start,
        start + PAGE_SIZE
      );

    bugTableBody.innerHTML =
      pageItems
        .map(renderRow)
        .join('');

    renderPagination(
      filtered.length
    );

    const rangeStart =
      start + 1;

    const rangeEnd =
      start +
      pageItems.length;

    if (
      filtered.length ===
      allBugs.length
    ) {

      resultCount.textContent =
        `Showing ${rangeStart}-${rangeEnd} of ${allBugs.length} bugs`;

    }

    else {

      resultCount.textContent =
        `Showing ${rangeStart}-${rangeEnd} of ${filtered.length} matching bugs (${allBugs.length} total)`;

    }
  }

  // =====================================================
  // SEARCH + FILTER EVENTS
  // =====================================================

  function handleFilterChange() {

    currentPage = 1;

    render();
  }

  searchInput.addEventListener(
    'input',
    handleFilterChange
  );

  filterSeverity.addEventListener(
    'change',
    handleFilterChange
  );

  filterStatus.addEventListener(
    'change',
    handleFilterChange
  );

  filterCategory.addEventListener(
    'change',
    handleFilterChange
  );

  filterLanguage.addEventListener(
    'change',
    handleFilterChange
  );

  // =====================================================
  // CLEAR FILTERS
  // =====================================================

  function clearFilters() {

    searchInput.value =
      '';

    filterSeverity.value =
      'all';

    filterStatus.value =
      'all';

    filterCategory.value =
      'all';

    filterLanguage.value =
      'all';

    currentPage = 1;

    render();
  }

  clearFiltersBtn.addEventListener(
    'click',
    clearFilters
  );

  emptyClearFiltersBtn.addEventListener(
    'click',
    clearFilters
  );

  // =====================================================
  // PAGINATION EVENTS
  // =====================================================

  historyPagination.addEventListener(
    'click',
    event => {

      const button =
        event.target.closest(
          '.history-pagination__btn'
        );

      if (
        !button ||
        button.disabled
      ) {
        return;
      }

      const pageValue =
        button.getAttribute(
          'data-page'
        );

      if (
        pageValue === 'prev'
      ) {

        currentPage =
          Math.max(
            1,
            currentPage - 1
          );

      }

      else if (
        pageValue === 'next'
      ) {

        currentPage += 1;

      }

      else {

        currentPage =
          Number(
            pageValue
          );

      }

      render();
    }
  );

  // =====================================================
  // BUG DETAILS
  // =====================================================

  async function openBugDetails(
    bugId
  ) {

    const token =
      localStorage.getItem(
        'bugsense_token'
      );

    if (!token) {

      window.location.href =
        'index.html';

      return;
    }

    try {

      const response =
        await fetch(
          `${API_BASE}/api/bugs/${bugId}`,
          {
            method: 'GET',

            headers: {
              'Authorization':
                `Bearer ${token}`
            }
          }
        );

      if (
        response.status === 401
      ) {

        localStorage.removeItem(
          'bugsense_token'
        );

        window.location.href =
          'index.html';

        return;
      }

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          'Unable to load bug details.'
        );
      }

      const bug =
        data.bug || {};

      const severity =
        normalizeSeverity(
          bug.severity
        );

      const status =
        normalizeStatus(
          bug.status
        );

      modalBugId.textContent =
        bug.bug_id ||
        `BUG-${bug.id}`;

      modalBugTitle.textContent =
        bug.title ||
        'Untitled Bug';

      modalBugSeverity.innerHTML =
        `
          <span
            class="badge-severity badge-severity--${severity}"
          >
            ${bug.severity || 'Unknown'}
          </span>
        `;

      modalBugStatus.innerHTML =
        `
          <span
            class="badge-status badge-status--${status}"
          >
            <i
              class="status-dot ${getStatusDotClass(bug.status)}"
            ></i>
            ${getStatusLabel(bug.status)}
          </span>
        `;

      modalBugDate.textContent =
        formatDate(
          bug.created_at
        );

      modalBugDescription.textContent =
        bug.description ||
        'No description provided.';

      modalBugError.textContent =
        bug.error_message ||
        'No error message provided.';

      if (
        modalViewFullAnalysis
      ) {

        modalViewFullAnalysis.href =
          `analysis-result.html?id=${bug.id}`;
      }

      if (
        bugDetailsModal
      ) {
        bugDetailsModal.show();
      }

    }

    catch (error) {

      console.error(
        'Failed to load bug details:',
        error
      );
    }
  }

  // =====================================================
  // TABLE EVENTS
  // =====================================================

  bugTableBody.addEventListener(
    'click',
    event => {

      const detailButton =
        event.target.closest(
          '.history-detail-btn'
        );

      if (
        detailButton
      ) {

        event.preventDefault();

        openBugDetails(
          detailButton.getAttribute(
            'data-bug-id'
          )
        );

        return;
      }

      if (
        event.target.closest(
          '.history-view-btn'
        )
      ) {
        return;
      }

      const row =
        event.target.closest(
          '.history-row'
        );

      if (
        row
      ) {

        openBugDetails(
          row.getAttribute(
            'data-bug-id'
          )
        );

      }
    }
  );

  bugTableBody.addEventListener(
    'keydown',
    event => {

      if (
        event.key !== 'Enter' &&
        event.key !== ' '
      ) {
        return;
      }

      const row =
        event.target.closest(
          '.history-row'
        );

      if (!row) {
        return;
      }

      event.preventDefault();

      openBugDetails(
        row.getAttribute(
          'data-bug-id'
        )
      );
    }
  );

  // =====================================================
  // START
  // =====================================================

  await loadBugHistory();

});