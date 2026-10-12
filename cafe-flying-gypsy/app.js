/* ============================================================
   Cafe Flying Gypsy's — app.js
   1201-A/4 GH Patil Path, Shivajinagar, Pune · open 24/7
   Vanilla JS, no dependencies, no build step.
   ============================================================ */
'use strict';

/* ------------------------------------------------------------
   ⚠️  PRICES
   The prices below marked with a number are REAL — they were taken
   from the cafe's public Google reviews. Every price set to  null
   is still unknown and renders as a muted "—".

   To fill them in, just replace the null. Example:
       { name:'Cheese Maggi', price:null,  ... }
       { name:'Cheese Maggi', price:179,   ... }
   Nothing else needs to change.
   ------------------------------------------------------------ */

const CONFIG = {
  name:      "Cafe Flying Gypsy's",
  phone:     '+919011147147',
  phoneText: '+91 90111 47147',
  whatsapp:  '919011147147',
  instagram: 'https://www.instagram.com/cafeflyinggypsys/',
  mapsDir:   'https://www.google.com/maps/dir/?api=1&destination=18.5240,73.8425',
  lat: 18.5240,
  lng: 73.8425
};

/* ---------------- menu ---------------- */
const MENU = [
  {
    id: 'maggi',
    label: 'Maggi',
    note: 'The reason people walk in at 2 AM.',
    items: [
      { name:'Italian Maggi',    price:169,  tag:'Most loved', desc:'Our most-ordered plate — cheesy, herby, and exactly right in the middle of the night.' },
      { name:'Cheese Maggi',     price:null, tag:'Veg',        desc:'Loaded with cheese, the way the regulars ask for it.' },
      { name:'Makhan Maggi',     price:null, tag:'Veg',        desc:'Buttery, mild and quietly comforting.' }
    ]
  },
  {
    id: 'pasta',
    label: 'Pasta & Ramen',
    note: 'The white-sauce pasta is the dish everyone tells you not to miss.',
    items: [
      { name:'White Sauce Pasta', price:289,  tag:'Most loved', desc:'Creamy mushroom penne, finished with herbed garlic bread on the side.' },
      { name:'Mix Sauce Pasta',   price:null, tag:'Veg',        desc:'Red and white sauce together — tangy and creamy at once.' },
      { name:'Cheesy Baked Pasta',price:null, tag:'Veg',        desc:'Baked until the cheese pulls, served with garlic bread sticks.' },
      { name:'Kimchi Ramen',      price:null, tag:'Spicy',      desc:'A little hot, a lot warming — the surprise favourite on the menu.' }
    ]
  },
  {
    id: 'pizza',
    label: 'Pizza & Sides',
    note: 'Stone-baked, hand-stretched, made to order.',
    items: [
      { name:'Paneer Tikka Pizza', price:null, tag:'Veg',   desc:'Paneer cubes, capsicum, onion and red pepper on a crisp base.' },
      { name:'Cheese Garlic Bread',price:null, tag:'Veg',   desc:'Straight from the oven with a herbed butter finish.' },
      { name:'Peri-Peri Fries',    price:null, tag:'Spicy', desc:'Dusted with peri-peri, served with a cool creamy dip.' },
      { name:'Loaded Cheesy Fries',price:null, tag:'Veg',   desc:'A full plate of fries under a blanket of cheese drizzle and herbs.' },
      { name:'Salted Fries',       price:null, tag:'Veg',   desc:'Thick-cut, properly crisp, with a white dip on the side.' }
    ]
  },
  {
    id: 'burgers',
    label: 'Burgers',
    note: 'Sesame buns, crisp patties, served with fries or nachos.',
    items: [
      { name:'Signature Sesame Burger', price:null, tag:'Veg', desc:'The big one — sesame bun, crisp patty, cheese and fresh salad.' },
      { name:'Cheese Burger',           price:null, tag:'Veg', desc:'Double cheese, no apologies.' },
      { name:'Crispy Veg Burger',       price:null, tag:'Veg', desc:'Crunchy patty with a tangy house sauce.' }
    ]
  },
  {
    id: 'shakes',
    label: 'Shakes & Frappes',
    note: 'Thick, cold and made with real ice cream.',
    items: [
      { name:'Crunchy Cheesecake Shake', price:155,  tag:'Most loved', desc:'Dessert and drink in the same glass.' },
      { name:'Oreo Nutella Shake',       price:219,  tag:'Veg',        desc:'Oreo and Nutella blended thick, topped with cream.' },
      { name:'KitKat Shake',             price:null, tag:'Veg',        desc:'Blended with real KitKat, chocolate drizzle on top.' },
      { name:'Noreo Shake',              price:null, tag:'Veg',        desc:'Nutella plus Oreo — the regulars\' shorthand.' },
      { name:'Blueberry Shake',          price:null, tag:'Veg',        desc:'Fruity, cold and not too sweet.' },
      { name:'Irish Frappe',             price:null, tag:'Veg',        desc:'Coffee-forward, blended and poured over ice.' }
    ]
  },
  {
    id: 'coffee',
    label: 'Coffee & Coolers',
    note: 'From a flat cappuccino to something tall and green.',
    items: [
      { name:'Cappuccino',    price:null, tag:'Veg', desc:'Properly pulled, with a heart in the foam.' },
      { name:'Cold Coffee',   price:null, tag:'Veg', desc:'Thick, chilled and generous.' },
      { name:'Iced Coffee',   price:null, tag:'Veg', desc:'Sweet and strong over ice.' },
      { name:'Cold Frappe',   price:null, tag:'Veg', desc:'After a long day at college, this is the one.' },
      { name:'Virgin Mojito', price:null, tag:'Veg', desc:'Lime, mint and a lot of fizz.' },
      { name:'Iced Tea',      price:null, tag:'Veg', desc:'Light, cold and refreshing.' }
    ]
  }
];

