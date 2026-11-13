/* Semtex Garage — page behaviour: header menu, scroll reveal, before/after carousel */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- scroll reveal ----------------------------------------------------
     [data-reveal-group]    its direct children fade up (a nested
                            [data-reveal-children] grid is skipped as a block)
     [data-reveal-children] its direct children fade up, staggered          */
  function initReveal() {
    // with reduced motion the CSS keeps only a short fade (no movement)
    if (!('IntersectionObserver' in window)) return;

    var targets = [];
    document.querySelectorAll('[data-reveal-group], [data-reveal-children]').forEach(function (parent) {
      Array.prototype.forEach.call(parent.children, function (el, i) {
        if (parent.hasAttribute('data-reveal-group') && el.hasAttribute('data-reveal-children')) return;
        el.style.setProperty('--reveal-delay', Math.min(i * 60, 300) + 'ms');   // stagger 30-80ms per item
        el.classList.add('reveal');
        targets.push(el);
      });
    });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    targets.forEach(function (el) { io.observe(el); });
  }

  /* --- before / after carousel ----------------------------------------
     Native horizontal scroll with scroll-snap does the swiping (touch, trackpad);
     this adds mouse dragging, arrows, keyboard, the active slide and the progress bar. */
  function initCarousel(section) {
    var track = section.querySelector('[data-ba-track]');
    var slides = Array.prototype.slice.call(track.querySelectorAll('.ba-slide'));
    var prev = section.querySelector('[data-ba-prev]');
    var next = section.querySelector('[data-ba-next]');
    var current = section.querySelector('[data-ba-current]');
    var bar = section.querySelector('[data-ba-progress]');
    var live = section.querySelector('[data-ba-live]');
    var n = slides.length;
    var index = -1, ticking = false;

    function pad(i) { return (i < 9 ? '0' : '') + (i + 1); }
    function step() { return n > 1 ? slides[1].offsetLeft - slides[0].offsetLeft : 1; }
    function leftOf(i) { return slides[i].offsetLeft - slides[0].offsetLeft; }

    function setActive(i) {
      if (i === index) return;
      index = i;
      slides.forEach(function (s, k) {
        s.classList.toggle('is-active', k === i);
        s.setAttribute('aria-hidden', k === i ? 'false' : 'true');
      });
      current.textContent = pad(i);
      prev.disabled = i === 0;
      next.disabled = i === n - 1;
      var h = slides[i].querySelector('h3');
      if (live) live.textContent = 'Rad ' + (i + 1) + ' od ' + n + ': ' + (h ? h.textContent : '');
    }

    function update() {
      ticking = false;
      var pos = track.scrollLeft / step();
      setActive(Math.max(0, Math.min(n - 1, Math.round(pos))));
      // write the transform on the bar itself (no inherited CSS variable)
      bar.style.transform = 'scaleX(' + Math.max(1 / n, Math.min(1, (pos + 1) / n)).toFixed(4) + ')';
    }

    // instant = keyboard: actions repeated from the keyboard are not animated
    function go(i, instant) {
      i = Math.max(0, Math.min(n - 1, i));
      track.scrollTo({ left: leftOf(i), behavior: reduce || instant ? 'auto' : 'smooth' });
    }

    track.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', function () { track.scrollLeft = leftOf(Math.max(index, 0)); update(); });

    prev.addEventListener('click', function () { go(index - 1); });
    next.addEventListener('click', function () { go(index + 1); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { go(index - 1, true); e.preventDefault(); }
      if (e.key === 'ArrowRight') { go(index + 1, true); e.preventDefault(); }
    });

    // mouse: drag 1:1 to scroll; on release snap to the nearest slide, and a quick flick
    // (velocity, not distance) moves one slide in its direction. Touch uses native scroll.
    var FLICK = 0.11;                       // px per ms
    var drag = null, moved = false;
    track.addEventListener('pointerdown', function (e) {
      if (drag || e.pointerType !== 'mouse' || e.button !== 0) return;
      var now = performance.now();
      drag = { id: e.pointerId, x: e.clientX, left: track.scrollLeft, from: index, lastX: e.clientX, lastT: now, v: 0 };
      moved = false;
    });
    track.addEventListener('pointermove', function (e) {
      if (!drag || e.pointerId !== drag.id) return;
      var dx = e.clientX - drag.x;
      if (!moved && Math.abs(dx) > 4) {
        moved = true;
        track.classList.add('is-dragging');
        track.setPointerCapture(e.pointerId);   // keep dragging when the cursor leaves the track
      }
      if (!moved) return;
      track.scrollLeft = drag.left - dx;
      var now = performance.now(), dt = now - drag.lastT;
      if (dt > 0) drag.v = 0.8 * ((e.clientX - drag.lastX) / dt) + 0.2 * drag.v;
      drag.lastX = e.clientX; drag.lastT = now;
    });
    function endDrag(e) {
      if (!drag || e.pointerId !== drag.id) return;
      var from = drag.from, v = drag.v;
      // a pause before letting go cancels the flick
      if (performance.now() - drag.lastT > 80) v = 0;
      drag = null;
      if (!moved) return;
      track.classList.remove('is-dragging');
      var target = Math.round(track.scrollLeft / step());
      if (Math.abs(v) > FLICK && target === from) target = from + (v < 0 ? 1 : -1);
      go(target);
    }
    track.addEventListener('pointerup', endDrag);
    track.addEventListener('pointercancel', endDrag);
    // a drag must not count as a click on a slide
    track.addEventListener('click', function (e) {
      if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; return; }
      var slide = e.target.closest('.ba-slide');
      var k = slides.indexOf(slide);
      if (k > -1 && k !== index) go(k);   // clicking the peeking slide brings it in
    }, true);

    update();
  }

  /* --- header: hamburger menu + real header height for layout ---------- */
  function initHeader() {
    var header = document.querySelector('[data-header]');
    if (!header) return;
    var toggle = header.querySelector('[data-nav-toggle]');
    var nav = header.querySelector('#site-nav');
    var root = document.documentElement;

    function setHeaderHeight() { root.style.setProperty('--header-h', header.offsetHeight + 'px'); }

    function setOpen(open) {
      header.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Zatvori meni' : 'Otvori meni');
    }

    toggle.addEventListener('click', function () { setOpen(!header.classList.contains('is-open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (header.classList.contains('is-open') && !header.contains(e.target)) setOpen(false);
    });
    window.addEventListener('resize', function () {
      setHeaderHeight();
      if (window.innerWidth >= 860) setOpen(false);
    });
    setHeaderHeight();
  }

  function init() {
    initHeader();
    document.querySelectorAll('#radovi').forEach(function (sec) { if (sec.querySelector('[data-ba-track]')) initCarousel(sec); });
    initReveal();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
