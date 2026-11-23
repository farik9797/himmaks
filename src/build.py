#!/usr/bin/env python3
"""Сборка статических макетов ХИММАКС (RU + KZ): главная, каталог, страница товара.

Запуск: python3 src/build.py
Данные: src/product.json (карточка товара), src/catalog-satu.json (товары с текущего сайта на Satu),
SITE / UI / CATS ниже (настройки компании, строки интерфейса, группы каталога).
PREVIEW = True показывает документы-заглушки с пометкой «образец» (на проде — False).
"""
import json, re, html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "src", ROOT / "site"
DOMAIN = "https://himmaks.kz"
PREVIEW = True
E = html.escape

SITE = {
    "phones": [
        {"tel": "+77472175547", "text": "+7 (747) 217-55-47", "note": {"ru": "Отдел продаж, Tele2", "kz": "Сату бөлімі, Tele2"}},
        {"tel": "+77782175547", "text": "+7 (778) 217-55-47", "note": {"ru": "Отдел продаж, Activ, WhatsApp", "kz": "Сату бөлімі, Activ, WhatsApp"}},
        {"tel": "+77182631100", "text": "+7 (718) 263-11-00", "note": {"ru": "Офис", "kz": "Кеңсе"}},
    ],
    "whatsapp": "77782175547",
    "email": "himmaks2020@mail.ru",
    "hours": {"ru": "Пн-Пт: 9:00-17:00", "kz": "Дүйсенбі-жұма: 9:00-17:00"},  # из разметки Satu (OpeningHoursSpecification)
    "address": {"ru": "Павлодар, ул. Циолковского, 144/4 (офис и склады)", "kz": "Павлодар, Циолковский к-сі, 144/4 (кеңсе және қоймалар)"},
}

# Картинки оформления: кадры из коллажей клиента (src/stock), обрезка и экспорт — scratchpad export.py
UI_IMG = {
    "hero": (742, 418), "about": (562, 409), "apps": (742, 306), "docs": (546, 409), "molecules": (733, 324),
    "head-product": (711, 426), "head-catalog": (562, 330),
    "cat-promyshlennaya-himiya": (747, 249), "cat-dezsredstva": (568, 379), "cat-ochistka-vody": (540, 360),
    "cat-pishchevye-dobavki": (540, 360), "cat-dobavki-k-betonu": (454, 303), "cat-kanistry": (486, 324),
    "cat-rastvoriteli": (561, 373),
    "head-about": (438, 394), "head-contacts": (562, 384), "delivery": (562, 375),
}
HERO_VIDEO = "assets/video/hero.mp4"  # появится файл — герой главной подхватит его фоном


def ui_img(name, pre, alt="", cls="", eager=False):
    w, h = UI_IMG[name]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="{cls}" src="{pre}img/ui/{name}.webp" width="{w}" height="{h}" alt="{E(alt)}" {load} decoding="async">'


# Группы каталога с Satu. img — фото группы, загруженное клиентом на Satu.
CATS = [
    {"slug": "promyshlennaya-himiya", "ru": "Промышленная химия", "kz": "Өнеркәсіптік химия"},
    {"slug": "dezsredstva", "ru": "Дезинфицирующие средства", "kz": "Дезинфекциялық құралдар"},
    {"slug": "ochistka-vody", "ru": "Очистка воды, химия для бассейна", "kz": "Суды тазарту, бассейн химиясы"},
    {"slug": "pishchevye-dobavki", "ru": "Пищевые добавки", "kz": "Тағамдық қоспалар"},
    {"slug": "dobavki-k-betonu", "ru": "Добавки к бетону", "kz": "Бетонға арналған қоспалар"},
    {"slug": "kanistry", "ru": "Канистры пластиковые", "kz": "Пластик канистрлер"},
    {"slug": "rastvoriteli", "ru": "Растворители", "kz": "Еріткіштер"},
]
CAT = {c["slug"]: c for c in CATS}

# Витрина главной: «Витрина» на himmaks.kz (Satu id), только товары в наличии
POPULAR = ["96314071", "96314098", "96314073", "96314095", "96314065", "96314088", "96314063", "gipohlorit-natriya"]