/* ---------------- gallery (the cafe's own photographs) ---------------- */
const GALLERY = [
  { file:'courtyard-blue-staircase.jpg',      w:243, h:406, cat:'interiors', cap:'The courtyard — blue staircase, palms and fairy lights' },
  { file:'paneer-tikka-pizza.jpg',            w:243, h:203, cat:'food',      cap:'Paneer tikka pizza, straight from the oven' },
  { file:'gypsy-girl-mural.jpg',              w:243, h:406, cat:'interiors', cap:'Our gypsy girl, hand-painted' },
  { file:'cheesy-loaded-fries.jpg',           w:243, h:406, cat:'food',      cap:'Loaded cheesy fries' },
  { file:'turquoise-gallery-wall.jpg',        w:243, h:244, cat:'interiors', cap:'The turquoise wall of frames and curios' },
  { file:'heart-latte-art-cappuccino.jpg',    w:243, h:174, cat:'drinks',    cap:'Cappuccino with heart latte art' },
  { file:'teddy-book-shelf-corner.jpg',       w:243, h:304, cat:'interiors', cap:'The reading corner — books, brick and one large teddy' },
  { file:'mushroom-white-sauce-pasta.jpg',    w:243, h:203, cat:'food',      cap:'Mushroom white-sauce pasta with garlic bread' },
  { file:'cafe-exterior-signboard.jpg',       w:243, h:244, cat:'interiors', cap:'The neon-lit entrance on GH Patil Path' },
  { file:'burger-nachos-chocolate-shake.jpg', w:243, h:406, cat:'food',      cap:'Sesame burger, nachos and a thick chocolate shake' },
  { file:'teal-wall-shelves-seating.jpg',     w:243, h:244, cat:'interiors', cap:'Quiet corner seats under the shelf wall' },
  { file:'shakes-mojito-fries-spread.jpg',    w:243, h:406, cat:'drinks',    cap:'Shakes, virgin mojito and peri-peri fries' },
  { file:'cafe-counter-interior.jpg',         w:243, h:174, cat:'interiors', cap:'Inside — the counter, hanging flowers and self-service' },
  { file:'cheesy-pasta-bake-garlic-bread.jpg',w:243, h:174, cat:'food',      cap:'Cheesy baked pasta and garlic bread sticks' },
  { file:'cold-coffee-frappe-courtyard.jpg',  w:243, h:304, cat:'drinks',    cap:'Iced coffee and frappes in the courtyard' },
  { file:'gypsy-mural-tables.jpg',            w:243, h:304, cat:'interiors', cap:'Wrought-iron tables beneath the mural' },
  { file:'burger-fries-outdoor-seating.jpg',  w:243, h:304, cat:'food',      cap:'Burgers and fries out in the open air' },
  { file:'birthday-celebration-table.jpg',    w:243, h:304, cat:'food',      cap:'Birthday spreads are a speciality here' }
];

