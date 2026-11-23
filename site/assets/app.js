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

    const apply = (resetLimit = true) => {
      if (resetLimit) limit = PAGE;
      const cat = $('input[name="cat"]:checked')?.value || '';
      const term = q.value.trim().toLowerCase();
      const ordered = sort.value === 'az'
        ? initial.slice().sort((a, b) => a.dataset.name.localeCompare(b.dataset.name, 'ru'))
        : initial;
      ordered.forEach(c => list.append(c));
      const match = ordered.filter(c =>
        (!cat || c.dataset.cats.split(' ').includes(cat)) &&
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
      history.replaceState(null, '', u);
    };

    $$('input[name="cat"]').forEach(r => r.addEventListener('change', () => apply()));
    stock.addEventListener('change', () => apply());
    sort.addEventListener('change', () => apply());
    q.addEventListener('input', () => apply());
    more.addEventListener('click', () => { limit += PAGE; apply(false); });
    $$('[data-reset]').forEach(b => b.addEventListener('click', () => {
      $('input[name="cat"][value=""]').checked = true;
      stock.checked = false; q.value = ''; sort.value = 'default';
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