UI = {
    "ru": {
        "lang": "ru", "og_locale": "ru_KZ",
        "nav": ["Каталог", "О компании", "Документация", "Доставка и оплата", "Контакты"],
        "home": "Главная", "catalog": "Каталог",
        "quote": "Запросить цену", "whatsapp": "Написать в WhatsApp", "menu": "Меню", "close": "Закрыть",
        "skip": "Перейти к содержимому", "lang_switch": "Язык сайта",
        "in_stock": "В наличии", "out_stock": "Нет в наличии", "more": "Подробнее",
        "goods": ("товар", "товара", "товаров"), "pos": ("позиция", "позиции", "позиций"),
        # главная
        "home_title": "ХИММАКС: промышленная химия и дезсредства в Павлодаре, доставка по Казахстану",
        "home_desc": "Химическая продукция и дезинфицирующие средства со склада в Павлодаре. Опт и розница, доставка по Казахстану. Цену и наличие уточнит менеджер.",
        "hero_h": "Химия и дезсредства со склада в Павлодаре",
        "hero_p": "Поставляем предприятиям Казахстана оптом и в розницу, с доставкой по стране.",
        "hero_cta": "Перейти в каталог",
        "hero_img_alt": "Канистра натрия гипохлорита с этикеткой ХИММАКС на складе в Павлодаре",
        "facts": [["warehouse", "Свой склад в Павлодаре"], ["handshake", "Опт и розница"], ["truck", "Доставка по Казахстану"], ["search-check", "Помощь в подборе"]],
        "h_cats": "Каталог продукции", "cats_all": "Весь каталог",
        "h_about": "Поставляем химию для производства, водоочистки и пищевой отрасли",
        "about_p": "«ХИММАКС» поставляет химическую продукцию и дезинфицирующие средства. Среди наших клиентов промышленные предприятия, крупные компании Казахстана, государственные учреждения и малый бизнес.",
        "about_list": ["Офис и склады в Павлодаре", "Продаём оптом и в розницу", "Отправляем по всему Казахстану", "Работаем более 6 лет"],
        "about_link": "О компании", "about_img_alt": "Склад с бочками и еврокубами на стеллажах",
        "h_popular": "Популярные товары", "prev": "Назад", "next": "Вперёд",
        "h_apps": "Для каких задач",
        "apps": [["waves", "Водоочистка и бассейны", "ochistka-vody"], ["factory", "Промышленность", "promyshlennaya-himiya"],
                 ["spray-can", "Дезинфекция", "dezsredstva"], ["wheat", "Пищевое производство", "pishchevye-dobavki"],
                 ["brick-wall", "Строительство", "dobavki-k-betonu"]],
        "h_docs": "Нужен паспорт или сертификат на товар?",
        "docs_p": "Менеджер пришлёт документы, которые есть на выбранную позицию.",
        "docs_btn": "Запросить документы", "docs_wa": "Здравствуйте! Нужны документы на товар: ",
        "h_questions": "Остались вопросы?",
        "questions_p": "Поможем подобрать продукцию и посчитать поставку.",
        "ask": "Задать вопрос",
        # каталог
        "cat_title": "Каталог химической продукции ХИММАКС: цены по запросу, склад в Павлодаре",
        "cat_desc": "Промышленная химия, дезинфицирующие средства, пищевые добавки, добавки к бетону и тара. Склад в Павлодаре, доставка по Казахстану.",
        "cat_h": "Каталог продукции",
        "cat_lead": "{n} {pos} в {g} группах. Цену, наличие и фасовку уточнит менеджер.",
        "search": "Поиск по названию", "search_ph": "Например, сода или перекись",
        "groups": "Группы", "all_goods": "Все товары", "filters": "Фильтры", "only_stock": "Только в наличии",
        "reset": "Сбросить", "found": "Найдено:", "sort": "Сортировка", "sort_default": "Сначала в наличии", "sort_az": "По алфавиту",
        "show_more": "Показать ещё", "empty_h": "Ничего не нашлось", "empty_p": "Измените запрос или напишите нам: подберём аналог.",
        "aside_h": "Не нашли нужный товар?", "aside_p": "Напишите, что нужно: проверим склад и предложим аналог.",
        # футер
        "foot_about": "Поставщик химической продукции и дезинфицирующих средств. Склад в Павлодаре, доставка по Казахстану.",
        "foot_catalog": "Каталог", "foot_company": "Компания", "foot_docs": "Документация", "foot_contacts": "Контакты",
        "foot_company_links": ["О компании", "Доставка и оплата", "Контакты"],
        "foot_docs_links": ["Сертификаты", "Паспорта безопасности", "Технические документы"],
        "privacy": "Политика конфиденциальности", "rights": "ХИММАКС",
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
        # форма
        "f_title": "Запрос цены", "f_title_general": "Заявка менеджеру", "f_product": "Товар", "f_product_ph": "Какой товар интересует",
        "f_name": "Имя", "f_phone": "Телефон",
        "f_pack": "Объём или фасовка", "f_pack_ph": "Например, 200 кг или 10 канистр", "f_pack_other": "Другой объём, укажу в комментарии",
        "f_region": "Регион доставки", "f_region_ph": "Например, Павлодар или Астана",
        "f_comment": "Комментарий", "f_comment_ph": "Нужный объём, сроки, вопросы",
        "f_submit": "Отправить заявку", "f_consent": "Нажимая кнопку, вы соглашаетесь на обработку персональных данных.",
        "f_phone_err": "Укажите телефон, чтобы менеджер мог перезвонить", "f_name_err": "Укажите, как к вам обращаться",
        "f_ok_h": "Заявка принята", "f_ok_p": "Менеджер перезвонит в рабочее время и уточнит цену и наличие.",
        "f_wa_h": "Заявка готова", "f_wa_p": "Отправьте её менеджеру в WhatsApp, он ответит в рабочее время.",
        "f_wa_btn": "Отправить в WhatsApp",
        "f_err": "Не получилось отправить. Позвоните нам или напишите в WhatsApp.",
        "wa_text": "Здравствуйте! Интересует товар «{product}». Подскажите цену и наличие.",
        "wa_hello": "Здравствуйте! Хочу уточнить по продукции ХИММАКС.",
        "wa_req": "Заявка с сайта",
        # страница товара
        "key_specs": "Основные характеристики", "packs": "Фасовка",
        "price_note": "Цену, наличие и сроки отгрузки уточнит менеджер.",
        "zoom": "Увеличить фото", "no_photo": "Фото товара появится позже",
        "tabs": ["Описание", "Применение", "Характеристики", "Хранение и поставка", "Документация"],
        "ids": ["opisanie", "primenenie", "harakteristiki", "hranenie", "dokumenty"],
        "h_desc": "Описание", "h_papps": "Области применения", "h_specs": "Характеристики",
        "h_storage": "Хранение и поставка", "h_pdocs": "Документация",
        "docs_all": "Все документы", "doc_open": "Открыть", "doc_download": "Скачать",
        "doc_request": "Запросить", "doc_sample": "Образец: файл предоставит заказчик",
        "doc_wa": "Здравствуйте! Пришлите, пожалуйста, документ «{doc}» на товар «{product}».",
    },
    "kz": {
        "lang": "kk", "og_locale": "kk_KZ",
        "nav": ["Каталог", "Компания туралы", "Құжаттама", "Жеткізу және төлем", "Байланыс"],
        "home": "Басты бет", "catalog": "Каталог",
        "quote": "Бағасын сұрау", "whatsapp": "WhatsApp-қа жазу", "menu": "Мәзір", "close": "Жабу",
        "skip": "Мазмұнға өту", "lang_switch": "Сайт тілі",
        "in_stock": "Қоймада бар", "out_stock": "Қоймада жоқ", "more": "Толығырақ",
        "goods": ("тауар", "тауар", "тауар"), "pos": ("позиция", "позиция", "позиция"),
        "home_title": "ХИММАКС: Павлодардағы өнеркәсіптік химия және дезинфекциялық құралдар, Қазақстан бойынша жеткізу",
        "home_desc": "Павлодардағы қоймадан химиялық өнімдер мен дезинфекциялық құралдар. Көтерме және бөлшек сауда, Қазақстан бойынша жеткізу. Бағасы мен қолда барын менеджер нақтылайды.",
        "hero_h": "Павлодардағы қоймадан химия және дезқұралдар",
        "hero_p": "Қазақстан кәсіпорындарына көтерме және бөлшек саудамен, ел бойынша жеткізумен жабдықтаймыз.",
        "hero_cta": "Каталогқа өту",
        "hero_img_alt": "Павлодардағы қоймада ХИММАКС заттаңбасы бар натрий гипохлориті канистрі",
        "facts": [["warehouse", "Павлодарда өз қоймамыз"], ["handshake", "Көтерме және бөлшек"], ["truck", "Қазақстан бойынша жеткізу"], ["search-check", "Таңдауға көмек"]],
        "h_cats": "Өнім каталогы", "cats_all": "Бүкіл каталог",
        "h_about": "Өндіріске, суды тазартуға және тамақ саласына химия жеткіземіз",
        "about_p": "«ХИММАКС» химиялық өнімдер мен дезинфекциялық құралдарды жеткізеді. Клиенттеріміздің арасында өнеркәсіп кәсіпорындары, Қазақстанның ірі компаниялары, мемлекеттік мекемелер және шағын бизнес бар.",
        "about_list": ["Кеңсе мен қоймалар Павлодарда", "Көтерме және бөлшек сатамыз", "Бүкіл Қазақстанға жібереміз", "6 жылдан астам жұмыс істейміз"],
        "about_link": "Компания туралы", "about_img_alt": "Сөрелерде бөшкелер мен еврокубтар тұрған қойма",
        "h_popular": "Танымал тауарлар", "prev": "Артқа", "next": "Алға",
        "h_apps": "Қандай міндеттерге",
        "apps": [["waves", "Суды тазарту және бассейндер", "ochistka-vody"], ["factory", "Өнеркәсіп", "promyshlennaya-himiya"],
                 ["spray-can", "Дезинфекция", "dezsredstva"], ["wheat", "Тамақ өндірісі", "pishchevye-dobavki"],
                 ["brick-wall", "Құрылыс", "dobavki-k-betonu"]],
        "h_docs": "Тауарға паспорт немесе сертификат керек пе?",
        "docs_p": "Менеджер таңдалған позицияға бар құжаттарды жібереді.",
        "docs_btn": "Құжаттарды сұрау", "docs_wa": "Сәлеметсіз бе! Тауарға құжаттар керек: ",
        "h_questions": "Сұрақтарыңыз бар ма?",
        "questions_p": "Өнімді таңдауға және жеткізуді есептеуге көмектесеміз.",
        "ask": "Сұрақ қою",
        "cat_title": "ХИММАКС химиялық өнімдер каталогы: бағасы сұрау бойынша, қойма Павлодарда",
        "cat_desc": "Өнеркәсіптік химия, дезинфекциялық құралдар, тағамдық қоспалар, бетонға арналған қоспалар және ыдыс. Қойма Павлодарда, Қазақстан бойынша жеткізу.",
        "cat_h": "Өнім каталогы",
        "cat_lead": "{g} топта {n} позиция. Бағасын, қолда барын және қаптамасын менеджер нақтылайды.",
        "search": "Атауы бойынша іздеу", "search_ph": "Мысалы, сода немесе асқын тотық",
        "groups": "Топтар", "all_goods": "Барлық тауарлар", "filters": "Сүзгілер", "only_stock": "Тек қоймада барлары",
        "reset": "Тазарту", "found": "Табылды:", "sort": "Сұрыптау", "sort_default": "Алдымен қоймада барлары", "sort_az": "Әліпби бойынша",
        "show_more": "Тағы көрсету", "empty_h": "Ештеңе табылмады", "empty_p": "Сұранысты өзгертіңіз немесе бізге жазыңыз: баламасын табамыз.",
        "aside_h": "Қажетті тауарды таппадыңыз ба?", "aside_p": "Не керегін жазыңыз: қойманы тексеріп, баламасын ұсынамыз.",
        "foot_about": "Химиялық өнімдер мен дезинфекциялық құралдарды жеткізуші. Қойма Павлодарда, Қазақстан бойынша жеткізу.",
        "foot_catalog": "Каталог", "foot_company": "Компания", "foot_docs": "Құжаттама", "foot_contacts": "Байланыс",
        "foot_company_links": ["Компания туралы", "Жеткізу және төлем", "Байланыс"],
        "foot_docs_links": ["Сертификаттар", "Қауіпсіздік паспорттары", "Техникалық құжаттар"],
        "privacy": "Құпиялылық саясаты", "rights": "ХИММАКС",
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
        "f_title": "Бағасын сұрау", "f_title_general": "Менеджерге өтінім", "f_product": "Тауар", "f_product_ph": "Қандай тауар қызықтырады",
        "f_name": "Атыңыз", "f_phone": "Телефон",
        "f_pack": "Көлемі немесе қаптамасы", "f_pack_ph": "Мысалы, 200 кг немесе 10 канистр", "f_pack_other": "Басқа көлем, түсініктемеде жазамын",
        "f_region": "Жеткізу өңірі", "f_region_ph": "Мысалы, Павлодар немесе Астана",
        "f_comment": "Түсініктеме", "f_comment_ph": "Қажетті көлем, мерзім, сұрақтар",
        "f_submit": "Өтінім жіберу", "f_consent": "Батырманы басу арқылы дербес деректерді өңдеуге келісім бересіз.",
        "f_phone_err": "Менеджер хабарласуы үшін телефонды көрсетіңіз", "f_name_err": "Сізге қалай жүгінуге болатынын көрсетіңіз",
        "f_ok_h": "Өтінім қабылданды", "f_ok_p": "Менеджер жұмыс уақытында хабарласып, бағасы мен қолда барын нақтылайды.",
        "f_wa_h": "Өтінім дайын", "f_wa_p": "Оны WhatsApp арқылы менеджерге жіберіңіз, ол жұмыс уақытында жауап береді.",
        "f_wa_btn": "WhatsApp-қа жіберу",
        "f_err": "Жіберу мүмкін болмады. Бізге қоңырау шалыңыз немесе WhatsApp-қа жазыңыз.",
        "wa_text": "Сәлеметсіз бе! «{product}» тауары қызықтырады. Бағасы мен қолда барын айтыңызшы.",
        "wa_hello": "Сәлеметсіз бе! ХИММАКС өнімдері бойынша сұрағым бар.",
        "wa_req": "Сайттан өтінім",
        "key_specs": "Негізгі сипаттамалар", "packs": "Қаптамасы",
        "price_note": "Бағасын, қолда барын және жөнелту мерзімін менеджер нақтылайды.",
        "zoom": "Фотоны үлкейту", "no_photo": "Тауар фотосы кейінірек қосылады",
        "tabs": ["Сипаттама", "Қолданылуы", "Сипаттамалар", "Сақтау және жеткізу", "Құжаттама"],
        "ids": ["sipattama", "qoldanyluy", "sipattamalar", "saqtau", "qujattar"],
        "h_desc": "Сипаттама", "h_papps": "Қолдану салалары", "h_specs": "Сипаттамалар",
        "h_storage": "Сақтау және жеткізу", "h_pdocs": "Құжаттама",
        "docs_all": "Барлық құжаттар", "doc_open": "Ашу", "doc_download": "Жүктеу",
        "doc_request": "Сұрау", "doc_sample": "Үлгі: файлды тапсырыс беруші ұсынады",
        "doc_wa": "Сәлеметсіз бе! «{product}» тауарына «{doc}» құжатын жіберіңізші.",
    },
}

