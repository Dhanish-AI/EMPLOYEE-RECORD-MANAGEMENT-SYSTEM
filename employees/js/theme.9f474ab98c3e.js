(function () {
  const root = document.documentElement;
  const toggle = document.getElementById('themeToggle');
  const STORAGE_KEY = 'erms-theme';

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }

  function getTheme() {
    return localStorage.getItem(STORAGE_KEY);
  }

  function init() {
    const stored = getTheme();
    if (stored) {
      setTheme(stored);
    }

    toggle?.addEventListener('click', (event) => {
      const targetButton = event.target.closest('[data-theme-target]');
      if (!targetButton) return;
      const theme = targetButton.getAttribute('data-theme-target');
      if (theme) {
        setTheme(theme);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
