#!/usr/bin/env python3
"""Сборка статического шаблона страницы товара ХИММАКС (RU + KZ).

Запуск: python3 src/build.py  ->  site/catalog/.../index.html и site/kz/katalog/.../index.html
Данные товара: src/product.json. Настройки компании и строки интерфейса: ниже, SITE и UI.
PREVIEW = True показывает пометку «образец» на документах-заглушках (на проде — False, заглушки скрыты).
"""
import json, re, html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "site"
DOMAIN = "https://himmaks.kz"
PREVIEW = True

SITE = {
    "phones": [
        {"tel": "+77472175547", "text": "+7 (747) 217-55-47", "note": {"ru": "Отдел продаж, Tele2", "kz": "Сату бөлімі, Tele2"}},
        {"tel": "+77782175547", "text": "+7 (778) 217-55-47", "note": {"ru": "Отдел продаж, Activ, WhatsApp", "kz": "Сату бөлімі, Activ, WhatsApp"}},
        {"tel": "+77182631100", "text": "+7 (718) 263-11-00", "note": {"ru": "Офис", "kz": "Кеңсе"}},
    ],
    "whatsapp": "77782175547",
    "email": "himmaks2020@mail.ru",
    "address": {"ru": "Павлодар, ул. Циолковского, 144/4 (офис и склады)", "kz": "Павлодар, Циолковский к-сі, 144/4 (кеңсе және қоймалар)"},
    "categories": [
        {"ru": "Промышленная химия", "kz": "Өнеркәсіптік химия"},
        {"ru": "Дезинфицирующие средства", "kz": "Дезинфекциялық құралдар"},
        {"ru": "Растворители", "kz": "Еріткіштер"},
        {"ru": "Канистры пластиковые", "kz": "Пластик канистрлер"},
        {"ru": "Пищевые добавки", "kz": "Тағамдық қоспалар"},
        {"ru": "Очистка воды, химия для бассейна", "kz": "Суды тазарту, бассейн химиясы"},
        {"ru": "Добавки к бетону", "kz": "Бетонға арналған қоспалар"},
    ],
}