# Склад на карте: метка с карты на странице контактов Satu (himmaks.kz/contacts)
GEO = (52.2716168, 76.9979234)

# Страницы «О компании» и «Контакты». Источник фактов: himmaks.kz/about_us и /contacts (Satu), 23.11.2026
UI["ru"].update({
    "about_title": "О компании ХИММАКС: поставщик химии и дезсредств в Павлодаре",
    "about_desc": "ТОО «ХИММАКС»: офис и склады в Павлодаре, химическая продукция и дезинфицирующие средства оптом и в розницу, доставка по Казахстану.",
    "about_h": "О компании",
    "about_lead": "«ХИММАКС» поставляет химическую продукцию и дезинфицирующие средства со склада в Павлодаре.",
    "about_body": [
        "Мы торговая компания. Продукция лежит на нашем складе в Павлодаре, на улице Циолковского, там же офис, где менеджеры принимают заказы.",
        "Покупают у нас промышленные предприятия, крупные компании Казахстана, государственные учреждения и малый бизнес. Продаём оптом и в розницу, от одной канистры до партии, и отправляем по всему Казахстану.",
        "Если нужной позиции нет в каталоге, напишите. Проверим склад и предложим аналог.",
    ],
    "about_facts_h": "Коротко о компании",
    "about_facts": [
        ["Форма", "ТОО"], ["Тип", "Торговая компания"], ["Сотрудники", "5-10 человек"],
        ["Офис и склады", "Павлодар, ул. Циолковского, 144/4"], ["Продажи", "Опт и розница"],
        ["Доставка", "По всему Казахстану"],
    ],
    "clients_h": "Кому поставляем",
    "clients": [["factory", "Промышленные предприятия"], ["building-2", "Крупные компании Казахстана"],
                ["landmark", "Государственные учреждения"], ["store", "Малый бизнес"]],
    "stock_h": "Что на складе",
    "steps_h": "Как оформить заказ",
    "steps": [
        ["Заявка", "Позвоните, напишите в WhatsApp или оставьте заявку на сайте."],
        ["Цена и документы", "Менеджер уточнит цену, наличие и фасовку и пришлёт документы, которые есть на товар."],
        ["Отгрузка", "Заберите заказ со склада на Циолковского или закажите доставку по Казахстану."],
    ],
    "delivery_alt": "Грузовик на трассе",
    "contacts_title": "Контакты ХИММАКС: телефоны, WhatsApp, адрес склада в Павлодаре",
    "contacts_desc": "Павлодар, ул. Циолковского, 144/4. Отдел продаж: +7 (747) 217-55-47, +7 (778) 217-55-47 (WhatsApp). Пн-Пт 9:00-17:00.",
    "contacts_h": "Контакты",
    "contacts_lead": "Офис и склады в Павлодаре. Отвечаем в рабочее время.",
    "c_phones": "Телефоны", "c_write": "Написать", "c_address": "Адрес", "c_hours": "Режим работы",
    "c_route": "Проезд по ул. Циолковского в сторону Большой объездной дороги (Жібек жолы), не доезжая до неё.",
    "c_maps": "Открыть в картах", "c_map_title": "Склад ХИММАКС на карте Павлодара",
    "c_strip_h": "Нужна цена или подбор продукции?",
    "c_strip_p": "Оставьте заявку: менеджер перезвонит и уточнит цену, наличие и фасовку.",
})
UI["kz"].update({
    "about_title": "ХИММАКС компаниясы туралы: Павлодардағы химия және дезқұралдар жеткізушісі",
    "about_desc": "«ХИММАКС» ЖШС: кеңсе мен қоймалар Павлодарда, химиялық өнімдер мен дезинфекциялық құралдар көтерме және бөлшек саудада, Қазақстан бойынша жеткізу.",
    "about_h": "Компания туралы",
    "about_lead": "«ХИММАКС» Павлодардағы қоймадан химиялық өнімдер мен дезинфекциялық құралдарды жеткізеді.",
    "about_body": [
        "Біз сауда компаниясымыз. Өнім Павлодардағы Циолковский көшесіндегі өз қоймамызда тұр, менеджерлер тапсырыс қабылдайтын кеңсе де сонда.",
        "Бізден өнеркәсіп кәсіпорындары, Қазақстанның ірі компаниялары, мемлекеттік мекемелер және шағын бизнес сатып алады. Көтерме және бөлшек сатамыз, бір канистрден бастап партияға дейін, бүкіл Қазақстанға жібереміз.",
        "Қажетті позиция каталогта болмаса, жазыңыз. Қойманы тексеріп, баламасын ұсынамыз.",
    ],
    "about_facts_h": "Компания туралы қысқаша",
    "about_facts": [
        ["Нысаны", "ЖШС"], ["Түрі", "Сауда компаниясы"], ["Қызметкерлер", "5-10 адам"],
        ["Кеңсе мен қоймалар", "Павлодар, Циолковский к-сі, 144/4"], ["Сауда", "Көтерме және бөлшек"],
        ["Жеткізу", "Бүкіл Қазақстан бойынша"],
    ],
    "clients_h": "Кімге жеткіземіз",
    "clients": [["factory", "Өнеркәсіп кәсіпорындары"], ["building-2", "Қазақстанның ірі компаниялары"],
                ["landmark", "Мемлекеттік мекемелер"], ["store", "Шағын бизнес"]],
    "stock_h": "Қоймада не бар",
    "steps_h": "Тапсырысты қалай рәсімдеу керек",
    "steps": [
        ["Өтінім", "Қоңырау шалыңыз, WhatsApp-қа жазыңыз немесе сайтта өтінім қалдырыңыз."],
        ["Баға және құжаттар", "Менеджер бағасын, қолда барын және қаптамасын нақтылап, тауарға бар құжаттарды жібереді."],
        ["Жөнелту", "Тапсырысты Циолковский көшесіндегі қоймадан алып кетіңіз немесе Қазақстан бойынша жеткізуге тапсырыс беріңіз."],
    ],
    "delivery_alt": "Тасжолдағы жүк көлігі",
    "contacts_title": "ХИММАКС байланыстары: телефондар, WhatsApp, Павлодардағы қойма мекенжайы",
    "contacts_desc": "Павлодар, Циолковский к-сі, 144/4. Сату бөлімі: +7 (747) 217-55-47, +7 (778) 217-55-47 (WhatsApp). Дүйсенбі-жұма 9:00-17:00.",
    "contacts_h": "Байланыс",
    "contacts_lead": "Кеңсе мен қоймалар Павлодарда. Жұмыс уақытында жауап береміз.",
    "c_phones": "Телефондар", "c_write": "Жазу", "c_address": "Мекенжай", "c_hours": "Жұмыс уақыты",
    "c_route": "Циолковский көшесімен Үлкен айналма жолға (Жібек жолы) қарай жүріп, оған жетпей тоқтаңыз.",
    "c_maps": "Картадан ашу", "c_map_title": "Павлодар картасындағы ХИММАКС қоймасы",
    "c_strip_h": "Баға немесе өнім таңдау керек пе?",
    "c_strip_p": "Өтінім қалдырыңыз: менеджер хабарласып, бағасын, қолда барын және қаптамасын нақтылайды.",
})


