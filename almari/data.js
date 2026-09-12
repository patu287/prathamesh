/* ══════════════════════════════════════════════════════════════════
   Almari · data.js
   Taxonomy + seed data. Two axes on purpose:
     SLOT  = where an item goes on the body  → drives the outfit builder
     TYPE  = what the garment actually is     → drives browsing & filters
   A kurta is a `top`. A Nehru jacket is `outer`. Pyjama is a `bottom`.
   ══════════════════════════════════════════════════════════════════ */

const SLOTS = [
  { id: 'top',       label: 'Tops',        short: 'Tops'   },
  { id: 'bottom',    label: 'Bottoms',     short: 'Bottoms'},
  { id: 'outer',     label: 'Outerwear',   short: 'Outer'  },
  { id: 'foot',      label: 'Footwear',    short: 'Shoes'  },
  { id: 'accessory', label: 'Accessories', short: 'Extras' }
];

const TYPES = [
  /* ---- tops ---- */
  { id: 'shirt',      slot: 'top', label: 'Shirt'        },
  { id: 'tshirt',     slot: 'top', label: 'T-shirt'      },
  { id: 'polo',       slot: 'top', label: 'Polo'         },
  { id: 'kurta',      slot: 'top', label: 'Kurta'        },
  { id: 'tunic',      slot: 'top', label: 'Tunic/Kameez' },
  { id: 'sweater',    slot: 'top', label: 'Sweater'      },
  { id: 'hoodie',     slot: 'top', label: 'Hoodie'       },
  { id: 'vest',       slot: 'top', label: 'Vest'         },
  /* ---- bottoms ---- */
  { id: 'jeans',      slot: 'bottom', label: 'Jeans'        },
  { id: 'formal-pant',slot: 'bottom', label: 'Formal Pant'  },
  { id: 'chinos',     slot: 'bottom', label: 'Chinos'       },
  { id: 'track',      slot: 'bottom', label: 'Track Pant'   },
  { id: 'shorts',     slot: 'bottom', label: 'Shorts'       },
  { id: 'pyjama',     slot: 'bottom', label: 'Pyjama/Salwar'},
  { id: 'dhoti',      slot: 'bottom', label: 'Dhoti'        },
  /* ---- outerwear ---- */
  { id: 'jacket',      slot: 'outer', label: 'Jacket'       },
  { id: 'nehru-jacket',slot: 'outer', label: 'Nehru Jacket' },
  { id: 'sherwani',    slot: 'outer', label: 'Sherwani'     },
  { id: 'blazer',      slot: 'outer', label: 'Blazer'       },
  { id: 'coat',        slot: 'outer', label: 'Coat'         },
  { id: 'raincoat',    slot: 'outer', label: 'Raincoat'     },
  /* ---- footwear ---- */
  { id: 'sneakers',     slot: 'foot', label: 'Sneakers'      },
  { id: 'formal-shoes', slot: 'foot', label: 'Formal Shoes'  },
  { id: 'loafers',      slot: 'foot', label: 'Loafers'       },
  { id: 'sandals',      slot: 'foot', label: 'Sandals'       },
  { id: 'kolhapuri',    slot: 'foot', label: 'Kolhapuri'     },
  { id: 'boots',        slot: 'foot', label: 'Boots'         },
  { id: 'sports-shoes', slot: 'foot', label: 'Sports Shoes'  },
  /* ---- accessories ---- */
  { id: 'watch',      slot: 'accessory', label: 'Watch'      },
  { id: 'belt',       slot: 'accessory', label: 'Belt'       },
  { id: 'cap',        slot: 'accessory', label: 'Cap'        },
  { id: 'sunglasses', slot: 'accessory', label: 'Sunglasses' },
  { id: 'wallet',     slot: 'accessory', label: 'Wallet'     },
  { id: 'socks',      slot: 'accessory', label: 'Socks'      },
  { id: 'scarf',      slot: 'accessory', label: 'Scarf/Stole'},
  { id: 'bag',        slot: 'accessory', label: 'Bag'        },
  { id: 'jewellery',  slot: 'accessory', label: 'Jewellery'  }
];

