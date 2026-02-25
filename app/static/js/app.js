/* ============================================
   CineMate — Interactive JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initSearch();
  initUserDropdown();
  initHeroRotation();
  initRatingStars();
  initMovieRowScroll();
  initIntersectionAnimations();
});

/* ---------- Navbar Scroll Effect ---------- */
function initNavbar() {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  const onScroll = () => {
    const scrolled = window.scrollY > 50;
    nav.classList.toggle('scrolled', scrolled);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ---------- Search ---------- */
function initSearch() {
  const input = document.getElementById('searchInput');
  const dropdown = document.getElementById('searchDropdown');
  if (!input || !dropdown) return;

  let timer = null;

  input.addEventListener('input', () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (q.length < 2) { dropdown.classList.remove('active'); return; }
    timer = setTimeout(() => fetchSearch(q, dropdown), 350);
  });

  input.addEventListener('focus', () => {
    if (dropdown.children.length > 0 && input.value.trim().length >= 2)
      dropdown.classList.add('active');
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-search'))
      dropdown.classList.remove('active');
  });
}

async function fetchSearch(q, dropdown) {
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    const movies = data.results || data || [];

    if (!movies.length) {
      dropdown.innerHTML = '<div style="padding:16px;color:var(--text-muted);text-align:center;">No results found</div>';
      dropdown.classList.add('active');
      return;
    }

    dropdown.innerHTML = movies.slice(0, 8).map(m => {
      const isTv = m.media_type === 'tv';
      const url = isTv ? `/tv/${m.id}` : `/movie/${m.id}`;
      const poster = m.poster_url || (m.poster_path ? 'https://image.tmdb.org/t/p/w92' + m.poster_path : '');
      const title = m.title || m.name || '';
      const date = (m.release_date || m.first_air_date || '').slice(0,4);
      const badge = isTv ? '<span style="font-size:0.6rem;padding:1px 5px;background:#8b5cf6;color:#fff;border-radius:3px;margin-left:4px;">TV</span>' : '';
      return `
      <a href="${url}" class="search-result-item">
        <img src="${poster}" alt="" style="width:40px;height:60px;border-radius:4px;object-fit:cover;flex-shrink:0;">
        <div>
          <div style="font-weight:600;font-size:0.9rem;">${title}${badge}</div>
          <div style="font-size:0.8rem;color:var(--text-muted);">${date} ${m.vote_average ? '★ ' + m.vote_average.toFixed(1) : ''}</div>
        </div>
      </a>`;
    }).join('');
    dropdown.classList.add('active');
  } catch (e) {
    console.error('Search error:', e);
  }
}

/* ---------- User Dropdown ---------- */
function initUserDropdown() {
  const toggle = document.getElementById('avatarBtn');
  const menu = document.getElementById('userDropdown');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('active');
  });

  document.addEventListener('click', () => menu.classList.remove('active'));
}

/* ---------- Hero Auto-Rotation ---------- */
function initHeroRotation() {
  const hero = document.getElementById('heroSection');
  if (!hero) return;
  const slides = hero.querySelectorAll('.hero-slide');
  const dots = hero.querySelectorAll('.hero-dot');
  if (slides.length <= 1) return;

  let current = 0;
  let interval;

  function goTo(idx) {
    slides[current].classList.remove('active');
    dots[current].classList.remove('active');
    current = idx % slides.length;
    slides[current].classList.add('active');
    dots[current].classList.add('active');
  }

  function next() { goTo(current + 1); }

  function startAuto() {
    clearInterval(interval);
    interval = setInterval(next, 5000);
  }

  dots.forEach(dot => {
    dot.addEventListener('click', () => {
      goTo(parseInt(dot.dataset.index));
      startAuto();
    });
  });

  startAuto();

  // Pause on hover
  hero.addEventListener('mouseenter', () => clearInterval(interval));
  hero.addEventListener('mouseleave', startAuto);
}

