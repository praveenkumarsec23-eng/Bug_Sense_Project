/* ==========================================================================
   BugSense — Bug Analyzer
   Connected to FastAPI backend
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  const API_BASE = window.BUGSENSE_CONFIG.API_BASE;

  // =====================================================
  // FORM ELEMENTS
  // =====================================================

  const form =
    document.getElementById('bugAnalyzerForm');

  const formAlert =
    document.getElementById('formAlert');

  const formAlertText =
    document.getElementById('formAlertText');

  const bugTitle =
    document.getElementById('bugTitle');

  const programmingLanguage =
    document.getElementById('programmingLanguage');

  const bugDescription =
    document.getElementById('bugDescription');

  const errorMessage =
    document.getElementById('errorMessage');

  const stackTrace =
    document.getElementById('stackTrace');

  const sourceCode =
    document.getElementById('sourceCode');

  const clearFormBtn =
    document.getElementById('clearFormBtn');

   // =====================================================
  // FILE UPLOAD
  // =====================================================

  const dropzone =
    document.getElementById('uploadDropzone');

  const fileInput =
    document.getElementById('fileInput');

  const uploadError =
    document.getElementById('uploadError');

  const filePreview =
    document.getElementById('uploadFilePreview');

  const fileNameEl =
    document.getElementById('uploadFileName');

  const fileSizeEl =
    document.getElementById('uploadFileSize');

  const removeFileBtn =
    document.getElementById('uploadFileRemove');

  const ALLOWED_EXTENSIONS = [
    '.py',
    '.java',
    '.js',
    '.ts',
    '.c',
    '.cpp',
    '.cc',
    '.cxx',
    '.cs',
    '.php'
  ];

  const MAX_FILE_SIZE_BYTES =
    1 * 1024 * 1024;

  let selectedFile = null;

  function formatFileSize(bytes) {

    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(2)} MB`;
  }

  function getExtension(filename) {

    const index =
      filename.lastIndexOf('.');

    return index === -1
      ? ''
      : filename
          .slice(index)
          .toLowerCase();
  }

  function showUploadError(message) {

    if (!uploadError) return;

    uploadError.textContent =
      message;

    uploadError.hidden =
      false;
  }

  function clearUploadError() {

    if (!uploadError) return;

    uploadError.hidden =
      true;

    uploadError.textContent =
      '';
  }

  function showFilePreview(
    filename,
    size
  ) {

    if (fileNameEl) {
      fileNameEl.textContent =
        filename;
    }

    if (fileSizeEl) {
      fileSizeEl.textContent =
        `Size: ${formatFileSize(size)}`;
    }

    if (filePreview) {
      filePreview.hidden =
        false;
    }

    if (dropzone) {
      dropzone.hidden =
        true;
    }
  }

  function resetUpload() {

    selectedFile =
      null;

    if (fileInput) {
      fileInput.value = '';
    }

    if (filePreview) {
      filePreview.hidden = true;
    }

    if (dropzone) {
      dropzone.hidden = false;
    }

    clearUploadError();
  }

  // =====================================================
  // UPLOAD SOURCE FILE TO BACKEND
  // =====================================================

  async function uploadSourceFile(file) {

    const token =
      localStorage.getItem(
        'bugsense_token'
      );

    if (!token) {
      window.location.href =
        'index.html';
      return null;
    }

    const formData =
      new FormData();

    formData.append(
      'file',
      file
    );

    const response =
      await fetch(
        `${API_BASE}/api/bugs/upload-source`,
        {
          method: 'POST',

          headers: {
            'Authorization':
              `Bearer ${token}`
          },

          body: formData
        }
      );

    if (response.status === 401) {

      localStorage.removeItem(
        'bugsense_token'
      );

      window.location.href =
        'index.html';

      return null;
    }

    const data =
      await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail ||
        'Unable to upload source file.'
      );
    }

    return data;
  }

  // =====================================================
  // HANDLE SOURCE FILE
  // =====================================================

  async function handleFile(file) {

    clearUploadError();

    if (!file) return;

    const extension =
      getExtension(file.name);

    if (
      !ALLOWED_EXTENSIONS.includes(
        extension
      )
    ) {

      showUploadError(
        'Unsupported source file type.'
      );

      selectedFile = null;

      if (fileInput) {
        fileInput.value = '';
      }

      return;
    }

    if (
      file.size >
      MAX_FILE_SIZE_BYTES
    ) {

      showUploadError(
        'Source file is too large. Maximum allowed size is 1 MB.'
      );

      selectedFile = null;

      if (fileInput) {
        fileInput.value = '';
      }

      return;
    }

    try {

      const data =
        await uploadSourceFile(file);

      if (
        !data ||
        !data.file
      ) {
        return;
      }

      selectedFile =
        file;

      // Fill source-code textarea
      sourceCode.value =
        data.file.code || '';

      // Automatically select detected language
      programmingLanguage.value =
        data.file.language || '';

      // Show uploaded file information
      showFilePreview(
        data.file.filename,
        data.file.size
      );

      clearUploadError();

    } catch (error) {

      console.error(
        'Source upload failed:',
        error
      );

      selectedFile = null;

      if (fileInput) {
        fileInput.value = '';
      }

      showUploadError(
        error.message ||
        'Unable to process source file.'
      );
    }
  }

  // =====================================================
  // FILE EVENTS
  // =====================================================

  if (
    dropzone &&
    fileInput
  ) {

    dropzone.addEventListener(
      'click',
      () => {
        fileInput.click();
      }
    );

    dropzone.addEventListener(
      'keydown',
      (event) => {

        if (
          event.key === 'Enter' ||
          event.key === ' '
        ) {

          event.preventDefault();

          fileInput.click();
        }
      }
    );

    fileInput.addEventListener(
      'change',
      async () => {

        if (
          fileInput.files &&
          fileInput.files[0]
        ) {

          await handleFile(
            fileInput.files[0]
          );
        }
      }
    );

    [
      'dragenter',
      'dragover'
    ].forEach(
      (eventName) => {

        dropzone.addEventListener(
          eventName,
          (event) => {

            event.preventDefault();
            event.stopPropagation();

            dropzone.classList.add(
              'is-dragover'
            );
          }
        );
      }
    );

    [
      'dragleave',
      'dragend'
    ].forEach(
      (eventName) => {

        dropzone.addEventListener(
          eventName,
          (event) => {

            event.preventDefault();
            event.stopPropagation();

            dropzone.classList.remove(
              'is-dragover'
            );
          }
        );
      }
    );

    dropzone.addEventListener(
      'drop',
      async (event) => {

        event.preventDefault();
        event.stopPropagation();

        dropzone.classList.remove(
          'is-dragover'
        );

        if (
          event.dataTransfer.files &&
          event.dataTransfer.files[0]
        ) {

          await handleFile(
            event.dataTransfer.files[0]
          );
        }
      }
    );
  }

  if (removeFileBtn) {

    removeFileBtn.addEventListener(
      'click',
      (event) => {

        event.stopPropagation();

        resetUpload();
      }
    );
  }

  // =====================================================
  // FORM ALERT
  // =====================================================

  function showFormAlert(message) {

    if (
      !formAlert ||
      !formAlertText
    ) {
      return;
    }

    formAlertText.textContent =
      message;

    formAlert.hidden =
      false;

    formAlert.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    });
  }

  function hideFormAlert() {

    if (!formAlert) return;

    formAlert.hidden =
      true;
  }

  // =====================================================
  // VALIDATION
  // =====================================================

  function hasAnyBugContent() {

    return Boolean(
      bugDescription.value.trim() ||
      errorMessage.value.trim() ||
      stackTrace.value.trim() ||
      sourceCode.value.trim() ||
      selectedFile
    );
  }

  function validateForm() {

    let isValid =
      true;

    if (!form.checkValidity()) {

      form.classList.add(
        'was-validated'
      );

      isValid =
        false;

    } else {

      form.classList.remove(
        'was-validated'
      );
    }

    if (!hasAnyBugContent()) {

      showFormAlert(
        'Please provide bug details or upload a file.'
      );

      isValid =
        false;

    } else {

      hideFormAlert();
    }

    return isValid;
  }

  // =====================================================
  // CLEAR FORM
  // =====================================================

  if (clearFormBtn) {

    clearFormBtn.addEventListener(
      'click',
      () => {

        form.reset();

        form.classList.remove(
          'was-validated'
        );

        hideFormAlert();

        resetUpload();

        [
          'optRootCause',
          'optSimilarBugs',
          'optFixRecommendation',
          'optDuplicateDetection'
        ].forEach(
          (id) => {

            const option =
              document.getElementById(id);

            if (option) {
              option.checked =
                true;
            }
          }
        );

        bugTitle.focus();
      }
    );
  }

  // =====================================================
  // ANALYSIS OVERLAY
  // =====================================================

  const overlay =
    document.getElementById(
      'analyzeOverlay'
    );

  const overlayStatusText =
    document.getElementById(
      'analyzeStatusText'
    );

  const AGENT_SEQUENCE = [
    'triage',
    'logAnalysis',
    'rootCause',
    'duplicate',
    'remediation'
  ];

  function setAgentState(
    agentKey,
    state
  ) {

    const icon =
      document.getElementById(
        `agentIcon-${agentKey}`
      );

    const status =
      document.getElementById(
        `agentStatus-${agentKey}`
      );

    if (
      !icon ||
      !status
    ) {
      return;
    }

    if (state === 'waiting') {

      icon.innerHTML =
        '<i class="bi bi-circle"></i>';

      status.textContent =
        'Waiting';

      status.className =
        'badge-status';

    } else if (
      state === 'running'
    ) {

      icon.innerHTML =
        '<i class="bi bi-arrow-repeat"></i>';

      status.textContent =
        'Running';

      status.className =
        'badge-status badge-status--analyzing';

    } else if (
      state === 'ready'
    ) {

      icon.innerHTML =
        '<i class="bi bi-check-circle-fill"></i>';

      status.textContent =
        'Ready';

      status.className =
        'badge-status badge-status--ready';
    }
  }

  function resetOverlay() {

    if (overlayStatusText) {

      overlayStatusText.textContent =
        'Preparing analysis…';
    }

    AGENT_SEQUENCE.forEach(
      (key) => {

        setAgentState(
          key,
          'waiting'
        );
      }
    );
  }

  function showOverlay() {

    resetOverlay();

    if (overlay) {
      overlay.hidden =
        false;
    }

    if (overlayStatusText) {

      overlayStatusText.textContent =
        'Submitting bug for analysis…';
    }

    setAgentState(
      'triage',
      'running'
    );

    setAgentState(
      'logAnalysis',
      'running'
    );
  }

  function hideOverlay() {

    if (overlay) {
      overlay.hidden =
        true;
    }
  }

  // =====================================================
  // READ UPLOADED TEXT FILE
  // =====================================================

  async function readSelectedFile() {

    if (!selectedFile) {
      return '';
    }

    try {

      return await selectedFile.text();

    } catch (error) {

      console.error(
        'Unable to read file:',
        error
      );

      return '';
    }
  }

  // =====================================================
  // BACKEND ANALYSIS
  // =====================================================

  async function analyzeBug() {

    const token =
      localStorage.getItem(
        'bugsense_token'
      );

    if (!token) {

      window.location.href =
        'index.html';

      return;
    }

    showOverlay();

    try {

      const uploadedContent =
        await readSelectedFile();

      let finalCode =
        sourceCode.value.trim();

      /*
       * Current backend accepts JSON, not a multipart file.
       * For supported source/text files, use the file contents
       * as code when the source-code field is empty.
       */
      if (
        !finalCode &&
        uploadedContent
      ) {
        finalCode =
          uploadedContent;
      }

      const requestBody = {

        title:
          bugTitle.value.trim(),

        language:
          programmingLanguage.value,

        description:
          bugDescription.value.trim(),

        error_message:
          errorMessage.value.trim(),

        stack_trace:
          stackTrace.value.trim(),

        code:
          finalCode,

        analyze_root_cause:
          document.getElementById(
            'optRootCause'
          )?.checked ?? true,

        search_similar_bugs:
          document.getElementById(
            'optSimilarBugs'
          )?.checked ?? true,

        generate_fix_recommendation:
          document.getElementById(
            'optFixRecommendation'
          )?.checked ?? true,

        detect_duplicates:
          document.getElementById(
            'optDuplicateDetection'
          )?.checked ?? true
      };

      

      const response =
        await fetch(
          `${API_BASE}/api/bugs/analyze`,
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json',

              'Authorization':
                `Bearer ${token}`
            },

            body:
              JSON.stringify(
                requestBody
              )
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
          'Bug analysis failed.'
        );
      }

  
      if (
        !data.bug ||
        !data.bug.id
      ) {

        throw new Error(
          'Backend did not return the created bug ID.'
        );
      }

      // Triage + Log Analysis completed successfully
      setAgentState(
        'triage',
        'ready'
      );

      setAgentState(
        'logAnalysis',
        'ready'
      );

      if (overlayStatusText) {

        overlayStatusText.textContent =
          'Analysis complete. Opening results…';
      }

      /*
       * IMPORTANT:
       * Pass the database bug ID to analysis-result.html.
       */
      window.location.href =
        `analysis-result.html?id=${data.bug.id}`;

    } catch (error) {

      console.error(
        'Bug analysis failed:',
        error
      );

      hideOverlay();

      showFormAlert(
        error.message ||
        'Unable to analyze the bug. Please try again.'
      );
    }
  }

  // =====================================================
  // FORM SUBMIT
  // =====================================================

  form.addEventListener(
    'submit',
    async (event) => {

      event.preventDefault();
      event.stopPropagation();

      if (!validateForm()) {
        return;
      }

      await analyzeBug();
    }
  );

});