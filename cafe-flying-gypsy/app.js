/* ================================================================
   CAFE FLYING GYPSY'S — app.js
   1201-A/4 GH Patil Path, Shivajinagar, Pune · open 24 hours
   Vanilla JS. No dependencies. No build step.
   ================================================================ */
'use strict';

/* ----------------------------------------------------------------
   BUSINESS
   ---------------------------------------------------------------- */
const CONFIG = {
  name:       "Cafe Flying Gypsy's",
  phone:      '+919011147147',
  phoneHuman: '+91 90111 47147',
  whatsapp:   '919011147147',
  instagram:  'https://www.instagram.com/cafeflyinggypsys/',
  email:      'contact@cafeflyinggypsys.online',
  mapsDir:    'https://www.google.com/maps/dir/?api=1&destination=18.5240,73.8425',
  reviewsUrl: 'https://search.google.com/local/reviews?placeid=ChIJTWY0G2TBwjsR9M0AcA-mZ0A'
};

/* ----------------------------------------------------------------
   SIGNATURES
   Each card is one of the cafe's own photographs paired with the
   real price from the printed menu.
   ---------------------------------------------------------------- */
const SIGNATURES = [
  { file:'mushroom-white-sauce-pasta.jpg', alt:'Creamy mushroom white-sauce pasta served with herbed garlic bread.',
    name:'Cheesy White Sauce Pasta', price:289, badge:'Most loved',
    note:'The dish people come back for. Mushroom penne, finished with garlic bread.' },

  { file:'paneer-tikka-pizza.jpg', alt:'A paneer tikka pizza with paneer cubes, capsicum, red pepper and onion.',
    name:'Tandoori Paneer Pizza', price:280, badge:'Wood-fired',
    note:'Spiced paneer, onion and sweet peppers on a crisp hand-stretched base.' },

  { file:'shakes-mojito-fries-spread.jpg', alt:'Two thick chocolate shakes, a green mojito and a plate of peri-peri fries with dip.',
    name:'Nutella-Oreo Shake', price:219, badge:'Thick',
    note:'Blended with real ice cream and topped with cream and chocolate.' },

  { file:'cheesy-loaded-fries.jpg', alt:'A plate of golden fries covered in cheese drizzle and herbs.',
    name:'Cheese Peri Peri Fries', price:209, badge:'Spicy',
    note:'Golden fries, peri-peri heat, and a blanket of cheese drizzle.' },

  { file:'burger-nachos-chocolate-shake.jpg', alt:'A sesame-seed burger with nachos and a thick chocolate shake.',
    name:'Crispy Paneer Burger', price:159, badge:'Late-night',
    note:'Crisp paneer patty, fresh salad, sesame bun. Order it at 2 AM — everyone does.' },

  { file:'heart-latte-art-cappuccino.jpg', alt:'A cappuccino with heart latte art in a heart-patterned mug.',
    name:'Cappuccino', price:119, badge:'All day',
    note:'Properly pulled on the Italian machine, with a heart in the foam.' }
];

/* ----------------------------------------------------------------
   MENU
   Taken from the cafe's printed card. Prices in ₹.
   Tags: (none) = vegetarian · Jain = no onion/garlic · Egg = contains egg
   ---------------------------------------------------------------- */
