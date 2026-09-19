/* ══════════════════════════════════════════════════════════════════
   Rojni · data.js
   Aspects, prompts, date helpers, small utilities. No dependencies.
   ══════════════════════════════════════════════════════════════════ */

const APP = { name: 'Rojni', tagline: 'रोजनी · the day, kept', version: '1.0' };

/* ── Aspects ────────────────────────────────────────────────────────
   EDIT THIS LIST to your own life. Everything else in the app is a
   lens over these. Keep it to 5–8; more than that and none of them
   get real attention. `id` must be stable — it is what entries store. */
const DEFAULT_ASPECTS = [
  { id: 'health',    name: 'Health',        glyph: '◍', color: '#4c7a63' },
  { id: 'work',      name: 'Work',          glyph: '◈', color: '#3f6b93' },
  { id: 'money',     name: 'Money',         glyph: '◎', color: '#8a7a3f' },
  { id: 'relations', name: 'Relationships', glyph: '❍', color: '#a4542f' },
  { id: 'learning',  name: 'Learning',      glyph: '◇', color: '#6a5a9c' },
  { id: 'inner',     name: 'Inner life',    glyph: '◐', color: '#7a4a6b' },
  { id: 'home',      name: 'Home',          glyph: '⌂', color: '#6f7d5f' },
  { id: 'play',      name: 'Play',          glyph: '✧', color: '#b07f2f' }
];

const ASPECT_COLORS = [
  '#4c7a63', '#3f6b93', '#8a7a3f', '#a4542f', '#6a5a9c',
  '#7a4a6b', '#6f7d5f', '#b07f2f', '#8c5a52', '#4a7a7a'
];

/* ── Prompts for empty days ─────────────────────────────────────── */
const PROMPTS = [
  'What took the most out of me today?',
  'What would I tell myself from a year ago?',
  'One thing I noticed and did not say out loud.',
  'What did I avoid today, and why?',
  'Who did I think about, and what did I think?',
  'What went better than I expected?',
  'What am I pretending not to know?',
  'The smallest good thing today.',
  'What did I do purely because I wanted to?',
  'Where did I spend money today, and how did it feel?',
  'What am I carrying that is not mine to carry?',
  'Describe today in five words, then explain the fifth.',
  'What did my body tell me today?',
  'What did I learn that I will forget by next week?',
  'Who deserves a thank-you I have not sent?',
  'What am I waiting for?',
  'What decision am I circling?',
  'What did today cost me?',
  'What was the best hour of today?',
  'What am I doing out of habit rather than choice?',
  'What made me laugh?',
  'What would make tomorrow 10% lighter?',
  'Something I did well, unmodestly.',
  'What angered me, and what was underneath it?',
  'What did I read, watch or hear that stuck?',
  'What am I hoping nobody asks me about?',
  'Where was I today that I want to remember?',
  'What is the story I keep telling myself?',
  'Who did I spend the most time with, and how was it?',
  'What would I do differently if nobody would ever know?',
  'What is one thing I want to stop doing?',
  'What am I grateful for that I did not earn?',
  'What has been sitting undone for weeks?',
  'What did I notice about someone else today?',
  'What is the hardest thing about right now?',
  'If today repeated for a year, where would I end up?',
  'What did I say yes to that I wanted to say no to?',
  'What is going right that I have stopped noticing?',
  'Which of my worries from last month came true?',
  'What did I make today, even badly?',
  'What am I learning too slowly?',
  'Whose voice do I hear when I doubt myself?',
  'What did I do today that my future self will thank me for?',
  'What is one small thing I am looking forward to?',
  'What part of today do I want to leave behind?',
  'What did I choose not to write about — and why not?',
  'What is true today that was not true a year ago?',
  'Where did I feel most like myself?',
  'If I only wrote one line for today, it would be:'
];

