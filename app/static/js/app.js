/**
 * CineMate — Interactive UI Engine
 * Netflix-level interactivity for the movie platform
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initSearch();
  initUserDropdown();
  initModal();
  initToastAutoHide();
});

/* ===== NAVBAR SCROLL EFFECT ===== */
function initNavbar() {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ===== LIVE SEARCH ===== */
function initSearch() {
  const input = document.getElementById('searchInput');
  const dropdown = document.getElementById('searchDropdown');
  if (!input || !dropdown) return;

  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2) { dropdown.classList.remove('show'); return; }
    timer = setTimeout(() => fetchSearch(q, dropdown), 350);
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-search')) dropdown.classList.remove('show');
  });
}

async function fetchSearch(query, dropdown) {
  try {
    const r = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await r.json();
    const results = data.results || [];
    if (!results.length) {
      dropdown.innerHTML = '<div style="padding:16px;text-align:center;color:var(--text3);font-size:var(--fs-sm)">No results found</div>';
      dropdown.classList.add('show');
      return;
    }
    dropdown.innerHTML = results.slice(0, 8).map(m => `
      <a href="/movie/${m.id}" class="sr-item">
        <img src="${m.poster_path ? 'https://image.tmdb.org/t/p/w92' + m.poster_path : ''}" 
             alt="${m.title}" onerror="this.style.display='none'">
        <div class="sr-info">
          <h4>${m.title}</h4>
          <span>${m.release_date ? m.release_date.substring(0,4) : ''} ${m.vote_average ? '· ★ ' + m.vote_average.toFixed(1) : ''}</span>
        </div>
      </a>
    `).join('');
    dropdown.classList.add('show');
  } catch (e) {
    console.error('Search failed:', e);
  }
}

/* ===== USER DROPDOWN ===== */
function initUserDropdown() {
  const btn = document.getElementById('avatarBtn');
  const dd = document.getElementById('userDropdown');
  if (!btn || !dd) return;

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    dd.classList.toggle('show');
  });
  document.addEventListener('click', () => dd.classList.remove('show'));
}

/* ===== MOVIE ROW SCROLLING ===== */
function scrollRow(arrow, direction) {
  const row = arrow.parentElement.querySelector('.movie-row-inner');
  if (!row) return;
  const scrollAmt = row.clientWidth * 0.75;
  row.scrollBy({ left: direction * scrollAmt, behavior: 'smooth' });
}

/* ===== WATCHLIST ===== */
async function addToWatchlist(movieId) {
  try {
    const r = await fetch(`/api/watchlist/add/${movieId}`, { method: 'POST' });
    const data = await r.json();
    if (r.ok) {
      showToast('Added to your watchlist!', 'success');
      const btn = document.getElementById('wlBtn');
      if (btn) { btn.innerHTML = '✓ In Watchlist'; }
    } else {
      showToast(data.error || 'Please sign in first', 'error');
    }
  } catch {
    showToast('Could not update watchlist', 'error');
  }
}

async function removeFromWatchlist(movieId) {
  try {
    const r = await fetch(`/api/watchlist/remove/${movieId}`, { method: 'POST' });
    if (r.ok) {
      showToast('Removed from watchlist', 'info');
      const btn = document.getElementById('wlBtn');
      if (btn) { btn.innerHTML = '+ Add to Watchlist'; }
    }
  } catch {
    showToast('Could not update watchlist', 'error');
  }
}

function removeFromWatchlistCard(el, movieId) {
  removeFromWatchlist(movieId).then(() => {
    const card = el.closest('.wl-item');
    if (card) { card.style.opacity = '0'; card.style.transform = 'scale(0.95)'; setTimeout(() => card.remove(), 300); }
  });
}

/* ===== RATING ===== */
async function rateMovie(tmdbId, rating) {
  try {
    const r = await fetch(`/api/rate/${tmdbId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rating })
    });
    if (r.ok) {
      showToast(`Rated ${rating}/10 ⭐`, 'success');
      // Update star visuals
      document.querySelectorAll(`.star-rating[data-tmdb="${tmdbId}"] .star`).forEach(s => {
        s.classList.toggle('active', parseInt(s.dataset.value) <= rating);
      });
    } else {
      showToast('Please sign in to rate', 'error');
    }
  } catch {
    showToast('Could not save rating', 'error');
  }
}

/* ===== REVIEW ===== */
async function submitReview(movieId) {
  const title = document.getElementById('reviewTitle')?.value;
  const content = document.getElementById('reviewContent')?.value;
  const isSpoiler = document.getElementById('isSpoiler')?.checked || false;

  if (!content || content.trim().length < 10) {
    showToast('Please write at least 10 characters', 'error');
    return;
  }

  try {
    const r = await fetch(`/api/review/${movieId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content, is_spoiler: isSpoiler })
    });
    if (r.ok) {
      showToast('Review submitted!', 'success');
      document.getElementById('reviewTitle').value = '';
      document.getElementById('reviewContent').value = '';
    } else {
      showToast('Could not submit review', 'error');
    }
  } catch {
    showToast('Could not submit review', 'error');
  }
}

/* ===== MODAL ===== */
function initModal() {
  const overlay = document.getElementById('modalOverlay');
  const close = document.getElementById('modalClose');
  const content = document.getElementById('modalContent');
  if (!overlay) return;

  const closeModal = () => {
    overlay.classList.remove('show');
    if (content) content.innerHTML = '';
  };

  if (close) close.addEventListener('click', closeModal);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });
}

function openTrailer(key) {
  const overlay = document.getElementById('modalOverlay');
  const content = document.getElementById('modalContent');
  if (!overlay || !content) return;
  content.innerHTML = `<iframe src="https://www.youtube.com/embed/${key}?autoplay=1" allow="autoplay; encrypted-media" allowfullscreen></iframe>`;
  overlay.classList.add('show');
}

/* ===== TOASTS ===== */
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

function initToastAutoHide() {
  document.querySelectorAll('.toast').forEach(t => {
    setTimeout(() => t.remove(), 4000);
  });
}