const MENU = [
  {
    id:'maggi', label:'Maggi', note:'The reason half of Shivajinagar walks in at 2 AM.',
    items:[
      { name:'Masala Maggi',              price:99,  desc:'The plain-and-perfect original. Still the best seller after midnight.' },
      { name:'Cheese Masala Maggi',       price:149, desc:'The classic, buried under a layer of molten cheese.' },
      { name:'Italian Cheese Maggi',      price:169, tag:'Most loved', desc:'Herbs, cheese and a tangy Italian twist. Our most ordered plate, full stop.' },
      { name:'Cheese Peri Peri Maggi',    price:169, tag:'Spicy', desc:'Peri-peri heat under a blanket of cheese. Not for the faint-hearted.' },
      { name:'Cheese Schezwan Maggi',     price:169, desc:'Schezwan sauce, garlic and cheese. Sharp, hot and addictive.' },
      { name:'Manchurian Cheese Maggi',   price:179, desc:'Manchurian gravy folded through, cheese melted over the top.' },
      { name:'Cheese Corn Maggi',         price:179, desc:'Sweet American corn and cheese. The mild one for the table\'s spice-avoider.' },
      { name:'Cheese Makhni Maggi',       price:199, desc:'Buttery makhani gravy and cheese. Rich enough to share — you won\'t.' },
      { name:'Jain Cheese Maggi',         price:169, tag:'Jain', desc:'No onion, no garlic, no compromise on flavour.' },
      { name:'Hot Chilli Garlic',         price:169, tag:'Spicy', desc:'For people who think Maggi has been too polite.' },
      { name:'Creamy Garlic Mushroom Maggi', price:259, desc:'Mushrooms, cream and roasted garlic. The grown-up one.' },
      { name:'Mexican Salsa with Nachos', price:269, desc:'Warm salsa and crisp nachos — the plate that starts arguments about ordering more.' }
    ]
  },
  {
    id:'starters', label:'Fries & Starters', note:'Fried to order, never held under a lamp.',
    items:[
      { name:'Plain Fries',          price:169, desc:'Thick-cut, salted and properly crisp, with a white dip on the side.' },
      { name:'Peri-Peri Fries',      price:189, tag:'Most loved', desc:'Super spicy — exactly how the regulars ask for them.' },
      { name:'Chipotle Fries',       price:189, desc:'Smoky chipotle dust, cooling dip.' },
      { name:'Jamaican Fries',       price:189, desc:'Jamaican jerk seasoning — warm, aromatic, mildly hot.' },
      { name:'Mexican Fries',        price:189, desc:'Mexican spice blend with a salsa-style finish.' },
      { name:'Cheese Peri Peri Fries', price:209, tag:'Spicy', desc:'The peri-peri fries, plus a generous cheese drizzle and herbs.' },
      { name:'Cheesey Corn Balls',   price:189, desc:'Crumb-fried, molten centre, sweet corn through it.' },
      { name:'Spicy Salsa Nachos',   price:229, desc:'Nachos under tomato salsa and jalapeños.' },
      { name:'Peri Peri Nachos',     price:249, desc:'Loaded nachos, peri-peri sauce and creamy mayo.' }
    ]
  },
  {
    id:'pasta', label:'Pasta', note:'Sauces made to order — nothing out of a jar.',
    items:[
      { name:'Cheesy White Sauce Pasta', price:289, tag:'Most loved', desc:'Creamy alfredo with mushrooms, finished with herbed garlic bread.' },
      { name:'Cheesy Pink Sauce Pasta',  price:289, desc:'White and red together — tangy and creamy in the same forkful.' },
      { name:'Red Sauce Cheesy Pasta',   price:289, desc:'Sharp tomato base, herbs, and cheese melted through.' }
    ]
  },
  {
    id:'pizza', label:'Pizza', note:'Hand-stretched, stone-baked, cut into eight.',
    items:[
      { name:'Cheese Burst Pizza',   price:269, desc:'A molten centre that collapses the moment you lift a slice.' },
      { name:'Corn Cheese Pizza',    price:259, desc:'Sweet corn and mozzarella. Simple and very hard to stop eating.' },
      { name:'Barbeque Pizza',       price:249, desc:'Smoky barbecue base with onion and peppers.' },
      { name:'Margherita Pizza',     price:249, desc:'Tomato, mozzarella, basil. The one that proves a kitchen is any good.' },
      { name:'Tandoori Paneer Pizza', price:280, tag:'Most loved', desc:'Tandoori-spiced paneer, capsicum, onion and red pepper.' }
    ]
  },
  {
    id:'burgers', label:'Burgers', note:'Sesame buns, crisp patties, sauces made in-house.',
    items:[
      { name:'Crispy Veg Burger',            price:149, desc:'The classic — crunchy veg patty, lettuce, mayo.' },
      { name:'Crispy Paneer Burger',         price:159, tag:'Most loved', desc:'Crisp paneer patty with fresh vegetables. The late-night default.' },
      { name:'Crispy Veg Cheese Burger',     price:169, desc:'The veg burger with melted cheese and house sauces.' },
      { name:'Crispy Veg Peri Peri Burger',  price:179, tag:'Spicy', desc:'Bold peri-peri kick over a crunchy veg patty.' },
      { name:'Crispy Veg Schezwan Burger',   price:179, tag:'Spicy', desc:'Zesty Schezwan sauce, crunchy layers.' },
      { name:'Crispy Veg Chipotle Burger',   price:179, desc:'Smoky chipotle sauce with crisp veg.' },
      { name:'Veg Mexican Burger',           price:179, desc:'Mexican-spiced veg patty with a salsa-style finish.' },
      { name:'Crispy Paneer Cheese Burger',  price:179, desc:'Paneer patty plus cheese. A very good decision.' },
      { name:'Crispy Paneer Peri Peri Burger', price:189, tag:'Spicy', desc:'Paneer patty with peri-peri heat.' },
      { name:'Crispy Paneer Schezwan Burger', price:189, tag:'Spicy', desc:'Paneer and Schezwan — sharp and hot.' },
      { name:'Paneer Mexican Burger',        price:189, desc:'Paneer patty with Mexican seasoning.' },
      { name:'Paneer Chipotle Burger',       price:189, desc:'Smoky chipotle over crisp paneer.' },
      { name:'Crispy Paneer BBQ Burger',     price:199, desc:'Barbecue-glazed paneer patty. The richest burger on the card.' }
    ]
  },
  {
    id:'sandwiches', label:'Sandwiches', note:'Grilled, toasted and cut on the diagonal.',
    items:[
      { name:'Cheesy Corn Sandwich',    price:189, desc:'Sweet corn and melted cheese, grilled until the edges crackle.' },
      { name:'Chef\'s Special Sandwich', price:200, desc:'The kitchen\'s own combination. Ask them what is in it today.' },
      { name:'Pizza Feel Sandwich',     price:200, desc:'Everything you like about pizza, pressed between two slices.' },
      { name:'Tandoori Cheese Sandwich', price:219, desc:'Tandoori-spiced filling with a proper cheese pull.' },
      { name:'Mexican Mushroom',        price:219, desc:'Mushrooms with Mexican seasoning and cheese.' },
      { name:'Cheese Sandwich',         price:220, desc:'Plainly named, generously made.' },
      { name:'Chocolate Sandwich',      price:220, desc:'Yes, really. Warm chocolate between toasted bread. Trust the regulars.' },
      { name:'Cheese Chilli Toast',     price:259, tag:'Spicy', desc:'Chilli, cheese and toast — the simplest great thing on the menu.' }
    ]
  },
  {
    id:'indian', label:'Indian & Eggs', note:'Our own Indian favourites, cooked to order.',
    items:[
      { name:'Egg Bhurji',            price:159, tag:'Egg',   desc:'The classic spicy scrambled egg with onion and tomato.' },
      { name:'Gypsy\'s Special Bhurji', price:220, tag:'Egg', desc:'Our house bhurji, loaded with a spice mix we do not share.' },
      { name:'Egg Keema',             price:349, tag:'Egg',   desc:'Minced egg cooked down with onion and Indian herbs.' },
      { name:'Mushroom Keema',        price:369, desc:'Minced mushrooms in a traditional masala. Rich and deeply savoury.' },
      { name:'Paneer Bhurji',         price:389, desc:'Scrambled cottage cheese with Indian spices. Best with bread on the side.' }
    ]
  },
  {
    id:'coffee', label:'Coffee & Tea', note:'Pulled on an Italian machine, all day and all night.',
    items:[
      { name:'Espresso (Single Shot, 30 ml)', price:70,  desc:'Short, dark and properly extracted.' },
      { name:'Green Tea',                     price:80,  desc:'For the table that came for the wifi and the quiet.' },
      { name:'Espresso (Double Shot, 60 ml)', price:100, desc:'Twice the shot for the second half of your evening.' },
      { name:'Irish Cappuccino',              price:109, desc:'Cappuccino with a warm Irish-style syrup.' },
      { name:'Cappuccino (200 ml)',           price:119, tag:'Most loved', desc:'Rich and foamy with a thick layer of milk foam.' },
      { name:'Café Latte',                    price:119, desc:'Smoother and milkier than the cappuccino.' },
      { name:'Americano',                     price:119, desc:'Espresso lengthened with hot water. Clean and bitter.' },
      { name:'Iced Americano',                price:119, desc:'The same, poured over ice.' },
      { name:'Café Mocha',                    price:139, desc:'Espresso, chocolate and steamed milk.' },
      { name:'Hazelnut Cappuccino',           price:149, tag:'Most loved', desc:'Nutty, warm and the one people order twice.' },
      { name:'Vanilla Cappuccino',            price:149, desc:'Softer, sweeter, gentler.' }
    ]
  },
  {
    id:'shakes', label:'Shakes', note:'Thick enough that the straw stands up on its own.',
    items:[
      { name:'Cotton Candy Shake',       price:149, desc:'Nostalgic, sweet and very pink.' },
      { name:'Saffron Shake',            price:159, desc:'Kesar through cold milk and ice cream.' },
      { name:'Raspberry Shake',          price:159, desc:'Sharp, fruity and cold.' },
      { name:'Refreshing Watermelon',    price:159, desc:'Light and summery, even in winter.' },
      { name:'Popcorn Caramel Shake',    price:159, desc:'Caramel and popcorn. Strange until you try it, then it is your order.' },
      { name:'Crunchy Cheesecake Shake', price:159, tag:'Most loved', desc:'Dessert and drink in the same glass. Genuinely excellent.' },
      { name:'Blueberry Shake',          price:169, desc:'Fruity, cold and not too sweet.' },
      { name:'Bubblegum Shake',          price:169, desc:'The one the kids at the table always want.' },
      { name:'Butterscotch Shake',       price:179, desc:'Rich, caramel-sweet, properly thick.' },
      { name:'Strawberry Shake',         price:179, desc:'A classic done with real ice cream.' },
      { name:'Red Velvet Shake',         price:179, desc:'Cream cheese notes and cocoa. Very photogenic.' },
      { name:'Oreo-Bounty Shake',        price:179, desc:'Coconut and chocolate with crushed Oreo.' },
      { name:'Rose Oreo Shake',          price:179, desc:'Rose syrup and Oreo — a very Pune combination.' },
      { name:'Black Forest Shake',       price:189, desc:'Cherry, chocolate and cream, in drinkable form.' },
      { name:'Kit Kat Cream Shake',      price:210, desc:'Blended with real KitKat and a chocolate drizzle.' },
      { name:'Nutella-Oreo Shake',       price:219, tag:'Most loved', desc:'Nutella and Oreo, blended thick and topped with cream.' }
    ]
  },
  {
    id:'frappe', label:'Frappes & Chocolate', note:'For when it is too hot for anything with steam coming off it.',
    items:[
      { name:'Café Frappe',              price:139, desc:'Blended coffee and ice, the house standard.' },
      { name:'Gypsy\'s Classic Cold Frappe', price:159, tag:'Most loved', desc:'Our own blend. Chocolate, coffee and a lot of cold.' },
      { name:'Chocolate Frappe',         price:159, desc:'Deep cocoa, no coffee needed.' },
      { name:'Irish Frappe',             price:159, desc:'The regulars\' pick after a long day at college.' },
      { name:'Hazelnut Frappe',          price:159, desc:'Nutty and cold.' },
      { name:'Vanilla Frappe',           price:159, desc:'Clean, sweet and simple.' },
      { name:'Creamy Coconut',           price:159, desc:'Coconut through cold cream. Summery.' },
      { name:'Creamy Tiramisu Frappe',   price:159, desc:'Mascarpone and cocoa, in a tall glass.' },
      { name:'Irish Brownie Frappe',     price:169, desc:'Blended with actual brownie. A dessert with a straw.' },
      { name:'Classic Hot Chocolate',    price:120, desc:'Premium cocoa and milk, nothing else needed.' },
      { name:'Irish Hot Chocolate',      price:129, desc:'Warm, sweet, faintly Irish.' },
      { name:'Hazelnut Hot Chocolate',   price:129, desc:'Nutty and thick.' },
      { name:'Orangy Hot Chocolate',     price:129, desc:'Orange and chocolate — a combination people travel for.' },
      { name:'Caramel Hot Chocolate',    price:129, desc:'Salted-sweet caramel through hot cocoa.' },
      { name:'Vanilla Hot Chocolate',    price:130, desc:'The softest version on the card.' }
    ]
  },
  {
    id:'coolers', label:'Mojitos & Iced Tea', note:'All non-alcoholic. All very cold.',
    items:[
      { name:'Classic Mojito',        price:119, desc:'Fresh lime, mint and soda over ice. Still the best one.' },
      { name:'Kiwi Mojito',           price:119, desc:'Tart kiwi and mint.' },
      { name:'Blue Lagoon',           price:129, desc:'Electric-blue citrus with lemon and a hint of orange.' },
      { name:'Green Apple',           price:129, desc:'Crisp green apple over crushed ice.' },
      { name:'Raspberry Mojito',      price:139, desc:'Juicy raspberries, lime and mint.' },
      { name:'Bubblegum Mojito',      price:139, desc:'Mint with a sweet bubblegum finish. Playful.' },
      { name:'Strawberry Mojito',     price:139, desc:'Fresh strawberries muddled with lime and mint.' },
      { name:'Spicy Guava',           price:159, desc:'Guava with chilli salt on the rim. Ask for it — it works.' },
      { name:'Pink Grapefruit & Litchi Highball', price:159, desc:'Grapefruit and litchi with sparkling soda. The most grown-up glass here.' },
      { name:'Peach Iced Tea',        price:139, desc:'Light, cold and refreshing.' },
      { name:'Passion Fruit Iced Tea', price:139, desc:'Sharp and tropical.' },
      { name:'Peach Passion Iced Tea', price:139, desc:'Both of the above, together.' },
      { name:'Berry Blast Iced Tea',  price:139, desc:'Mixed berries over ice.' },
      { name:'Strawberry Iced Tea',   price:139, desc:'Mildly sweet, very drinkable.' },
      { name:'Green Apple Iced Tea',  price:139, desc:'Tart and crisp.' },
      { name:'Lemongrass Iced Tea',   price:169, desc:'Fragrant, herbal and the most interesting tea on the menu.' }
    ]
  }
];

