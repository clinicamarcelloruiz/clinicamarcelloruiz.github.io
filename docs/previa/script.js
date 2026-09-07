(() => {
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('navegacao');
  const mobile = window.matchMedia('(max-width: 900px)');
  const header = document.querySelector('.site-header');
  const setOpen = (open) => {
    nav.hidden = mobile.matches && !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.querySelector('span').textContent = open ? 'Fechar' : 'Menu';
    header.classList.toggle('menu-open', mobile.matches && open);
  };
  toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', (event) => {
    if (event.target.closest('a') && mobile.matches) setOpen(false);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && mobile.matches && !nav.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
  mobile.addEventListener('change', () => setOpen(false));
  setOpen(false);
  document.getElementById('year').textContent = new Date().getFullYear();

  const video = document.getElementById('hero-video');
  const playback = document.getElementById('video-toggle');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const hero = document.querySelector('.hero');
  const booking = document.querySelector('.mobile-booking');
  let manuallyPaused = false;
  let heroVisible = true;
  const updatePlayback = () => {
    playback.querySelector('.playback-icon').textContent = video.paused ? '▶' : 'Ⅱ';
    playback.querySelector('.playback-label').textContent = video.paused ? 'Reproduzir vídeo' : 'Pausar vídeo';
    playback.setAttribute('aria-label', video.paused ? 'Reproduzir vídeo de fundo' : 'Pausar vídeo de fundo');
  };
  const play = () => {
    if (video.error) return;
    video.play().catch(updatePlayback);
  };
  const autoplayAllowed = () => !reducedMotion.matches && !navigator.connection?.saveData && !manuallyPaused;
  const syncPlayback = () => {
    if (document.hidden || !heroVisible) video.pause();
    else if (autoplayAllowed()) play();
  };
  playback.hidden = false;
  video.muted = true;
  video.addEventListener('play', updatePlayback);
  video.addEventListener('pause', updatePlayback);
  video.addEventListener('error', () => { playback.hidden = true; });
  playback.addEventListener('click', () => {
    manuallyPaused = !video.paused;
    if (video.paused) play();
    else video.pause();
  });
  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) video.pause();
    else syncPlayback();
  });
  document.addEventListener('visibilitychange', syncPlayback);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      heroVisible = entry.isIntersecting;
      booking.classList.toggle('visible', !heroVisible);
      syncPlayback();
    }, { threshold: 0 }).observe(hero);
    if (!reducedMotion.matches) {
      const sections = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          if (!reducedMotion.matches) entry.target.animate([
            { opacity: .35, transform: 'translateY(22px)' },
            { opacity: 1, transform: 'translateY(0)' }
          ], { duration: 800, easing: 'cubic-bezier(.2,.6,.3,1)' });
          sections.unobserve(entry.target);
        });
      }, { threshold: .1 });
      document.querySelectorAll('.section-heading, .about-grid, .steps, .social-heading').forEach(el => sections.observe(el));
    }
  } else {
    booking.classList.add('visible');
  }
  const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 36);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  updatePlayback();
  syncPlayback();
})();