UI = {
    "ru": {
        "lang": "ru", "hreflang": "ru", "og_locale": "ru_KZ",
        "nav": ["Каталог", "О компании", "Документация", "Доставка и оплата", "Контакты"],
        "home": "Главная", "catalog": "Каталог",
        "quote": "Запросить цену", "whatsapp": "Написать в WhatsApp", "menu": "Меню", "close": "Закрыть",
        "skip": "Перейти к содержимому",
        "in_stock": "В наличии", "out_stock": "Под заказ",
        "key_specs": "Основные характеристики", "packs": "Фасовка",
        "price_note": "Цену, наличие и сроки отгрузки уточнит менеджер.",
        "zoom": "Увеличить фото", "no_photo": "Фото товара появится позже",
        "tabs": ["Описание", "Применение", "Характеристики", "Хранение и поставка", "Документация"],
        "ids": ["opisanie", "primenenie", "harakteristiki", "hranenie", "dokumenty"],
        "h_desc": "Описание", "h_apps": "Области применения", "h_specs": "Характеристики",
        "h_storage": "Хранение и поставка", "h_docs": "Документация",
        "docs_all": "Все документы", "doc_open": "Открыть", "doc_download": "Скачать",
        "doc_request": "Запросить", "doc_sample": "Образец: файл предоставит заказчик",
        "doc_wa": "Здравствуйте! Пришлите, пожалуйста, документ «{doc}» на товар «{product}».",
        "h_why": "Почему ХИММАКС",
        "why": [
            ["warehouse", "Свой склад в Павлодаре", "Отгружаем со склада на ул. Циолковского."],
            ["truck", "Доставка по Казахстану", "Отправляем в любой регион, сроки считает менеджер."],
            ["handshake", "Опт и розница", "Продаём от одной канистры до партии."],
            ["search-check", "Помогаем с подбором", "Подскажем реагент и фасовку под вашу задачу."],
            ["clock", "Более 6 лет работы", "Поставляем химию предприятиям и госучреждениям."],
        ],
        "cta_h": "Нужна консультация или подбор продукции?",
        "cta_p": "Свяжитесь с менеджером: поможем уточнить характеристики, фасовку, наличие и условия поставки.",
        "cta_btn": "Связаться с нами",
        "foot_about": "Поставщик химической продукции и дезинфицирующих средств. Склад в Павлодаре, доставка по Казахстану.",
        "foot_catalog": "Каталог", "foot_company": "Компания", "foot_docs": "Документация", "foot_contacts": "Контакты",
        "foot_company_links": ["О компании", "Доставка и оплата", "Контакты"],
        "foot_docs_links": ["Сертификаты", "Паспорта безопасности", "Технические документы"],
        "privacy": "Политика конфиденциальности", "rights": "ХИММАКС",
        "f_title": "Запрос цены", "f_product": "Товар", "f_name": "Имя", "f_phone": "Телефон",
        "f_pack": "Объём или фасовка", "f_pack_other": "Другой объём, укажу в комментарии",
        "f_region": "Регион доставки", "f_region_ph": "Например, Павлодар или Астана",
        "f_comment": "Комментарий", "f_comment_ph": "Нужный объём, сроки, вопросы",
        "f_submit": "Отправить заявку", "f_consent": "Нажимая кнопку, вы соглашаетесь на обработку персональных данных.",
        "f_required": "Обязательное поле", "f_phone_err": "Укажите телефон, чтобы менеджер мог перезвонить",
        "f_name_err": "Укажите, как к вам обращаться",
        "f_ok_h": "Заявка принята", "f_ok_p": "Менеджер перезвонит в рабочее время и уточнит цену и наличие.",
        "f_wa_h": "Заявка готова", "f_wa_p": "Отправьте её менеджеру в WhatsApp, он ответит в рабочее время.",
        "f_wa_btn": "Отправить в WhatsApp",
        "f_err": "Не получилось отправить. Позвоните нам или напишите в WhatsApp.",
        "wa_text": "Здравствуйте! Интересует товар «{product}». Подскажите цену и наличие.",
        "wa_req": "Заявка с сайта", "lang_switch": "Язык сайта",
    },
    "kz": {
        "lang": "kk", "hreflang": "kk", "og_locale": "kk_KZ",
        "nav": ["Каталог", "Компания туралы", "Құжаттама", "Жеткізу және төлем", "Байланыс"],
        "home": "Басты бет", "catalog": "Каталог",
        "quote": "Бағасын сұрау", "whatsapp": "WhatsApp-қа жазу", "menu": "Мәзір", "close": "Жабу",
        "skip": "Мазмұнға өту",
        "in_stock": "Қоймада бар", "out_stock": "Тапсырыс бойынша",
        "key_specs": "Негізгі сипаттамалар", "packs": "Қаптамасы",
        "price_note": "Бағасын, қолда барын және жөнелту мерзімін менеджер нақтылайды.",
        "zoom": "Фотоны үлкейту", "no_photo": "Тауар фотосы кейінірек қосылады",
        "tabs": ["Сипаттама", "Қолданылуы", "Сипаттамалар", "Сақтау және жеткізу", "Құжаттама"],
        "ids": ["sipattama", "qoldanyluy", "sipattamalar", "saqtau", "qujattar"],
        "h_desc": "Сипаттама", "h_apps": "Қолдану салалары", "h_specs": "Сипаттамалар",
        "h_storage": "Сақтау және жеткізу", "h_docs": "Құжаттама",
        "docs_all": "Барлық құжаттар", "doc_open": "Ашу", "doc_download": "Жүктеу",
        "doc_request": "Сұрау", "doc_sample": "Үлгі: файлды тапсырыс беруші ұсынады",
        "doc_wa": "Сәлеметсіз бе! «{product}» тауарына «{doc}» құжатын жіберіңізші.",
        "h_why": "Неге ХИММАКС",
        "why": [
            ["warehouse", "Павлодарда өз қоймамыз", "Циолковский көшесіндегі қоймадан жөнелтеміз."],
            ["truck", "Қазақстан бойынша жеткізу", "Кез келген өңірге жібереміз, мерзімін менеджер есептейді."],
            ["handshake", "Көтерме және бөлшек сауда", "Бір канистрден бастап партияға дейін сатамыз."],
            ["search-check", "Таңдауға көмектесеміз", "Міндетіңізге сай реагент пен қаптаманы ұсынамыз."],
            ["clock", "6 жылдан астам жұмыс", "Кәсіпорындар мен мемлекеттік мекемелерге химия жеткіземіз."],
        ],
        "cta_h": "Кеңес немесе өнім таңдау керек пе?",
        "cta_p": "Менеджерге хабарласыңыз: сипаттамаларды, қаптаманы, қолда барын және жеткізу шарттарын нақтылауға көмектесеміз.",
        "cta_btn": "Бізбен байланысу",
        "foot_about": "Химиялық өнімдер мен дезинфекциялық құралдарды жеткізуші. Қойма Павлодарда, Қазақстан бойынша жеткізу.",
        "foot_catalog": "Каталог", "foot_company": "Компания", "foot_docs": "Құжаттама", "foot_contacts": "Байланыс",
        "foot_company_links": ["Компания туралы", "Жеткізу және төлем", "Байланыс"],
        "foot_docs_links": ["Сертификаттар", "Қауіпсіздік паспорттары", "Техникалық құжаттар"],
        "privacy": "Құпиялылық саясаты", "rights": "ХИММАКС",
        "f_title": "Бағасын сұрау", "f_product": "Тауар", "f_name": "Атыңыз", "f_phone": "Телефон",
        "f_pack": "Көлемі немесе қаптамасы", "f_pack_other": "Басқа көлем, түсініктемеде жазамын",
        "f_region": "Жеткізу өңірі", "f_region_ph": "Мысалы, Павлодар немесе Астана",
        "f_comment": "Түсініктеме", "f_comment_ph": "Қажетті көлем, мерзім, сұрақтар",
        "f_submit": "Өтінім жіберу", "f_consent": "Батырманы басу арқылы дербес деректерді өңдеуге келісім бересіз.",
        "f_required": "Міндетті өріс", "f_phone_err": "Менеджер хабарласуы үшін телефонды көрсетіңіз",
        "f_name_err": "Сізге қалай жүгінуге болатынын көрсетіңіз",
        "f_ok_h": "Өтінім қабылданды", "f_ok_p": "Менеджер жұмыс уақытында хабарласып, бағасы мен қолда барын нақтылайды.",
        "f_wa_h": "Өтінім дайын", "f_wa_p": "Оны WhatsApp арқылы менеджерге жіберіңіз, ол жұмыс уақытында жауап береді.",
        "f_wa_btn": "WhatsApp-қа жіберу",
        "f_err": "Жіберу мүмкін болмады. Бізге қоңырау шалыңыз немесе WhatsApp-қа жазыңыз.",
        "wa_text": "Сәлеметсіз бе! «{product}» тауары қызықтырады. Бағасы мен қолда барын айтыңызшы.",
        "wa_req": "Сайттан өтінім", "lang_switch": "Сайт тілі",
    },
}