/* ---------- Rating Stars ---------- */
function initRatingStars() {
  const widget = document.querySelector('.rating-widget');
  if (!widget) return;
  const tmdbId = widget.dataset.tmdb;
  const stars = widget.querySelectorAll('.rating-star');
  const label = document.getElementById('ratingLabel');

  stars.forEach(star => {
    star.addEventListener('click', async () => {
      const val = parseFloat(star.dataset.value);
      try {
        const res = await fetch('/api/rate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tmdb_id: parseInt(tmdbId), rating: val })
        });
        const data = await res.json();
        if (data.success !== false) {
          stars.forEach(s => {
            s.classList.toggle('active', parseFloat(s.dataset.value) <= val);
          });
          if (label) label.textContent = val + '/5';
          showToast('Rating saved!', 'success');
        } else {
          showToast(data.error || 'Failed to save rating', 'error');
        }
      } catch (e) {
        showToast('Network error', 'error');
      }
    });

    star.addEventListener('mouseenter', () => {
      const val = parseFloat(star.dataset.value);
      stars.forEach(s => {
        s.style.opacity = parseFloat(s.dataset.value) <= val ? '1' : '0.3';
      });
    });
  });

  widget.addEventListener('mouseleave', () => {
    stars.forEach(s => s.style.opacity = '');
  });
}

/* ---------- Watchlist ---------- */
async function toggleWatchlist(movieId, isInWatchlist) {
  const endpoint = isInWatchlist ? '/api/watchlist/remove' : '/api/watchlist/add';
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tmdb_id: movieId })
    });
    const data = await res.json();
    if (data.success !== false) {
      const btn = document.getElementById('watchlistBtn');
      if (btn) {
        const nowIn = !isInWatchlist;
        btn.onclick = () => toggleWatchlist(movieId, nowIn);
        const svg = btn.querySelector('svg');
        if (svg) svg.setAttribute('fill', nowIn ? 'currentColor' : 'none');
        btn.childNodes[btn.childNodes.length - 1].textContent = nowIn ? ' In Watchlist' : ' Add to Watchlist';
      }
      showToast(isInWatchlist ? 'Removed from watchlist' : 'Added to watchlist!', 'success');
    } else {
      showToast(data.error || 'Failed', 'error');
    }
  } catch (e) {
    showToast('Network error', 'error');
  }
}

async function removeFromWatchlist(tmdbId, btnEl) {
  try {
    const res = await fetch('/api/watchlist/remove', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tmdb_id: tmdbId })
    });
    const data = await res.json();
    if (data.success !== false) {
      const card = btnEl.closest('.movie-card');
      if (card) {
        card.style.transition = 'opacity .3s, transform .3s';
        card.style.opacity = '0';
        card.style.transform = 'scale(0.8)';
        setTimeout(() => card.remove(), 300);
      }
      showToast('Removed from watchlist', 'success');
    }
  } catch (e) {
    showToast('Network error', 'error');
  }
}

/* ---------- Trailer Modal ---------- */
function playTrailer(youtubeKey) {
  const modal = document.getElementById('trailerModal');
  const iframe = document.getElementById('trailerFrame');
  if (!modal || !iframe) return;
  iframe.src = `https://www.youtube.com/embed/${youtubeKey}?autoplay=1&rel=0`;
  modal.classList.add('active');
}

function closeTrailerModal() {
  const modal = document.getElementById('trailerModal');
  const iframe = document.getElementById('trailerFrame');
  if (modal) modal.classList.remove('active');
  if (iframe) iframe.src = '';
}

// Close modal on backdrop click or close button
document.addEventListener('click', (e) => {
  if (e.target.id === 'trailerModal') closeTrailerModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeTrailerModal();
});
const modalCloseBtn = document.getElementById('modalClose');
if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeTrailerModal);

/* ---------- Toast Notifications ---------- */
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/* ---------- Movie Row Horizontal Scroll ---------- */
function initMovieRowScroll() {
  document.querySelectorAll('.movie-row').forEach(row => {
    let isDown = false, startX, scrollLeft;
    row.addEventListener('mousedown', (e) => {
      isDown = true; startX = e.pageX - row.offsetLeft; scrollLeft = row.scrollLeft;
      row.style.cursor = 'grabbing';
    });
    row.addEventListener('mouseleave', () => { isDown = false; row.style.cursor = 'grab'; });
    row.addEventListener('mouseup', () => { isDown = false; row.style.cursor = 'grab'; });
    row.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - row.offsetLeft;
      row.scrollLeft = scrollLeft - (x - startX) * 1.5;
    });
  });
}

/* ---------- Intersection Observer Animations ---------- */
function initIntersectionAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.animate-fade-up, .movie-section').forEach(el => {
    observer.observe(el);
  });
}
