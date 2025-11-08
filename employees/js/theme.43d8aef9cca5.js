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

    toggle?.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      setTheme(next);
    });
  }

  document.addEventListener('DOMContentLoaded', init);
})();
