// Движение сайта ХИММАКС: плавный скролл (Lenis) и появление блоков (GSAP + ScrollTrigger).
// Каждая анимация с задачей: иерархия героя, появление разделов при прокрутке, обратная связь шапки.
// При prefers-reduced-motion, без GSAP или без JS ничего не прячется и не двигается.
(() => {
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !window.gsap || !window.ScrollTrigger) { root.classList.remove('motion'); return; }
  gsap.registerPlugin(ScrollTrigger);
  const ease = 'power3.out';

  // ---------- Плавный скролл
  if (window.Lenis) {
    const lenis = new Lenis({
      duration: 1.1,
      easing: t => 1 - Math.pow(1 - t, 4),
      prevent: node => Boolean(node.closest && node.closest('dialog')),
    });
    lenis.on('scroll', ScrollTrigger.update);
    let idle;
    lenis.on('scroll', () => {
      root.classList.add('is-scrolling');
      clearTimeout(idle);
      idle = setTimeout(() => root.classList.remove('is-scrolling'), 150);
    });
    gsap.ticker.add(time => lenis.raf(time * 1000));
    gsap.ticker.lagSmoothing(0);

    // Открыта форма или мобильное меню: страница стоит
    const sync = () => {
      const busy = document.querySelector('dialog[open]') || document.querySelector('.main-nav.open');
      busy ? lenis.stop() : lenis.start();
    };
    new MutationObserver(sync).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['open', 'class'] });

    // Якоря на странице: с отступом под липкую шапку и навигацию раздела
    document.addEventListener('click', e => {
      const a = e.target.closest('a[href^="#"]');
      if (!a || a.classList.contains('skip') || a.hash.length < 2) return;
      const target = document.getElementById(a.hash.slice(1));
      if (!target) return;
      e.preventDefault();
      const offset = parseInt(getComputedStyle(root).scrollPaddingTop, 10) || 0;
      lenis.scrollTo(target, { offset: -offset });
      history.replaceState(null, '', a.hash);
    });
  }

  // ---------- Шапка: тень после начала прокрутки
  const header = document.querySelector('.site-header');
  if (header) {
    ScrollTrigger.create({ start: 8, onToggle: self => header.classList.toggle('is-scrolled', self.isActive) });
  }

  // ---------- Первый экран: заголовок, текст, кнопки по очереди
  const intro = gsap.utils.toArray('.hero-text h1, .hero-text .lead, .hero-actions, .hero-facts li, .product-head h1, .product-head .lead, .product-head .search');
  if (intro.length) {
    gsap.fromTo(intro, { y: 24, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 0.8, ease, stagger: 0.07, delay: 0.05,
      onComplete: () => root.classList.remove('motion') });
  } else {
    root.classList.remove('motion');
  }

  // ---------- Фон героя: лёгкий параллакс
  if (document.querySelector('.home-hero .hero-bg')) {
    gsap.to('.home-hero .hero-bg', { yPercent: 10, ease: 'none',
      scrollTrigger: { trigger: '.home-hero', start: 'top top', end: 'bottom top', scrub: true } });
  }

  // ---------- Разделы: появляются один раз при входе в экран
  const reveal = [
    '.block-head', '.block > h2', '.block-why > h2',
    '.cat-grid > li', '.rail > .card', '.why > li', '.steps > li', '.info-grid > li', '.clients > li',
    '.regions > li', '.faq-item', '.app-links > li', '.pay-list > li',
    '.about-panel', '.banner-track', '.docs-strip', '.cta-text', '.cta-side',
    '.contact-item', '.map-frame', '.specs', '.prose', '.review',
  ].join(',');
  const items = gsap.utils.toArray(reveal).filter(el => !el.closest('.home-hero, .product-head, dialog'));
  gsap.set(items, { y: 28, autoAlpha: 0 });
  ScrollTrigger.batch(items, {
    start: 'top 90%',
    once: true,
    onEnter: batch => gsap.to(batch, { y: 0, autoAlpha: 1, duration: 0.7, ease, stagger: 0.06, overwrite: true }),
  });
  // Картинки догружаются лениво: пересчитать точки срабатывания
  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
