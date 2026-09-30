/* ==========================================================================
   BugSense — Knowledge Base
   Connected to the real BugSense backend API.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  const API_BASE = window.BUGSENSE_CONFIG.API_BASE;
  const PAGE_SIZE = 8;

  let allKnowledge = [];
  let currentPage = 1;

  /* ---------------------------------------------------------------------
     Element references
     --------------------------------------------------------------------- */

  const searchInput =
    document.getElementById('kbSearchInput');

  const filterCategory =
    document.getElementById('kbFilterCategory');

  const filterLanguage =
    document.getElementById('kbFilterLanguage');

  const filterSeverity =
    document.getElementById('kbFilterSeverity');

  const filterSource =
    document.getElementById('kbFilterSource');

  const clearFiltersBtn =
    document.getElementById('kbClearFiltersBtn');

  const emptyClearFiltersBtn =
    document.getElementById('kbEmptyClearFiltersBtn');

  const resultCount =
    document.getElementById('kbResultCount');

  const kbTableBody =
    document.getElementById('kbTableBody');

  const kbTable =
    document.getElementById('kbTable');

  const kbEmpty =
    document.getElementById('kbEmpty');

  const kbPagination =
    document.getElementById('kbPagination');

  const kbRecentList =
    document.getElementById('kbRecentList');

// =====================================================
// KNOWLEDGE BASE LOADING STATE
// =====================================================

const knowledgeBaseContent =
  document.getElementById('knowledgeBaseContent');

const knowledgeBaseLoader =
  document.getElementById('knowledgeBaseLoader');


function revealKnowledgeBase() {

  if (!knowledgeBaseContent) {
    return;
  }

  requestAnimationFrame(() => {

    requestAnimationFrame(() => {

      knowledgeBaseContent.classList.remove(
        'kb-data-loading',
        'kb-data-error'
      );

      knowledgeBaseContent.classList.add(
        'kb-data-ready'
      );

    });

  });
}