# ---------------------------------------------------------------- helpers

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


def plural(n, forms):
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:
        return forms[0]
    if 2 <= n10 <= 4 and not 12 <= n100 <= 14:
        return forms[1]
    return forms[2]


def depth_prefix(path):
    return "../" * path.count("/")


def urls(p):
    """Пути страниц сайта для обоих языков (относительно корня)."""
    return {
        "home": {"ru": "", "kz": "kz/"},
        "catalog": {"ru": "catalog/", "kz": "kz/katalog/"},
        "about": {"ru": "o-kompanii/", "kz": "kz/kompaniya-turaly/"},
        "contacts": {"ru": "kontakty/", "kz": "kz/baylanys/"},
        "product": {"ru": f"catalog/{p['category']['ru']['slug']}/{p['slug']['ru']}/",
                    "kz": f"kz/katalog/{p['category']['kz']['slug']}/{p['slug']['kz']}/"},
    }


def picture(img, L, pre, sizes, cls, eager):
    base, ws = img["base"], img["widths"]
    srcset = lambda ext: ", ".join(f"{pre}img/{base}-{w}.{ext} {w}w" for w in ws)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img class="{cls}" src="{pre}img/{base}-{ws[1]}.webp" width="{img["w"]}" height="{img["h"]}" '
            f'alt="{E(img["alt"][L])}" {load} decoding="async"></picture>')


# ---------------------------------------------------------------- shared chrome

def head(L, title, desc, here, alts, og_image, ld=(), og_type="website", noindex=False):
    t = UI[L]
    pre = depth_prefix(here)
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f"""<!doctype html>
<html lang="{t['lang']}" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{DOMAIN}/{here}">
<link rel="alternate" hreflang="ru" href="{DOMAIN}/{alts['ru']}">
<link rel="alternate" hreflang="kk" href="{DOMAIN}/{alts['kz']}">
<link rel="alternate" hreflang="x-default" href="{DOMAIN}/{alts['ru']}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="{t['og_locale']}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{DOMAIN}/{here}">
<meta property="og:image" content="{DOMAIN}/{og_image}">
<meta name="theme-color" content="#0b1a3a">
<link rel="icon" href="{pre}img/logo.webp" type="image/webp">
<script>document.documentElement.classList.replace('no-js','js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Onest:wght@400;600&display=swap">
<link rel="stylesheet" href="{pre}assets/styles.css">
{ld_html}
</head>
<body>
<a class="skip" href="#main">{E(t['skip'])}</a>
"""


def header(L, here, alts, active, U):
    t = UI[L]
    pre = depth_prefix(here)
    targets = [U["catalog"][L], U["about"][L], None, None, U["contacts"][L]]
    nav = "".join(
        f'<li><a href="{pre + targets[i] if targets[i] is not None else "#"}"{" aria-current=\"page\"" if i == active else ""}>{E(n)}</a></li>'
        for i, n in enumerate(t["nav"]))
    lang = (f'<div class="lang" role="group" aria-label="{E(t["lang_switch"])}">'
            f'<a href="{pre}{alts["ru"]}" hreflang="ru" lang="ru"{" aria-current=\"true\"" if L == "ru" else ""}>RU</a>'
            f'<a href="{pre}{alts["kz"]}" hreflang="kk" lang="kk"{" aria-current=\"true\"" if L == "kz" else ""}>KZ</a></div>')
    ph = SITE["phones"][0]
    return f"""<header class="site-header">
  <div class="container header-row">
    <a class="logo" href="{pre}{U['home'][L]}"><img src="{pre}img/logo.webp" width="240" height="165" alt="ХИММАКС"></a>
    <nav class="main-nav" id="site-nav" aria-label="{E(t['menu'])}"><ul>{nav}</ul>{lang.replace('class="lang"', 'class="lang lang-nav"')}</nav>
    <div class="header-actions">
      <a class="header-phone" href="tel:{ph['tel']}">{icon('phone')}<span>{ph['text']}</span></a>
      {lang}
      <button class="btn btn-primary btn-sm header-cta" type="button" data-quote data-general>{E(t['quote'])}</button>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="{E(t['menu'])}">{icon('menu', 'icon i-open')}{icon('x', 'icon i-close')}</button>
    </div>
  </div>
</header>
"""


