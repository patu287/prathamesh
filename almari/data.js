/* ══════════════════════════════════════════════════════════════════
   My Wardrobe · data.js
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

/* ---------- lookup helpers ---------- */
const typeById = id => TYPES.find(t => t.id === id) || { id, slot: '', label: id || 'Item' };
const slotById = id => SLOTS.find(s => s.id === id) || { id, label: id || '' };
const typesIn  = slot => TYPES.filter(t => t.slot === slot);

/** Auto-name an item when the name field is left blank. */
function autoName(item) {
  return (item && item.name) ? item.name : typeById(item && item.type).label;
}

/** Searchable haystack. Tolerates fields from older backups. */
function haystack(item) {
  const bits = [
    item.name, typeById(item.type).label, slotById(item.slot).label,
    item.brand, item.fabric, item.size, item.notes,
    (item.occasions || []).join(' ')
  ];
  return bits.filter(Boolean).join(' ').toLowerCase();
}

/* ══════════════════════════════════════════════════════════════════
   Feature 2 · Outfits
   A Look is one item per slot. The `from` field maps a Look slot onto a
   wardrobe slot, so `layer` draws from the same pool as `top` — that is
   what makes shirt-under-sweater possible.
   ══════════════════════════════════════════════════════════════════ */

const LOOK_SLOTS = [
  { id: 'top',       label: 'Top',         from: 'top',       required: true,  multi: false, hint: 'Shirt, tee, kurta' },
  { id: 'layer',     label: 'Layer',       from: 'top',       required: false, multi: false, hint: 'A second top — sweater over a shirt' },
  { id: 'bottom',    label: 'Bottom',      from: 'bottom',    required: true,  multi: false, hint: 'Jeans, chinos, pyjama' },
  { id: 'outer',     label: 'Outerwear',   from: 'outer',     required: false, multi: false, hint: 'Jacket, blazer, Nehru jacket' },
  { id: 'foot',      label: 'Footwear',    from: 'foot',      required: true,  multi: false, hint: 'Shoes, sandals, Kolhapuri' },
  { id: 'accessory', label: 'Accessories', from: 'accessory', required: false, multi: true,  hint: 'Watch, belt, cap — as many as you like' }
];

const lookSlotById = id => LOOK_SLOTS.find(s => s.id === id) || null;

const LAUNDRY = [
  { id: 'clean',    label: 'Clean',              short: 'Clean'   },
  { id: 'worn',     label: 'Worn once',          short: 'Worn'    },
  { id: 'dirty',    label: 'Dirty',              short: 'Dirty'   },
  { id: 'cleaning', label: 'At the dry-cleaner', short: 'Cleaner' }
];
const LAUNDRY_ORDER = LAUNDRY.map(l => l.id);
const laundryById = id => LAUNDRY.find(l => l.id === id) || LAUNDRY[0];
const nextLaundry = id => LAUNDRY_ORDER[(LAUNDRY_ORDER.indexOf(id) + 1) % LAUNDRY_ORDER.length];

/** Clean or worn-once — the clothes you would actually put on today. */
const isWearable = i => !i.laundry || i.laundry === 'clean' || i.laundry === 'worn';

/** "Festival look", or "Kurta + Pyjama" when there is no occasion. */
function autoLookName(look, items) {
  const list = items || [];
  const byId = id => list.find(i => i.id === id);
  const occ = (look.occasions || [])[0];
  if (occ) return `${occ} look`;
  const top = byId(look.slots && look.slots.top);
  const bottom = byId(look.slots && look.slots.bottom);
  if (top && bottom) return `${typeById(top.type).label} + ${typeById(bottom.type).label}`;
  if (top) return `${typeById(top.type).label} look`;
  return 'New look';
}

/**
 * How well a candidate goes with what is already picked.
 * Shared occasions are the signal — a wedding kurta and wedding shoes are a
 * real pairing.
 */
function matchScore(candidate, chosen) {
  const picked = (chosen || []).filter(Boolean);
  if (!picked.length) return { occ: 0, total: 0 };
  let occ = 0;
  picked.forEach(s => {
    occ += (candidate.occasions || []).filter(o => (s.occasions || []).includes(o)).length;
  });
  return { occ, total: occ };
}

/** tops × bottoms × shoes — how many looks the wardrobe can already make. */
function combinations(items) {
  const wearable = (items || []).filter(isWearable);
  const pool = wearable.length >= 3 ? wearable : (items || []);
  const n = slot => pool.filter(i => i.slot === slot).length;
  return { tops: n('top'), bottoms: n('bottom'), shoes: n('foot'), total: n('top') * n('bottom') * n('foot') };
}

/* ---------- demo wardrobe (no photos — uses neutral tiles) ---------- */
const SAMPLE_ITEMS = [
  { name: 'White Oxford Shirt',    slot: 'top',   type: 'shirt',        occasions: ['Office', 'Casual', 'Wedding'] },
  { name: 'Indigo Cotton Kurta',   slot: 'top',   type: 'kurta',        occasions: ['Festival', 'Casual'] },
  { name: 'Marigold Festive Kurta',slot: 'top',   type: 'kurta',        occasions: ['Festival', 'Wedding'] },
  { name: 'Grey Crewneck Tee',     slot: 'top',   type: 'tshirt',       occasions: ['Casual', 'Gym'] },
  { name: 'Black Slim Jeans',      slot: 'bottom',type: 'jeans',        occasions: ['Casual', 'Party'] },
  { name: 'Beige Chinos',          slot: 'bottom',type: 'chinos',       occasions: ['Office', 'Casual'] },
  { name: 'White Pyjama',          slot: 'bottom',type: 'pyjama',       occasions: ['Festival', 'Wedding'] },
  { name: 'Olive Nehru Jacket',    slot: 'outer', type: 'nehru-jacket', occasions: ['Wedding', 'Festival'] },
  { name: 'Black Bomber Jacket',   slot: 'outer', type: 'jacket',       occasions: ['Casual', 'Travel'] },
  { name: 'White Sneakers',        slot: 'foot',  type: 'sneakers',     occasions: ['Casual', 'Travel'] },
  { name: 'Brown Kolhapuri',       slot: 'foot',  type: 'kolhapuri',    occasions: ['Casual', 'Festival'] },
  { name: 'Black Formal Shoes',    slot: 'foot',  type: 'formal-shoes', occasions: ['Office', 'Wedding'] },
  { name: 'Steel Watch',           slot: 'accessory', type: 'watch',    occasions: ['Office', 'Wedding'] },
  { name: 'Brown Leather Belt',    slot: 'accessory', type: 'belt',     occasions: ['Office', 'Casual'] }
];