/* ----------------------------------------------------------------
   THE HOURS
   A 24-hour cafe does not have one mood. It has six.
   ---------------------------------------------------------------- */
const HOURS = [
  { time:'07:00', label:'First light',
    text:'The espresso machine warms up before the street does. A cappuccino, the newspaper, and the corner table that gets the morning sun through the teal frame.' },
  { time:'11:30', label:'Work hours',
    text:'Laptops out, cold coffees going warm. The upstairs tables stay quiet, the wifi behaves, and nobody rushes you off a chair.' },
  { time:'15:30', label:'The lull',
    text:'Slack hour. Uno, chess and tic-tac-toe come off the shelf, the snooker table opens up, and the dog claims the sunniest patch of courtyard.' },
  { time:'19:00', label:'Golden hour',
    text:'The fairy lights come on in the courtyard and the palms start to glow. This is when the place is at its most photogenic — and it knows it.' },
  { time:'22:00', label:'Second service',
    text:'Pizzas out of the oven, shakes going out four at a time, and every table in the house full. Book ahead, or get lucky.' },
  { time:'01:30', label:'The real shift',
    text:'The lights stay on and the kitchen stays open. Maggi, cheese toast and thick shakes — the reason people say a 24-hour cafe in Pune actually means something.' }
];

/* ----------------------------------------------------------------
   GALLERY — the cafe's own photographs
   ---------------------------------------------------------------- */