/* ---------------- reviews (real, public Google reviews) ---------------- */
const REVIEWS = [
  { who:'Rushabh G.', init:'RG', stars:4, when:'Google review',
    text:'Turned out to be such a hidden gem. The interiors are super creative — a mix of rustic and artsy, with lots of little details. I tried their paneer pizza and creamy pasta and both were packed with flavour.' },
  { who:'vulimiri S.', init:'VS', stars:5, when:'Google review',
    text:'Will I visit this place again? Yes, why not. Proper cafe vibe, friendly staff and the food the best. Don\'t miss the white sauce pasta. The owner is very friendly and the place is Instagram worthy.' },
  { who:'Pratiksha D.', init:'PD', stars:5, when:'Google review',
    text:'I was skeptical at first, but it exceeded my expectations. The food was really good and worth every penny — surprisingly affordable too. I ordered mix sauce pasta, kimchi ramen and an Irish frappe, and everything was wow.' },
  { who:'Nupur S.', init:'NS', stars:5, when:'Google review',
    text:'The cafe is an all-rounder — from the ambience to the snooker section, everything is just perfect. Don\'t miss out on their awesome burger menu. It is indeed a must visit, 100% recommend.' },
  { who:'Vaishnavi K.', init:'VK', stars:4, when:'Google review',
    text:'Great ambience, super fresh. As you enter you will fall in love with the turquoise. The food quality is nice too — loved the food here. Overall a nice experience.' },
  { who:'Tisha M.', init:'TM', stars:4, when:'Google review',
    text:'A nice casual place to pass the time. We had the cheese Maggi — my favourite. There are games and books as well. It\'s like chill and relax.' }
];

/* ============================================================
   helpers
   ============================================================ */
const $  = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const inr = n => '₹' + Number(n).toLocaleString('en-IN');

/* ============================================================
   1. sticky nav
   ============================================================ */
(function stickyNav(){
  const nav = $('#nav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('is-stuck', window.scrollY > 24);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive:true });
})();

/* ============================================================
   2. mobile drawer
   ============================================================ */
(function drawer(){
  const burger = $('#hamburger');
  const panel  = $('#drawer');
  if (!burger || !panel) return;

  let open = false;

  const setOpen = state => {
    open = state;
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';

    if (open){
      panel.hidden = false;
      requestAnimationFrame(() => panel.classList.add('is-open'));
    } else {
      panel.classList.remove('is-open');
      const done = () => { if (!open){ panel.hidden = true; } };
      setTimeout(done, prefersReduced ? 0 : 340);
    }
  };

  burger.addEventListener('click', () => setOpen(!open));

  // close on link tap
  $$('a', panel).forEach(a => a.addEventListener('click', () => setOpen(false)));

  // close on escape / resize to desktop
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && open) setOpen(false); });
  window.addEventListener('resize', () => { if (window.innerWidth > 980 && open) setOpen(false); });
})();

/* ============================================================
   3. scroll reveal
   ============================================================ */