const WEEK_QUESTIONS = [
  { id: 'mattered',  label: 'What mattered this week?',        hint: 'Not what happened — what actually mattered.' },
  { id: 'drained',   label: 'What drained me?',                hint: 'People, tasks, habits, screens, expectations.' },
  { id: 'next',      label: 'One thing for next week',         hint: 'One. This becomes a key point.' }
];

/* ── Utilities ──────────────────────────────────────────────────── */
const uid = (p = 'x') => p + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

/* The local date key. Never derived from a UTC instant — an 11:40pm
   entry must land on today, not tomorrow. */
function dateKey(d = new Date()) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
const todayKey = () => dateKey(new Date());

function parseKey(key) {
  const [y, m, d] = key.split('-').map(Number);
  return new Date(y, m - 1, d);
}

const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const DAYS   = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

function fmtLong(key) {
  const d = parseKey(key);
  return `${DAYS[d.getDay()]}, ${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}
function fmtShort(key) {
  const d = parseKey(key);
  return `${d.getDate()} ${MONTHS[d.getMonth()].slice(0, 3)} ${String(d.getFullYear()).slice(2)}`;
}
function fmtMedium(key) {
  const d = parseKey(key);
  return `${DAYS[d.getDay()].slice(0, 3)}, ${d.getDate()} ${MONTHS[d.getMonth()].slice(0, 3)}`;
}

/* "12 days ago" / "today" / "yesterday" */
function daysAgo(key) {
  const a = parseKey(key).getTime();
  const b = parseKey(todayKey()).getTime();
  return Math.round((b - a) / 86400000);
}
function relDate(key) {
  const n = daysAgo(key);
  if (n === 0) return 'today';
  if (n === 1) return 'yesterday';
  if (n === -1) return 'tomorrow';
  if (n > 1 && n < 30) return `${n} days ago`;
  if (n >= 30 && n < 365) return `${Math.round(n / 30)} months ago`;
  if (n >= 365) { const y = Math.round(n / 365); return y === 1 ? 'a year ago' : `${y} years ago`; }
  return fmtShort(key);
}
function fmtClock(seconds) {
  const s = Math.max(0, Math.round(seconds || 0));
  const m = Math.floor(s / 60);
  const r = s % 60;
  if (m >= 60) return `${Math.floor(m / 60)}:${String(m % 60).padStart(2, '0')}:${String(r).padStart(2, '0')}`;
  return `${m}:${String(r).padStart(2, '0')}`;
}
function fmtSize(bytes) {
  if (!bytes) return '0 KB';
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / 1048576).toFixed(bytes < 10485760 ? 1 : 0)} MB`;
  return `${(bytes / 1073741824).toFixed(2)} GB`;
}
function escapeHTML(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/* First real line of an entry — used as its title everywhere. */
function entryTitle(entry) {
  if (entry.title) return entry.title;
  const text = blocksText(entry);
  if (!text) {
    const hasAudio = (entry.blocks || []).some(b => b.t === 'audio');
    const hasPhoto = (entry.blocks || []).some(b => b.t === 'photo');
    if (hasAudio && hasPhoto) return 'Voice note + photo';
    if (hasAudio) return 'Voice note';
    if (hasPhoto) return 'Photo';
    return 'Untitled';
  }
  const first = text.split('\n').map(l => l.trim()).filter(Boolean)[0] || text;
  return first.length > 92 ? first.slice(0, 92).trimEnd() + '…' : first;
}
function blocksText(entry) {
  return (entry.blocks || [])
    .filter(b => b.t === 'text' || b.t === 'quote')
    .map(b => b.text)
    .filter(Boolean)
    .join('\n');
}
function fullText(entry) {
  return (entry.blocks || [])
    .map(b => (b.t === 'text' || b.t === 'quote') ? b.text : (b.t === 'photo' ? '[photo]' : b.t === 'audio' ? '[audio]' : ''))
    .filter(Boolean)
    .join(' ');
}
function wordCount(entry) {
  const t = blocksText(entry).trim();
  return t ? t.split(/\s+/).length : 0;
}
function aspectById(aspects, id) {
  return aspects.find(a => a.id === id) || null;
}
