/*
 * KMVTECH Education - sponsored banners (managed from the admin portal).
 * Put this file at: education/js/kmv-ads.js
 * On a page, add:  <div data-kmv-ad="home"></div>   (or "dashboard" or "courses")
 * and, once near the end of the page:  <script src="/education/js/kmv-ads.js" defer></script>
 * It never breaks a page: if anything goes wrong, nothing is shown.
 */
(function () {
  'use strict';
  var BASE = 'https://nzjojrebyvxuawnkitth.supabase.co';
  var KEY = 'sb_publishable_EKcJxtkPvorUeuLB9Q2xLA_SYIWzDDa';

  function rpc(name, body) {
    return fetch(BASE + '/rest/v1/rpc/' + name, {
      method: 'POST', keepalive: true,
      headers: { apikey: KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
  }
  function track(id, event) { try { rpc('ad_track', { p_ad_id: id, p_event: event }).catch(function () {}); } catch (e) {} }

  function styles() {
    if (document.getElementById('kmv-ad-css')) return;
    var s = document.createElement('style'); s.id = 'kmv-ad-css';
    s.textContent =
      '.kmv-ad{margin:22px auto;max-width:1200px;padding:0 16px}' +
      '.kmv-ad-label{display:block;font:600 10.5px/1.4 "DM Sans",system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#6B7280;margin:0 0 6px}' +
      '.kmv-ad a{display:block;border-radius:12px;overflow:hidden;border:1px solid rgba(128,128,128,.28);background:#fff;line-height:0}' +
      '.kmv-ad img{display:block;width:100%;height:auto;max-height:320px;object-fit:contain}' +
      '[data-theme="dark"] .kmv-ad-label{color:#9CA3AF}';
    document.head.appendChild(s);
  }

  function seenKey(id) { return 'kmv-ad-seen-' + id; }
  function alreadyCounted(id) { try { return !!sessionStorage.getItem(seenKey(id)); } catch (e) { return false; } }
  function markCounted(id) { try { sessionStorage.setItem(seenKey(id), '1'); } catch (e) {} }

  function watchView(el, ad) {
    if (alreadyCounted(ad.id)) return;
    var done = false;
    function count() { if (done) return; done = true; markCounted(ad.id); track(ad.id, 'view'); }
    if (!('IntersectionObserver' in window)) { count(); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { count(); io.disconnect(); } });
    }, { threshold: 0.5 });
    io.observe(el);
  }

  function render(box, ad) {
    if (!ad || !ad.image_path || !/^https?:\/\//i.test(String(ad.link_url || ''))) return;
    var img = new Image();
    img.onload = function () {
      var wrap = document.createElement('aside'); wrap.className = 'kmv-ad'; wrap.setAttribute('aria-label', 'Sponsored message');
      var label = document.createElement('span'); label.className = 'kmv-ad-label';
      label.textContent = 'Sponsored' + (ad.advertiser ? ' \u00b7 ' + ad.advertiser : '');
      var a = document.createElement('a'); a.href = ad.link_url; a.target = '_blank'; a.rel = 'sponsored noopener noreferrer';
      a.setAttribute('aria-label', 'Sponsored: ' + ad.title);
      a.appendChild(img); wrap.appendChild(label); wrap.appendChild(a);
      box.appendChild(wrap);
      var clicked = function () { track(ad.id, 'click'); };
      a.addEventListener('click', clicked); a.addEventListener('auxclick', clicked);
      watchView(wrap, ad);
    };
    img.onerror = function () {};
    img.alt = String(ad.title || ''); img.decoding = 'async';
    img.src = BASE + '/storage/v1/object/public/ads/' + encodeURI(ad.image_path);
  }

  function fill(box) {
    var place = box.getAttribute('data-kmv-ad');
    rpc('get_ads', { p_placement: place, p_limit: 1 })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (list) { if (list && list.length) render(box, list[0]); })
      .catch(function () {});
  }

  function start() {
    try {
      var boxes = document.querySelectorAll('[data-kmv-ad]');
      if (!boxes.length || !window.fetch) return;
      styles();
      Array.prototype.forEach.call(boxes, function (b) { try { fill(b); } catch (e) {} });
    } catch (e) {}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