(function reveal(){
  const els = $$('.reveal');
  if (!els.length) return;

  if (prefersReduced || !('IntersectionObserver' in window)){
    els.forEach(el => el.classList.add('is-in'));
    return;
  }

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      obs.unobserve(entry.target);
    });
  }, { rootMargin:'0px 0px -8% 0px', threshold:0.12 });

  els.forEach(el => io.observe(el));
})();

/* ============================================================
   4. menu tabs
   ============================================================ */
(function menu(){
  const tabsEl   = $('.tabs');
  const panelsEl = $('#menuPanels');
  if (!tabsEl || !panelsEl) return;

  // build tabs
  MENU.forEach((cat, i) => {
    const b = document.createElement('button');
    b.className = 'tab';
    b.type = 'button';
    b.role = 'tab';
    b.id = `tab-${cat.id}`;
    b.dataset.panel = cat.id;
    b.setAttribute('aria-controls', `panel-${cat.id}`);
    b.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
    b.textContent = cat.label;
    tabsEl.appendChild(b);
  });

  // build panels
  MENU.forEach((cat, i) => {
    const panel = document.createElement('div');
    panel.className = 'panel';
    panel.id = `panel-${cat.id}`;
    panel.role = 'tabpanel';
    panel.setAttribute('aria-labelledby', `tab-${cat.id}`);
    if (i !== 0) panel.hidden = true;

    const note = document.createElement('p');
    note.className = 'panel-note';
    note.textContent = cat.note;
    panel.appendChild(note);

    const list = document.createElement('div');
    list.className = 'items';

    cat.items.forEach(item => {
      const row = document.createElement('article');
      row.className = 'item';

      const top = document.createElement('div');
      top.className = 'item-top';

      const h = document.createElement('h4');
      h.textContent = item.name;
      top.appendChild(h);

      if (item.tag){
        const t = document.createElement('span');
        t.className = 'tag ' + (item.tag === 'Spicy' ? 'hot' : item.tag === 'Most loved' ? '' : 'veg');
        t.textContent = item.tag;
        top.appendChild(t);
      }

      const price = document.createElement('span');
      if (item.price === null || item.price === undefined){
        price.className = 'price is-tbd';
        price.textContent = '—';
        price.title = "Price being updated — WhatsApp us for today's rate";
      } else {
        price.className = 'price';
        price.textContent = inr(item.price);
      }

      const desc = document.createElement('p');
      desc.textContent = item.desc;

      row.append(top, price, desc);
      list.appendChild(row);
    });

    panel.appendChild(list);
    panelsEl.appendChild(panel);
  });

  // tab switching (roving focus)
  const tabs = $$('.tab', tabsEl);
  const select = tab => {
    tabs.forEach(t => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      const panel = document.getElementById(`panel-${t.dataset.panel}`);
      if (panel) panel.hidden = !on;
    });
  };

  tabs.forEach((tab, i) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', e => {
      let next = null;
      if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
      if (e.key === 'ArrowLeft')  next = tabs[(i - 1 + tabs.length) % tabs.length];
      if (e.key === 'Home')       next = tabs[0];
      if (e.key === 'End')        next = tabs[tabs.length - 1];
      if (next){ e.preventDefault(); next.focus(); select(next); }
    });
  });
})();

/* ============================================================
   5. gallery + lightbox
   ============================================================ */
