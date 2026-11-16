'use strict';
const buttons = [...document.querySelectorAll('[data-filter]')];
const papers = [...document.querySelectorAll('.paper')];
const search = document.querySelector('#publication-search');
const status = document.querySelector('#filter-status');
const empty = document.querySelector('#empty-state');
let filter = 'all';
document.querySelector('.publication-controls').hidden = false;
status.hidden = false;
function update() {
  const query = search.value.trim().toLowerCase();
  let count = 0;
  for (const paper of papers) {
    paper.hidden = !(filter === 'all' || paper.dataset.kind === filter) || !paper.dataset.search.includes(query);
    if (!paper.hidden) count++;
  }
  for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.filter === filter));
  status.textContent = `${count} of ${papers.length} publications`;
  empty.hidden = count !== 0;
}
for (const button of buttons) button.addEventListener('click', () => { filter = button.dataset.filter; update(); });
search.addEventListener('input', update);
document.querySelector('#reset-filters').addEventListener('click', () => { filter = 'all'; search.value = ''; update(); search.focus(); });
for (const button of document.querySelectorAll('.copy-citation')) {
  button.hidden = false;
  button.addEventListener('click', async () => {
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(button.dataset.citation);
      document.querySelector('#copy-status').textContent = 'Citation copied.';
      button.textContent = 'Copied';
      setTimeout(() => { button.textContent = 'Copy citation'; }, 2000);
    } catch {
      const row = button.closest('.paper-actions');
      let fallback = row.querySelector('textarea');
      if (!fallback) { fallback = document.createElement('textarea'); fallback.readOnly = true; fallback.className = 'citation-fallback'; fallback.setAttribute('aria-label', 'Citation to copy'); row.appendChild(fallback); }
      fallback.value = button.dataset.citation;
      fallback.focus(); fallback.select();
      document.querySelector('#copy-status').textContent = 'Automatic copying is unavailable. The citation is selected for manual copying.';
    }
  });
}
update();
