/* Light/dark theme switch shared by every page.
   Loaded in <head> so a saved choice applies before the first paint (no flash).
   With no saved choice the page follows the system setting. */
(() => {
  const KEY = 'notes-theme';
  const root = document.documentElement;
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage blocked: follow the system */ }
  if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);

  const mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  const current = () => root.getAttribute('data-theme') || (mq && mq.matches ? 'dark' : 'light');
  const SUN = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.6M12 19.4V22M2 12h2.6M19.4 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>';
  const MOON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 14.2A8.6 8.6 0 0 1 9.8 3.5a8.6 8.6 0 1 0 10.7 10.7z"/></svg>';

  const paint = (btn) => {
    const dark = current() === 'dark';
    btn.innerHTML = dark ? SUN : MOON;
    const label = dark ? 'Switch to light theme' : 'Switch to dark theme';
    btn.setAttribute('aria-label', label);
    btn.title = label;
  };

  const mount = () => {
    if (document.getElementById('theme-toggle')) return;
    const btn = document.createElement('button');
    btn.id = 'theme-toggle';
    btn.type = 'button';
    btn.className = 'theme-toggle';
    paint(btn);
    btn.addEventListener('click', () => {
      const next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* choice lasts for this page only */ }
      paint(btn);
    });
    if (mq && mq.addEventListener) mq.addEventListener('change', () => paint(btn));
    document.body.appendChild(btn);
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