const GALLERY = [
  { file:'courtyard-blue-staircase.jpg',       w:243, h:406, cat:'interiors', cap:'The courtyard — blue staircase, palms and fairy lights' },
  { file:'paneer-tikka-pizza.jpg',             w:243, h:203, cat:'food',      cap:'Tandoori paneer pizza, straight from the oven' },
  { file:'gypsy-girl-mural.jpg',               w:243, h:406, cat:'interiors', cap:'The gypsy girl, hand-painted on the wall' },
  { file:'cheesy-loaded-fries.jpg',            w:243, h:406, cat:'food',      cap:'Cheese peri-peri fries, loaded' },
  { file:'turquoise-gallery-wall.jpg',         w:243, h:244, cat:'interiors', cap:'The turquoise wall of frames and curios' },
  { file:'heart-latte-art-cappuccino.jpg',     w:243, h:174, cat:'drinks',    cap:'Cappuccino, with a heart in the foam' },
  { file:'teddy-book-shelf-corner.jpg',        w:243, h:304, cat:'interiors', cap:'The reading corner — books, brick, one large teddy' },
  { file:'mushroom-white-sauce-pasta.jpg',     w:243, h:203, cat:'food',      cap:'Mushroom white-sauce pasta with garlic bread' },
  { file:'cafe-exterior-signboard.jpg',        w:243, h:244, cat:'interiors', cap:'The entrance on GH Patil Path' },
  { file:'burger-nachos-chocolate-shake.jpg',  w:243, h:406, cat:'food',      cap:'Burger, nachos and a thick chocolate shake' },
  { file:'teal-wall-shelves-seating.jpg',      w:243, h:244, cat:'interiors', cap:'Quiet tables under the shelf wall' },
  { file:'shakes-mojito-fries-spread.jpg',     w:243, h:406, cat:'drinks',    cap:'Shakes, virgin mojito and peri-peri fries' },
  { file:'cafe-counter-interior.jpg',          w:243, h:174, cat:'interiors', cap:'Inside — the counter, hanging flowers, self-service' },
  { file:'cheesy-pasta-bake-garlic-bread.jpg', w:243, h:174, cat:'food',      cap:'Cheesy baked pasta and garlic bread sticks' },
  { file:'cold-coffee-frappe-courtyard.jpg',   w:243, h:304, cat:'drinks',    cap:'Iced coffee and frappes in the courtyard' },
  { file:'gypsy-mural-tables.jpg',             w:243, h:304, cat:'interiors', cap:'Wrought-iron tables beneath the mural' },
  { file:'burger-fries-outdoor-seating.jpg',   w:243, h:304, cat:'food',      cap:'Burgers and fries out in the open air' },
  { file:'birthday-celebration-table.jpg',     w:243, h:304, cat:'food',      cap:'Birthday spreads happen here — tell us in advance' }
];

