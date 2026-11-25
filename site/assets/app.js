(() => {
  const T = window.HM_I18N || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Мобильное меню
  const toggle = $('.menu-toggle'), nav = $('#site-nav');
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });

  // Диалоги: закрытие по кнопке и подложке
  $$('dialog').forEach(d => d.addEventListener('click', e => {
    if (e.target === d || e.target.closest('[data-close]')) d.close();
  }));

  // ---------- Страница товара: галерея, фасовка, вкладки
  const main = $('.gallery-main'), zoom = $('#zoom-modal');
  $$('.thumb').forEach(btn => btn.addEventListener('click', () => {
    const pic = btn.querySelector('picture').cloneNode(true);
    const img = pic.querySelector('img');
    img.className = 'gallery-img';
    img.removeAttribute('loading');
    pic.querySelectorAll('source').forEach(s => s.sizes = '(min-width: 1024px) 560px, 100vw');
    main.querySelector('picture').replaceWith(pic);
    $$('.thumb').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
  }));
  main?.addEventListener('click', () => {
    const img = main.querySelector('img');
    let z = $('.zoom-img', zoom);
    if (!z) { z = document.createElement('img'); z.className = 'zoom-img'; zoom.append(z); }
    z.src = img.currentSrc || img.src;
    z.alt = img.alt;
    zoom.showModal();
  });

  const packValue = () => $('input[name="pack"]:checked')?.value || '';
  const waBtn = $('[data-wa]');
  const waBase = waBtn?.getAttribute('href');
  const syncWa = () => {
    const p = packValue();
    if (!waBtn || !p) return;
    const url = new URL(waBase);
    url.searchParams.set('text', url.searchParams.get('text') + ' ' + T.f_pack + ': ' + p + '.');
    waBtn.href = url.toString();
  };
  $$('input[name="pack"]').forEach(r => r.addEventListener('change', syncWa));
  syncWa();

  const links = $$('.section-nav a');
  const targets = links.map(a => document.getElementById(a.hash.slice(1))).filter(Boolean);
  if ('IntersectionObserver' in window && targets.length) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) links.forEach(a => a.setAttribute('aria-current', String(a.hash === '#' + en.target.id)));
    }), { rootMargin: '-140px 0px -60% 0px' });
    targets.forEach(t => io.observe(t));
  }

  // ---------- Форма заявки
  const modal = $('#quote-modal'), form = $('.quote-form');
  const pageProduct = form?.dataset.product || '';
  const showState = state => {
    form.hidden = state !== 'form';
    $$('[data-done]', modal).forEach(el => el.hidden = el.dataset.done !== state);
  };
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-quote]');
    if (!btn || !form) return;
    const f = form.elements;
    const product = btn.dataset.product || (btn.hasAttribute('data-general') ? '' : pageProduct);
    f.product.value = product;
    f.product.readOnly = Boolean(product);
    $('#quote-title').textContent = product ? T.f_title : T.f_title_general;
    if (f.pack.tagName === 'SELECT') {
      const p = packValue();
      [...f.pack.options].forEach(o => { if (o.text === p) f.pack.value = o.value; });
    }
    showState('form');
    modal.showModal();
    (product ? f.name : f.product).focus();
  });

  const setErr = (input, msg) => {
    input.setAttribute('aria-invalid', msg ? 'true' : 'false');
    input.closest('.field').querySelector('.err').textContent = msg || '';
  };
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const f = form.elements;
    const phoneOk = f.phone.value.replace(/\D/g, '').length >= 10;
    setErr(f.name, f.name.value.trim() ? '' : T.f_name_err);
    setErr(f.phone, phoneOk ? '' : T.f_phone_err);
    if (!f.name.value.trim()) return f.name.focus();
    if (!phoneOk) return f.phone.focus();

    const pack = f.pack.tagName === 'SELECT' ? f.pack.options[f.pack.selectedIndex].text : f.pack.value.trim();
    const lines = [
      T.wa_req,
      f.product.value.trim() && `${T.f_product}: ${f.product.value.trim()}`,
      `${T.f_name}: ${f.name.value.trim()}`,
      `${T.f_phone}: ${f.phone.value.trim()}`,
      pack && `${T.f_pack}: ${pack}`,
      f.region.value.trim() && `${T.f_region}: ${f.region.value.trim()}`,
      f.comment.value.trim() && `${T.f_comment}: ${f.comment.value.trim()}`,
    ].filter(Boolean);

    const endpoint = form.dataset.endpoint;
    if (endpoint) {
      // На WordPress сюда подставляется обработчик (admin-ajax / REST): товар и параметры уходят менеджеру
      const btn = form.querySelector('[type="submit"]');
      btn.disabled = true;
      try {
        const res = await fetch(endpoint, { method: 'POST', body: new FormData(form) });
        if (!res.ok) throw new Error(res.status);
        if (window.HM_THANKS) { location.href = window.HM_THANKS; return; }
        showState('ok');
      } catch {
        alert(T.f_err);
      } finally {
        btn.disabled = false;
      }
      return;
    }
    $('[data-wa-send]', modal).href = `https://wa.me/${window.HM_WA}?text=${encodeURIComponent(lines.join('\n'))}`;
    showState('wa');
  });
  $('[data-wa-send]')?.addEventListener('click', () => {
    if (window.HM_THANKS) setTimeout(() => { location.href = window.HM_THANKS; }, 400);
  });

  // ---------- Главная: фоновое видео героя (не грузим на телефонах, при экономии трафика и reduced motion)
  const hv = $('.hero-video');
  if (hv && !reduce && matchMedia('(min-width: 900px)').matches && !(navigator.connection && navigator.connection.saveData)) {
    hv.src = hv.dataset.src;
    hv.addEventListener('playing', () => hv.classList.add('is-playing'), { once: true });
    hv.play().catch(() => {});
  }

  // ---------- Главная: баннеры новинок и акций (без автопрокрутки)
  const track = $('[data-slider]');
  if (track) {
    const slides = $$('.banner', track), dots = $$('.banner-dot');
    const current = () => Math.round(track.scrollLeft / track.clientWidth);
    const go = i => {
      const n = (i + slides.length) % slides.length;
      track.scrollTo({ left: slides[n].offsetLeft - slides[0].offsetLeft, behavior: reduce ? 'auto' : 'smooth' });
    };
    const mark = () => dots.forEach((d, i) => d.setAttribute('aria-current', String(i === current())));
    $$('[data-slide]').forEach(b => b.addEventListener('click', () => go(current() + Number(b.dataset.slide))));
    dots.forEach(d => d.addEventListener('click', () => go(Number(d.dataset.to))));
    track.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); go(current() + (e.key === 'ArrowRight' ? 1 : -1)); }
    });
    let timer;
    track.addEventListener('scroll', () => { clearTimeout(timer); timer = setTimeout(mark, 80); }, { passive: true });
    mark();
  }

  // ---------- Главная: лента популярных товаров
  const rail = $('.rail');
  $$('[data-rail]').forEach(btn => btn.addEventListener('click', () => {
    const step = rail.clientWidth * 0.8 * Number(btn.dataset.rail);
    rail.scrollBy({ left: step, behavior: reduce ? 'auto' : 'smooth' });
  }));

  // ---------- Каталог: группы, наличие, поиск, сортировка, «Показать ещё»
  const list = $('[data-cards]');
  if (list) {
    const PAGE = 12;
    const cards = $$('.card', list);
    const initial = cards.slice();
    const q = $('input[name="q"]'), stock = $('input[name="stock"]'), sort = $('select[name="sort"]');
    const more = $('[data-more]'), empty = $('[data-empty]'), count = $('[data-count]');
    let limit = PAGE;

    const params = new URLSearchParams(location.search);
    const startCat = params.get('cat') || '';
    const radio = $(`input[name="cat"][value="${CSS.escape(startCat)}"]`);
    if (radio) radio.checked = true;
    if (params.get('q')) q.value = params.get('q');
    // Назначение и фасовка: внутри группы флажков «или», между группами «и»
    const facets = { use: 'fuse', pack: 'fpack' };
    Object.entries(facets).forEach(([param, name]) => (params.get(param) || '').split(',').filter(Boolean)
      .forEach(v => { const box = $(`input[name="${name}"][value="${CSS.escape(v)}"]`); if (box) box.checked = true; }));
    const picked = name => $$(`input[name="${name}"]:checked`).map(b => b.value);
    const hasAny = (attr, want) => !want.length || want.some(v => attr.split(' ').includes(v));

    const apply = (resetLimit = true) => {
      if (resetLimit) limit = PAGE;
      const cat = $('input[name="cat"]:checked')?.value || '';
      const term = q.value.trim().toLowerCase();
      const ordered = sort.value === 'az'
        ? initial.slice().sort((a, b) => a.dataset.name.localeCompare(b.dataset.name, 'ru'))
        : initial;
      ordered.forEach(c => list.append(c));
      const uses = picked('fuse'), packs = picked('fpack');
      const match = ordered.filter(c =>
        (!cat || c.dataset.cats.split(' ').includes(cat)) &&
        hasAny(c.dataset.use, uses) && hasAny(c.dataset.pack, packs) &&
        (!stock.checked || c.dataset.stock === '1') &&
        (!term || c.dataset.name.includes(term)));
      cards.forEach(c => c.hidden = true);
      match.slice(0, limit).forEach(c => c.hidden = false);
      count.textContent = match.length;
      empty.hidden = match.length > 0;
      more.hidden = match.length <= limit;

      const u = new URL(location.href);
      cat ? u.searchParams.set('cat', cat) : u.searchParams.delete('cat');
      term ? u.searchParams.set('q', term) : u.searchParams.delete('q');
      uses.length ? u.searchParams.set('use', uses.join(',')) : u.searchParams.delete('use');
      packs.length ? u.searchParams.set('pack', packs.join(',')) : u.searchParams.delete('pack');
      history.replaceState(null, '', u);
    };

    $$('input[name="cat"], input[name="fuse"], input[name="fpack"]').forEach(r => r.addEventListener('change', () => apply()));
    stock.addEventListener('change', () => apply());
    sort.addEventListener('change', () => apply());
    q.addEventListener('input', () => apply());
    more.addEventListener('click', () => { limit += PAGE; apply(false); });
    $$('[data-reset]').forEach(b => b.addEventListener('click', () => {
      $('input[name="cat"][value=""]').checked = true;
      stock.checked = false; q.value = ''; sort.value = 'default';
      $$('input[name="fuse"], input[name="fpack"]').forEach(b => { b.checked = false; });
      apply();
    }));
    // Фильтры раскрыты на десктопе и свёрнуты на телефоне
    const wide = matchMedia('(min-width: 900px)'), filters = $('.filters');
    const syncFilters = () => { filters.open = wide.matches; };
    wide.addEventListener('change', syncFilters);
    syncFilters();
    apply();
  }
})();