const OCCASIONS = ['Casual', 'Office', 'Wedding', 'Festival', 'Party', 'Gym', 'Travel', 'Sleep'];
const SEASONS   = ['Summer', 'Monsoon', 'Winter', 'All year'];
const FABRICS   = ['Cotton', 'Linen', 'Khadi', 'Silk', 'Wool', 'Denim', 'Rayon', 'Chiffon', 'Leather', 'Polyester', 'Blend', 'Other'];
const PATTERNS  = ['Solid', 'Striped', 'Checked', 'Printed', 'Embroidered', 'Floral', 'Colour-block', 'Other'];

/* Colour names are also used as searchable keywords. */
const COLORS = [
  { id: 'white',    label: 'White',    hex: '#F6F3EC' },
  { id: 'cream',    label: 'Cream',    hex: '#EFE3CB' },
  { id: 'beige',    label: 'Beige',    hex: '#D8C3A2' },
  { id: 'grey',     label: 'Grey',     hex: '#948F88' },
  { id: 'black',    label: 'Black',    hex: '#232120' },
  { id: 'navy',     label: 'Navy',     hex: '#2B3560' },
  { id: 'blue',     label: 'Blue',     hex: '#4A86C8' },
  { id: 'sky',      label: 'Sky',      hex: '#A9CFEA' },
  { id: 'teal',     label: 'Teal',     hex: '#2E7C7A' },
  { id: 'green',    label: 'Green',    hex: '#4C7A48' },
  { id: 'olive',    label: 'Olive',    hex: '#77783F' },
  { id: 'yellow',   label: 'Yellow',   hex: '#E8C84C' },
  { id: 'marigold', label: 'Marigold', hex: '#E9922F' },
  { id: 'orange',   label: 'Orange',   hex: '#D96A2B' },
  { id: 'rust',     label: 'Rust',     hex: '#A8481F' },
  { id: 'red',      label: 'Red',      hex: '#B3312C' },
  { id: 'maroon',   label: 'Maroon',   hex: '#6E2230' },
  { id: 'pink',     label: 'Pink',     hex: '#E0A0B4' },
  { id: 'purple',   label: 'Purple',   hex: '#6E4C93' },
  { id: 'brown',    label: 'Brown',    hex: '#7A5236' },
  { id: 'gold',     label: 'Gold',     hex: '#C9A227' },
  { id: 'silver',   label: 'Silver',   hex: '#C0C4C8' }
];

/* ---------- lookup helpers ---------- */
const typeById   = id => TYPES.find(t => t.id === id) || { id, slot: '', label: id };
const slotById   = id => SLOTS.find(s => s.id === id) || { id, label: id };
const colorById  = id => COLORS.find(c => c.id === id) || null;
const typesIn    = slot => TYPES.filter(t => t.slot === slot);

/** Auto-name an item from its colours + type: "Navy Kurta". */
function autoName(item) {
  const names = (item.colors || []).map(id => (colorById(id) || {}).label).filter(Boolean);
  const label = typeById(item.type).label;
  if (names.length === 1) return `${names[0]} ${label}`;
  if (names.length > 1)   return `${names.slice(0, 2).join(' & ')} ${label}`;
  return label;
}

/** Searchable haystack for one item. */
function haystack(item) {
  const bits = [
    item.name, autoName(item), typeById(item.type).label, slotById(item.slot).label,
    item.brand, item.fabric, item.pattern, item.size, item.notes,
    (item.colors || []).map(id => (colorById(id) || {}).label).join(' '),
    (item.occasions || []).join(' '),
    (item.seasons || []).join(' ')
  ];
  return bits.filter(Boolean).join(' ').toLowerCase();
}

