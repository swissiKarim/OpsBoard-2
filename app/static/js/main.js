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

  // Close sidebar on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
        return;
      }
      // Also close modal if open
      var modal = document.getElementById('new-incident-modal');
      if (modal && modal.classList.contains('open')) {
        modal.classList.remove('open');
      }
    }
  });

  // ── Global search (client-side redirect) ──────────────────────────────────
  var globalSearch = document.getElementById('global-search');
  if (globalSearch) {
    globalSearch.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && globalSearch.value.trim()) {
        window.location.href = '/incidents?q=' + encodeURIComponent(globalSearch.value.trim());
      }
    });
  }

})();