(function gallery(){
  const grid = $('#galGrid');
  const lb   = $('#lightbox');
  if (!grid || !lb) return;

  const lbImg   = $('#lbImg');
  const lbCap   = $('#lbCap');
  const lbCount = $('#lbCount');
  const lbClose = $('#lbClose');
  const lbPrev  = $('#lbPrev');
  const lbNext  = $('#lbNext');

  let visible = GALLERY.slice();
  let index = 0;

  // ---- build the grid ----
  GALLERY.forEach((shot, i) => {
    const fig = document.createElement('figure');
    fig.className = 'gal-item';
    fig.dataset.cat = shot.cat;
    fig.dataset.index = String(i);
    fig.tabIndex = 0;
    fig.role = 'button';
    fig.setAttribute('aria-label', `Open image: ${shot.cap}`);

    const img = document.createElement('img');
    img.src = `images/${shot.file}`;
    img.width = shot.w;
    img.height = shot.h;
    img.loading = 'lazy';
    img.decoding = 'async';
    img.alt = shot.cap;

    const cap = document.createElement('figcaption');
    cap.textContent = shot.cap;

    fig.append(img, cap);
    grid.appendChild(fig);
  });

  const items = $$('.gal-item', grid);

  // ---- filters ----
  const filters = $$('.filter');
  filters.forEach(btn => {
    btn.addEventListener('click', () => {
      filters.forEach(b => {
        const on = b === btn;
        b.classList.toggle('is-on', on);
        b.setAttribute('aria-selected', String(on));
      });

      const want = btn.dataset.filter;
      visible = [];
      items.forEach(fig => {
        const keep = want === 'all' || fig.dataset.cat === want;
        fig.classList.toggle('is-hidden', !keep);
        if (keep) visible.push(GALLERY[Number(fig.dataset.index)]);
      });
    });
  });

  // ---- lightbox ----
  let lastFocus = null;

  const render = () => {
    const shot = visible[index];
    if (!shot) return;
    lbImg.src = `images/${shot.file}`;
    lbImg.alt = shot.cap;
    lbCap.textContent = shot.cap;
    lbCount.textContent = `${index + 1} / ${visible.length}`;
  };

  const open = i => {
    index = i;
    lastFocus = document.activeElement;
    render();
    lb.hidden = false;
    requestAnimationFrame(() => lb.classList.add('is-open'));
    document.body.style.overflow = 'hidden';
    lbClose.focus();
  };

  const close = () => {
    lb.classList.remove('is-open');
    const done = () => {
      lb.hidden = true;
      lbImg.src = '';
      if (lastFocus) lastFocus.focus();
    };
    setTimeout(done, prefersReduced ? 0 : 300);
    document.body.style.overflow = '';
  };

  const step = dir => {
    if (!visible.length) return;
    index = (index + dir + visible.length) % visible.length;
    render();
  };

  items.forEach(fig => {
    const i = Number(fig.dataset.index);
    const openFromFig = () => {
      const pos = visible.findIndex(s => s.file === GALLERY[i].file);
      open(pos === -1 ? 0 : pos);
    };
    fig.addEventListener('click', openFromFig);
    fig.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' '){ e.preventDefault(); openFromFig(); }
    });
  });

  lbClose.addEventListener('click', close);
  lbNext.addEventListener('click', () => step(1));
  lbPrev.addEventListener('click', () => step(-1));
  lb.addEventListener('click', e => { if (e.target === lb) close(); });

  document.addEventListener('keydown', e => {
    if (lb.hidden) return;
    if (e.key === 'Escape')     close();
    if (e.key === 'ArrowRight') step(1);
    if (e.key === 'ArrowLeft')  step(-1);
  });

  // swipe on touch devices
  let touchX = 0;
  lb.addEventListener('touchstart', e => { touchX = e.changedTouches[0].clientX; }, { passive:true });
  lb.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 48) step(dx < 0 ? 1 : -1);
  }, { passive:true });
})();

/* ============================================================
   6. reviews
   ============================================================ */
