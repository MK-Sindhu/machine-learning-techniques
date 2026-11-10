/* Shared behaviour for all MLT note pages: problem-table quiz toggle, contents highlight. */
(() => {
  /* ---------- Quiz toggle for the problem table ---------- */
  const qBtn = document.getElementById('quiz-toggle');
  const table = document.getElementById('map-table');
  if (qBtn && table) {
    qBtn.addEventListener('click', () => {
      const on = qBtn.getAttribute('aria-pressed') !== 'true';
      qBtn.setAttribute('aria-pressed', String(on));
      qBtn.textContent = on ? 'Show all answers' : 'Hide answers to test yourself';
      table.querySelectorAll('td.ans').forEach(td => {
        td.querySelector('.ans-text').hidden = on;
        td.querySelector('.reveal').hidden = !on;
      });
    });
    table.addEventListener('click', e => {
      const b = e.target.closest('.reveal');
      if (!b) return;
      b.hidden = true;
      b.closest('td').querySelector('.ans-text').hidden = false;
    });
  }

  /* ---------- Contents highlight ---------- */
  const links = [...document.querySelectorAll('.toc a[href^="#"]')];
  const byId = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting && byId.has(en.target.id)) {
          links.forEach(a => a.classList.remove('on'));
          byId.get(en.target.id).classList.add('on');
        }
      });
    }, { rootMargin: '-15% 0px -75% 0px' });
    document.querySelectorAll('main section[id]').forEach(s => io.observe(s));
  }
})();
