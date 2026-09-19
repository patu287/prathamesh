/* ══════════════════════════════════════════════════════════════════
   Rojni · store.js
   Local-first storage. IndexedDB holds five tables; audio and photos
   are Blobs, so a decade of them fits comfortably. Nothing is ever
   uploaded anywhere. Falls back to localStorage (text only, media as
   data URLs) where IndexedDB is unavailable — notably file:// pages.

   Tables
     entries    { id, date, blocks[], mood, energy, aspects[], … }
     media      { id, entryId, type, blob, thumb, peaks, duration }
     keypoints  { id, text, aspects[], date, sourceEntryId, status }
     aspects    { id, name, glyph, color, order, bigRock, focus[] }
     meta       { key, value }          settings: pin, onboarded, …
   ══════════════════════════════════════════════════════════════════ */

const Store = (() => {
  const DB_NAME = 'rojni';
  const DB_VERSION = 1;
  const T_ENTRIES = 'entries', T_MEDIA = 'media', T_KEYS = 'keypoints',
        T_ASPECTS = 'aspects', T_META = 'meta';
  const TABLES = [T_ENTRIES, T_MEDIA, T_KEYS, T_ASPECTS, T_META];

  let dbPromise = null;
  let useLS = false;
  const LS = {
    [T_ENTRIES]: 'rojni.entries.v1', [T_MEDIA]: 'rojni.media.v1',
    [T_KEYS]: 'rojni.keys.v1', [T_ASPECTS]: 'rojni.aspects.v1', [T_META]: 'rojni.meta.v1'
  };

  function openDB() {
    if (!('indexedDB' in window)) { useLS = true; return Promise.resolve(null); }
    if (!dbPromise) {
      dbPromise = new Promise((resolve) => {
        let req;
        try { req = indexedDB.open(DB_NAME, DB_VERSION); }
        catch (err) { useLS = true; return resolve(null); }

        req.onupgradeneeded = () => {
          const db = req.result;
          TABLES.forEach(t => {
            if (!db.objectStoreNames.contains(t)) {
              const store = db.createObjectStore(t, { keyPath: t === T_META ? 'key' : 'id' });
              if (t === T_MEDIA) store.createIndex('entryId', 'entryId', { unique: false });
              if (t === T_ENTRIES) store.createIndex('date', 'date', { unique: false });
            }
          });
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => { useLS = true; resolve(null); };
        req.onblocked = () => { useLS = true; resolve(null); };
      });
    }
    return dbPromise;
  }

  /* ── localStorage fallback ────────────────────────────────────────
     A Blob cannot be JSON-serialised — it stringifies to "{}" and every
     voice note would silently vanish — so media goes in as a data URL. */
  const blobToDataURL = blob => new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onload = () => resolve(fr.result);
    fr.onerror = () => reject(fr.error);
    fr.readAsDataURL(blob);
  });
  const dataURLToBlob = url => {
    const [head, body] = String(url).split(',');
    const mime = (head.match(/data:([^;]+)/) || [, 'application/octet-stream'])[1];
    const bin = atob(body || '');
    const arr = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    return new Blob([arr], { type: mime });
  };

  async function lsRead(table) {
    try {
      const raw = JSON.parse(localStorage.getItem(LS[table]) || '[]');
      if (table !== T_MEDIA) return raw;
      return raw.map(r => {
        const m = Object.assign({}, r);
        if (m.data && !m.blob) { try { m.blob = dataURLToBlob(m.data); } catch (e) { m.blob = null; } }
        delete m.data;
        return m;
      });
    } catch (err) { return []; }
  }

  async function lsWrite(table, records) {
    let rows = records;
    if (table === T_MEDIA) {
      rows = [];
      for (const m of records) {
        const copy = Object.assign({}, m);
        copy.blob = undefined;
        if (m.blob) copy.data = await blobToDataURL(m.blob);
        delete copy.blob;
        rows.push(copy);
      }
    }
    try {
      localStorage.setItem(LS[table], JSON.stringify(rows));
      return true;
    } catch (err) {
      throw new Error('Storage is full — this browser has no IndexedDB, so audio and photo space is very limited. Serve the app over http (see README) for full storage.');
    }
  }

  /* ── generic table ops ────────────────────────────────────────── */
  function reqAsPromise(req, fallback) {
    return new Promise((resolve) => {
      req.onsuccess = () => resolve(req.result == null ? fallback : req.result);
      req.onerror = () => resolve(fallback);
    });
  }

  async function readTable(table) {
    const db = await openDB();
    if (!db) return lsRead(table);
    return reqAsPromise(db.transaction(table, 'readonly').objectStore(table).getAll(), []);
  }

  async function readAll() {
    const [entries, media, keypoints, aspects, metaRows] = await Promise.all([
      readTable(T_ENTRIES), readTable(T_MEDIA), readTable(T_KEYS), readTable(T_ASPECTS), readTable(T_META)
    ]);
    const meta = {};
    (metaRows || []).forEach(r => { if (r && r.key !== undefined) meta[r.key] = r.value; });
    return { entries, media, keypoints, aspects, meta };
  }

  async function put(table, rec) {
    const db = await openDB();
    if (!db) {
      const rows = await lsRead(table);
      const i = rows.findIndex(x => (table === T_META ? x.key : x.id) === (table === T_META ? rec.key : rec.id));
      if (i >= 0) rows[i] = rec; else rows.push(rec);
      await lsWrite(table, rows);
      return rec;
    }
    return new Promise((resolve, reject) => {
      const tx = db.transaction(table, 'readwrite');
      tx.objectStore(table).put(rec);
      tx.oncomplete = () => resolve(rec);
      tx.onerror = () => reject(tx.error);
    });
  }

  async function remove(table, id) {
    const db = await openDB();
    if (!db) {
      const rows = await lsRead(table);
      await lsWrite(table, rows.filter(x => (table === T_META ? x.key : x.id) !== id));
      return;
    }
    return new Promise((resolve) => {
      const tx = db.transaction(table, 'readwrite');
      tx.objectStore(table).delete(id);
      tx.oncomplete = tx.onerror = () => resolve();
    });
  }

  async function clearAll() {
    const db = await openDB();
    if (!db) { Object.values(LS).forEach(k => localStorage.removeItem(k)); return; }
    await Promise.all(TABLES.map(t => new Promise((resolve) => {
      const tx = db.transaction(t, 'readwrite');
      tx.objectStore(t).clear();
      tx.oncomplete = tx.onerror = () => resolve();
    })));
  }

  async function putMany(table, records) {
    if (!records.length) return;
    const db = await openDB();
    if (!db) {
      const rows = await lsRead(table);
      const keyOf = r => (table === T_META ? r.key : r.id);
      records.forEach(r => {
        const i = rows.findIndex(x => keyOf(x) === keyOf(r));
        if (i >= 0) rows[i] = r; else rows.push(r);
      });
      await lsWrite(table, rows);
      return;
    }
    return new Promise((resolve, reject) => {
      const tx = db.transaction(table, 'readwrite');
      records.forEach(r => tx.objectStore(table).put(r));
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  const mediaFor = id => readTable(T_MEDIA).then(all => all.filter(m => m.entryId === id));

  async function deleteEntryCascade(entryId) {
    const media = await mediaFor(entryId);
    await Promise.all(media.map(m => remove(T_MEDIA, m.id)));
    await remove(T_ENTRIES, entryId);
  }

  /* ── photos ───────────────────────────────────────────────────────
     Re-encode through a canvas: downscale + JPEG. A pleasant side
     effect is that this drops EXIF entirely, GPS included — so the app
     strips location data by default rather than storing it. */
  function compressImage(file, maxDim = 1400, quality = 0.8) {
    return new Promise((resolve, reject) => {
      const src = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        let { width: w, height: h } = img;
        const scale = Math.min(1, maxDim / Math.max(w, h));
        w = Math.max(1, Math.round(w * scale));
        h = Math.max(1, Math.round(h * scale));
        const canvas = document.createElement('canvas');
        canvas.width = w; canvas.height = h;
        canvas.getContext('2d').drawImage(img, 0, 0, w, h);
        URL.revokeObjectURL(src);
        canvas.toBlob(blob => {
          if (!blob) return reject(new Error('Could not process that photo.'));
          resolve({ blob, width: w, height: h });
        }, 'image/jpeg', quality);
      };
      img.onerror = () => { URL.revokeObjectURL(src); reject(new Error('Could not read that photo.')); };
      img.src = src;
    });
  }

  function thumbnail(blob, maxDim = 320, quality = 0.72) {
    return compressImage(blob, maxDim, quality).then(r => r.blob).catch(() => null);
  }

  /* Read the capture date out of a JPEG before the canvas re-encode
     destroys it. Returns a 'YYYY-MM-DD' key, or null. */
  async function exifDate(file) {
    try {
      const buf = await file.slice(0, 256 * 1024).arrayBuffer();
      const view = new DataView(buf);
      if (view.getUint16(0) !== 0xFFD8) return null;
      let offset = 2;
      while (offset < view.byteLength - 4) {
        const marker = view.getUint16(offset);
        const size = view.getUint16(offset + 2);
        if (marker === 0xFFE1) {
          const start = offset + 4;
          if (view.getUint32(start) !== 0x45786966) return null;  // "Exif"
          let dir = start + 6;
          const little = view.getUint16(dir) === 0x4949;
          const read16 = o => view.getUint16(o, little);
          const read32 = o => view.getUint32(o, little);
          const ifd0 = dir + read32(dir + 4);
          const count = read16(ifd0);
          let exifIFD = 0;
          for (let i = 0; i < count; i++) {
            const e = ifd0 + 2 + i * 12;
            if (read16(e) === 0x8769) exifIFD = dir + read32(e + 8);
          }
          if (!exifIFD) return null;
          const ecount = read16(exifIFD);
          for (let i = 0; i < ecount; i++) {
            const e = exifIFD + 2 + i * 12;
            if (read16(e) === 0x9003) {                     // DateTimeOriginal
              const p = dir + read32(e + 8);
              const s = String.fromCharCode(...new Uint8Array(buf, p, 19));
              const m = s.match(/^(\d{4}):(\d{2}):(\d{2})/);
              if (m) return `${m[1]}-${m[2]}-${m[3]}`;
            }
          }
          return null;
        }
        if ((marker & 0xFF00) !== 0xFF00) return null;
        offset += 2 + size;
      }
      return null;
    } catch (err) { return null; }
  }

  /* ── audio ────────────────────────────────────────────────────────
     Decode once at save time into 64 peak buckets, so the timeline can
     draw a waveform forever after without touching the audio data. */
  async function waveform(blob, buckets = 64) {
    try {
      const Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return null;
      const buf = await blob.arrayBuffer();
      const ctx = new Ctx();
      const audio = await ctx.decodeAudioData(buf);
      const chan = audio.getChannelData(0);
      const step = Math.max(1, Math.floor(chan.length / buckets));
      const peaks = [];
      for (let i = 0; i < buckets; i++) {
        let max = 0;
        const base = i * step;
        for (let j = 0; j < step; j++) {
          const v = Math.abs(chan[base + j] || 0);
          if (v > max) max = v;
        }
        peaks.push(Math.min(255, Math.round(max * 255)));
      }
      ctx.close();
      return peaks;
    } catch (err) {
      return null;   // WebM without a duration header can fail to decode — not fatal
    }
  }

  /* Pick a recorder MIME type that this browser will actually accept.
     Android Chrome gives webm/opus, Safari gives mp4. Never hardcode. */
  function pickAudioMime() {
    if (!window.MediaRecorder) return null;
    const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
    for (const c of candidates) {
      try { if (MediaRecorder.isTypeSupported(c)) return c; } catch (e) {}
    }
    return '';
  }

  /* ── storage state ────────────────────────────────────────────────
     Without persist() the browser is free to evict this origin under
     storage pressure — silently. Ask on first entry, not when it's full. */
  async function requestPersist() {
    try {
      if (!navigator.storage || !navigator.storage.persist) return 'unsupported';
      if (await navigator.storage.persisted()) return 'granted';
      const ok = await navigator.storage.persist();
      return ok ? 'granted' : 'denied';
    } catch (err) { return 'unsupported'; }
  }

  async function estimate() {
    try {
      if (!navigator.storage || !navigator.storage.estimate) return null;
      const { usage, quota } = await navigator.storage.estimate();
      return { usage, quota };
    } catch (err) { return null; }
  }

  /* ── backup: a real ZIP of real files ─────────────────────────────
     A store-only (uncompressed) ZIP writer, ~80 lines, no dependency.
     The point is that a backup is `journal.json` next to a `media/`
     folder of actual .webm and .jpg files — readable by anything in
     twenty years, not a database dump. Because it is store-only, the
     reader below is equally small. */
  const CRC_TABLE = (() => {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      t[n] = c >>> 0;
    }
    return t;
  })();
  function crc32(bytes) {
    let c = 0xFFFFFFFF;
    for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }
  const dosTime = d => ((d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1)) & 0xFFFF;
  const dosDate = d => (((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate()) & 0xFFFF;

  function makeZip(files) {
    const enc = new TextEncoder();
    const now = new Date();
    const t = dosTime(now), d = dosDate(now);
    const chunks = [];
    const central = [];
    let offset = 0;

    for (const f of files) {
      const name = enc.encode(f.name);
      const data = f.bytes;
      const crc = crc32(data);
      const local = new Uint8Array(30 + name.length);
      const lv = new DataView(local.buffer);
      lv.setUint32(0, 0x04034b50, true);
      lv.setUint16(4, 20, true);
      lv.setUint16(6, 0x0800, true);      // UTF-8 names
      lv.setUint16(8, 0, true);           // stored, no compression
      lv.setUint16(10, t, true);
      lv.setUint16(12, d, true);
      lv.setUint32(14, crc, true);
      lv.setUint32(18, data.length, true);
      lv.setUint32(22, data.length, true);
      lv.setUint16(26, name.length, true);
      lv.setUint16(28, 0, true);
      local.set(name, 30);

      chunks.push(local, data);

      const cd = new Uint8Array(46 + name.length);
      const cv = new DataView(cd.buffer);
      cv.setUint32(0, 0x02014b50, true);
      cv.setUint16(4, 20, true);
      cv.setUint16(6, 20, true);
      cv.setUint16(8, 0x0800, true);
      cv.setUint16(10, 0, true);
      cv.setUint16(12, t, true);
      cv.setUint16(14, d, true);
      cv.setUint32(16, crc, true);
      cv.setUint32(20, data.length, true);
      cv.setUint32(24, data.length, true);
      cv.setUint16(28, name.length, true);
      cv.setUint32(42, offset, true);
      cd.set(name, 46);
      central.push(cd);

      offset += local.length + data.length;
    }

    const cdSize = central.reduce((n, c) => n + c.length, 0);
    const end = new Uint8Array(22);
    const ev = new DataView(end.buffer);
    ev.setUint32(0, 0x06054b50, true);
    ev.setUint16(8, files.length, true);
    ev.setUint16(10, files.length, true);
    ev.setUint32(12, cdSize, true);
    ev.setUint32(16, offset, true);
    return new Blob([...chunks, ...central, end], { type: 'application/zip' });
  }

  function readZip(arrayBuffer) {
    const bytes = new Uint8Array(arrayBuffer);
    const view = new DataView(arrayBuffer);
    let eocd = -1;
    for (let i = bytes.length - 22; i >= 0 && i > bytes.length - 66000; i--) {
      if (view.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
    }
    if (eocd < 0) throw new Error('That does not look like a Rojni backup (.zip).');
    const count = view.getUint16(eocd + 10, true);
    let p = view.getUint32(eocd + 16, true);
    const out = [];
    const dec = new TextDecoder();
    for (let i = 0; i < count; i++) {
      if (view.getUint32(p, true) !== 0x02014b50) break;
      const method = view.getUint16(p + 10, true);
      const size = view.getUint32(p + 24, true);
      const nameLen = view.getUint16(p + 28, true);
      const extraLen = view.getUint16(p + 30, true);
      const commentLen = view.getUint16(p + 32, true);
      const localAt = view.getUint32(p + 42, true);
      const name = dec.decode(bytes.subarray(p + 46, p + 46 + nameLen));
      const lNameLen = view.getUint16(localAt + 26, true);
      const lExtraLen = view.getUint16(localAt + 28, true);
      const dataAt = localAt + 30 + lNameLen + lExtraLen;
      if (method !== 0) throw new Error(`"${name}" is compressed. Re-export from Rojni, or unzip and import journal.json.`);
      out.push({ name, bytes: bytes.subarray(dataAt, dataAt + size) });
      p += 46 + nameLen + extraLen + commentLen;
    }
    return out;
  }

  /* Export everything. Returns { blob, filename, counts } */
  async function exportBackup() {
    const { entries, media, keypoints, aspects, meta } = await readAll();
    const dec = new TextDecoder();
    const files = [];
    const mediaIndex = [];

    for (const m of media) {
      const ext = m.type === 'audio'
        ? (String(m.mime).includes('mp4') ? 'm4a' : 'webm')
        : 'jpg';
      const name = `media/${m.id}.${ext}`;
      try {
        const bytes = new Uint8Array(await m.blob.arrayBuffer());
        files.push({ name, bytes });
        mediaIndex.push(Object.assign({}, m, { blob: undefined, file: name }));
      } catch (err) {
        mediaIndex.push(Object.assign({}, m, { blob: undefined, file: null }));
      }
    }

    const manifest = {
      app: 'rojni', version: APP.version, exportedAt: new Date().toISOString(),
      counts: { entries: entries.length, media: media.length, keypoints: keypoints.length },
      entries, keypoints, aspects,
      media: mediaIndex,
      meta: { pin: (meta || {}).pin || null, theme: (meta || {}).theme || null }
    };
    files.unshift({ name: 'journal.json', bytes: new TextEncoder().encode(JSON.stringify(manifest, null, 2)) });

    const stamp = todayKey();
    return {
      blob: makeZip(files),
      filename: `rojni-backup-${stamp}.zip`,
      counts: manifest.counts,
      bytes: files.reduce((n, f) => n + f.bytes.length, 0)
    };
  }

  /* Import a backup from exportBackup(). Merges — never wipes. */
  async function importBackup(arrayBuffer) {
    const files = readZip(arrayBuffer);
    const manifestFile = files.find(f => /(^|\/)journal\.json$/.test(f.name));
    if (!manifestFile) throw new Error('The backup has no journal.json inside it.');
    const manifest = JSON.parse(new TextDecoder().decode(manifestFile.bytes));
    if (manifest.app !== 'rojni') throw new Error('That file was not made by Rojni.');

    const byName = new Map(files.map(f => [f.name, f]));
    const media = (manifest.media || []).map(m => {
      const f = m.file ? byName.get(m.file) : null;
      let blob = null;
      if (f) {
        const ext = m.file.split('.').pop().toLowerCase();
        const mime = m.mime || (ext === 'jpg' ? 'image/jpeg' : ext === 'm4a' ? 'audio/mp4' : 'audio/webm');
        blob = new Blob([f.bytes], { type: mime });
      }
      return Object.assign({}, m, { blob, file: undefined });
    }).filter(m => m.blob);

    await putMany(T_ENTRIES, manifest.entries || []);
    await putMany(T_KEYS, manifest.keypoints || []);
    await putMany(T_ASPECTS, manifest.aspects || []);
    await putMany(T_MEDIA, media);

    return {
      entries: (manifest.entries || []).length,
      media: media.length,
      keypoints: (manifest.keypoints || []).length,
      missingMedia: (manifest.media || []).length - media.length
    };
  }

  /* ── PIN gate ─────────────────────────────────────────────────────
     A hash, not encryption. This stops someone who picks up your
     unlocked phone. It does not stop anyone with the device and a
     devtools console. The UI says so plainly. */
  async function hashPin(pin, salt) {
    const data = new TextEncoder().encode(`rojni:${salt}:${pin}`);
    if (window.crypto && crypto.subtle) {
      const digest = await crypto.subtle.digest('SHA-256', data);
      return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
    }
    let h = 5381;
    for (const b of data) h = ((h << 5) + h + b) >>> 0;
    return 'w' + h.toString(16);
  }
  const makeSalt = () => Array.from({ length: 12 }, () => Math.floor(Math.random() * 36).toString(36)).join('');

  return {
    readAll, readTable, put, putMany, remove, clearAll, mediaFor, deleteEntryCascade,
    compressImage, thumbnail, exifDate, waveform, pickAudioMime,
    requestPersist, estimate,
    exportBackup, importBackup,
    hashPin, makeSalt,
    blobToDataURL, dataURLToBlob,
    get usingFallback() { return useLS; },
    T: { ENTRIES: T_ENTRIES, MEDIA: T_MEDIA, KEYS: T_KEYS, ASPECTS: T_ASPECTS, META: T_META }
  };
})();