def why_block(L):
    t = UI[L]
    items = "".join(f'<li class="why-item">{icon(ic, "icon why-icon")}<h3>{E(h)}</h3><p>{E(tx)}</p></li>' for ic, h, tx in t["why"])
    return f'<section class="container block block-why"><h2>{E(t["h_why"])}</h2><ul class="why">{items}</ul></section>'


def cta_band(L, pre, wa_text=None):
    t = UI[L]
    phones = "".join(f'<li><a href="tel:{ph["tel"]}">{ph["text"]}</a><span>{E(ph["note"][L])}</span></li>' for ph in SITE["phones"][:2])
    return f"""<section class="cta-band">
    {ui_img('molecules', pre, cls='cta-art')}
    <div class="container cta-row">
      <div class="cta-text"><h2>{E(t['cta_h'])}</h2><p>{E(t['cta_p'])}</p>
        <div class="actions">
          <button class="btn btn-primary" type="button" data-quote data-general>{E(t['cta_btn'])}</button>
          <a class="btn btn-ghost btn-on-dark" href="{wa_link(wa_text or t['wa_hello'])}" target="_blank" rel="noopener">{icon('whatsapp')}{E(t['whatsapp'])}</a>
        </div>
      </div>
      <div class="cta-side"><ul class="cta-phones">{phones}</ul><p class="cta-hours">{E(SITE['hours'][L])}</p></div>
    </div>
  </section>"""


def footer(L, here, U):
    t = UI[L]
    pre = depth_prefix(here)
    cat_url = pre + U["catalog"][L]
    cats = "".join(f'<li><a href="{cat_url}?cat={c["slug"]}">{E(c[L])}</a></li>' for c in CATS)
    comp_href = [pre + U["about"][L], "#", pre + U["contacts"][L]]
    comp = "".join(f'<li><a href="{h}">{E(c)}</a></li>' for c, h in zip(t["foot_company_links"], comp_href))
    docs = "".join(f'<li><a href="#">{E(c)}</a></li>' for c in t["foot_docs_links"])
    phones = "".join(f'<li><a href="tel:{ph["tel"]}">{icon("phone")}<span>{ph["text"]}<small>{E(ph["note"][L])}</small></span></a></li>' for ph in SITE["phones"])
    return f"""<footer class="site-footer">
  <div class="container foot-grid">
    <div class="foot-brand"><img class="foot-logo" src="{pre}img/logo.webp" width="240" height="165" alt="ХИММАКС" loading="lazy"><p>{E(t['foot_about'])}</p></div>
    <div><h2 class="foot-h">{E(t['foot_catalog'])}</h2><ul>{cats}</ul></div>
    <div><h2 class="foot-h">{E(t['foot_company'])}</h2><ul>{comp}</ul><h2 class="foot-h foot-h-2">{E(t['foot_docs'])}</h2><ul>{docs}</ul></div>
    <div><h2 class="foot-h">{E(t['foot_contacts'])}</h2><ul class="foot-contacts">{phones}
      <li><a href="mailto:{SITE['email']}">{icon('mail')}<span>{SITE['email']}</span></a></li>
      <li><a href="{wa_link(t['wa_hello'])}" target="_blank" rel="noopener">{icon('whatsapp')}<span>WhatsApp</span></a></li>
      <li class="foot-addr">{icon('map-pin')}<span>{E(SITE['address'][L])}</span></li>
      <li class="foot-addr">{icon('clock')}<span>{E(SITE['hours'][L])}</span></li></ul></div>
  </div>
  <div class="container foot-bottom"><p>© 2026 {E(t['rights'])}</p><a href="#">{E(t['privacy'])}</a></div>
</footer>
"""