E = html.escape


def icon(name, cls="icon"):
    svg = (SRC / "icons" / f"{name}.svg").read_text()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
    svg = re.sub(r'\s(width|height|class)="[^"]*"', "", svg, count=3)
    if "<title>" in svg:  # simple-icons
        svg = re.sub(r"<title>.*?</title>", "", svg)
        svg = svg.replace("<svg", '<svg fill="currentColor"', 1)
    svg = re.sub(r"\s+", " ", svg)
    return svg.replace("<svg", f'<svg class="{cls}" aria-hidden="true" focusable="false"', 1)


def wa_link(text):
    return f"https://wa.me/{SITE['whatsapp']}?text={quote(text)}"


def page_paths(p):
    ru = f"catalog/{p['category']['ru']['slug']}/{p['slug']['ru']}/"
    kz = f"kz/katalog/{p['category']['kz']['slug']}/{p['slug']['kz']}/"
    return {"ru": ru, "kz": kz}


def picture(img, L, pre, sizes, cls, eager):
    base, ws = img["base"], img["widths"]
    srcset = lambda ext: ", ".join(f"{pre}img/{base}-{w}.{ext} {w}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img class="{cls}" src="{pre}img/{base}-{ws[1]}.webp" width="{img["w"]}" height="{img["h"]}" '
            f'alt="{E(img["alt"][L])}" {load} decoding="async"></picture>')