/* ---------- demo wardrobe (no photos — uses colour tiles) ---------- */
const SAMPLE_ITEMS = [
  { name: 'White Oxford Shirt', slot: 'top', type: 'shirt', colors: ['white'], occasions: ['Office', 'Casual', 'Wedding'], seasons: ['All year'], fabric: 'Cotton', pattern: 'Solid', size: 'M', brand: 'Van Heusen', price: 1499, notes: 'Slim fit. Iron on medium.' },
  { name: 'Indigo Cotton Kurta', slot: 'top', type: 'kurta', colors: ['navy'], occasions: ['Festival', 'Casual'], seasons: ['Summer', 'Monsoon'], fabric: 'Cotton', pattern: 'Solid', size: 'M', brand: 'Manyavar', price: 1299, notes: 'Pairs with the beige pyjama.' },
  { name: 'Marigold Festive Kurta', slot: 'top', type: 'kurta', colors: ['marigold', 'gold'], occasions: ['Festival', 'Wedding'], seasons: ['All year'], fabric: 'Silk', pattern: 'Embroidered', size: 'M', brand: 'Manyavar', price: 3499, notes: 'Ganesh festival. Dry clean only.' },
  { name: 'Grey Crewneck Tee', slot: 'top', type: 'tshirt', colors: ['grey'], occasions: ['Casual', 'Gym'], seasons: ['All year'], fabric: 'Cotton', pattern: 'Solid', size: 'M', brand: 'Uniqlo', price: 590 },
  { name: 'Black Slim Jeans', slot: 'bottom', type: 'jeans', colors: ['black'], occasions: ['Casual', 'Party'], seasons: ['All year'], fabric: 'Denim', pattern: 'Solid', size: '32', brand: "Levi's", price: 2499, notes: 'Waist taken in 1 inch by the tailor near Rankala.' },
  { name: 'Beige Chinos', slot: 'bottom', type: 'chinos', colors: ['beige'], occasions: ['Office', 'Casual'], seasons: ['All year'], fabric: 'Cotton', pattern: 'Solid', size: '32', brand: 'Peter England', price: 1299 },
  { name: 'White Pyjama', slot: 'bottom', type: 'pyjama', colors: ['white', 'cream'], occasions: ['Festival', 'Wedding'], seasons: ['All year'], fabric: 'Cotton', pattern: 'Solid', size: 'Free' },
  { name: 'Olive Nehru Jacket', slot: 'outer', type: 'nehru-jacket', colors: ['olive'], occasions: ['Wedding', 'Festival'], seasons: ['Winter'], fabric: 'Blend', pattern: 'Solid', size: 'M', price: 2199 },
  { name: 'Black Bomber Jacket', slot: 'outer', type: 'jacket', colors: ['black'], occasions: ['Casual', 'Travel'], seasons: ['Winter', 'Monsoon'], fabric: 'Polyester', pattern: 'Solid', size: 'M', brand: 'Roadster', price: 1899 },
  { name: 'White Sneakers', slot: 'foot', type: 'sneakers', colors: ['white'], occasions: ['Casual', 'Travel'], seasons: ['All year'], fabric: 'Other', pattern: 'Solid', size: 'UK 8', brand: 'Nike', price: 3295 },
  { name: 'Brown Kolhapuri Chappal', slot: 'foot', type: 'kolhapuri', colors: ['brown'], occasions: ['Casual', 'Festival'], seasons: ['Summer'], fabric: 'Leather', pattern: 'Solid', size: 'UK 8', notes: 'Handmade, Tarabai Road.' },
  { name: 'Black Formal Shoes', slot: 'foot', type: 'formal-shoes', colors: ['black'], occasions: ['Office', 'Wedding'], seasons: ['All year'], fabric: 'Leather', pattern: 'Solid', size: 'UK 8', brand: 'Bata', price: 2099 },
  { name: 'Steel Chronograph Watch', slot: 'accessory', type: 'watch', colors: ['silver', 'black'], occasions: ['Office', 'Wedding'], seasons: ['All year'], fabric: 'Other', pattern: 'Solid', brand: 'Casio', price: 4995 },
  { name: 'Brown Leather Belt', slot: 'accessory', type: 'belt', colors: ['brown'], occasions: ['Office', 'Casual'], seasons: ['All year'], fabric: 'Leather', pattern: 'Solid', size: '34', price: 799 }
];
