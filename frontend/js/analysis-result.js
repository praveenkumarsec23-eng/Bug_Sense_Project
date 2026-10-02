document.addEventListener('DOMContentLoaded', async () => {

  const API_BASE = window.BUGSENSE_CONFIG.API_BASE;

 let currentBugId = null;
let currentBug = null;
let currentAnalysis = null;
  // =====================================================
  // TOAST
  // =====================================================

  const toastEl = document.getElementById('resultToast');
  const toastMessage = document.getElementById('resultToastMessage');
  const toastIcon = document.getElementById('resultToastIcon');

  const bsToast = toastEl
    ? new bootstrap.Toast(toastEl, { delay: 3200 })
    : null;

  function showToast(message, type = 'success') {
    if (!toastEl || !bsToast) return;

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

  // =====================================================
  // HELPERS
  // =====================================================

  function setText(id, value, fallback = 'Not available') {
    const element = document.getElementById(id);

    if (!element) return;

    if (
      value === null ||
      value === undefined ||
      value === ''
    ) {
      element.textContent = fallback;
      return;
    }

    element.textContent = value;
  }

  function formatDate(dateString) {
    if (!dateString) {
      return 'Not available';
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return dateString;
    }

    return date.toLocaleDateString(
      'en-IN',
      {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      }
    );
  }

  function getConfidencePercent(confidence) {
    const value = Number(confidence || 0);

    if (Number.isNaN(value)) {
      return 0;
    }

    if (value <= 1) {
      return Math.round(value * 100);
    }

    return Math.round(value);
  }
// =====================================================
// ANALYSIS RESULT PAGE LOADING STATE
// =====================================================

const analysisResultContent =
  document.getElementById('analysisResultContent');

const analysisResultLoader =
  document.getElementById('analysisResultLoader');


function revealAnalysisResult() {

  if (!analysisResultContent) {
    return;
  }

  /*
   * Wait for the browser to paint the fully populated
   * result before revealing it.
   */
  requestAnimationFrame(() => {

    requestAnimationFrame(() => {

      analysisResultContent.classList.remove(
        'analysis-data-loading',
        'analysis-data-error'
      );

      analysisResultContent.classList.add(
        'analysis-data-ready'
      );

    });

  });
}


function showAnalysisResultError() {

  if (!analysisResultContent || !analysisResultLoader) {
    return;
  }

  analysisResultContent.classList.remove(
    'analysis-data-loading',
    'analysis-data-ready'
  );

  analysisResultContent.classList.add(
    'analysis-data-error'
  );

  analysisResultLoader.innerHTML = `
    <span class="analysis-result-loader__error-icon">
      <i class="bi bi-exclamation-triangle"></i>
    </span>

    <div class="analysis-result-loader__text">
      <strong>Could not load analysis result</strong>
      <span>Please refresh the page and try again.</span>
    </div>
  `;
}
  // =====================================================
  // SEVERITY
  // =====================================================

  function applySeverityBadge(element, severity) {
    if (!element) return;

    const value = severity || 'Unknown';

    element.textContent = value;
    element.className = 'badge-severity';

    const normalized = value.toLowerCase();

    if (
      [
        'critical',
        'high',
        'medium',
        'low'
      ].includes(normalized)
    ) {
      element.classList.add(
        `badge-severity--${normalized}`
      );
    }
  }

  function updateSeverityBadge(severity) {
    applySeverityBadge(
      document.getElementById('summarySeverity'),
      severity
    );
  }

  function updateSeverityAssessment(severity) {
    applySeverityBadge(
      document.getElementById('severityAssessmentValue'),
      severity
    );
  }

  // =====================================================
  // STATUS
  // =====================================================

  function updateStatusBadge(status) {
    const badge =
      document.getElementById('bugStatusBadge');

    if (!badge) return;

    const value = status || 'Analyzed';
    const normalized = value.toLowerCase();

    if (normalized === 'resolved') {
      badge.className =
        'badge-status badge-status--resolved';

      badge.innerHTML =
        '<i class="status-dot status-dot--green"></i>Resolved';

      return;
    }

    badge.className =
      'badge-status badge-status--ready';

    badge.innerHTML =
      `<i class="status-dot status-dot--green"></i>${value}`;
  }

  // =====================================================
  // AGENT COUNT
  // =====================================================

  function updateAgentsCompletedCount(analysis) {
    const agentsTag =
      document.getElementById('agentsCompletedTag');

    if (!agentsTag) return;

    let completed = 0;

    // Triage Agent
    if (
      analysis.bug_type ||
      analysis.priority ||
      analysis.triage_reason
    ) {
      completed++;
    }

    // Log Analysis Agent
    if (
      analysis.exception_type ||
      analysis.failure_file ||
      analysis.failure_line ||
      analysis.failure_function ||
      analysis.failure_code
    ) {
      completed++;
    }

    // Root Cause Agent
    if (
      analysis.root_cause &&
      analysis.root_cause.trim() !== ''
    ) {
      completed++;
    }

    // Duplicate Detection Agent
    if (
      analysis.duplicate_reason &&
      analysis.duplicate_reason !==
        'Duplicate detection was not performed.'
    ) {
      completed++;
    }

    // Remediation Agent
    if (
      (analysis.solution &&
        analysis.solution.trim() !== '') ||
      (analysis.fixed_code &&
        analysis.fixed_code.trim() !== '')
    ) {
      completed++;
    }

    agentsTag.textContent =
      `${completed} / 5 Agents Completed`;
  }

  // =====================================================
  // TRIAGE AGENT
  // =====================================================

  function updateTriageAgent(analysis, bug) {
    const status =
      document.getElementById('triageAgentStatus');

    const icon =
      document.getElementById('triageAgentIcon');

    if (status) {
      status.textContent = 'Completed';

      status.className =
        'badge-status badge-status--resolved';
    }

    if (icon) {
      icon.innerHTML =
        '<i class="bi bi-check-circle-fill"></i>';
    }

    const details = [];

    if (analysis.bug_type) {
      details.push(
        `Category: ${analysis.bug_type}`
      );
    }

    if (bug.severity) {
      details.push(
        `Severity: ${bug.severity}`
      );
    }

    if (analysis.priority) {
      details.push(
        `Priority: ${analysis.priority}`
      );
    }

    if (analysis.triage_reason) {
      details.push(
        `Reason: ${analysis.triage_reason}`
      );
    }

    setText(
      'triageAgentResult',
      details.join(' | '),
      'Triage analysis completed.'
    );
  }

  // =====================================================
  // LOG ANALYSIS AGENT
  // =====================================================

  function updateLogAnalysisAgent(analysis) {
    const status =
      document.getElementById('logAgentStatus');

    const icon =
      document.getElementById('logAgentIcon');

    const hasLogResult =
      analysis.exception_type ||
      analysis.failure_file ||
      analysis.failure_line ||
      analysis.failure_function ||
      analysis.failure_code;

    if (hasLogResult) {

      if (status) {
        status.textContent = 'Completed';

        status.className =
          'badge-status badge-status--resolved';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-check-circle-fill"></i>';
      }

      const details = [];

      if (analysis.exception_type) {
        details.push(
          `Exception: ${analysis.exception_type}`
        );
      }

      if (analysis.failure_file) {
        details.push(
          `File: ${analysis.failure_file}`
        );
      }

      if (analysis.failure_line) {
        details.push(
          `Line: ${analysis.failure_line}`
        );
      }

      if (analysis.failure_function) {
        details.push(
          `Function: ${analysis.failure_function}`
        );
      }

      setText(
        'logAgentResult',
        details.join(' | '),
        'Log analysis completed.'
      );

    } else {

      if (status) {
        status.textContent = 'No Data';
        status.className = 'badge-status';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-exclamation-circle"></i>';
      }

      setText(
        'logAgentResult',
        'No stack-trace information was detected.'
      );
    }

    setText(
      'failureFile',
      analysis.failure_file,
      'Not detected'
    );

    setText(
      'failureLine',
      analysis.failure_line,
      '—'
    );

    setText(
      'failureFunction',
      analysis.failure_function,
      'Not detected'
    );

    setText(
      'failureException',
      analysis.exception_type,
      'Not detected'
    );

    setText(
      'failureCodeSnippet',
      analysis.failure_code,
      'No failure code was detected.'
    );
  }

  // =====================================================
  // ROOT CAUSE AGENT
  // =====================================================

  function updateRootCauseAgent(analysis) {
    const status =
      document.getElementById('rootCauseAgentStatus');

    const icon =
      document.getElementById('rootCauseAgentIcon');

    const hasRootCause =
      analysis.root_cause &&
      analysis.root_cause.trim() !== '';

    if (hasRootCause) {

      if (status) {
        status.textContent = 'Completed';

        status.className =
          'badge-status badge-status--resolved';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-check-circle-fill"></i>';
      }

      setText(
        'rootCauseAgentResult',
        analysis.explanation ||
        analysis.root_cause,
        'Root cause analysis completed.'
      );

    } else {

      if (status) {
        status.textContent = 'Pending';
        status.className = 'badge-status';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-hourglass-split"></i>';
      }

      setText(
        'rootCauseAgentResult',
        'Root cause analysis was not requested or is not available.'
      );
    }

    setText(
      'rootCauseText',
      analysis.root_cause,
      'Root cause analysis is not available.'
    );

    const confidencePercent =
      getConfidencePercent(
        analysis.confidence
      );

    setText(
      'rootCauseConfidence',
      `${confidencePercent}%`
    );

    const rootCauseBar =
      document.getElementById(
        'rootCauseConfidenceBar'
      );

    if (rootCauseBar) {
      rootCauseBar.style.width =
        `${confidencePercent}%`;
    }

    setText(
      'confidenceRootCause',
      `${confidencePercent}%`
    );

    const rootCauseSummaryBar =
      document.getElementById(
        'confidenceRootCauseBar'
      );

    if (rootCauseSummaryBar) {
      rootCauseSummaryBar.style.width =
        `${confidencePercent}%`;
    }
  }

  // =====================================================
  // DUPLICATE DETECTION AGENT
  // =====================================================

  function updateDuplicateAgent(analysis) {
    const status =
      document.getElementById('duplicateAgentStatus');

    const icon =
      document.getElementById('duplicateAgentIcon');

    const result =
      document.getElementById('duplicateAgentResult');

    const similarTag =
      document.getElementById('similarBugsTag');

    const tableBody =
      document.getElementById('similarBugsTableBody');

    const confidenceText =
      document.getElementById('confidenceDuplicate');

    const confidenceBar =
      document.getElementById('confidenceDuplicateBar');

    const confidencePercent =
      getConfidencePercent(
        analysis.duplicate_confidence
      );

    const duplicateWasPerformed =
      analysis.duplicate_reason &&
      analysis.duplicate_reason !==
        'Duplicate detection was not performed.';

    if (duplicateWasPerformed) {

      if (status) {
        status.textContent = 'Completed';

        status.className =
          'badge-status badge-status--resolved';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-check-circle-fill"></i>';
      }

      if (similarTag) {
        similarTag.textContent =
          'RAG Retrieval';
      }

      const details = [];

      if (analysis.is_duplicate) {
        details.push(
          'Duplicate detected'
        );
      } else {
        details.push(
          'No duplicate detected'
        );
      }

      if (analysis.matched_bug_id) {
        details.push(
          `Closest match: BUG-${analysis.matched_bug_id}`
        );
      }

      details.push(
        `Duplicate confidence: ${confidencePercent}%`
      );

      if (analysis.duplicate_reason) {
        details.push(
          `Reason: ${analysis.duplicate_reason}`
        );
      }

      if (result) {
        result.textContent =
          details.join(' | ');
      }

    } else {

      if (status) {
        status.textContent = 'Pending';
        status.className =
          'badge-status';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-hourglass-split"></i>';
      }

      if (result) {
        result.textContent =
          'Duplicate detection was not performed.';
      }
    }

    if (confidenceText) {
      confidenceText.textContent =
        duplicateWasPerformed
          ? `${confidencePercent}%`
          : 'Pending';
    }

    if (confidenceBar) {
      confidenceBar.style.width =
        duplicateWasPerformed
          ? `${confidencePercent}%`
          : '0%';
    }

    if (!tableBody) {
      return;
    }

    tableBody.innerHTML = '';

    if (
      duplicateWasPerformed &&
      analysis.matched_bug_id &&
      analysis.matched_knowledge_id
    ) {

      const row =
        document.createElement('tr');

      const matchedKnowledge =
        analysis.matched_knowledge || {};

      const matchedTitle =
        matchedKnowledge.title ||
        `Knowledge Base Match KB-${analysis.matched_knowledge_id}`;

      row.innerHTML = `
        <td class="mono">
          BUG-${analysis.matched_bug_id}
        </td>

        <td>
          ${matchedTitle}
        </td>

        <td>
          ${confidencePercent}%
        </td>

        <td>
         <span class="badge-status badge-status--resolved">
    Related Bug
</span> 
        </td>

        <td class="text-end">
          <button
            type="button"
            class="btn btn-ghost btn-sm"
            id="viewKnowledgeMatchBtn"
          >
            KB-${analysis.matched_knowledge_id}
          </button>
        </td>
      `;

      tableBody.appendChild(row);

      const viewButton =
        document.getElementById(
          'viewKnowledgeMatchBtn'
        );

      if (viewButton) {
        viewButton.addEventListener(
          'click',
          () => {
            window.location.href =
              'knowledge-base.html';
          }
        );
      }

      return;
    }

    const row =
      document.createElement('tr');

    row.innerHTML = `
      <td colspan="5">
        <div class="result-empty-state">

          <i class="bi bi-database-search"></i>

          <div>

            <strong>
              No duplicate historical bug detected.
            </strong>

            <p>
              No Knowledge Base entry exceeded the
              configured duplicate threshold.
            </p>

          </div>

        </div>
      </td>
    `;

    tableBody.appendChild(row);
  }

  // =====================================================
  // REMEDIATION AGENT
  // =====================================================

  function updateRemediationAgent(analysis) {
    const status =
      document.getElementById(
        'remediationAgentStatus'
      );

    const icon =
      document.getElementById(
        'remediationAgentIcon'
      );

    const result =
      document.getElementById(
        'remediationAgentResult'
      );

    const recommendedFixTag =
      document.getElementById(
        'recommendedFixTag'
      );

    const confidenceText =
      document.getElementById(
        'confidenceFix'
      );

    const confidenceBar =
      document.getElementById(
        'confidenceFixBar'
      );

    const hasSolution =
      analysis.solution &&
      analysis.solution.trim() !== '';

    const hasFixedCode =
      analysis.fixed_code &&
      analysis.fixed_code.trim() !== '';

    const remediationCompleted =
      hasSolution || hasFixedCode;

    if (remediationCompleted) {

      if (status) {
        status.textContent =
          'Completed';

        status.className =
          'badge-status badge-status--resolved';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-check-circle-fill"></i>';
      }

      if (result) {
        result.textContent =
          analysis.solution ||
          'Fix recommendation generated successfully.';
      }

      if (recommendedFixTag) {
        recommendedFixTag.textContent =
          'Remediation Agent';
      }

      if (confidenceText) {
        confidenceText.textContent =
          'Generated';
      }

      if (confidenceBar) {
        confidenceBar.style.width =
          '100%';
      }

    } else {

      if (status) {
        status.textContent =
          'Pending';

        status.className =
          'badge-status';
      }

      if (icon) {
        icon.innerHTML =
          '<i class="bi bi-hourglass-split"></i>';
      }

      if (result) {
        result.textContent =
          'Fix recommendation was not generated.';
      }

      if (recommendedFixTag) {
        recommendedFixTag.textContent =
          'Pending Remediation';
      }

      if (confidenceText) {
        confidenceText.textContent =
          'Pending';
      }

      if (confidenceBar) {
        confidenceBar.style.width =
          '0%';
      }
    }

    setText(
      'recommendedFixText',
      analysis.solution,
      'Fix recommendation is not available.'
    );

    setText(
      'fixCodeAfter',
      analysis.fixed_code,
      'Corrected code is not available.'
    );

    const recommendationReason =
      document.getElementById(
        'recommendationReason'
      );

    if (recommendationReason) {

      if (remediationCompleted) {

        recommendationReason.textContent =
          'The Remediation Agent generated this recommendation using the detected exception, failure point, root cause, submitted code, and relevant historical knowledge-base context.';

      } else {

        recommendationReason.textContent =
          'Remediation reasoning is not available because a fix recommendation was not generated.';
      }
    }

    const copyButton =
      document.getElementById(
        'copyFixBtn'
      );

    if (copyButton) {
      copyButton.disabled =
        !hasFixedCode;
    }
  }

  // =====================================================
  // POPULATE PAGE
  // =====================================================

  function populateResult(data) {

    const bug = data.bug || {};
const analysis = data.analysis || {};

currentBugId = bug.id || null;
currentBug = bug;
currentAnalysis = analysis;

    // ===================================================
    // BUG SUMMARY
    // ===================================================

    setText(
      'resultBugId',
      bug.bug_id
    );

    setText(
      'summaryBugId',
      bug.bug_id
    );

    setText(
      'summaryBugTitle',
      bug.title
    );

    setText(
      'summaryLanguage',
      bug.language
    );

    setText(
      'summaryCategory',
      analysis.bug_type,
      'Uncategorized'
    );

    updateSeverityBadge(
      bug.severity
    );

    setText(
      'summaryPriority',
      analysis.priority,
      'Not available'
    );

    updateStatusBadge(
      bug.status
    );

    setText(
      'summarySubmitted',
      formatDate(bug.created_at)
    );

    setText(
      'summaryDataTag',
      'Database'
    );

    // ===================================================
    // AGENT 1 - TRIAGE
    // ===================================================

    updateTriageAgent(
      analysis,
      bug
    );

    // ===================================================
    // AGENT 2 - LOG ANALYSIS
    // ===================================================

    updateLogAnalysisAgent(
      analysis
    );

    // ===================================================
    // AGENT 3 - ROOT CAUSE
    // ===================================================

    updateRootCauseAgent(
      analysis
    );

    // ===================================================
    // AGENT 4 - DUPLICATE DETECTION
    // ===================================================

    updateDuplicateAgent(
      analysis
    );

    // ===================================================
    // AGENT 5 - REMEDIATION
    // ===================================================

    updateRemediationAgent(
      analysis
    );

    // ===================================================
    // COMPLETED AGENT COUNT
    // ===================================================

    updateAgentsCompletedCount(
      analysis
    );

    // ===================================================
    // SEVERITY ASSESSMENT
    // ===================================================

    updateSeverityAssessment(
      bug.severity
    );

    setText(
      'priorityAssessmentValue',
      analysis.priority,
      'Not available'
    );

    setText(
      'impactAssessmentValue',
      analysis.triage_reason,
      'Triage impact information is not available.'
    );

    setText(
      'severityAssessmentExplanation',
      analysis.triage_reason,
      'Triage assessment completed.'
    );

    // ===================================================
    // ORIGINAL CODE
    // ===================================================

    setText(
      'originalCodeBefore',
      bug.code,
      'No source code was submitted.'
    );

    // ===================================================
    // RESOLVED BUTTON
    // ===================================================

    const resolvedButton =
      document.getElementById(
        'markResolvedBtn'
      );

    if (
      resolvedButton &&
      (bug.status || '')
        .toLowerCase() === 'resolved'
    ) {
      resolvedButton.disabled = true;

      resolvedButton.innerHTML =
        '<i class="bi bi-check2-circle"></i> Resolved';
    }
  }

  // =====================================================
  // LOAD RESULT
  // =====================================================

  async function loadResult() {

  const params =
    new URLSearchParams(
      window.location.search
    );

  const bugId =
    params.get('id');

  // ---------------------------------------------------
  // Validate Bug ID
  // ---------------------------------------------------

  if (!bugId) {

    console.error(
      'Bug ID is missing from the URL.'
    );

    showAnalysisResultError();

    showToast(
      'Bug ID is missing from the URL.',
      'error'
    );

    return;
  }

  currentBugId = bugId;

  // ---------------------------------------------------
  // Authentication
  // ---------------------------------------------------

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

    // -------------------------------------------------
    // Fetch complete bug + analysis
    // -------------------------------------------------

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

    // -------------------------------------------------
    // Authentication expired / invalid
    // -------------------------------------------------

    if (response.status === 401) {

      localStorage.removeItem(
        'bugsense_token'
      );

      window.location.href =
        'index.html';

      return;
    }

    // -------------------------------------------------
    // Bug does not exist
    // -------------------------------------------------

    if (response.status === 404) {

      throw new Error(
        'Bug analysis could not be found.'
      );
    }

    // -------------------------------------------------
    // Parse response
    // -------------------------------------------------

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
        'Unable to load analysis result.'
      );
    }

   
    // -------------------------------------------------
    // Populate EVERYTHING while content is hidden
    // -------------------------------------------------

    populateResult(data);

    // -------------------------------------------------
    // Reveal only after DOM contains real API data
    // -------------------------------------------------

    revealAnalysisResult();

  } catch (error) {

    console.error(
      'Failed to load analysis:',
      error
    );

    /*
     * Do NOT reveal placeholder/demo content when the
     * backend request fails.
     */
    showAnalysisResultError();

    showToast(
      error.message ||
      'Unable to load analysis result.',
      'error'
    );
  }
}

  // =====================================================
  // COPY FIX
  // =====================================================

  const copyFixBtn =
    document.getElementById(
      'copyFixBtn'
    );

  if (copyFixBtn) {

    copyFixBtn.addEventListener(
      'click',
      async () => {

        if (
          !currentAnalysis ||
          !currentAnalysis.fixed_code
        ) {
          showToast(
            'No generated fix is available.',
            'error'
          );

          return;
        }

        const code =
          currentAnalysis.fixed_code;

        try {

          if (
            navigator.clipboard &&
            window.isSecureContext
          ) {

            await navigator.clipboard
              .writeText(code);

          } else {

            const textarea =
              document.createElement(
                'textarea'
              );

            textarea.value = code;

            textarea.style.position =
              'fixed';

            textarea.style.opacity =
              '0';

            document.body
              .appendChild(textarea);

            textarea.focus();
            textarea.select();

            document.execCommand(
              'copy'
            );

            document.body
              .removeChild(textarea);
          }

          showToast(
            'Fix copied to clipboard.'
          );

        } catch (error) {

          console.error(error);

          showToast(
            'Could not copy the fix.',
            'error'
          );
        }
      }
    );
  }
 // =====================================================