function showKnowledgeBaseError() {

  if (
    !knowledgeBaseContent ||
    !knowledgeBaseLoader
  ) {
    return;
  }

  knowledgeBaseContent.classList.remove(
    'kb-data-loading',
    'kb-data-ready'
  );

  knowledgeBaseContent.classList.add(
    'kb-data-error'
  );

  knowledgeBaseLoader.innerHTML = `
    <span class="kb-loader__error-icon">
      <i class="bi bi-exclamation-triangle"></i>
    </span>

    <div class="kb-loader__text">
      <strong>Could not load knowledge base</strong>
      <span>Please refresh the page and try again.</span>
    </div>
  `;
}
  /* ---------------------------------------------------------------------
     Helpers
     --------------------------------------------------------------------- */

  function safeText(value, fallback = '—') {
    if (
      value === null ||
      value === undefined ||
      value === ''
    ) {
      return fallback;
    }

    return String(value);
  }


  function escapeHtml(value) {
    return safeText(value, '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }


  function normalizeSeverity(value) {
    const severity =
      safeText(value, 'unknown').toLowerCase();

    if (
      ['critical', 'high', 'medium', 'low']
        .includes(severity)
    ) {
      return severity;
    }

    return 'unknown';
  }


  function severityLabel(value) {
    const severity = normalizeSeverity(value);

    const labels = {
      critical: 'Critical',
      high: 'High',
      medium: 'Medium',
      low: 'Low',
      unknown: 'Pending'
    };

    return labels[severity];
  }


  function formatDate(value) {
    if (!value) {
      return 'Date unavailable';
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return 'Date unavailable';
    }

    return date.toLocaleDateString(
      'en-GB',
      {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }
    );
  }


  /* ---------------------------------------------------------------------
     Statistics
     --------------------------------------------------------------------- */

  function updateStatistics() {

    const statValues =
      document.querySelectorAll(
        '.dash-stats .stat-card__value'
      );

    if (statValues.length < 4) {
      return;
    }

    const totalEntries =
      allKnowledge.length;

    const resolvedBugs =
      allKnowledge.filter(
        item =>
          safeText(
            item.status,
            ''
          ).toLowerCase() === 'resolved'
      ).length;

    const rootCauses =
      allKnowledge.filter(
        item =>
          item.root_cause &&
          item.root_cause.trim()
      ).length;

    const fixRecommendations =
      allKnowledge.filter(
        item =>
          item.solution &&
          item.solution.trim()
      ).length;

    statValues[0].textContent =
      totalEntries;

    statValues[1].textContent =
      resolvedBugs;

    statValues[2].textContent =
      rootCauses;

    statValues[3].textContent =
      fixRecommendations;
  }

/* ---------------------------------------------------------------------
   Filtering
   --------------------------------------------------------------------- */

function normalizeLanguage(value) {
  const language =
    safeText(value, '')
      .trim()
      .toLowerCase();

  const aliases = {
    'java': 'java',

    'python': 'python',
    'py': 'python',

    'javascript': 'javascript',
    'js': 'javascript',

    'typescript': 'typescript',
    'ts': 'typescript',

    'c': 'c',

    'c++': 'cpp',
    'cpp': 'cpp',

    'c#': 'csharp',
    'csharp': 'csharp',

    'php': 'php'
  };

  return aliases[language] || language;
}


function getFilteredKnowledge() {

  const query =
    searchInput.value
      .trim()
      .toLowerCase();

  const category =
    filterCategory.value;

  const language =
    filterLanguage.value;

  const severity =
    filterSeverity.value;

  const source =
    filterSource.value;

  return allKnowledge.filter(
    item => {

      const searchableFields = [
        item.knowledge_id,
        item.bug_id,
        item.title,
        item.category,
        item.language,
        item.description,
        item.error,
        item.root_cause,
        item.solution,
        item.source
      ];

      const matchesQuery =
        !query ||
        searchableFields.some(
          field =>
            safeText(
              field,
              ''
            )
              .toLowerCase()
              .includes(query)
        );

      const matchesCategory =
        category === 'all' ||
        item.category === category;

      const matchesLanguage =
        language === 'all' ||
        normalizeLanguage(item.language) ===
        normalizeLanguage(language);

      const matchesSeverity =
        severity === 'all' ||
        normalizeSeverity(
          item.severity
        ) === severity;

      const matchesSource =
        source === 'all' ||
        item.source === source;

      return (
        matchesQuery &&
        matchesCategory &&
        matchesLanguage &&
        matchesSeverity &&
        matchesSource
      );
    }
  );
}

  /* ---------------------------------------------------------------------
     Table
     --------------------------------------------------------------------- */

  function renderRow(item) {

    const severity =
      normalizeSeverity(
        item.severity
      );

    return `
      <tr
        data-kb-id="${item.id}"
        class="history-row"
        tabindex="0"
      >

        <td>
          <span class="mono">
            ${escapeHtml(
              item.knowledge_id ||
              `KB-${item.id}`
            )}
          </span>
        </td>

        <td>
          ${escapeHtml(
            item.title ||
            'Untitled Knowledge'
          )}
        </td>

        <td>
          ${escapeHtml(
            item.category ||
            'Uncategorized'
          )}
        </td>

        <td>
          ${escapeHtml(
            item.language ||
            'Unknown'
          )}
        </td>

        <td>
          <span
            class="badge-severity
            badge-severity--${severity}"
          >
            ${severityLabel(
              item.severity
            )}
          </span>
        </td>

        <td class="kb-root-cause-cell">
          ${escapeHtml(
            item.root_cause ||
            'Root cause not available.'
          )}
        </td>

               <td>
          <span class="mono">
            RAG Ready
          </span>
        </td>

        <td class="text-end">

          <button
            type="button"
            class="dash-view-btn kb-view-btn"
            data-kb-id="${item.id}"
            aria-label="View knowledge details"
          >
            <i class="bi bi-eye"></i>
            View
          </button>

        </td>

      </tr>
    `;
  }


  /* ---------------------------------------------------------------------
     Pagination
     --------------------------------------------------------------------- */

  function renderPagination(totalItems) {

    const totalPages =
      Math.max(
        1,
        Math.ceil(
          totalItems / PAGE_SIZE
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
      kbPagination.innerHTML = '';
      return;
    }

    let html = `
      <button
        type="button"
        class="kb-pagination__btn"
        data-page="prev"
        ${currentPage === 1
          ? 'disabled'
          : ''}
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
          class="kb-pagination__btn
          ${page === currentPage
            ? 'active'
            : ''}"
          data-page="${page}"
        >
          ${page}
        </button>
      `;
    }

    html += `
      <button
        type="button"
        class="kb-pagination__btn"
        data-page="next"
        ${currentPage === totalPages
          ? 'disabled'
          : ''}
      >
        Next
        <i class="bi bi-chevron-right"></i>
      </button>
    `;

    kbPagination.innerHTML =
      html;
  }


  /* ---------------------------------------------------------------------
     Main rendering
     --------------------------------------------------------------------- */

  function render() {

    const filtered =
      getFilteredKnowledge();

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

      kbTable.hidden =
        true;

      kbEmpty.hidden =
        false;

      kbPagination.innerHTML =
        '';

      resultCount.textContent =
        `Showing 0 of ${allKnowledge.length} entries`;

      return;
    }

    kbTable.hidden =
      false;

    kbEmpty.hidden =
      true;

    const start =
      (currentPage - 1) *
      PAGE_SIZE;

    const pageItems =
      filtered.slice(
        start,
        start + PAGE_SIZE
      );

    kbTableBody.innerHTML =
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
      allKnowledge.length
    ) {

      resultCount.textContent =
        `Showing ${rangeStart}-${rangeEnd} of ${allKnowledge.length} entries`;

    } else {

      resultCount.textContent =
        `Showing ${rangeStart}-${rangeEnd} of ${filtered.length} matching entries (${allKnowledge.length} total)`;
    }
  }


  /* ---------------------------------------------------------------------
     Recently Added
     --------------------------------------------------------------------- */

  function renderRecentlyAdded() {

    if (
      allKnowledge.length === 0
    ) {

      kbRecentList.innerHTML = `
        <li>

          <span class="kb-recent-list__icon">
            <i class="bi bi-hourglass-split"></i>
          </span>

          <div class="kb-recent-list__info">

            <p>
              No knowledge entries available yet.
            </p>

            <small>
              Resolved bugs added to the knowledge base
              will appear here automatically.
            </small>

          </div>

        </li>
      `;

      return;
    }

    const recent =
      [...allKnowledge]
        .sort(
          (a, b) =>
            new Date(
              b.created_at
            ) -
            new Date(
              a.created_at
            )
        )
        .slice(0, 4);

    kbRecentList.innerHTML =
      recent
        .map(
          item => `
            <li>

              <span class="kb-recent-list__icon">
                <i class="bi bi-journal-plus"></i>
              </span>

              <div class="kb-recent-list__info">

                <p>
                  <span class="mono">
                    ${escapeHtml(
                      item.knowledge_id ||
                      `KB-${item.id}`
                    )}
                  </span>
                  —
                  ${escapeHtml(
                    item.title ||
                    'Untitled Knowledge'
                  )}
                </p>

                <small>
                  ${escapeHtml(
                    item.category ||
                    'Uncategorized'
                  )}
                  ·
                  ${escapeHtml(
                    item.language ||
                    'Unknown'
                  )}
                  ·
                  <span class="kb-recent-list__meta">
                    ${formatDate(
                      item.created_at
                    )}
                  </span>
                </small>

              </div>

            </li>
          `
        )
        .join('');
  }


  /* ---------------------------------------------------------------------
     Knowledge Details Modal
     --------------------------------------------------------------------- */

  const kbDetailsModalEl =
    document.getElementById(
      'kbDetailsModal'
    );

  const kbDetailsModal =
    new bootstrap.Modal(
      kbDetailsModalEl
    );

  const modalKbId =
    document.getElementById(
      'modalKbId'
    );

  const modalKbStatus =
    document.getElementById(
      'modalKbStatus'
    );

  const modalKbTitle =
    document.getElementById(
      'modalKbTitle'
    );

  const modalKbBugId =
    document.getElementById(
      'modalKbBugId'
    );

  const modalKbCategory =
    document.getElementById(
      'modalKbCategory'
    );

  const modalKbLanguage =
    document.getElementById(
      'modalKbLanguage'
    );

  const modalKbSeverity =
    document.getElementById(
      'modalKbSeverity'
    );

  const modalKbSource =
    document.getElementById(
      'modalKbSource'
    );

  const modalKbError =
    document.getElementById(
      'modalKbError'
    );

  const modalKbRootCause =
    document.getElementById(
      'modalKbRootCause'
    );

  const modalKbResolution =
    document.getElementById(
      'modalKbResolution'
    );

  const modalKbWhyRelevant =
    document.getElementById(
      'modalKbWhyRelevant'
    );

  const modalAnalyzeSimilarBtn =
    document.getElementById(
      'modalAnalyzeSimilarBtn'
    );


  function openKnowledgeDetails(
    kbId
  ) {

    const item =
      allKnowledge.find(
        entry =>
          String(entry.id) ===
          String(kbId)
      );

    if (!item) {
      return;
    }

    const severity =
      normalizeSeverity(
        item.severity
      );

    modalKbId.textContent =
      item.knowledge_id ||
      `KB-${item.id}`;

    modalKbStatus.innerHTML = `
      <span class="badge-status">

        <i class="status-dot"></i>

        ${escapeHtml(
          item.status ||
          'Knowledge Entry'
        )}

      </span>
    `;

    modalKbTitle.textContent =
      safeText(
        item.title
      );

    modalKbBugId.textContent =
      safeText(
        item.bug_id,
        'Not linked'
      );

    modalKbCategory.textContent =
      safeText(
        item.category,
        'Uncategorized'
      );

    modalKbLanguage.textContent =
      safeText(
        item.language,
        'Unknown'
      );

    modalKbSeverity.innerHTML = `
      <span
        class="badge-severity
        badge-severity--${severity}"
      >
        ${severityLabel(
          item.severity
        )}
      </span>
    `;

    modalKbSource.textContent =
      safeText(
        item.source,
        'Knowledge Base'
      );

    modalKbError.textContent =
      safeText(
        item.error,
        'No error message stored.'
      );

    modalKbRootCause.textContent =
      safeText(
        item.root_cause,
        'Root cause not available.'
      );

    modalKbResolution.textContent =
      safeText(
        item.solution,
        'Resolution not available.'
      );

        modalKbWhyRelevant.textContent =
      'This knowledge entry is available to BugSense semantic retrieval. When a new bug is analyzed, its diagnostic context is compared with historical knowledge using embedding-based similarity, and the most relevant past issues can support duplicate detection and remediation.';

    kbDetailsModal.show();
  }


  /* ---------------------------------------------------------------------
     Events
     --------------------------------------------------------------------- */

  function handleFilterChange() {
    currentPage = 1;
    render();
  }


  searchInput.addEventListener(
    'input',
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

  filterSeverity.addEventListener(
    'change',
    handleFilterChange
  );

  filterSource.addEventListener(
    'change',
    handleFilterChange
  );


  function clearFilters() {

    searchInput.value = '';

    filterCategory.value =
      'all';

    filterLanguage.value =
      'all';

    filterSeverity.value =
      'all';

    filterSource.value =
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


  kbPagination.addEventListener(
    'click',
    event => {

      const btn =
        event.target.closest(
          '.kb-pagination__btn'
        );

      if (
        !btn ||
        btn.disabled
      ) {
        return;
      }

      const pageValue =
        btn.getAttribute(
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

      } else if (
        pageValue === 'next'
      ) {

        currentPage += 1;

      } else {

        currentPage =
          Number(pageValue);
      }

      render();
    }
  );


  kbTableBody.addEventListener(
    'click',
    event => {

      const viewBtn =
        event.target.closest(
          '.kb-view-btn'
        );

      if (viewBtn) {

        event.preventDefault();

        openKnowledgeDetails(
          viewBtn.getAttribute(
            'data-kb-id'
          )
        );

        return;
      }

      const row =
        event.target.closest(
          '.history-row'
        );

      if (row) {

        openKnowledgeDetails(
          row.getAttribute(
            'data-kb-id'
          )
        );
      }
    }
  );


  kbTableBody.addEventListener(
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

      openKnowledgeDetails(
        row.getAttribute(
          'data-kb-id'
        )
      );
    }
  );


  modalAnalyzeSimilarBtn.addEventListener(
    'click',
    event => {

      event.preventDefault();

      window.location.href =
        'bug-analyzer.html';
    }
  );


  /* ---------------------------------------------------------------------
     Backend API
     --------------------------------------------------------------------- */
async function loadKnowledgeBase() {

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
        `${API_BASE}/api/knowledge`,
        {
          headers: {
            Authorization:
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
        'Unable to load knowledge base.'
      );
    }

    // Store real backend knowledge
    allKnowledge =
      Array.isArray(data.entries)
        ? data.entries
        : [];

    currentPage = 1;

    // Populate everything while still hidden
    updateStatistics();

    renderRecentlyAdded();

    render();

    // Reveal only after real data is rendered
    revealKnowledgeBase();

  } catch (error) {

    console.error(
      'Knowledge Base error:',
      error
    );

    /*
     * Do not reveal empty/demo content
     * when the API request fails.
     */
    showKnowledgeBaseError();
  }
}

  /* ---------------------------------------------------------------------
     Initial load
     --------------------------------------------------------------------- */

  loadKnowledgeBase();

});