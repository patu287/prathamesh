/* ══════════════════════════════════════════════════════════════════
   Almari · store.js
   Local-first storage. IndexedDB holds the items (photos are Blobs,
   so hundreds of pictures fit comfortably). Falls back to
   localStorage where IndexedDB is unavailable.
   Nothing is ever uploaded anywhere.
   ══════════════════════════════════════════════════════════════════ */

const Store = (() => {
  const DB_NAME = 'almari';
  const DB_VERSION = 1;
  const OBJ = 'items';
  const LS_KEY = 'almari.items.v1';

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
          if (!db.objectStoreNames.contains(OBJ)) db.createObjectStore(OBJ, { keyPath: 'id' });
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => { useLS = true; resolve(null); };
        req.onblocked = () => { useLS = true; resolve(null); };
      });
    }
    return dbPromise;
  }

  function tx(db, mode) { return db.transaction(OBJ, mode).objectStore(OBJ); }

  /* ---- localStorage fallback ----
     Used when IndexedDB is blocked (notably file:// pages). A Blob cannot be
     JSON-serialised — it stringifies to "{}" and every photo would silently
     vanish — so photos are stored as data URLs on this path instead. */
  function lsRead() {
    try {
      const raw = JSON.parse(localStorage.getItem(LS_KEY) || '[]');
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

  async function lsWrite(items) {
    const rows = [];
    for (const it of items) {
      const copy = Object.assign({}, it);
      if (copy.photoBlob) copy.photo = await blobToDataURL(copy.photoBlob);
      delete copy.photoBlob;
      rows.push(copy);
    }
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(rows));
      return true;
    } catch (err) {
      throw new Error('Storage is full. This browser has no IndexedDB, so photo space is limited — serve the app over http (see README).');
    }
  }

  /* ---- CRUD ---- */
  async function all() {
    const db = await openDB();
    if (!db) return lsRead();
    return new Promise((resolve) => {
      const req = tx(db, 'readonly').getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => resolve([]);
    });
  }

  async function put(item) {
    const db = await openDB();
    if (!db) {
      const items = lsRead();
      const i = items.findIndex(x => x.id === item.id);
      if (i >= 0) items[i] = item; else items.push(item);
      await lsWrite(items);
      return item;
    }
    return new Promise((resolve, reject) => {
      const req = tx(db, 'readwrite').put(item);
      req.onsuccess = () => resolve(item);
      req.onerror = () => reject(req.error);
    });
  }

  async function remove(id) {
    forgetPhoto(id);
    const db = await openDB();
    if (!db) { await lsWrite(lsRead().filter(x => x.id !== id)); return; }
    return new Promise((resolve) => {
      const req = tx(db, 'readwrite').delete(id);
      req.onsuccess = req.onerror = () => resolve();
    });
  }

  /** Replace the whole wardrobe (used by import + sample seeding). */
  async function replaceAll(items) {
    const db = await openDB();
    if (!db) { await lsWrite(items); return; }
    return new Promise((resolve, reject) => {
      const t = db.transaction(OBJ, 'readwrite');
      t.objectStore(OBJ).clear();
      items.forEach(it => t.objectStore(OBJ).put(it));
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
  async function exportJSON(items) {
    const list = items || await all();
    const out = [];
    for (const it of list) {
      const copy = Object.assign({}, it);
      copy.photo = it.photoBlob ? await blobToDataURL(it.photoBlob) : null;
      delete copy.photoBlob;
      out.push(copy);
    }
    return JSON.stringify({ app: 'almari', version: 1, exportedAt: new Date().toISOString(), items: out }, null, 2);
  }

  async function importJSON(text) {
    const data = JSON.parse(text);
    const raw = Array.isArray(data) ? data : data.items;
    if (!Array.isArray(raw)) throw new Error('That file does not look like an Almari backup.');
    const items = [];
    for (const r of raw) {
      const it = Object.assign({}, r);
      it.id = it.id || uid();
      if (!it.slot) it.slot = (typeById(it.type) || {}).slot || 'top';
      it.colors = it.colors || []; it.occasions = it.occasions || []; it.seasons = it.seasons || [];
      it.createdAt = it.createdAt || Date.now();
      it.photoBlob = it.photo ? dataURLToBlob(it.photo) : null;
      delete it.photo;
      items.push(it);
    }
    await replaceAll(items);
    return items;
  }

  /* ---- misc ---- */
  function uid() {
    return 'i' + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  /** Build full item records from the demo list in data.js. */
  function seedSamples() {
    const now = Date.now();
    return SAMPLE_ITEMS.map((s, i) => Object.assign({
      id: uid(),
      photoBlob: null,
      worn: 0,
      lastWorn: null,
      createdAt: now - i * 60000
    }, s));
  }

  return {
    all, put, remove, replaceAll, photoURL, forgetPhoto,
    compressImage, exportJSON, importJSON, seedSamples, uid,
    backend: () => (useLS ? 'localStorage' : 'IndexedDB')
  };
})();