def quote_dialog(L, here, product=None, packs=None):
    """Форма запроса цены. product=None — общая заявка, поле товара редактируемое."""
    t = UI[L]
    pre = depth_prefix(here)
    if packs:
        pack_field = (f'<select name="pack">' + "".join(f'<option>{E(k["label"][L])}</option>' for k in packs)
                      + f'<option value="other">{E(t["f_pack_other"])}</option></select>')
    else:
        pack_field = f'<input name="pack" placeholder="{E(t["f_pack_ph"])}">'
    i18n = json.dumps({k: t[k] for k in ["f_phone_err", "f_name_err", "f_err", "wa_req", "f_product", "f_name", "f_phone",
                                         "f_pack", "f_region", "f_comment", "f_title", "f_title_general"]}, ensure_ascii=False)
    return f"""<dialog class="modal" id="quote-modal" aria-labelledby="quote-title">
  <div class="modal-body">
    <button class="modal-close" type="button" data-close aria-label="{E(t['close'])}">{icon('x')}</button>
    <form class="quote-form" novalidate data-endpoint="" data-product="{E(product or '')}">
      <h2 id="quote-title">{E(t['f_title'])}</h2>
      <label class="field"><span>{E(t['f_product'])}</span><input name="product" value="{E(product or '')}" placeholder="{E(t['f_product_ph'])}"{' readonly' if product else ''}></label>
      <div class="field-row">
        <label class="field"><span>{E(t['f_name'])}</span><input name="name" autocomplete="name" required><small class="err" aria-live="polite"></small></label>
        <label class="field"><span>{E(t['f_phone'])}</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" placeholder="+7" required><small class="err" aria-live="polite"></small></label>
      </div>
      <label class="field"><span>{E(t['f_pack'])}</span>{pack_field}</label>
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
<script>window.HM_I18N={i18n};window.HM_WA="{SITE['whatsapp']}";</script>
<script src="{pre}assets/app.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- catalog data

def load_goods(p):
    """Товары с Satu + замены: два листинга гипохлорита натрия сведены в одну карточку с готовой страницей."""
    raw = json.loads((SRC / "catalog-satu.json").read_text())
    goods, gipo = [], None
    for g in raw:
        item = {"id": g["id"], "cats": [g["cat"]], "name": g["name"], "img": f"img/p/{g['id']}.webp",
                "stock": g["presence"] == "В наличии", "page": None}
        if g["name"].strip() == "Гипохлорит натрия":
            if gipo is None:
                gipo = item
                item.update(id="gipohlorit-natriya", name=p["name"]["ru"], name_kz=p["name"]["kz"],
                            img="img/gipohlorit-natriya-480.webp", page=True)
                goods.append(item)
            elif g["cat"] not in gipo["cats"]:
                gipo["cats"].append(g["cat"])
            continue
        goods.append(item)
    return goods


def goods_card(g, L, pre, U, tag="li"):
    t = UI[L]
    name = g.get("name_kz") if L == "kz" and g.get("name_kz") else g["name"]
    href = pre + U["product"][L] if g["page"] else None
    cat_name = CAT[g["cats"][0]][L]
    title = f'<a href="{href}">{E(name)}</a>' if href else E(name)
    media = (f'<img src="{pre}{g["img"]}" width="480" height="480" alt="{E(name)}" loading="lazy" decoding="async">')
    media = f'<a class="card-media" href="{href}" tabindex="-1" aria-hidden="true">{media}</a>' if href else f'<div class="card-media">{media}</div>'
    stock = (f'<p class="status">{icon("circle-check")}{E(t["in_stock"])}</p>' if g["stock"]
             else f'<p class="status status-off">{E(t["out_stock"])}</p>')
    more = f'<a class="text-link card-more" href="{href}">{E(t["more"])}</a>' if href else ""
    return (f'<{tag} class="card" data-cats="{" ".join(g["cats"])}" data-name="{E(name.lower())}" data-stock="{int(g["stock"])}">'
            f'{media}<div class="card-body"><p class="card-cat">{E(cat_name)}</p><h3 class="card-title">{title}</h3>{stock}'
            f'<div class="card-actions"><button class="btn btn-primary btn-sm" type="button" data-quote data-product="{E(name)}">{E(t["quote"])}</button>{more}</div></div></{tag}>')


def cat_cards(L, pre, goods, U):
    t = UI[L]
    cat_url = pre + U["catalog"][L]
    counts = {c["slug"]: sum(1 for g in goods if c["slug"] in g["cats"]) for c in CATS}
    return "".join(
        f'<li><a class="cat-card" href="{cat_url}?cat={c["slug"]}">{ui_img("cat-" + c["slug"], pre)}'
        f'<span class="cat-name">{E(c[L])}</span><span class="cat-count">{counts[c["slug"]]} {plural(counts[c["slug"]], t["goods"])}</span></a></li>'
        for c in CATS)


def page_head(L, pre, U, here_key, img, h1, lead):
    t = UI[L]
    return f"""<section class="product-head">
    {ui_img(img, pre, cls='head-bg', eager=True)}
    <div class="container">
      <nav class="crumbs" aria-label="breadcrumbs"><ol><li><a href="{pre}{U['home'][L]}">{E(t['home'])}</a></li><li aria-current="page">{E(h1)}</li></ol></nav>
      <h1>{E(h1)}</h1>
      <p class="lead">{E(lead)}</p>
    </div>
  </section>"""


def crumbs_ld(L, U, key, name):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": UI[L]["home"], "item": f"{DOMAIN}/{U['home'][L]}"},
        {"@type": "ListItem", "position": 2, "name": name, "item": f"{DOMAIN}/{U[key][L]}"}]}


def org_ld():
    lat, lon = GEO
    return {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": f"{DOMAIN}/#org", "name": "ХИММАКС",
            "url": DOMAIN + "/", "logo": f"{DOMAIN}/img/logo.webp", "image": f"{DOMAIN}/img/logo.webp", "email": SITE["email"],
            "telephone": SITE["phones"][0]["text"],
            "address": {"@type": "PostalAddress", "streetAddress": "ул. Циолковского, 144/4", "addressLocality": "Павлодар", "addressCountry": "KZ"},
            "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lon},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                           "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                           "opens": "09:00", "closes": "17:00"}]}


# ---------------------------------------------------------------- pages

def render_home(L, p, goods, U):
    t = UI[L]
    here = U["home"][L]
    pre = depth_prefix(here)
    cat_url = pre + U["catalog"][L]
    ld_org = {"@context": "https://schema.org", "@type": "Organization", "name": "ХИММАКС", "url": DOMAIN + "/",
              "logo": f"{DOMAIN}/img/logo.webp", "email": SITE["email"],
              "telephone": [ph["text"] for ph in SITE["phones"]],
              "address": {"@type": "PostalAddress", "streetAddress": "ул. Циолковского, 144/4", "addressLocality": "Павлодар", "addressCountry": "KZ"}}

    video = ""
    if (OUT / HERO_VIDEO).exists():
        video = (f'<video class="hero-video" muted loop playsinline preload="none" poster="{pre}img/ui/hero.webp" '
                 f'data-src="{pre}{HERO_VIDEO}"></video>')
    facts = "".join(f'<li>{icon(ic)}<span>{E(tx)}</span></li>' for ic, tx in t["facts"])
    cats = cat_cards(L, pre, goods, U)
    by_id = {g["id"]: g for g in goods}
    popular = "".join(goods_card(by_id[i], L, pre, U) for i in POPULAR if i in by_id)
    about_list = "".join(f'<li>{icon("circle-check")}<span>{E(x)}</span></li>' for x in t["about_list"])
    apps = "".join(f'<li><a class="app-link" href="{cat_url}?cat={slug}">{icon(ic)}<span>{E(name)}</span></a></li>' for ic, name, slug in t["apps"])

    body = f"""<main id="main">
  <section class="home-hero">
    <div class="hero-bg" aria-hidden="true">{ui_img('hero', pre, cls='hero-poster', eager=True)}{video}</div>
    <div class="container hero-grid">
      <div class="hero-text">
        <h1>{E(t['hero_h'])}</h1>
        <p class="lead">{E(t['hero_p'])}</p>
        <div class="actions hero-actions">
          <a class="btn btn-primary" href="{cat_url}">{E(t['hero_cta'])}</a>
          <button class="btn btn-ghost btn-on-dark" type="button" data-quote data-general>{E(t['quote'])}</button>
        </div>
        <ul class="hero-facts">{facts}</ul>
      </div>
    </div>
  </section>

  <section class="container block">
    <div class="block-head"><h2>{E(t['h_cats'])}</h2><a class="text-link" href="{cat_url}">{E(t['cats_all'])}</a></div>
    <ul class="cat-grid">{cats}</ul>
  </section>

  <section class="container">
    <div class="about-panel">
      <div class="about-text">
        <h2>{E(t['h_about'])}</h2>
        <p>{E(t['about_p'])}</p>
        <ul class="about-list">{about_list}</ul>
        <a class="btn btn-primary" href="{pre}{U['about'][L]}">{E(t['about_link'])}</a>
      </div>
      <div class="about-media">{ui_img('about', pre, t['about_img_alt'])}</div>
    </div>
  </section>

  <section class="container block" aria-labelledby="popular-h">
    <div class="block-head"><h2 id="popular-h">{E(t['h_popular'])}</h2>
      <div class="rail-nav"><button class="icon-btn" type="button" data-rail="-1" aria-label="{E(t['prev'])}">{icon('chevron-left')}</button><button class="icon-btn" type="button" data-rail="1" aria-label="{E(t['next'])}">{icon('chevron-right')}</button></div>
    </div>
    <ul class="rail" tabindex="0">{popular}</ul>
  </section>

  <section class="apps-band">
    {ui_img('apps', pre, cls='apps-bg')}
    <div class="container apps-row"><h2>{E(t['h_apps'])}</h2><ul class="app-links">{apps}</ul></div>
  </section>

  <section class="container block docs-strip">
    {ui_img('docs', pre, cls='docs-thumb')}
    <div><h2>{E(t['h_docs'])}</h2><p>{E(t['docs_p'])}</p></div>
    <a class="btn btn-ghost" href="{wa_link(t['docs_wa'])}" target="_blank" rel="noopener">{icon('whatsapp')}{E(t['docs_btn'])}</a>
  </section>

  {cta_band(L, pre)}