/* ----------------------------------------------------------------
   REVIEWS — real, public Google reviews, reproduced as written
   ---------------------------------------------------------------- */
const REVIEWS = [
  { who:'Rushabh G.', init:'RG', stars:4,
    text:'Turned out to be such a hidden gem. The interiors are super creative — a mix of rustic and artsy, with lots of little details. I tried their paneer pizza and creamy pasta and both were packed with flavour. Already planning to come back.' },
  { who:'Nupur S.', init:'NS', stars:5,
    text:'An all-rounder — from the ambience to the snooker section, everything is just perfect. Don\'t miss out on their awesome burger menu. It is indeed a must visit, 100% recommend.' },
  { who:'vulimiri S.', init:'VS', stars:5,
    text:'Will I visit this place again? Yes, why not. Proper cafe vibe, friendly staff and the food the best. Don\'t miss the white sauce pasta. The owner is very friendly and the place is Instagram worthy.' },
  { who:'Pratiksha D.', init:'PD', stars:5,
    text:'I was skeptical at first, but it exceeded my expectations. The food was really good and worth every penny — surprisingly affordable too. I ordered mix sauce pasta, kimchi ramen and an Irish frappe, and everything was wow.' },
  { who:'Vaishnavi K.', init:'VK', stars:4,
    text:'Great ambience, super fresh. As you enter you will fall in love with the turquoise. The food quality is nice too — loved the food here. Overall a nice experience.' },
  { who:'Tisha M.', init:'TM', stars:4,
    text:'A nice casual place to pass the time. We had the cheese Maggi — my favourite. There are games and books as well. It\'s like chill and relax.' }
];

