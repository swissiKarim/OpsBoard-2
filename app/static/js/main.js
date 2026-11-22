/* OpsBoard – main JS */
(function () {
  'use strict';

  // ── Theme toggle ──────────────────────────────────────────────────────────
  var html = document.documentElement;
  var themeBtn = document.getElementById('theme-toggle');
  var stored = localStorage.getItem('theme');
  var preferred = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  var initial = stored || preferred;
  html.setAttribute('data-theme', initial);

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }

  // ── Sidebar toggle (mobile) ───────────────────────────────────────────────
  var sidebar = document.getElementById('sidebar');
  var sidebarToggle = document.getElementById('sidebar-toggle');
  var sidebarOverlay = document.getElementById('sidebar-overlay');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('open');
    if (sidebarOverlay) {
      sidebarOverlay.classList.add('visible');
      sidebarOverlay.setAttribute('aria-hidden', 'false');
    }
    if (sidebarToggle) sidebarToggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    if (sidebarOverlay) {
      sidebarOverlay.classList.remove('visible');
      sidebarOverlay.setAttribute('aria-hidden', 'true');
    }
    if (sidebarToggle) sidebarToggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      var isOpen = sidebar && sidebar.classList.contains('open');
      if (isOpen) { closeSidebar(); } else { openSidebar(); }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
  }

  // ── Global search (client-side redirect) ──────────────────────────────────
  var globalSearch = document.getElementById('global-search');
  if (globalSearch) {
    globalSearch.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && globalSearch.value.trim()) {
        window.location.href = '/incidents?q=' + encodeURIComponent(globalSearch.value.trim());
      }
    });
  }

  // ── New Incident Modal ────────────────────────────────────────────────────
  var modalOverlay  = document.getElementById('modal-new-incident');
  var openModalBtn  = document.getElementById('btn-new-incident');
  var closeModalBtn = modalOverlay && modalOverlay.querySelector('[data-testid="modal-close-btn"]');
  var cancelBtn     = modalOverlay && modalOverlay.querySelector('[data-testid="modal-cancel-btn"]');
  var incidentForm  = document.getElementById('new-incident-form');
  var toastEl       = document.getElementById('toast-incident-created');

  // Focusable selector used by the focus-trap
  var FOCUSABLE = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');

  function getFocusableElements() {
    if (!modalOverlay) return [];
    return Array.prototype.slice.call(modalOverlay.querySelectorAll(FOCUSABLE));
  }

  function openModal() {
    if (!modalOverlay) return;
    modalOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    // Focus first focusable element inside modal
    var focusable = getFocusableElements();
    if (focusable.length) focusable[0].focus();
  }

  function closeModal() {
    if (!modalOverlay) return;
    modalOverlay.classList.remove('open');
    document.body.style.overflow = '';
    // Return focus to the trigger button
    if (openModalBtn) openModalBtn.focus();
  }

  if (openModalBtn) {
    openModalBtn.addEventListener('click', openModal);
  }

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', closeModal);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', closeModal);
  }

  // Close on overlay backdrop click (click outside modal box)
  if (modalOverlay) {
    modalOverlay.addEventListener('click', function (e) {
      if (e.target === modalOverlay) closeModal();
    });
  }

  // ── Focus trap inside modal ───────────────────────────────────────────────
  document.addEventListener('keydown', function (e) {
    // Escape: close sidebar or modal
    if (e.key === 'Escape') {
      if (sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
        return;
      }
      if (modalOverlay && modalOverlay.classList.contains('open')) {
        closeModal();
        return;
      }
    }

    // Tab: trap focus inside modal when it is open
    if (e.key === 'Tab' && modalOverlay && modalOverlay.classList.contains('open')) {
      var focusable = getFocusableElements();
      if (!focusable.length) { e.preventDefault(); return; }
      var first = focusable[0];
      var last  = focusable[focusable.length - 1];
      if (e.shiftKey) {
        // Shift+Tab from first → wrap to last
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        // Tab from last → wrap to first
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
  });

  // ── Toast helper ─────────────────────────────────────────────────────────
  function showToast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.remove('hidden');
    setTimeout(function () {
      toastEl.classList.add('hidden');
    }, 4000);
  }

  // ── New Incident form submission ──────────────────────────────────────────
  if (incidentForm) {
    incidentForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var form = e.target;
      var titleEl    = form.querySelector('[data-testid="modal-incident-title"]');
      var serviceEl  = form.querySelector('[data-testid="modal-incident-service"]');
      var severityEl = form.querySelector('[data-testid="modal-incident-severity"]');
      var descEl     = form.querySelector('[data-testid="modal-incident-description"]');

      var payload = {
        title:       titleEl    ? titleEl.value    : '',
        service_id:  serviceEl  ? parseInt(serviceEl.value, 10) : 0,
        severity:    severityEl ? severityEl.value : '',
        description: descEl     ? descEl.value     : '',
      };

      fetch('/api/incidents', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      })
        .then(function (resp) {
          if (resp.ok) {
            return resp.json().then(function (data) {
              closeModal();
              form.reset();
              showToast('Incident #' + data.id + ' created successfully!');
              // Reload after toast so the new incident appears in lists
              setTimeout(function () { window.location.reload(); }, 1500);
            });
          } else {
            return resp.json().then(function (err) {
              alert('Error: ' + (err.detail || JSON.stringify(err)));
            });
          }
        })
        .catch(function (ex) {
          alert('Network error: ' + ex.message);
        });
    });
  }

})();
