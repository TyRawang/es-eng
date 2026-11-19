// ESM Engineers — site behaviour. Every page works without this file; it only adds enhancements.
document.documentElement.classList.add('js');

// Mobile navigation
(() => {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  if (!toggle || !nav) return;
  const setOpen = (open) => {
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('is-open', open);
  };
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && nav.classList.contains('is-open')) {
      setOpen(false);
      toggle.focus();
    }
  });
  document.addEventListener('click', (event) => {
    if (nav.classList.contains('is-open') && !nav.contains(event.target) && !toggle.contains(event.target)) setOpen(false);
  });
  window.matchMedia('(min-width: 992px)').addEventListener('change', () => setOpen(false));
})();

// Home hero photo switcher
(() => {
  const image = document.getElementById('hero-image');
  const choices = [...document.querySelectorAll('[data-hero-image]')];
  if (!image || !choices.length) return;
  choices.forEach((choice) => {
    choice.addEventListener('click', () => {
      image.src = choice.dataset.heroImage;
      image.alt = choice.dataset.heroAlt;
      image.dataset.scene = choice.dataset.scene;
      choices.forEach((item) => item.setAttribute('aria-pressed', String(item === choice)));
    });
  });
})();

// Home services list: show the matching photo on hover or focus
(() => {
  const links = [...document.querySelectorAll('.showcase-list a')];
  const images = [...document.querySelectorAll('.showcase-media img')];
  if (!links.length || !images.length) return;
  const show = (index) => {
    links.forEach((link, i) => link.classList.toggle('is-active', i === index));
    images.forEach((img, i) => img.classList.toggle('is-active', i === index));
  };
  links.forEach((link, index) => {
    link.addEventListener('pointerenter', () => show(index));
    link.addEventListener('focus', () => show(index));
  });
})();

// Inquiry forms: build an email draft from the fields
document.querySelectorAll('form[data-email]').forEach((form) => {
  const button = form.querySelector('button[type=submit]');
  if (button) button.disabled = false;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const details = Array.from(new FormData(form))
      .filter(([, value]) => String(value).trim())
      .map(([label, value]) => `${label}: ${String(value).trim()}`)
      .join('\n\n');
    form.querySelector('.form-status').textContent = form.dataset.status;
    window.location.href = `mailto:${form.dataset.email}?subject=${encodeURIComponent(form.dataset.subject)}&body=${encodeURIComponent(details)}`;
  });
});

// Reveal sections as they scroll into view
(() => {
  const items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window)) {
    items.forEach((item) => item.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  items.forEach((item) => observer.observe(item));
})();