/* ================================================================
   helpers
   ================================================================ */
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const inr = n => '₹' + Number(n).toLocaleString('en-IN');

/* ================================================================
   1 · scroll progress + sticky nav
   ================================================================ */
(function chrome(){
  const nav = $('#nav');
  const bar = $('#progress');

  const update = () => {
    const y = window.scrollY;
    if (nav) nav.classList.toggle('is-stuck', y > 22);
    if (bar){
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const p = max > 0 ? Math.min(y / max, 1) : 0;
      bar.style.scale = `${p} 1`;
    }
  };
  update();
  window.addEventListener('scroll', update, { passive:true });
  window.addEventListener('resize', update, { passive:true });
})();

/* ================================================================
   2 · mobile drawer
   ================================================================ */
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
      setTimeout(() => { if (!open) panel.hidden = true; }, reduced ? 0 : 360);
    }
  };

  burger.addEventListener('click', () => setOpen(!open));
  $$('a', panel).forEach(a => a.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && open){ setOpen(false); burger.focus(); }
  });
  window.addEventListener('resize', () => { if (window.innerWidth > 980 && open) setOpen(false); });

  // re-sync if the viewport crosses the breakpoint while open
  window.addEventListener('orientationchange', () => setOpen(false));
})();

/* ================================================================
   3 · reveal on scroll
   ================================================================ */
const revealObserver = (() => {
  if (reduced || !('IntersectionObserver' in window)) return null;
  return new IntersectionObserver((entries, obs) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      obs.unobserve(en.target);
    });
  }, { rootMargin:'0px 0px -7% 0px', threshold:0.1 });
})();

const observeReveals = (root = document) => {
  const els = $$('.reveal', root);
  if (!revealObserver){ els.forEach(el => el.classList.add('is-in')); return; }
  els.forEach(el => { if (!el.classList.contains('is-in')) revealObserver.observe(el); });
};

/* ================================================================
   4 · signatures
   ================================================================ */