def render(p, L):
    t, paths = UI[L], page_paths(p)
    pre = "../" * paths[L].count("/")
    name, short = p["name"][L], p["short"][L]
    url = f"{DOMAIN}/{paths[L]}"
    cat = p["category"][L]["name"]
    ids = t["ids"]
    wa_main = wa_link(t["wa_text"].format(product=name))
    key_specs = [s for s in p["specs"] if s["key"] and s["value"][L].strip()]
    all_specs = [s for s in p["specs"] if s["value"][L].strip()]
    docs = [d for d in p["documents"] if PREVIEW or not d["placeholder"]]
    storage = [s for s in p["storage"] if s["value"][L].strip()]
    apps = p["applications"]

    # --- JSON-LD: только опубликованные свойства, без цены, рейтинга и наличия
    crumbs = [(t["home"], f"{DOMAIN}/" + ("kz/" if L == "kz" else "")), (t["catalog"], None), (cat, None), (name, url)]
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": u} if u else {})} for i, (n, u) in enumerate(crumbs)]}
    ld_product = {"@context": "https://schema.org", "@type": "Product", "name": name, "description": short,
                  "category": cat, "url": url,
                  "image": [f"{DOMAIN}/img/{i['base']}-{i['widths'][-1]}.webp" for i in p["images"]],
                  "additionalProperty": [{"@type": "PropertyValue", "name": s["label"][L], "value": s["value"][L]} for s in all_specs]}

    # --- галерея
    imgs = p["images"]
    if imgs:
        main = (f'<button class="gallery-main" type="button" data-zoom aria-label="{E(t["zoom"])}">'
                f'{picture(imgs[0], L, pre, "(min-width: 1024px) 560px, 100vw", "gallery-img", True)}'
                f'<span class="zoom-hint">{icon("search-check")}</span></button>')
        thumbs = ""
        if len(imgs) > 1:
            thumbs = '<ul class="thumbs">' + "".join(
                f'<li><button type="button" class="thumb" data-thumb="{i}" aria-pressed="{str(i == 0).lower()}" aria-label="{E(im["alt"][L])}">'
                f'{picture(im, L, pre, "96px", "thumb-img", False)}</button></li>' for i, im in enumerate(imgs)) + "</ul>"
        gallery = main + thumbs
    else:
        gallery = f'<div class="gallery-empty">{icon("image")}<p>{E(t["no_photo"])}</p></div>'

    status = ""
    if p["availability"]["show"]:
        ok = p["availability"]["in_stock"]
        status = f'<p class="status{"" if ok else " status-order"}">{icon("circle-check")}{E(t["in_stock"] if ok else t["out_stock"])}</p>'

    dl = lambda rows: "".join(f'<div class="spec-row"><dt>{E(s["label"][L])}</dt><dd>{E(s["value"][L])}</dd></div>' for s in rows)

    packs = ""
    if p["packs"]:
        packs = (f'<fieldset class="packs"><legend>{E(t["packs"])}</legend><div class="pack-list">' + "".join(
            f'<label class="pack"><input type="radio" name="pack" value="{E(k["label"][L])}"{" checked" if i == 0 else ""}><span>{E(k["label"][L])}</span></label>'
            for i, k in enumerate(p["packs"])) + "</div></fieldset>")

    desc = "".join(f"<{tag}>{E(txt)}</{tag}>" for tag, txt in p["description"][L])

    apps_html = "".join(
        f'<li class="app">{icon(a["icon"], "icon app-icon")}<h3>{E(a["title"][L])}</h3><p>{E(a["text"][L])}</p></li>' for a in apps)

    def doc_row(d):
        meta = ", ".join(x for x in [d["format"], d["size"]] if x)
        title = d["title"][L]
        if d["file"]:
            act = (f'<a class="btn btn-ghost btn-sm" href="{pre}{d["file"]}" target="_blank" rel="noopener">{icon("eye")}{E(t["doc_open"])}</a>'
                   f'<a class="btn btn-ghost btn-sm" href="{pre}{d["file"]}" download>{icon("download")}{E(t["doc_download"])}</a>')
        else:
            act = f'<a class="btn btn-ghost btn-sm" href="{wa_link(t["doc_wa"].format(doc=title, product=name))}" target="_blank" rel="noopener">{icon("whatsapp")}{E(t["doc_request"])}</a>'
        sample = f'<span class="doc-sample">{E(t["doc_sample"])}</span>' if d["placeholder"] else ""
        return (f'<li class="doc{" doc-placeholder" if d["placeholder"] else ""}">{icon("file-text", "icon doc-icon")}'
                f'<div class="doc-text"><p class="doc-title">{E(title)}</p><p class="doc-meta">{E(d["type"][L])}{(", " + E(meta)) if meta else ""}</p>{sample}</div>'
                f'<div class="doc-actions">{act}</div></li>')

    docs_html = "".join(doc_row(d) for d in docs)

    # секции и вкладки: показываем только непустые
    sections = [(ids[0], t["tabs"][0], True), (ids[1], t["tabs"][1], bool(apps)), (ids[2], t["tabs"][2], bool(all_specs)),
                (ids[3], t["tabs"][3], bool(storage)), (ids[4], t["tabs"][4], bool(docs))]
    tabs = "".join(f'<li><a href="#{i}">{E(n)}</a></li>' for i, n, on in sections if on)

    phones_head = SITE["phones"][0]
    nav_links = "".join(f'<li><a href="{pre}{"kz/" if L == "kz" else ""}#"{" aria-current=\"page\"" if i == 0 else ""}>{E(n)}</a></li>' for i, n in enumerate(t["nav"]))
    other = "kz" if L == "ru" else "ru"
    lang_sw = (f'<div class="lang" role="group" aria-label="{E(t["lang_switch"])}">'
               f'<a href="{pre}{paths["ru"]}" hreflang="ru" lang="ru"{" aria-current=\"true\"" if L == "ru" else ""}>RU</a>'
               f'<a href="{pre}{paths["kz"]}" hreflang="kk" lang="kk"{" aria-current=\"true\"" if L == "kz" else ""}>KZ</a></div>')

    why = "".join(f'<li class="why-item">{icon(ic, "icon why-icon")}<h3>{E(h)}</h3><p>{E(tx)}</p></li>' for ic, h, tx in t["why"])
    foot_cats = "".join(f'<li><a href="#">{E(c[L])}</a></li>' for c in SITE["categories"])
    foot_comp = "".join(f'<li><a href="#">{E(c)}</a></li>' for c in t["foot_company_links"])
    foot_docs = "".join(f'<li><a href="#">{E(c)}</a></li>' for c in t["foot_docs_links"])
    foot_phones = "".join(f'<li><a href="tel:{ph["tel"]}">{icon("phone")}<span>{ph["text"]}<small>{E(ph["note"][L])}</small></span></a></li>' for ph in SITE["phones"])
    cta_phones = "".join(f'<li><a href="tel:{ph["tel"]}">{ph["text"]}</a><span>{E(ph["note"][L])}</span></li>' for ph in SITE["phones"][:2])

    pack_opts = "".join(f'<option>{E(k["label"][L])}</option>' for k in p["packs"]) + f'<option value="other">{E(t["f_pack_other"])}</option>'

    i18n_js = json.dumps({k: t[k] for k in ["f_required", "f_phone_err", "f_name_err", "f_err", "wa_req", "f_product", "f_name", "f_phone", "f_pack", "f_region", "f_comment", "close", "menu"]}, ensure_ascii=False)

    return f"""<!doctype html>
<html lang="{t['lang']}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(p['seo'][L]['title'])}</title>
<meta name="description" content="{E(p['seo'][L]['description'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ru" href="{DOMAIN}/{paths['ru']}">
<link rel="alternate" hreflang="kk" href="{DOMAIN}/{paths['kz']}">
<link rel="alternate" hreflang="x-default" href="{DOMAIN}/{paths['ru']}">
<meta property="og:type" content="product">
<meta property="og:locale" content="{t['og_locale']}">
<meta property="og:title" content="{E(name)}">
<meta property="og:description" content="{E(short)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/img/{imgs[0]['base']}-{imgs[0]['widths'][-1]}.webp">
<meta name="theme-color" content="#0b1a3a">
<script>document.documentElement.classList.replace('no-js','js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Onest:wght@400;600&display=swap">
<link rel="stylesheet" href="{pre}assets/styles.css">
<script type="application/ld+json">{json.dumps(ld_bc, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(ld_product, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{E(t['skip'])}</a>
<header class="site-header">
  <div class="container header-row">
    <a class="logo" href="{pre}{'kz/' if L == 'kz' else ''}"><img src="{pre}img/logo.webp" width="240" height="165" alt="ХИММАКС"></a>
    <nav class="main-nav" id="site-nav" aria-label="{E(t['menu'])}"><ul>{nav_links}</ul>{lang_sw.replace('class="lang"', 'class="lang lang-nav"')}</nav>
    <div class="header-actions">
      <a class="header-phone" href="tel:{phones_head['tel']}">{icon('phone')}<span>{phones_head['text']}</span></a>
      {lang_sw}
      <button class="btn btn-primary btn-sm header-cta" type="button" data-quote>{E(t['quote'])}</button>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="{E(t['menu'])}">{icon('menu', 'icon i-open')}{icon('x', 'icon i-close')}</button>
    </div>
  </div>
</header>

<main id="main">
  <section class="product-head">
    <div class="container">
      <nav class="crumbs" aria-label="breadcrumbs"><ol>
        <li><a href="{pre}{'kz/' if L == 'kz' else ''}">{E(t['home'])}</a></li>
        <li><a href="#">{E(t['catalog'])}</a></li>
        <li><a href="#">{E(cat)}</a></li>
        <li aria-current="page">{E(name)}</li>
      </ol></nav>
      <h1>{E(name)}</h1>
      <p class="lead">{E(short)}</p>
    </div>
  </section>

  <section class="product-main container" aria-label="{E(name)}">
    <div class="gallery">{gallery}</div>
    <div class="buybox">
      {status}
      <h2 class="buybox-h">{E(t['key_specs'])}</h2>
      <dl class="specs specs-key">{dl(key_specs)}</dl>
      {packs}
      <div class="actions">
        <button class="btn btn-primary" type="button" data-quote>{E(t['quote'])}</button>
        <a class="btn btn-ghost" href="{wa_main}" target="_blank" rel="noopener" data-wa>{icon('whatsapp')}{E(t['whatsapp'])}</a>
      </div>
      <p class="price-note">{E(t['price_note'])}</p>
    </div>
  </section>

  <nav class="section-nav" aria-label="{E(name)}"><div class="container"><ul>{tabs}</ul></div></nav>

  <div class="container content-grid">
    <section id="{ids[0]}" class="block block-desc"><h2>{E(t['h_desc'])}</h2><div class="prose">{desc}</div></section>
    {f'<section id="{ids[1]}" class="block block-apps"><h2>{E(t["h_apps"])}</h2><ul class="apps">{apps_html}</ul></section>' if apps else ''}
  </div>

  <div class="band-light"><div class="container content-grid">
    {f'<section id="{ids[2]}" class="block"><h2>{E(t["h_specs"])}</h2><dl class="specs specs-full">{dl(all_specs)}</dl></section>' if all_specs else ''}
    {f'<section id="{ids[3]}" class="block"><h2>{E(t["h_storage"])}</h2><dl class="specs specs-full">{dl(storage)}</dl></section>' if storage else ''}
  </div></div>

  {f'''<section id="{ids[4]}" class="container block block-docs">
    <div class="block-head"><h2>{E(t["h_docs"])}</h2><a class="text-link" href="#">{E(t["docs_all"])}</a></div>
    <ul class="docs">{docs_html}</ul>
  </section>''' if docs else ''}

  <section class="container block block-why">
    <h2>{E(t['h_why'])}</h2>
    <ul class="why">{why}</ul>
  </section>

  <section class="cta-band">
    <div class="container cta-row">
      <div class="cta-text"><h2>{E(t['cta_h'])}</h2><p>{E(t['cta_p'])}</p>
        <div class="actions">
          <button class="btn btn-primary" type="button" data-quote data-general>{E(t['cta_btn'])}</button>
          <a class="btn btn-ghost btn-on-dark" href="{wa_link(t['wa_text'].format(product=name))}" target="_blank" rel="noopener">{icon('whatsapp')}{E(t['whatsapp'])}</a>
        </div>
      </div>
      <ul class="cta-phones">{cta_phones}</ul>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container foot-grid">
    <div class="foot-brand"><img class="foot-logo" src="{pre}img/logo.webp" width="240" height="165" alt="ХИММАКС" loading="lazy"><p>{E(t['foot_about'])}</p></div>
    <div><h2 class="foot-h">{E(t['foot_catalog'])}</h2><ul>{foot_cats}</ul></div>
    <div><h2 class="foot-h">{E(t['foot_company'])}</h2><ul>{foot_comp}</ul><h2 class="foot-h foot-h-2">{E(t['foot_docs'])}</h2><ul>{foot_docs}</ul></div>
    <div><h2 class="foot-h">{E(t['foot_contacts'])}</h2><ul class="foot-contacts">{foot_phones}
      <li><a href="mailto:{SITE['email']}">{icon('mail')}<span>{SITE['email']}</span></a></li>
      <li><a href="{wa_main}" target="_blank" rel="noopener">{icon('whatsapp')}<span>WhatsApp</span></a></li>
      <li class="foot-addr">{icon('map-pin')}<span>{E(SITE['address'][L])}</span></li></ul></div>
  </div>
  <div class="container foot-bottom"><p>© 2026 {E(t['rights'])}</p><a href="#">{E(t['privacy'])}</a></div>
</footer>

<dialog class="modal" id="quote-modal" aria-labelledby="quote-title">
  <div class="modal-body">
    <button class="modal-close" type="button" data-close aria-label="{E(t['close'])}">{icon('x')}</button>
    <form class="quote-form" novalidate data-endpoint="" data-product="{E(name)}">
      <h2 id="quote-title">{E(t['f_title'])}</h2>
      <label class="field"><span>{E(t['f_product'])}</span><input name="product" value="{E(name)}" readonly></label>
      <div class="field-row">
        <label class="field"><span>{E(t['f_name'])}</span><input name="name" autocomplete="name" required><small class="err" aria-live="polite"></small></label>
        <label class="field"><span>{E(t['f_phone'])}</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7" required><small class="err" aria-live="polite"></small></label>
      </div>
      <label class="field"><span>{E(t['f_pack'])}</span><select name="pack">{pack_opts}</select></label>
      <label class="field"><span>{E(t['f_region'])}</span><input name="region" autocomplete="address-level1" placeholder="{E(t['f_region_ph'])}"></label>
      <label class="field"><span>{E(t['f_comment'])}</span><textarea name="comment" rows="3" placeholder="{E(t['f_comment_ph'])}"></textarea></label>
      <button class="btn btn-primary btn-block" type="submit">{E(t['f_submit'])}</button>
      <p class="consent">{E(t['f_consent'])}</p>
    </form>
    <div class="quote-done" hidden data-done="ok"><h2>{E(t['f_ok_h'])}</h2><p>{E(t['f_ok_p'])}</p></div>
    <div class="quote-done" hidden data-done="wa"><h2>{E(t['f_wa_h'])}</h2><p>{E(t['f_wa_p'])}</p>
      <a class="btn btn-primary btn-block" href="#" target="_blank" rel="noopener" data-wa-send>{icon('whatsapp')}{E(t['f_wa_btn'])}</a></div>
  </div>
</dialog>

<dialog class="modal modal-zoom" id="zoom-modal" aria-label="{E(name)}">
  <button class="modal-close" type="button" data-close aria-label="{E(t['close'])}">{icon('x')}</button>
  </dialog>

<script>window.HM_I18N={i18n_js};window.HM_WA="{SITE['whatsapp']}";</script>
<script src="{pre}assets/app.js" defer></script>
</body>
</html>
"""


def main():
    p = json.loads((SRC / "product.json").read_text())
    paths = page_paths(p)
    for L in ("ru", "kz"):
        out = OUT / paths[L] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(p, L))
        print("→", out.relative_to(ROOT))
    (OUT / "index.html").write_text(f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>ХИММАКС: макеты страниц</title>
<meta name="description" content="Превью шаблонов сайта ХИММАКС"><meta name="robots" content="noindex">
<link rel="stylesheet" href="assets/styles.css"></head><body><main class="container hub"><h1>ХИММАКС: макеты</h1><ul>
<li><a class="text-link" href="{paths['ru']}">Страница товара, RU</a></li>
<li><a class="text-link" href="{paths['kz']}">Страница товара, KZ</a></li></ul></main></body></html>
""")


if __name__ == "__main__":
    main()