// MARK AS RESOLVED
// =====================================================

const markResolvedBtn =
  document.getElementById('markResolvedBtn');

if (markResolvedBtn) {

  markResolvedBtn.addEventListener(
    'click',
    async (event) => {

      event.preventDefault();
      event.stopPropagation();

      if (!currentBugId) {
        showToast(
          'Bug ID is missing.',
          'error'
        );
        return;
      }

      const token =
        localStorage.getItem('bugsense_token');

      if (!token) {
        window.location.href = 'index.html';
        return;
      }

      const originalHTML =
        markResolvedBtn.innerHTML;

      try {

        // Loading state
        markResolvedBtn.disabled = true;

        markResolvedBtn.innerHTML = `
          <span
            class="spinner-border spinner-border-sm me-2"
            role="status"
            aria-hidden="true">
          </span>
          Resolving...
        `;

        // Update backend
        const response =
          await fetch(
            `${API_BASE}/api/bugs/${currentBugId}/resolve`,
            {
              method: 'POST',

              headers: {
                'Authorization':
                  `Bearer ${token}`
              }
            }
          );

        let data = {};

        try {
          data = await response.json();
        } catch (jsonError) {
          data = {};
        }

        if (!response.ok) {
          throw new Error(
            data.detail ||
            'Unable to mark bug as resolved.'
          );
        }

        // Update local state immediately
        if (currentBug) {
          currentBug.status = 'Resolved';
        }

        // Update status badge immediately
        updateStatusBadge('Resolved');

        // Update button immediately
        markResolvedBtn.disabled = true;

        markResolvedBtn.innerHTML =
          '<i class="bi bi-check2-circle"></i> Resolved';

        // Success message
        showToast(
          data.message ||
          'Bug marked as resolved successfully.',
          'success'
        );

      } catch (error) {

        console.error(
          'Failed to resolve bug:',
          error
        );

        // Restore button only when request failed
        markResolvedBtn.disabled = false;
        markResolvedBtn.innerHTML =
          originalHTML;

        showToast(
          error.message ||
          'Unable to mark bug as resolved.',
          'error'
        );
      }
    }
  );
}
  // =====================================================
  // VIEW DETAILS
  // =====================================================

  const viewDetailsBtn =
    document.getElementById(
      'viewDetailsBtn'
    );

  if (viewDetailsBtn) {

    viewDetailsBtn.addEventListener(
      'click',
      () => {

        if (
          currentAnalysis &&
          currentAnalysis.solution
        ) {

          showToast(
            'The recommendation was generated by the Remediation Agent using the current bug analysis.'
          );

        } else {

          showToast(
            'Remediation details are not available.',
            'error'
          );
        }
      }
    );
  }

 // =========================================================