(function signatures(){
  const grid = $('#sigGrid');
  if (!grid) return;

  SIGNATURES.forEach((s, i) => {
    const card = document.createElement('article');
    card.className = 'sig-card reveal';
    card.style.setProperty('--d', `${(i % 3) * 90}ms`);

    const fig = document.createElement('figure');
    fig.className = 'sig-img';

    const img = document.createElement('img');
    img.src = `images/${s.file}`;
    img.alt = s.alt;
    // explicit intrinsic size: reserves the box before the photo arrives
    img.width = 243;
    img.height = 185;
    img.loading = i < 3 ? 'eager' : 'lazy';
    img.decoding = 'async';
    fig.appendChild(img);

    if (s.badge){
      const badge = document.createElement('span');
      badge.className = 'sig-badge';
      badge.textContent = s.badge;
      fig.appendChild(badge);
    }

    const body = document.createElement('div');
    body.className = 'sig-body';

    const top = document.createElement('div');
    top.className = 'sig-top';

    const h = document.createElement('h3');
    h.textContent = s.name;

    const price = document.createElement('span');
    price.className = 'sig-price';
    price.textContent = inr(s.price);

    top.append(h, price);

    const p = document.createElement('p');
    p.textContent = s.note;

    body.append(top, p);
    card.append(fig, body);
    grid.appendChild(card);
  });
})();

/* ================================================================
   5 · menu — tabs, panels, keyboard support
   ================================================================ */
(function menu(){
  const tabsEl   = $('.tabs');
  const panelsEl = $('#menuPanels');
  if (!tabsEl || !panelsEl) return;

  const tagClass = t => {
    if (!t) return 'veg';
    if (t === 'Spicy') return 'hot';
    if (t === 'Jain')  return 'jain';
    if (t === 'Egg')   return 'egg';
    return 'veg';
  };

  MENU.forEach((cat, i) => {
    // tab
    const b = document.createElement('button');
    b.className = 'tab';
    b.type = 'button';
    b.id = `tab-${cat.id}`;
    b.dataset.panel = cat.id;
    b.setAttribute('role', 'tab');
    b.setAttribute('aria-controls', `panel-${cat.id}`);
    b.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
    b.tabIndex = i === 0 ? 0 : -1;
    b.textContent = cat.label;
    tabsEl.appendChild(b);

    // panel
    const panel = document.createElement('div');
    panel.className = 'panel';
    panel.id = `panel-${cat.id}`;
    panel.setAttribute('role', 'tabpanel');
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
        t.className = 'tag ' + tagClass(item.tag);
        t.textContent = item.tag;
        top.appendChild(t);
      }

      const price = document.createElement('span');
      price.className = 'price';
      price.textContent = inr(item.price);

      const desc = document.createElement('p');
      desc.textContent = item.desc;

      row.append(top, price, desc);
      list.appendChild(row);
    });

    panel.appendChild(list);
    panelsEl.appendChild(panel);
  });

  const tabs = $$('.tab', tabsEl);
  const select = tab => {
    tabs.forEach(t => {
      const on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      const panel = document.getElementById(`panel-${t.dataset.panel}`);
      if (!panel) return;
      panel.hidden = !on;
      if (on){ panel.style.animation = 'none'; void panel.offsetWidth; panel.style.animation = ''; }
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
      if (next){
        e.preventDefault();
        next.focus();
        select(next);
        next.scrollIntoView({ block:'nearest', inline:'center', behavior: reduced ? 'auto' : 'smooth' });
      }
    });
  });
})();

/* ================================================================
   6 · the hours
   ================================================================ */
(function hours(){
  const list = $('#hoursList');
  if (!list) return;

  HOURS.forEach((h, i) => {
    const li = document.createElement('li');
    li.className = 'hour reveal';
    li.style.setProperty('--d', `${Math.min(i, 5) * 70}ms`);

    const dot = document.createElement('span');
    dot.className = 'hour-dot';
    dot.setAttribute('aria-hidden', 'true');

    const time = document.createElement('b');
    time.className = 'hour-time';
    time.textContent = h.time;

    const body = document.createElement('div');
    body.className = 'hour-body';
    const label = document.createElement('h3');
    label.textContent = h.label;
    const text = document.createElement('p');
    text.textContent = h.text;
    body.append(label, text);

    li.append(dot, time, body);
    list.appendChild(li);
  });
})();

