const heroImage = document.querySelector('.hero-banner-box .banner-image');
const heroChoices = [...document.querySelectorAll('[data-hero-image]')];
heroChoices.forEach((choice) => {
  choice.addEventListener('click', () => {
    heroImage.src = choice.dataset.heroImage;
    heroImage.dataset.heroScene = choice.dataset.heroScene;
    heroImage.alt = choice.getAttribute('aria-label');
    heroChoices.forEach((item) => item.setAttribute('aria-pressed', String(item === choice)));
  });
});

document.querySelectorAll('[data-service-index]').forEach((link) => {
  const section = link.closest('.service-content-wrapper');
  const links = [...section.querySelectorAll('[data-service-index]')];
  const images = [...section.querySelectorAll('.single-image-service')];
  const counts = [...section.querySelectorAll('.service-number')];
  const show = () => {
    const index = Number(link.dataset.serviceIndex);
    [links, images, counts].forEach((group) =>
      group.forEach((item, position) => item.classList.toggle('active', position === index))
    );
  };
  link.addEventListener('pointerenter', show);
  link.addEventListener('focus', show);
});

document.querySelectorAll('form[data-email]').forEach((form) => {
  form.querySelector('button[type=submit]').disabled = false;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const details = Array.from(new FormData(form))
      .filter(([, value]) => String(value).trim())
      .map(([label, value]) => label + ': ' + String(value).trim())
      .join('\n\n');
    form.querySelector('.form-status').textContent = form.dataset.status;
    window.location.href = 'mailto:' + form.dataset.email + '?subject=' +
      encodeURIComponent(form.dataset.subject) + '&body=' + encodeURIComponent(details);
  });
});