(function reviews(){
  const grid = $('#revGrid');
  if (!grid) return;

  const stars = n => '★★★★★'.slice(0, n) + '☆☆☆☆☆'.slice(0, 5 - n);

  REVIEWS.forEach((r, i) => {
    const card = document.createElement('article');
    card.className = 'rev-card reveal';
    card.style.setProperty('--d', `${(i % 3) * 90}ms`);

    const head = document.createElement('div');
    head.className = 'rev-head';

    const av = document.createElement('span');
    av.className = 'rev-avatar';
    av.setAttribute('aria-hidden', 'true');
    av.textContent = r.init;

    const who = document.createElement('div');
    who.className = 'rev-who';
    const b = document.createElement('b');
    b.textContent = r.who;
    const s = document.createElement('small');
    s.textContent = r.when;
    who.append(b, s);

    head.append(av, who);

    const st = document.createElement('span');
    st.className = 'rev-stars';
    st.setAttribute('aria-label', `${r.stars} out of 5 stars`);
    st.textContent = stars(r.stars);

    const p = document.createElement('p');
    p.textContent = r.text;

    card.append(head, st, p);
    grid.appendChild(card);
  });

  // newly injected cards need to join the reveal observer
  if (!prefersReduced && 'IntersectionObserver' in window){
    const io = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        obs.unobserve(entry.target);
      });
    }, { rootMargin:'0px 0px -8% 0px', threshold:0.1 });
    $$('.rev-card.reveal', grid).forEach(el => io.observe(el));
  } else {
    $$('.rev-card.reveal', grid).forEach(el => el.classList.add('is-in'));
  }
})();

/* ============================================================
   7. reservation → WhatsApp
   ============================================================ */
(function reservation(){
  const form  = $('#reserveForm');
  if (!form) return;

  const errEl = $('#formError');
  const nameEl  = $('#rName');
  const dateEl  = $('#rDate');
  const timeEl  = $('#rTime');
  const guestEl = $('#rGuests');
  const seatEl  = $('#rSeat');
  const noteEl  = $('#rNote');

  // sensible defaults: today, 8 PM
  const today = new Date();
  const iso = d => d.toISOString().slice(0, 10);
  dateEl.min = iso(today);
  dateEl.value = iso(today);
  timeEl.value = '20:00';

  const clearErrors = () => {
    [nameEl, dateEl, timeEl, guestEl].forEach(el => el.classList.remove('has-error'));
    errEl.hidden = true;
  };

  const fail = (el, msg) => {
    el.classList.add('has-error');
    errEl.textContent = msg;
    errEl.hidden = false;
    el.focus();
  };

  // live-clear as the guest fixes things
  form.addEventListener('input', e => {
    if (e.target.classList) e.target.classList.remove('has-error');
    errEl.hidden = true;
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    clearErrors();

    const name   = nameEl.value.trim();
    const date   = dateEl.value;
    const time   = timeEl.value;
    const guests = guestEl.value;
    const seat   = seatEl.value;
    const note   = noteEl.value.trim();

    if (!name)   return fail(nameEl,   'Please tell us your name.');
    if (!date)   return fail(dateEl,   'Please pick a date.');
    if (!time)   return fail(timeEl,   'Please pick a time.');
    if (!guests) return fail(guestEl,  'How many guests should we set the table for?');

    // pretty date for the message, e.g. "Sat, 11 Oct 2026"
    let pretty = date;
    try {
      pretty = new Date(date + 'T00:00:00').toLocaleDateString('en-IN', {
        weekday:'short', day:'numeric', month:'short', year:'numeric'
      });
    } catch (_) { /* keep ISO string */ }

    // 24-hour → 12-hour
    let prettyTime = time;
    const [hh, mm] = time.split(':').map(Number);
    if (!Number.isNaN(hh)){
      const suffix = hh >= 12 ? 'PM' : 'AM';
      const h12 = hh % 12 === 0 ? 12 : hh % 12;
      prettyTime = `${h12}:${String(mm ?? 0).padStart(2, '0')} ${suffix}`;
    }

    const lines = [
      `Hi ${CONFIG.name}! I'd like to book a table.`,
      '',
      `Name: ${name}`,
      `Date: ${pretty}`,
      `Time: ${prettyTime}`,
      `Guests: ${guests}`,
      `Seating: ${seat}`
    ];
    if (note) lines.push(`Note: ${note}`);
    lines.push('', 'Sent from your website 🙂');

    const url = `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(lines.join('\n'))}`;
    window.open(url, '_blank', 'noopener');
  });
})();

/* ============================================================
   8. footer year
   ============================================================ */
(function year(){
  const el = $('#year');
  if (el) el.textContent = String(new Date().getFullYear());
})();
