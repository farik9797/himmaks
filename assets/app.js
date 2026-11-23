(() => {
  const T = window.HM_I18N || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // Мобильное меню
  const toggle = $('.menu-toggle'), nav = $('#site-nav');
  toggle?.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });

  // Галерея: миниатюры и увеличение
  const main = $('.gallery-main');
  const zoom = $('#zoom-modal');
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

  // Закрытие диалогов: кнопка и клик по подложке
  $$('dialog').forEach(d => {
    d.addEventListener('click', e => { if (e.target === d || e.target.closest('[data-close]')) d.close(); });
  });

  // Выбранная фасовка → ссылка WhatsApp и форма
  const product = $('.quote-form')?.dataset.product || '';
  const packValue = () => $('input[name="pack"]:checked')?.value || '';
  const waBtn = $('[data-wa]');
  const waBase = waBtn?.getAttribute('href');
  const syncWa = () => {
    if (!waBtn) return;
    const p = packValue();
    if (!p) return;
    const url = new URL(waBase);
    url.searchParams.set('text', url.searchParams.get('text') + ' ' + T.f_pack + ': ' + p + '.');
    waBtn.href = url.toString();
  };
  $$('input[name="pack"]').forEach(r => r.addEventListener('change', syncWa));
  syncWa();

  // Форма запроса цены
  const modal = $('#quote-modal'), form = $('.quote-form');
  const showState = state => {
    form.hidden = state !== 'form';
    $$('[data-done]', modal).forEach(el => el.hidden = el.dataset.done !== state);
  };
  $$('[data-quote]').forEach(btn => btn.addEventListener('click', () => {
    showState('form');
    const sel = form.elements.pack;
    const p = packValue();
    if (p) [...sel.options].forEach(o => { if (o.text === p) sel.value = o.value; });
    modal.showModal();
    form.elements.name.focus();
  }));

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

    const packText = f.pack.options[f.pack.selectedIndex].text;
    const lines = [
      T.wa_req,
      `${T.f_product}: ${f.product.value}`,
      `${T.f_name}: ${f.name.value.trim()}`,
      `${T.f_phone}: ${f.phone.value.trim()}`,
      `${T.f_pack}: ${packText}`,
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

  // Подсветка активной вкладки при прокрутке
  const links = $$('.section-nav a');
  const targets = links.map(a => document.getElementById(a.hash.slice(1))).filter(Boolean);
  if ('IntersectionObserver' in window && targets.length) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (!en.isIntersecting) return;
        links.forEach(a => a.setAttribute('aria-current', String(a.hash === '#' + en.target.id)));
      });
    }, { rootMargin: '-140px 0px -60% 0px' });
    targets.forEach(t => io.observe(t));
  }
})();
