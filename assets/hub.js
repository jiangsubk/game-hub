/* ============================================================
   Arcade Hub — 交互
   ============================================================ */

(function () {
  'use strict';

  var GAMES = [
    { href: 'games/thunder-fighter/index.html', best: 'thunderBest' },
    { href: 'games/tetris/index.html',          best: 'gamehub:tetris:best' },
    { href: 'games/tetris-pygame/index.html',   best: null }
  ];

  /* ---------- 安全读取 localStorage ---------- */

  function readNumber(key) {
    if (!key) return null;
    try {
      var raw = window.localStorage.getItem(key);
      if (raw === null) return null;
      var n = parseInt(raw, 10);
      return isNaN(n) ? null : n;
    } catch (e) {
      return null;
    }
  }

  /* ---------- 回填最高分 ---------- */

  function paintBests() {
    var slots = document.querySelectorAll('[data-best]');
    for (var i = 0; i < slots.length; i++) {
      var kind = slots[i].getAttribute('data-best');
      var key = kind === 'thunder' ? 'thunderBest'
              : kind === 'tetris'  ? 'gamehub:tetris:best'
              : null;
      var val = readNumber(key);
      if (val !== null && val > 0) {
        slots[i].textContent = '最佳 ' + val.toLocaleString('en-US');
        slots[i].classList.add('has-score');
      }
    }
  }

  /* ---------- 键盘快捷入口 ---------- */

  function onKey(e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var tag = (e.target && e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;

    var idx = -1;
    if (e.key === '1') idx = 0;
    else if (e.key === '2') idx = 1;
    else if (e.key === '3') idx = 2;

    if (idx >= 0 && GAMES[idx]) {
      window.location.href = GAMES[idx].href;
    }
  }

  /* ---------- 卡片点击涟漪反馈 ---------- */

  function bindCards() {
    var cards = document.querySelectorAll('.card');
    for (var i = 0; i < cards.length; i++) {
      cards[i].addEventListener('pointerdown', function () {
        this.style.transform = 'translateY(-1px) scale(0.995)';
      });
      cards[i].addEventListener('pointerup', function () {
        this.style.transform = '';
      });
      cards[i].addEventListener('pointerleave', function () {
        this.style.transform = '';
      });
    }
  }

  /* ---------- 启动 ---------- */

  function init() {
    paintBests();
    bindCards();
    document.addEventListener('keydown', onKey);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