</main>
"""
    return (head(L, t["home_title"], t["home_desc"], here, U["home"], "img/gipohlorit-natriya-1029.webp", [ld_org])
            + header(L, here, U["home"], -1, U) + body + footer(L, here, U) + quote_dialog(L, here))


def render_catalog(L, p, goods, U):
    t = UI[L]
    here = U["catalog"][L]
    pre = depth_prefix(here)
    counts = {c["slug"]: sum(1 for g in goods if c["slug"] in g["cats"]) for c in CATS}
    order = sorted(goods, key=lambda g: not g["stock"])
    cards = "".join(goods_card(g, L, pre, U) for g in order)
    groups = (f'<label class="group"><input type="radio" name="cat" value="" checked><span>{E(t["all_goods"])}</span><span class="group-n">{len(goods)}</span></label>'
              + "".join(f'<label class="group"><input type="radio" name="cat" value="{c["slug"]}"><span>{E(c[L])}</span><span class="group-n">{counts[c["slug"]]}</span></label>' for c in CATS))
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": t["home"], "item": f"{DOMAIN}/{U['home'][L]}"},
        {"@type": "ListItem", "position": 2, "name": t["catalog"], "item": f"{DOMAIN}/{here}"}]}

    body = f"""<main id="main">
  <section class="product-head">
    {ui_img('head-catalog', pre, cls='head-bg', eager=True)}
    <div class="container">
      <nav class="crumbs" aria-label="breadcrumbs"><ol><li><a href="{pre}{U['home'][L]}">{E(t['home'])}</a></li><li aria-current="page">{E(t['catalog'])}</li></ol></nav>
      <h1>{E(t['cat_h'])}</h1>
      <p class="lead">{E(t['cat_lead'].format(n=len(goods), g=len(CATS), pos=plural(len(goods), t['pos'])))}</p>
      <label class="search"><span class="visually-hidden">{E(t['search'])}</span>{icon('search-check')}<input type="search" name="q" placeholder="{E(t['search_ph'])}" autocomplete="off"></label>
    </div>
  </section>

  <div class="container catalog-layout">
    <aside class="catalog-aside">
      <details class="filters" open>
        <summary>{icon('sliders-horizontal')}{E(t['filters'])}</summary>
        <fieldset class="groups"><legend>{E(t['groups'])}</legend>{groups}</fieldset>
        <label class="check"><input type="checkbox" name="stock"><span>{E(t['only_stock'])}</span></label>
        <button class="text-link reset" type="button" data-reset>{E(t['reset'])}</button>
      </details>
      <div class="aside-cta"><h2>{E(t['aside_h'])}</h2><p>{E(t['aside_p'])}</p>
        <button class="btn btn-primary btn-sm" type="button" data-quote data-general>{E(t['ask'])}</button></div>
    </aside>
    <section class="catalog-main" aria-label="{E(t['catalog'])}">
      <div class="toolbar">
        <p class="found" aria-live="polite">{E(t['found'])} <strong data-count>{len(goods)}</strong></p>
        <label class="sort"><span>{E(t['sort'])}</span><select name="sort"><option value="default">{E(t['sort_default'])}</option><option value="az">{E(t['sort_az'])}</option></select></label>
      </div>
      <ul class="cards" data-cards>{cards}</ul>
      <div class="empty" hidden data-empty><h2>{E(t['empty_h'])}</h2><p>{E(t['empty_p'])}</p>
        <button class="btn btn-ghost btn-sm" type="button" data-reset>{E(t['reset'])}</button></div>
      <button class="btn btn-ghost more-btn" type="button" data-more hidden>{E(t['show_more'])}</button>
    </section>
  </div>

  {why_block(L)}
  {cta_band(L, pre)}
</main>
"""
    return (head(L, t["cat_title"], t["cat_desc"], here, U["catalog"], "img/ui/head-catalog.webp", [ld_bc])
            + header(L, here, U["catalog"], 0, U) + body + footer(L, here, U) + quote_dialog(L, here))


def render_product(L, p, U):
    t = UI[L]
    here = U["product"][L]
    pre = depth_prefix(here)
    name, short = p["name"][L], p["short"][L]
    url = f"{DOMAIN}/{here}"
    cat_slug = "ochistka-vody"
    cat = p["category"][L]["name"]
    ids = t["ids"]
    wa_main = wa_link(t["wa_text"].format(product=name))
    key_specs = [s for s in p["specs"] if s["key"] and s["value"][L].strip()]
    all_specs = [s for s in p["specs"] if s["value"][L].strip()]
    docs = [d for d in p["documents"] if PREVIEW or not d["placeholder"]]
    storage = [s for s in p["storage"] if s["value"][L].strip()]
    apps = p["applications"]
    cat_url = pre + U["catalog"][L]

    crumbs = [(t["home"], f"{DOMAIN}/{U['home'][L]}"), (t["catalog"], f"{DOMAIN}/{U['catalog'][L]}"),
              (cat, f"{DOMAIN}/{U['catalog'][L]}?cat={cat_slug}"), (name, url)]
    ld_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}
    ld_product = {"@context": "https://schema.org", "@type": "Product", "name": name, "description": short,
                  "category": cat, "url": url,
                  "image": [f"{DOMAIN}/img/{i['base']}-{i['widths'][-1]}.webp" for i in p["images"]],
                  "additionalProperty": [{"@type": "PropertyValue", "name": s["label"][L], "value": s["value"][L]} for s in all_specs]}

    imgs = p["images"]
    if imgs:
        gallery = (f'<button class="gallery-main" type="button" data-zoom aria-label="{E(t["zoom"])}">'
                   f'{picture(imgs[0], L, pre, "(min-width: 1024px) 560px, 100vw", "gallery-img", True)}'
                   f'<span class="zoom-hint">{icon("search-check")}</span></button>')
        if len(imgs) > 1:
            gallery += '<ul class="thumbs">' + "".join(
                f'<li><button type="button" class="thumb" data-thumb="{i}" aria-pressed="{str(i == 0).lower()}" aria-label="{E(im["alt"][L])}">'
                f'{picture(im, L, pre, "96px", "thumb-img", False)}</button></li>' for i, im in enumerate(imgs)) + "</ul>"
    else:
        gallery = f'<div class="gallery-empty">{icon("image")}<p>{E(t["no_photo"])}</p></div>'

    status = ""
    if p["availability"]["show"]:
        ok = p["availability"]["in_stock"]
        status = (f'<p class="status">{icon("circle-check")}{E(t["in_stock"])}</p>' if ok
                  else f'<p class="status status-off">{E(t["out_stock"])}</p>')

    dl = lambda rows: "".join(f'<div class="spec-row"><dt>{E(s["label"][L])}</dt><dd>{E(s["value"][L])}</dd></div>' for s in rows)
    packs = ""
    if p["packs"]:
        packs = (f'<fieldset class="packs"><legend>{E(t["packs"])}</legend><div class="pack-list">' + "".join(
            f'<label class="pack"><input type="radio" name="pack" value="{E(k["label"][L])}"{" checked" if i == 0 else ""}><span>{E(k["label"][L])}</span></label>'
            for i, k in enumerate(p["packs"])) + "</div></fieldset>")
    desc = "".join(f"<{tag}>{E(txt)}</{tag}>" for tag, txt in p["description"][L])
    apps_html = "".join(f'<li class="app">{icon(a["icon"], "icon app-icon")}<h3>{E(a["title"][L])}</h3><p>{E(a["text"][L])}</p></li>' for a in apps)

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

    sections = [(ids[0], t["tabs"][0], True), (ids[1], t["tabs"][1], bool(apps)), (ids[2], t["tabs"][2], bool(all_specs)),
                (ids[3], t["tabs"][3], bool(storage)), (ids[4], t["tabs"][4], bool(docs))]
    tabs = "".join(f'<li><a href="#{i}">{E(n)}</a></li>' for i, n, on in sections if on)

    body = f"""<main id="main">
  <section class="product-head">
    {ui_img('head-product', pre, cls='head-bg')}
    <div class="container">
      <nav class="crumbs" aria-label="breadcrumbs"><ol>
        <li><a href="{pre}{U['home'][L]}">{E(t['home'])}</a></li>
        <li><a href="{cat_url}">{E(t['catalog'])}</a></li>
        <li><a href="{cat_url}?cat={cat_slug}">{E(cat)}</a></li>
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
    {f'<section id="{ids[1]}" class="block block-apps"><h2>{E(t["h_papps"])}</h2><ul class="apps">{apps_html}</ul></section>' if apps else ''}
  </div>

  <div class="band-light"><div class="container content-grid">
    {f'<section id="{ids[2]}" class="block"><h2>{E(t["h_specs"])}</h2><dl class="specs specs-full">{dl(all_specs)}</dl></section>' if all_specs else ''}
    {f'<section id="{ids[3]}" class="block"><h2>{E(t["h_storage"])}</h2><dl class="specs specs-full">{dl(storage)}</dl></section>' if storage else ''}
  </div></div>

  {f'''<section id="{ids[4]}" class="container block block-docs">
    <div class="block-head"><h2>{E(t["h_pdocs"])}</h2><a class="text-link" href="#">{E(t["docs_all"])}</a></div>
    <ul class="docs">{"".join(doc_row(d) for d in docs)}</ul>
  </section>''' if docs else ''}

  {why_block(L)}
  {cta_band(L, pre, t['wa_text'].format(product=name))}