// RE-ANALYZE CURRENT BUG
// =========================================================

const reanalyzeBtn = document.getElementById("reanalyzeBtn");

if (reanalyzeBtn) {
    reanalyzeBtn.addEventListener("click", async (event) => {
        event.preventDefault();

        if (!currentBugId) {
            showToast(
                "Unable to re-analyze because the Bug ID is missing.",
                "danger"
            );
            return;
        }

        const originalHTML = reanalyzeBtn.innerHTML;

        try {
            // -------------------------------------------------
            // Loading state
            // -------------------------------------------------

            reanalyzeBtn.disabled = true;

            reanalyzeBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"></span>
                Re-analyzing...
            `;

            // -------------------------------------------------
            // Re-run backend multi-agent pipeline
            // -------------------------------------------------

           const response = await fetch(
 `${API_BASE}/api/bugs/${currentBugId}/reanalyze`,
                {
                    method: "POST",
                    headers: {
    "Authorization": `Bearer ${localStorage.getItem("bugsense_token")}`
}
                }
            );

            let data = {};

            try {
                data = await response.json();
            } catch (jsonError) {
                data = {};
            }

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Failed to re-analyze the bug."
                );
            }

            // -------------------------------------------------
            // Success
            // -------------------------------------------------

            showToast(
                data.message || "Bug re-analyzed successfully.",
                "success"
            );

            // Reload the same analysis result.
            // BUG-38 remains BUG-38.
            await loadResult();

        } catch (error) {
            console.error("Re-analysis failed:", error);

            showToast(
                error.message ||
                "Unable to re-analyze the bug.",
                "danger"
            );

        } finally {
            reanalyzeBtn.disabled = false;
            reanalyzeBtn.innerHTML = originalHTML;
        }
    });
}
 // =====================================================
// EXPORT REPORT
// =====================================================

function escapeReportHtml(value) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return 'Not available';
  }

  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


function buildBugSenseReport() {

  if (!currentBug || !currentAnalysis) {
    return null;
  }

  const bug = currentBug;
  const analysis = currentAnalysis;

  const bugDisplayId =
    bug.bug_id ||
    (bug.id ? `BUG-${bug.id}` : 'Not available');

  const rootConfidence =
    getConfidencePercent(
      analysis.confidence
    );

  const duplicateConfidence =
    getConfidencePercent(
      analysis.duplicate_confidence
    );

  const duplicateStatus =
    analysis.is_duplicate
      ? 'Possible duplicate detected'
      : 'No duplicate detected';

  const matchedBug =
    analysis.matched_bug_id
      ? `BUG-${analysis.matched_bug_id}`
      : 'No matching bug';

  const matchedKnowledge =
    analysis.matched_knowledge_id
      ? `KB-${analysis.matched_knowledge_id}`
      : 'No matching knowledge entry';

  const generatedAt =
    new Date().toLocaleString(
      'en-IN',
      {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }
    );

  return `
<!DOCTYPE html>
<html lang="en">

<head>

  <meta charset="UTF-8">

  <title>
    ${escapeReportHtml(bugDisplayId)} - BugSense Analysis Report
  </title>

  <style>

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      padding: 40px;
      background: #ffffff;
      color: #1f2937;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 13px;
      line-height: 1.6;
    }

    .report {
      max-width: 900px;
      margin: 0 auto;
    }

    .report-header {
      border-bottom: 3px solid #111827;
      padding-bottom: 20px;
      margin-bottom: 28px;
    }

    .brand {
      font-size: 26px;
      font-weight: 700;
      margin: 0;
      color: #111827;
    }

    .brand-subtitle {
      margin: 4px 0 0;
      color: #6b7280;
      font-size: 13px;
    }

    .report-title {
      margin: 24px 0 5px;
      font-size: 21px;
      color: #111827;
    }

    .report-meta {
      color: #6b7280;
      margin: 0;
    }

    .section {
      margin-top: 28px;
      page-break-inside: avoid;
    }

    .section-title {
      font-size: 16px;
      font-weight: 700;
      color: #111827;
      padding-bottom: 7px;
      margin-bottom: 12px;
      border-bottom: 1px solid #d1d5db;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px 24px;
    }

    .summary-item {
      border-bottom: 1px solid #e5e7eb;
      padding: 7px 0;
    }

    .label {
      display: block;
      color: #6b7280;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      margin-bottom: 2px;
    }

    .value {
      color: #111827;
      font-weight: 500;
    }

    .agent {
      border: 1px solid #d1d5db;
      border-radius: 6px;
      padding: 12px 14px;
      margin-bottom: 10px;
      page-break-inside: avoid;
    }

    .agent-name {
      font-weight: 700;
      color: #111827;
      margin-bottom: 5px;
    }

    .agent-result {
      color: #374151;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .text-block {
      color: #374151;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    .code {
      background: #f3f4f6;
      border: 1px solid #d1d5db;
      border-radius: 5px;
      padding: 12px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-family: "Courier New", monospace;
      font-size: 11px;
      color: #111827;
    }

    .confidence {
      margin-top: 8px;
      font-weight: 700;
    }

    .footer {
      margin-top: 35px;
      padding-top: 15px;
      border-top: 1px solid #d1d5db;
      color: #6b7280;
      font-size: 10px;
      line-height: 1.5;
    }

    .no-print {
      margin-bottom: 25px;
      text-align: right;
    }

    .print-button {
      border: none;
      border-radius: 5px;
      padding: 9px 16px;
      background: #111827;
      color: #ffffff;
      font-weight: 700;
      cursor: pointer;
    }

    @media print {

      body {
        padding: 0;
      }

      .no-print {
        display: none;
      }

      .section,
      .agent,
      .code {
        page-break-inside: avoid;
      }

      @page {
        size: A4;
        margin: 15mm;
      }
    }

  </style>

</head>

<body>

<div class="report">

  <div class="no-print">
    <button
      class="print-button"
      onclick="window.print()"
    >
      Save / Print PDF
    </button>
  </div>

  <header class="report-header">

    <h1 class="brand">
      BugSense
    </h1>

    <p class="brand-subtitle">
      AI Smart Bug Analyzer &amp; Fix Advisor
    </p>

    <h2 class="report-title">
      Bug Analysis Report
    </h2>

    <p class="report-meta">
      ${escapeReportHtml(bugDisplayId)}
      &nbsp; | &nbsp;
      Generated ${escapeReportHtml(generatedAt)}
    </p>

  </header>


  <!-- BUG SUMMARY -->

  <section class="section">

    <div class="section-title">
      1. Bug Summary
    </div>

    <div class="summary-grid">

      <div class="summary-item">
        <span class="label">Bug ID</span>
        <span class="value">
          ${escapeReportHtml(bugDisplayId)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Title</span>
        <span class="value">
          ${escapeReportHtml(bug.title)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Language</span>
        <span class="value">
          ${escapeReportHtml(bug.language)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Category</span>
        <span class="value">
          ${escapeReportHtml(analysis.bug_type)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Severity</span>
        <span class="value">
          ${escapeReportHtml(bug.severity)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Priority</span>
        <span class="value">
          ${escapeReportHtml(analysis.priority)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Status</span>
        <span class="value">
          ${escapeReportHtml(bug.status)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Submitted</span>
        <span class="value">
          ${escapeReportHtml(formatDate(bug.created_at))}
        </span>
      </div>

    </div>

  </section>


  <!-- TRIAGE -->

  <section class="section">

    <div class="section-title">
      2. Multi-Agent Analysis
    </div>

    <div class="agent">

      <div class="agent-name">
        Triage Agent
      </div>

      <div class="agent-result">
Category: ${escapeReportHtml(analysis.bug_type)}
Severity: ${escapeReportHtml(bug.severity)}
Priority: ${escapeReportHtml(analysis.priority)}
Reason: ${escapeReportHtml(analysis.triage_reason)}
      </div>

    </div>


    <!-- LOG ANALYSIS -->

    <div class="agent">

      <div class="agent-name">
        Log Analysis Agent
      </div>

      <div class="agent-result">
Exception: ${escapeReportHtml(analysis.exception_type)}
File: ${escapeReportHtml(analysis.failure_file)}
Line: ${escapeReportHtml(analysis.failure_line)}
Function: ${escapeReportHtml(analysis.failure_function)}
      </div>

    </div>


    <!-- ROOT CAUSE -->

    <div class="agent">

      <div class="agent-name">
        Root Cause Agent
      </div>

      <div class="agent-result">
${escapeReportHtml(
  analysis.explanation ||
  analysis.root_cause
)}
      </div>

    </div>


    <!-- DUPLICATE DETECTION -->

    <div class="agent">

      <div class="agent-name">
        Duplicate Detection Agent
      </div>

      <div class="agent-result">
Result: ${escapeReportHtml(duplicateStatus)}
Closest Bug: ${escapeReportHtml(matchedBug)}
Knowledge Entry: ${escapeReportHtml(matchedKnowledge)}
Duplicate Confidence: ${duplicateConfidence}%
Reason: ${escapeReportHtml(analysis.duplicate_reason)}
      </div>

    </div>


    <!-- REMEDIATION -->

    <div class="agent">

      <div class="agent-name">
        Remediation Agent
      </div>

      <div class="agent-result">
${escapeReportHtml(analysis.solution)}
      </div>

    </div>

  </section>


  <!-- FAILURE POINT -->

  <section class="section">

    <div class="section-title">
      3. Failure Point
    </div>

    <div class="summary-grid">

      <div class="summary-item">
        <span class="label">Exception</span>
        <span class="value">
          ${escapeReportHtml(analysis.exception_type)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">File</span>
        <span class="value">
          ${escapeReportHtml(analysis.failure_file)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Line</span>
        <span class="value">
          ${escapeReportHtml(analysis.failure_line)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Function</span>
        <span class="value">
          ${escapeReportHtml(analysis.failure_function)}
        </span>
      </div>

    </div>

    <p class="label" style="margin-top: 15px;">
      Detected Failure Code
    </p>

    <pre class="code">${escapeReportHtml(
      analysis.failure_code
    )}</pre>

  </section>


  <!-- ROOT CAUSE -->

  <section class="section">

    <div class="section-title">
      4. Probable Root Cause
    </div>

    <div class="text-block">
      ${escapeReportHtml(analysis.root_cause)}
    </div>

    <div class="confidence">
      Root Cause Confidence:
      ${rootConfidence}%
    </div>

  </section>


  <!-- HISTORICAL MATCH -->

  <section class="section">

    <div class="section-title">
      5. Semantic Knowledge Retrieval
    </div>

    <div class="text-block">
      ${escapeReportHtml(duplicateStatus)}
    </div>

    <div class="summary-grid">

      <div class="summary-item">
        <span class="label">Closest Historical Bug</span>
        <span class="value">
          ${escapeReportHtml(matchedBug)}
        </span>
      </div>

      <div class="summary-item">
        <span class="label">Knowledge Entry</span>
        <span class="value">
          ${escapeReportHtml(matchedKnowledge)}
        </span>
      </div>

      <div class="summary-item">
       <span class="label">Duplicate Confidence</span>
        <span class="value">
          ${duplicateConfidence}%
        </span>
      </div>

    </div>

    <p class="text-block">
      ${escapeReportHtml(analysis.duplicate_reason)}
    </p>

  </section>


  <!-- ORIGINAL CODE -->

  <section class="section">

    <div class="section-title">
      6. Submitted Source Code
    </div>

    <pre class="code">${escapeReportHtml(
      bug.code
    )}</pre>

  </section>


  <!-- RECOMMENDED FIX -->

  <section class="section">

    <div class="section-title">
      7. Recommended Fix
    </div>

    <div class="text-block">
      ${escapeReportHtml(analysis.solution)}
    </div>

    <p class="label" style="margin-top: 15px;">
      Corrected Code
    </p>

    <pre class="code">${escapeReportHtml(
      analysis.fixed_code
    )}</pre>

  </section>


  <!-- CONFIDENCE -->

  <section class="section">

    <div class="section-title">
      8. Analysis Confidence
    </div>

    <div class="summary-grid">

      <div class="summary-item">
        <span class="label">
          Root Cause Analysis
        </span>

        <span class="value">
          ${rootConfidence}%
        </span>
      </div>

      <div class="summary-item">
        <span class="label">
          Duplicate Detection
        </span>

        <span class="value">
          ${duplicateConfidence}%
        </span>
      </div>

      <div class="summary-item">
        <span class="label">
          Fix Recommendation
        </span>

        <span class="value">
          ${
            analysis.solution ||
            analysis.fixed_code
              ? 'Generated'
              : 'Not available'
          }
        </span>
      </div>

    </div>

  </section>


  <footer class="footer">

    <strong>BugSense — AI Smart Bug Analyzer &amp; Fix Advisor</strong>

    <br><br>

    This report was generated from BugSense multi-agent analysis
    and semantic knowledge-base retrieval.

    Generated recommendations should be reviewed before being
    applied to production code.

    <br><br>

    Report generated:
    ${escapeReportHtml(generatedAt)}

  </footer>

</div>

</body>

</html>
  `;
}


const exportReportBtn =
  document.getElementById(
    'exportReportBtn'
  );

if (exportReportBtn) {

  exportReportBtn.addEventListener(
    'click',
    () => {

      if (!currentBug || !currentAnalysis) {

        showToast(
          'Analysis data is not available for export.',
          'error'
        );

        return;
      }

      const reportHtml =
        buildBugSenseReport();

      if (!reportHtml) {

        showToast(
          'Unable to generate the report.',
          'error'
        );

        return;
      }

      const reportWindow =
        window.open(
          '',
          '_blank'
        );

      if (!reportWindow) {

        showToast(
          'Popup was blocked. Please allow popups to export the report.',
          'error'
        );

        return;
      }

      reportWindow.document.open();
      reportWindow.document.write(reportHtml);
      reportWindow.document.close();

      reportWindow.focus();

      showToast(
        'BugSense report generated successfully.'
      );
    }
  );
}
  // =====================================================
  // START
  // =====================================================

  await loadResult();

});