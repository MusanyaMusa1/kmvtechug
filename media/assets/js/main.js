// King Musah Media — shared site behaviour
// Theme toggle (light/dark, remembered in localStorage) + mobile menu

// Tries jpg -> jpeg -> png -> webp for a story photo; if none exist, hides the
// <img> so the placeholder icon underneath shows instead. No editing needed —
// just name your photo file to match the story slug and drop it in assets/images/.
window.handleImgError = function (img) {
  var exts = ['jfif', 'jpg', 'jpeg', 'png', 'webp'];
  var idx = parseInt(img.getAttribute('data-ext-idx') || '0', 10) + 1;
  if (idx < exts.length) {
    img.setAttribute('data-ext-idx', idx);
    img.src = img.getAttribute('data-base') + '.' + exts[idx];
  } else {
    img.style.display = 'none';
  }
};

(function () {
  var root = document.documentElement;
  var stored = localStorage.getItem('kmm-theme');
  var prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  var initial = stored || (prefersLight ? 'light' : 'dark');
  if (initial === 'light') root.setAttribute('data-theme', 'light');

  function updateToggleIcon() {
    var btn = document.getElementById('themeBtn');
    if (!btn) return;
    var isLight = root.getAttribute('data-theme') === 'light';
    btn.textContent = isLight ? '\u263E' : '\u2600'; // moon / sun
    btn.setAttribute('aria-label', isLight ? 'Switch to dark mode' : 'Switch to light mode');
  }

  window.toggleTheme = function () {
    var isLight = root.getAttribute('data-theme') === 'light';
    if (isLight) {
      root.removeAttribute('data-theme');
      localStorage.setItem('kmm-theme', 'dark');
    } else {
      root.setAttribute('data-theme', 'light');
      localStorage.setItem('kmm-theme', 'light');
    }
    updateToggleIcon();
  };

  document.addEventListener('DOMContentLoaded', function () {
    updateToggleIcon();

    var hamburger = document.getElementById('hamburgerBtn');
    var mobileMenu = document.getElementById('mob');
    if (hamburger && mobileMenu) {
      hamburger.addEventListener('click', function () {
        var open = mobileMenu.classList.toggle('open');
        hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }

    var path = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      if (href.endsWith(path) && path !== '') {
        a.classList.add('active');
        a.setAttribute('aria-current', 'page');
      }
    });
  });
})();
