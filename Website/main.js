/**
 * DataSetu — India Public Data Analytics Platform
 * main.js | v1.0 — Education Module
 */

'use strict';

/* ── Scroll reveal ──────────────────────────────────────────── */
(function initReveal() {
  const els = document.querySelectorAll('.reveal');
  if (!els.length) return;

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  els.forEach((el) => io.observe(el));
})();

/* ── Header scroll shadow ───────────────────────────────────── */
(function initHeaderShadow() {
  const header = document.getElementById('site-header');
  if (!header) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      header.classList.toggle('scrolled', window.scrollY > 10);
      ticking = false;
    });
  }, { passive: true });
})();

/* ── Chatbot placeholder: chip → input fill ─────────────────── */
(function initChatChips() {
  const chips   = document.querySelectorAll('.chat-chip');
  const input   = document.getElementById('chat-input');
  if (!chips.length || !input) return;

  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      input.value = chip.dataset.q || chip.textContent.trim();
      input.focus();
    });
  });
})();

/* ── Active section highlight (future nav) ──────────────────── */
(function initActiveSection() {
  const sections = document.querySelectorAll('section[id]');
  if (!sections.length) return;

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          document.querySelectorAll('[data-section-link]').forEach((el) => {
            el.classList.toggle('active-section', el.dataset.sectionLink === e.target.id);
          });
        }
      });
    },
    { threshold: 0.4 }
  );

  sections.forEach((s) => io.observe(s));
})();