</main>

<dialog class="modal modal-zoom" id="zoom-modal" aria-label="{E(name)}">
  <button class="modal-close" type="button" data-close aria-label="{E(t['close'])}">{icon('x')}</button>
</dialog>
"""
    return (head(L, p["seo"][L]["title"], p["seo"][L]["description"], here, U["product"],
                 f"img/{imgs[0]['base']}-{imgs[0]['widths'][-1]}.webp", [ld_bc, ld_product], og_type="product")
            + header(L, here, U["product"], 0, U) + body + footer(L, here, U) + quote_dialog(L, here, name, p["packs"]))


def render_about(L, goods, U):
    t = UI[L]
    here = U["about"][L]
    pre = depth_prefix(here)
    body_p = "".join(f"<p>{E(x)}</p>" for x in t["about_body"])
    facts = "".join(f'<div class="spec-row"><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in t["about_facts"])
    clients = "".join(f'<li>{icon(ic)}<span>{E(x)}</span></li>' for ic, x in t["clients"])
    steps = "".join(f'<li><h3>{E(h)}</h3><p>{E(x)}</p></li>' for h, x in t["steps"])
    ld_page = {"@context": "https://schema.org", "@type": "AboutPage", "url": f"{DOMAIN}/{here}", "name": t["about_title"],
               "about": {"@id": f"{DOMAIN}/#org"}}

    body = f"""<main id="main">
  {page_head(L, pre, U, 'about', 'head-about', t['about_h'], t['about_lead'])}

  <div class="container content-grid">
    <section class="block"><div class="prose">{body_p}</div></section>
    <section class="block" aria-labelledby="facts-h"><h2 id="facts-h" class="h-sm">{E(t['about_facts_h'])}</h2><dl class="specs">{facts}</dl></section>
  </div>

  <div class="band-light"><section class="container block"><h2>{E(t['clients_h'])}</h2><ul class="clients">{clients}</ul></section></div>

  <section class="container block">
    <div class="block-head"><h2>{E(t['stock_h'])}</h2><a class="text-link" href="{pre}{U['catalog'][L]}">{E(t['cats_all'])}</a></div>
    <ul class="cat-grid">{cat_cards(L, pre, goods, U)}</ul>
  </section>

  <section class="container block-end">
    <div class="about-panel">
      <div class="about-text">
        <h2>{E(t['steps_h'])}</h2>
        <ol class="steps">{steps}</ol>
        <button class="btn btn-primary" type="button" data-quote data-general>{E(t['quote'])}</button>
      </div>
      <div class="about-media">{ui_img('delivery', pre, t['delivery_alt'])}</div>
    </div>
  </section>

  {cta_band(L, pre)}
</main>
"""
    return (head(L, t["about_title"], t["about_desc"], here, U["about"], "img/ui/head-about.webp",
                 [crumbs_ld(L, U, "about", t["about_h"]), org_ld(), ld_page])
            + header(L, here, U["about"], 1, U) + body + footer(L, here, U) + quote_dialog(L, here))


def render_contacts(L, U):
    t = UI[L]
    here = U["contacts"][L]
    pre = depth_prefix(here)
    lat, lon = GEO
    phones = "".join(f'<li><a class="c-phone" href="tel:{ph["tel"]}">{ph["text"]}</a><span>{E(ph["note"][L])}</span></li>' for ph in SITE["phones"])
    maps = [("Яндекс Карты", f"https://yandex.kz/maps/?pt={lon},{lat}&z=17&l=map"),
            ("2ГИС", f"https://2gis.kz/pavlodar?m={lon},{lat}/17"),
            ("Google Maps", f"https://www.google.com/maps/search/?api=1&query={lat},{lon}")]
    map_links = "".join(f'<li><a class="text-link" href="{u}" target="_blank" rel="noopener">{E(n)}</a></li>' for n, u in maps)
    # OpenStreetMap: без рекламы и трекеров (виджет Яндекса показывал рекламу конкурентов и грузил пиксели DSP)
    map_src = (f"https://www.openstreetmap.org/export/embed.html?bbox={lon - 0.008:.6f}%2C{lat - 0.004:.6f}%2C"
               f"{lon + 0.008:.6f}%2C{lat + 0.004:.6f}&layer=mapnik&marker={lat}%2C{lon}")

    body = f"""<main id="main">
  {page_head(L, pre, U, 'contacts', 'head-contacts', t['contacts_h'], t['contacts_lead'])}

  <div class="container block contacts-grid">
    <div class="contact-list">
      <section class="contact-item">
        <div class="c-head">{icon('phone')}<h2>{E(t['c_phones'])}</h2></div>
        <ul class="c-phones">{phones}</ul>
      </section>
      <section class="contact-item">
        <div class="c-head">{icon('send')}<h2>{E(t['c_write'])}</h2></div>
        <div class="actions">
          <a class="btn btn-primary btn-sm" href="{wa_link(t['wa_hello'])}" target="_blank" rel="noopener">{icon('whatsapp')}{E(t['whatsapp'])}</a>
          <a class="btn btn-ghost btn-sm" href="mailto:{SITE['email']}">{icon('mail')}{SITE['email']}</a>
        </div>
      </section>
      <section class="contact-item">
        <div class="c-head">{icon('map-pin')}<h2>{E(t['c_address'])}</h2></div>
        <p class="c-strong">{E(SITE['address'][L])}</p>
        <p class="c-note">{E(t['c_route'])}</p>
        <p class="c-note">{E(t['c_maps'])}:</p>
        <ul class="c-maps">{map_links}</ul>
      </section>
      <section class="contact-item">
        <div class="c-head">{icon('clock')}<h2>{E(t['c_hours'])}</h2></div>
        <p class="c-strong">{E(SITE['hours'][L])}</p>
      </section>
    </div>
    <div class="map-frame">
      <iframe src="{map_src}" title="{E(t['c_map_title'])}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>
  </div>

  <section class="container block-end docs-strip">
    {ui_img('docs', pre, cls='docs-thumb')}
    <div><h2>{E(t['c_strip_h'])}</h2><p>{E(t['c_strip_p'])}</p></div>
    <button class="btn btn-primary" type="button" data-quote data-general>{E(t['quote'])}</button>
  </section>
</main>
"""
    return (head(L, t["contacts_title"], t["contacts_desc"], here, U["contacts"], "img/ui/head-contacts.webp",
                 [crumbs_ld(L, U, "contacts", t["contacts_h"]), org_ld()])
            + header(L, here, U["contacts"], 4, U) + body + footer(L, here, U) + quote_dialog(L, here))


def main():
    p = json.loads((SRC / "product.json").read_text())
    U = urls(p)
    goods = load_goods(p)
    for L in ("ru", "kz"):
        for kind, html_ in (("home", render_home(L, p, goods, U)), ("catalog", render_catalog(L, p, goods, U)),
                            ("product", render_product(L, p, U)), ("about", render_about(L, goods, U)),
                            ("contacts", render_contacts(L, U))):
            out = OUT / U[kind][L] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html_)
            print("→", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
