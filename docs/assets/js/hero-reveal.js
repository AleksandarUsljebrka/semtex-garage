/**
 * Hero reveal: headlights switching on (light layers over one photo), once per page load.
 * Waits until the photo and all light layers are loaded and decoded (no flicker),
 * then adds .is-playing; the timeline itself is pure CSS (hero-reveal.css).
 * With prefers-reduced-motion the same light-up plays as plain fades (no movement).
 */
(function () {
  'use strict';

  var DECODE_CAP = 1500;  // ms, a decode that never settles must not hold the hero dark

  function waitForImage(img) {
    var loaded = img.complete && img.naturalWidth > 0
      ? Promise.resolve()
      : new Promise(function (resolve) {
          img.addEventListener('load', resolve, { once: true });
          img.addEventListener('error', resolve, { once: true });
        });
    return loaded.then(function () {
      if (!img.decode) return undefined;
      return Promise.race([
        img.decode().catch(function () {}),
        new Promise(function (resolve) { setTimeout(resolve, DECODE_CAP); })
      ]);
    });
  }

  function whenVisible() {
    if (!document.hidden) return Promise.resolve();
    return new Promise(function (resolve) {
      document.addEventListener('visibilitychange', function onVis() {
        if (document.hidden) return;
        document.removeEventListener('visibilitychange', onVis);
        resolve();
      });
    });
  }

  function msVar(el, name, fallback) {
    var v = parseFloat(getComputedStyle(el).getPropertyValue(name));
    return isNaN(v) ? fallback : v;
  }

  function init(root) {
    if (root.classList.contains('is-playing') || root.classList.contains('is-done')) return;

    // the section around the photo gets .is-text once the lights are up; on small screens
    // the hero text waits for it (styles.css). Never leave the text hidden for long.
    var section = root.closest('.hero') || root;
    var showText = function () { section.classList.add('is-text'); };
    // safety net: if something stalls, show the text and the lit car anyway
    var textFallback = setTimeout(function () {
      showText();
      if (!root.classList.contains('is-playing')) root.classList.add('is-done');
    }, 6000);

    // reduced motion gets the same timeline; CSS plays it as plain fades (no movement)

    var images = Array.prototype.slice.call(root.querySelectorAll('img'));

    Promise.all(images.map(waitForImage))
      .then(whenVisible)
      .then(function () {
        // two frames so the unlit photo is painted before anything moves
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            root.classList.add('is-playing');

            // text comes in while the light is still spreading over the floor
            setTimeout(function () { clearTimeout(textFallback); showText(); },
              msVar(root, '--hr-beam-at', 1250) + 450);

            // once the slowest layer (haze, 1.4s after the low beams) is up, settle into the static final state
            var total = msVar(root, '--hr-beam-at', 1250) + 1700;
            setTimeout(function () {
              root.classList.add('is-done');
              root.classList.remove('is-playing');
            }, total);
          });
        });
      });
  }

  function initAll() {
    var roots = document.querySelectorAll('[data-hero-reveal]');
    for (var i = 0; i < roots.length; i++) init(roots[i]);
  }

  window.HeroReveal = { init: init };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initAll);
  else initAll();
})();
