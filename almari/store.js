/* ══════════════════════════════════════════════════════════════════
   Almari · store.js
   Local-first storage. IndexedDB holds two tables — `items` and `looks`.
   Photos are Blobs, so hundreds fit comfortably. Falls back to
   localStorage where IndexedDB is unavailable (notably file:// pages).
   Nothing is ever uploaded anywhere.
   ══════════════════════════════════════════════════════════════════ */

const Store = (() => {
  const DB_NAME = 'almari';
  const DB_VERSION = 2;          // v2 adds the `looks` table
  const T_ITEMS = 'items';
  const T_LOOKS = 'looks';
  const LS = { items: 'almari.items.v1', looks: 'almari.looks.v1' };

  let dbPromise = null;
  let useLS = false;

  function openDB() {
    if (!('indexedDB' in window)) { useLS = true; return Promise.resolve(null); }
    if (!dbPromise) {
      dbPromise = new Promise((resolve) => {
        let req;
        try { req = indexedDB.open(DB_NAME, DB_VERSION); }
        catch (err) { useLS = true; return resolve(null); }

        req.onupgradeneeded = () => {
          const db = req.result;
          [T_ITEMS, T_LOOKS].forEach(t => {
            if (!db.objectStoreNames.contains(t)) db.createObjectStore(t, { keyPath: 'id' });
          });
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => { useLS = true; resolve(null); };
        req.onblocked = () => { useLS = true; resolve(null); };
      });
    }
    return dbPromise;
  }

  function tx(db, table, mode) { return db.transaction(table, mode).objectStore(table); }

  /* ---- localStorage fallback ----
     A Blob cannot be JSON-serialised — it stringifies to "{}" and every photo
     would silently vanish — so photos are stored as data URLs on this path. */
  function lsRead(table) {
    try {
      const raw = JSON.parse(localStorage.getItem(LS[table]) || '[]');
      if (table !== T_ITEMS) return raw;
      return raw.map(r => {
        const it = Object.assign({}, r);
        if (it.photo && !it.photoBlob) {
          try { it.photoBlob = dataURLToBlob(it.photo); }
          catch (err) { it.photoBlob = null; }
        }
        delete it.photo;
        return it;
      });
    } catch (err) { return []; }
  }

  async function lsWrite(table, records) {
    let rows = records;
    if (table === T_ITEMS) {
      rows = [];
      for (const it of records) {
        const copy = Object.assign({}, it);
        if (copy.photoBlob) copy.photo = await blobToDataURL(copy.photoBlob);
        delete copy.photoBlob;
        rows.push(copy);
      }
    }
    try {
      localStorage.setItem(LS[table], JSON.stringify(rows));
      return true;
    } catch (err) {
      throw new Error('Storage is full. This browser has no IndexedDB, so photo space is limited — serve the app over http (see README).');
    }
  }

  /* ---- generic table ops ---- */
  async function readTable(table) {
    const db = await openDB();
    if (!db) return lsRead(table);
    return new Promise((resolve) => {
      const req = tx(db, table, 'readonly').getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => resolve([]);
    });
  }

  async function writeRecord(table, rec) {
    const db = await openDB();
    if (!db) {
      const rows = lsRead(table);
      const i = rows.findIndex(x => x.id === rec.id);
      if (i >= 0) rows[i] = rec; else rows.push(rec);
      await lsWrite(table, rows);
      return rec;
    }
    return new Promise((resolve, reject) => {
      const req = tx(db, table, 'readwrite').put(rec);
      req.onsuccess = () => resolve(rec);
      req.onerror = () => reject(req.error);
    });
  }

  async function deleteRecord(table, id) {
    if (table === T_ITEMS) forgetPhoto(id);
    const db = await openDB();
    if (!db) { await lsWrite(table, lsRead(table).filter(x => x.id !== id)); return; }
    return new Promise((resolve) => {
      const req = tx(db, table, 'readwrite').delete(id);
      req.onsuccess = req.onerror = () => resolve();
    });
  }

  async function writeTable(table, records) {
    const db = await openDB();
    if (!db) { await lsWrite(table, records); return; }
    return new Promise((resolve, reject) => {
      const t = db.transaction(table, 'readwrite');
      t.objectStore(table).clear();
      records.forEach(r => t.objectStore(table).put(r));
      t.oncomplete = () => resolve();
      t.onerror = () => reject(t.error);
    });
  }

  /* ---- object-URL cache for photos ---- */
  const urls = new Map();

  function photoURL(item) {
    if (!item || !item.photoBlob) return null;
    if (urls.has(item.id)) return urls.get(item.id);
    const url = URL.createObjectURL(item.photoBlob);
    urls.set(item.id, url);
    return url;
  }

  function forgetPhoto(id) {
    const url = urls.get(id);
    if (url) { URL.revokeObjectURL(url); urls.delete(id); }
  }

  /* ---- image handling ---- */
  /** Downscale + re-encode so a phone photo costs ~60–120 KB, not 4 MB. */
  function compressImage(file, maxDim = 1000, quality = 0.8) {
    return new Promise((resolve, reject) => {
      if (!file || !/^image\//.test(file.type)) return reject(new Error('That file is not an image.'));
      const src = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        try {
          const iw = img.naturalWidth || img.width || maxDim;
          const ih = img.naturalHeight || img.height || maxDim;
          const scale = Math.min(1, maxDim / Math.max(iw, ih));
          const w = Math.max(1, Math.round(iw * scale));
          const h = Math.max(1, Math.round(ih * scale));
          const canvas = document.createElement('canvas');
          canvas.width = w; canvas.height = h;
          const ctx = canvas.getContext('2d');
          ctx.fillStyle = '#ffffff';              // flatten transparency
          ctx.fillRect(0, 0, w, h);
          ctx.drawImage(img, 0, 0, w, h);
          canvas.toBlob((blob) => {
            URL.revokeObjectURL(src);
            blob ? resolve(blob) : reject(new Error('Could not read that photo.'));
          }, 'image/jpeg', quality);
        } catch (err) {
          URL.revokeObjectURL(src);
          reject(err);
        }
      };
      img.onerror = () => { URL.revokeObjectURL(src); reject(new Error('Could not read that photo.')); };
      img.src = src;
    });
  }

  const blobToDataURL = blob => new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onload = () => resolve(fr.result);
    fr.onerror = () => reject(fr.error);
    fr.readAsDataURL(blob);
  });

  function dataURLToBlob(dataURL) {
    const [head, body] = String(dataURL).split(',');
    const mime = (head.match(/:(.*?);/) || [, 'image/jpeg'])[1];
    const bin = atob(body);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new Blob([bytes], { type: mime });
  }

  /* ---- backup ---- */
  async function exportJSON(items, looks) {
    const itemList = items || await readTable(T_ITEMS);
    const out = [];
    for (const it of itemList) {
      const copy = Object.assign({}, it);
      copy.photo = it.photoBlob ? await blobToDataURL(it.photoBlob) : null;
      delete copy.photoBlob;
      out.push(copy);
    }
    return JSON.stringify({
      app: 'almari', version: 2, exportedAt: new Date().toISOString(),
      items: out, looks: looks || await readTable(T_LOOKS)
    }, null, 2);
  }

  async function importJSON(text) {
    const data = JSON.parse(text);
    const rawItems = Array.isArray(data) ? data : data.items;
    if (!Array.isArray(rawItems)) throw new Error('That file does not look like an Almari backup.');

    const items = [];
    for (const r of rawItems) {
      const it = Object.assign({}, r);
      it.id = it.id || uid('i');
      if (!it.slot) it.slot = (typeById(it.type) || {}).slot || 'top';
      it.colors = it.colors || []; it.occasions = it.occasions || []; it.seasons = it.seasons || [];
      it.laundry = it.laundry || 'clean';
      it.createdAt = it.createdAt || Date.now();
      it.photoBlob = it.photo ? dataURLToBlob(it.photo) : null;
      delete it.photo;
      items.push(it);
    }

    const known = new Set(items.map(i => i.id));
    const looks = (Array.isArray(data.looks) ? data.looks : []).map(l => {
      const slots = Object.assign({}, l.slots);
      LOOK_SLOTS.forEach(s => {
        if (s.multi) slots[s.id] = (slots[s.id] || []).filter(id => known.has(id));
        else if (slots[s.id] && !known.has(slots[s.id])) slots[s.id] = null;
      });
      return Object.assign({}, l, {
        id: l.id || uid('o'), slots,
        occasions: l.occasions || [], seasons: l.seasons || [],
        rating: l.rating || 0, worn: l.worn || 0,
        createdAt: l.createdAt || Date.now()
      });
    });

    await writeTable(T_ITEMS, items);
    await writeTable(T_LOOKS, looks);
    return { items, looks };
  }

  /* ---- misc ---- */
  function uid(prefix) {
    return (prefix || 'i') + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  /** Demo wardrobe + three demo looks built from it. */
  function seedSamples() {
    const now = Date.now();
    const items = SAMPLE_ITEMS.map((s, i) => Object.assign({}, s, {
      id: uid('i'),
      photoBlob: null,
      laundry: 'clean',
      worn: 0,
      lastWorn: null,
      createdAt: now - i * 60000
    }));

    const byType = {};
    items.forEach(it => { (byType[it.type] = byType[it.type] || []).push(it); });
    const pick = (type, idx) => {
      const list = byType[type] || [];
      return (list[idx || 0] || {}).id || null;
    };

    const drafted = [
      { name: 'Office Classic', occasions: ['Office'], seasons: ['All year'], rating: 4,
        slots: { top: pick('shirt'), bottom: pick('chinos'), foot: pick('formal-shoes'),
                 accessory: [pick('watch'), pick('belt')].filter(Boolean) },
        notes: 'Monday-to-Thursday rotation.' },
      { name: 'Festival Set', occasions: ['Festival', 'Wedding'], seasons: ['All year'], rating: 5,
        slots: { top: pick('kurta', 1), bottom: pick('pyjama'), outer: pick('nehru-jacket'), foot: pick('kolhapuri') },
        notes: 'Ganesh festival. Kurta is dry-clean only.' },
      { name: 'Weekend Errands', occasions: ['Casual'], seasons: ['Summer', 'Monsoon'], rating: 3,
        slots: { top: pick('tshirt'), bottom: pick('jeans'), foot: pick('sneakers') },
        notes: '' }
    ];

    const looks = drafted
      .filter(l => l.slots.top && l.slots.bottom && l.slots.foot)
      .map((l, i) => Object.assign({}, l, {
        id: uid('o'), worn: 0, lastWorn: null, photoBlob: null,
        createdAt: now - i * 30000, updatedAt: now - i * 30000
      }));

    return { items, looks };
  }

  return {
    /* items */
    all: () => readTable(T_ITEMS),
    put: rec => writeRecord(T_ITEMS, rec),
    remove: id => deleteRecord(T_ITEMS, id),
    replaceAll: rows => writeTable(T_ITEMS, rows),
    /* looks */
    allLooks: () => readTable(T_LOOKS),
    putLook: rec => writeRecord(T_LOOKS, rec),
    removeLook: id => deleteRecord(T_LOOKS, id),
    replaceAllLooks: rows => writeTable(T_LOOKS, rows),
    /* shared */
    photoURL, forgetPhoto, compressImage, exportJSON, importJSON, seedSamples, uid,
    backend: () => (useLS ? 'localStorage' : 'IndexedDB')
  };
})();
