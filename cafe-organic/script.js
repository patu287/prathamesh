/* KERN — interactions
   Vanilla JS, no dependencies. Everything degrades gracefully. */

const root = document.documentElement;
root.classList.add('js');

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = window.matchMedia('(pointer: fine)').matches;

/* ---------- Opening hours (the café lives in Zürich) ---------- */
const TZ = 'Europe/Zurich';
// hours[day] = [open, close] in decimal hours; 0 = Sunday
const HOURS = {
  0: [9, 16],
  1: [7.5, 18], 2: [7.5, 18], 3: [7.5, 18], 4: [7.5, 18], 5: [7.5, 18],
  6: [8.5, 17]
};
const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

const fmt = (h) => {
  const hh = Math.floor(h);
  const mm = Math.round((h - hh) * 60);
  return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`;
};

function zurichNow() {
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone: TZ, weekday: 'short', hour: 'numeric', minute: 'numeric', hourCycle: 'h23'
  }).formatToParts(new Date());
  const get = (t) => parts.find((p) => p.type === t)?.value;
  const dayMap = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  return {
    day: dayMap[get('weekday')],
    hour: parseInt(get('hour'), 10),
    minute: parseInt(get('minute'), 10)
  };
}

function updateStatus() {
  const { day, hour, minute } = zurichNow();
  const now = hour + minute / 60;
  const [open, close] = HOURS[day];
  const live = document.getElementById('liveStatus');
  const text = document.getElementById('liveText');
  const dot = live.querySelector('.dot');

  if (now >= open && now < close) {
    dot.className = 'dot open';
    text.textContent = `Open now · until ${fmt(close)}`;
  } else {
    dot.className = 'dot closed';
    if (now < open) {
      text.textContent = `Closed · opens ${fmt(open)} today`;
    } else {
      // find next opening day
      let d = (day + 1) % 7;
      const label = d === (day + 1) % 7 ? 'tomorrow' : DAY_NAMES[d];
      text.textContent = `Closed · opens ${fmt(HOURS[d][0])} ${label}`;
    }
  }

  // highlight today in the hours table
  const row = day >= 1 && day <= 5 ? 1 : day;
  document.querySelectorAll('#hours tr').forEach((tr) => {
    tr.classList.toggle('today', Number(tr.dataset.day) === row);
  });
}
updateStatus();
setInterval(updateStatus, 60 * 1000);

/* ---------- Menu ---------- */
const MENU = {
  espresso: [
    ['Ristretto', 'Short, intense and sweet. Two-thirds of a shot.', 4.2],
    ['Espresso', 'Our house blend, double shot, nothing added.', 4.0],
    ['Cortado', 'Equal parts espresso and warm milk.', 4.8],
    ['Cappuccino', 'Classic 160 ml with a thick, glossy foam.', 5.2],
    ['Flat White', 'Silky microfoam over a ristretto base.', 5.4],
    ['Single Origin Espresso', 'Ask the bar. The origin rotates every week.', 5.6]
  ],
  filter: [
    ['V60 — Lindo', 'Hand-brewed, 15 g in, 250 ml out. Bright and floral.', 6.2],
    ['Mora Filter', 'Honey process. Sweet, round, red cherry.', 6.0],
    ['Cold Brew', 'Steeped for 16 hours. Served over a single cube.', 5.8],
    ['Chemex for Two', 'A slow, clean pour for two, with a small sweet.', 12.0],
    ['Affogato', 'Vanilla gelato with a hot espresso shot poured over.', 6.5]
  ],
  tea: [
    ['Matcha Latte', 'Ceremonial grade from Uji, whisked to order.', 6.0],
    ['Hojicha Latte', 'Roasted green tea. Warm, nutty, low in caffeine.', 5.6],
    ['Earl Grey Lab', 'Bergamot, cornflower and an oolong base.', 4.8],
    ['Chamomile & Honey', 'Loose leaf, steeped in a glass pot.', 4.5]
  ],
  bakery: [
    ['Butter Croissant', 'Laminated by hand over 48 hours.', 4.5],
    ['Pain au Chocolat', 'Two bars of dark chocolate, one golden shell.', 4.8],
    ['Cardamom Bun', 'Swedish-style, with brown sugar and pearl sugar.', 4.9],
    ['Rye & Seed Loaf', 'Sliced to order, served with cultured butter.', 5.2],
    ['Lemon Olive Oil Cake', 'Gluten-free on request. Baked each morning.', 4.6]
  ]
};

const tabs = [...document.querySelectorAll('.tab')];
const list = document.getElementById('panel');
const indicator = document.querySelector('.tab-indicator');

function renderMenu(key) {
  list.innerHTML = MENU[key].map(([name, desc, price], i) => `
    <li style="--i:${i}">
      <span class="idx">${String(i + 1).padStart(2, '0')}</span>
      <span class="item-name">${name}<span class="item-desc">${desc}</span></span>
      <span class="price"><small>CHF</small>${price.toFixed(2)}</span>
    </li>`).join('');
  // restart the panel entrance animation on every tab switch
  list.style.animation = 'none';
  void list.offsetWidth;
  list.style.animation = '';
}

function moveIndicator(tab) {
  if (!indicator) return;
  const rect = tab.getBoundingClientRect();
  const parent = tab.parentElement.getBoundingClientRect();
  indicator.style.width = `${rect.width - 22}px`;
  indicator.style.setProperty('--tx', `${rect.left - parent.left}px`);
  indicator.style.transform = `translateX(${rect.left - parent.left}px)`;
}

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    tabs.forEach((t) => {
      t.classList.toggle('active', t === tab);
      t.setAttribute('aria-selected', String(t === tab));
    });
    renderMenu(tab.dataset.tab);
    moveIndicator(tab);
  });
});
renderMenu('espresso');
moveIndicator(tabs[0]);
window.addEventListener('resize', () => moveIndicator(tabs.find((t) => t.classList.contains('active'))));
document.fonts?.ready.then(() => moveIndicator(tabs.find((t) => t.classList.contains('active'))));

/* ---------- Nav state ---------- */
const nav = document.getElementById('nav');
const onScroll = () => {
  nav.classList.toggle('scrolled', window.scrollY > 24);
  parallaxTick();
};

/* ---------- Scroll reveals ---------- */
const revealTargets = document.querySelectorAll('.reveal-up, .reveal-scale, .map');
const io = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    const el = entry.target;
    el.classList.add('in');
    if (el.querySelector && el.querySelector('[data-count]')) countUp(el);
    if (el.matches('[data-count]')) countUp(el.parentElement);
    io.unobserve(el);
  });
}, { threshold: 0.14, rootMargin: '0px 0px -6% 0px' });

revealTargets.forEach((el) => io.observe(el));

// Stats count-up
const stats = document.querySelectorAll('.stat b');
const statIO = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) { countUp(e.target.closest('.stat')); statIO.unobserve(e.target); }
  });
}, { threshold: 0.6 });
stats.forEach((s) => statIO.observe(s));

const counted = new WeakSet();
function countUp(scope) {
  const targets = scope.matches && scope.matches('[data-count]') ? [scope] : scope.querySelectorAll('[data-count]');
  targets.forEach((el) => {
    if (counted.has(el)) return;
    counted.add(el);
    const end = parseInt(el.dataset.count, 10);
    if (reduceMotion || end === 0) { el.textContent = end; return; }
    const dur = 1600;
    const start = performance.now();
    const step = (now) => {
      const t = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - t, 4);
      el.textContent = Math.round(end * eased);
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });
}

/* ---------- Parallax on framed photos ---------- */
const parallaxImgs = [...document.querySelectorAll('img.parallax')];
let ticking = false;
function parallaxTick() {
  if (reduceMotion || ticking) return;
  ticking = true;
  requestAnimationFrame(() => {
    const vh = window.innerHeight;
    parallaxImgs.forEach((img) => {
      const box = img.parentElement.getBoundingClientRect();
      if (box.bottom < -100 || box.top > vh + 100) return;
      const progress = ((box.top + box.height / 2) - vh / 2) / (vh / 2 + box.height / 2);
      const clamped = Math.max(-1, Math.min(1, progress));
      // image is 116% tall with top: -8%, so it can travel ~8% of the frame each way
      const offset = clamped * -0.07 * box.height;
      img.style.setProperty('--py', `${offset.toFixed(1)}px`);
    });
    ticking = false;
  });
}
window.addEventListener('scroll', onScroll, { passive: true });
window.addEventListener('resize', parallaxTick);
onScroll();

/* ---------- Magnetic buttons (desktop pointer only) ---------- */
if (finePointer && !reduceMotion) {
  document.querySelectorAll('.magnetic').forEach((btn) => {
    btn.addEventListener('pointermove', (e) => {
      const r = btn.getBoundingClientRect();
      const x = e.clientX - (r.left + r.width / 2);
      const y = e.clientY - (r.top + r.height / 2);
      btn.style.transform = `translate(${x * 0.18}px, ${y * 0.3}px)`;
    });
    btn.addEventListener('pointerleave', () => { btn.style.transform = ''; });
  });
}

/* ---------- Reservation form ---------- */
const form = document.getElementById('reserveForm');
const content = document.getElementById('formContent');
const success = document.getElementById('formSuccess');
const dateInput = document.getElementById('fDate');

// Earliest bookable date = today (Zürich), max 14 days ahead
const zDate = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
dateInput.min = zDate;
const maxDate = new Date(Date.now() + 14 * 864e5);
dateInput.max = new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).format(maxDate);

function setError(id, msg) {
  const input = document.getElementById(id);
  const field = input.closest('.field');
  const err = field.querySelector('.err');
  field.classList.toggle('invalid', Boolean(msg));
  err.textContent = msg || '';
  return !msg;
}

function validate() {
  const name = document.getElementById('fName').value.trim();
  const email = document.getElementById('fEmail').value.trim();
  const date = dateInput.value;
  const time = document.getElementById('fTime').value;
  let ok = true;
  ok = setError('fName', name.length < 2 ? 'Please enter your name' : '') && ok;
  ok = setError('fEmail', /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ? '' : 'Enter a valid email') && ok;
  ok = setError('fDate', !date ? 'Choose a date' : (date < zDate || date > dateInput.max) ? 'Within the next 14 days' : '') && ok;
  ok = setError('fTime', time ? '' : 'Choose a time') && ok;
  return ok;
}

['fName', 'fEmail', 'fDate', 'fTime'].forEach((id) => {
  document.getElementById(id).addEventListener('input', () => {
    if (document.getElementById(id).closest('.field').classList.contains('invalid')) validate();
  });
});

form.addEventListener('submit', (e) => {
  e.preventDefault();
  if (!validate()) {
    const first = form.querySelector('.field.invalid input, .field.invalid select');
    first?.focus();
    return;
  }
  const name = document.getElementById('fName').value.trim().split(' ')[0];
  const date = new Date(dateInput.value + 'T12:00:00');
  const when = `${date.toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' })} at ${document.getElementById('fTime').value}`;
  const guests = document.getElementById('fGuests').value;
  document.getElementById('successName').textContent = name;
  document.getElementById('successWhen').textContent = `${when} for ${guests}`;

  content.classList.add('leaving');
  setTimeout(() => {
    content.hidden = true;
    content.classList.remove('leaving');
    success.hidden = false;
  }, reduceMotion ? 0 : 450);
});

document.getElementById('resetForm').addEventListener('click', () => {
  form.reset();
  dateInput.min = zDate;
  document.querySelectorAll('.field.invalid').forEach((f) => f.classList.remove('invalid'));
  document.querySelectorAll('.err').forEach((e) => (e.textContent = ''));
  success.hidden = true;
  content.hidden = false;
  document.getElementById('fName').focus();
});

/* ---------- Newsletter ---------- */
document.getElementById('subscribe').addEventListener('submit', (e) => {
  e.preventDefault();
  const form2 = e.currentTarget;
  const input = form2.querySelector('input');
  if (!input.checkValidity()) { input.reportValidity(); return; }
  const btn = form2.querySelector('button span');
  btn.textContent = 'Subscribed ✓';
  input.value = '';
  input.placeholder = 'See you in your inbox.';
  setTimeout(() => { btn.textContent = 'Subscribe'; input.placeholder = 'Email for roast drops'; }, 3200);
});