/* ================================================================
   7 · gallery + lightbox
   ================================================================ */
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

  GALLERY.forEach((shot, i) => {
    const fig = document.createElement('figure');
    fig.className = 'gal-item';
    fig.dataset.cat = shot.cat;
    fig.dataset.index = String(i);
    fig.tabIndex = 0;
    fig.setAttribute('role', 'button');
    fig.setAttribute('aria-label', `Open image: ${shot.cap}`);

    // the single most likely image to LCP is the first one in the grid
    const img = document.createElement('img');
    img.src = `images/${shot.file}`;
    img.width = shot.w;
    img.height = shot.h;
    img.loading = 'lazy';
    img.decoding = 'async';
    if (i === 0) img.fetchPriority = 'low';
    img.alt = shot.cap;

    const cap = document.createElement('figcaption');
    cap.textContent = shot.cap;

    fig.append(img, cap);
    grid.appendChild(fig);
  });

  const items = $$('.gal-item', grid);

  // filters
  $$('.filter').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.filter').forEach(b => {
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

  // lightbox
  let lastFocus = null;

  const render = () => {
    const shot = visible[index];
    if (!shot) return;
    lbImg.src = `images/${shot.file}`;
    lbImg.alt = shot.cap;
    lbCap.textContent = shot.cap;
    lbCount.textContent = `${index + 1} / ${visible.length}`;
  };

  const open = pos => {
    index = Math.max(0, pos);
    lastFocus = document.activeElement;
    render();
    lb.hidden = false;
    requestAnimationFrame(() => lb.classList.add('is-open'));
    document.body.style.overflow = 'hidden';
    lbClose.focus();
  };

  const close = () => {
    lb.classList.remove('is-open');
    setTimeout(() => {
      lb.hidden = true;
      lbImg.src = '';
      document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    }, reduced ? 0 : 300);
  };

  const step = d => {
    if (!visible.length) return;
    index = (index + d + visible.length) % visible.length;
    render();
  };

  items.forEach(fig => {
    const openFromFig = () => {
      const shot = GALLERY[Number(fig.dataset.index)];
      const pos = visible.findIndex(s => s.file === shot.file);
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

  let touchX = 0;
  lb.addEventListener('touchstart', e => { touchX = e.changedTouches[0].clientX; }, { passive:true });
  lb.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 48) step(dx < 0 ? 1 : -1);
  }, { passive:true });
})();

/* ================================================================
   8 · reviews
   ================================================================ */
(function reviews(){
  const grid = $('#revGrid');
  if (!grid) return;

  const starRow = n => '★★★★★'.slice(0, n) + '☆☆☆☆☆'.slice(0, 5 - n);

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
    s.textContent = 'Google review';
    who.append(b, s);

    head.append(av, who);

    const st = document.createElement('span');
    st.className = 'rev-stars';
    st.setAttribute('aria-label', `${r.stars} out of 5 stars`);
    st.textContent = starRow(r.stars);

    const p = document.createElement('p');
    p.textContent = r.text;

    card.append(head, st, p);
    grid.appendChild(card);
  });
})();

/* ================================================================
   9 · reservation → WhatsApp
   ================================================================ */
(function reservation(){
  const form = $('#reserveForm');
  if (!form) return;

  const errEl   = $('#formError');
  const nameEl  = $('#rName');
  const dateEl  = $('#rDate');
  const timeEl  = $('#rTime');
  const guestEl = $('#rGuests');
  const seatEl  = $('#rSeat');
  const noteEl  = $('#rNote');

  // default: today, 8 PM
  const today = new Date();
  const iso = d => {
    const p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  };
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

    if (!name)   return fail(nameEl,  'Please tell us your name.');
    if (!date)   return fail(dateEl,  'Please pick a date.');
    if (!time)   return fail(timeEl,  'Please pick a time.');
    if (!guests) return fail(guestEl, 'How many guests should we set the table for?');

    let pretty = date;
    try {
      pretty = new Date(`${date}T00:00:00`).toLocaleDateString('en-IN', {
        weekday:'short', day:'numeric', month:'short', year:'numeric'
      });
    } catch (_){ /* keep ISO */ }

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
      `Where: ${seat}`
    ];
    if (note) lines.push(`Note: ${note}`);
    lines.push('', 'Sent from your website 🙂');

    window.open(
      `https://wa.me/${CONFIG.whatsapp}?text=${encodeURIComponent(lines.join('\n'))}`,
      '_blank',
      'noopener'
    );
  });
})();

/* ================================================================
   10 · footer year
   ================================================================ */
(function year(){
  const el = $('#year');
  if (el) el.textContent = String(new Date().getFullYear());
})();

/* ================================================================
   11 · kick off reveals (after all dynamic content is injected)
   ================================================================ */
observeReveals();
if (document.readyState !== 'complete'){
  window.addEventListener('load', () => observeReveals(), { once:true });
}
