// Frame Innovations site worker (Cloudflare Pages, advanced mode).
// Serves the static site and handles the waitlist:
//   POST /api/waitlist          -> saves a sign-up to the D1 database bound as DB
//   GET  /api/waitlist.csv?key= -> downloads every sign-up as CSV (key = the EXPORT_KEY secret)
// Everything else is passed to the static files.

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

let tableReady = false;
async function ensureTable(db) {
  if (tableReady) return;
  await db.prepare(`CREATE TABLE IF NOT EXISTS waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT, type TEXT, printers INTEGER, message TEXT,
    source TEXT, country TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  )`).run();
  tableReady = true;
}

const clip = (v, n) => { if (v == null) return null; const t = String(v).trim().slice(0, n); return t || null; };
const csvCell = v => { const t = v == null ? '' : String(v); return /[",\n\r]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t; };

async function addToWaitlist(request, env) {
  if (!env.DB) return json({ error: 'The waitlist isn’t connected yet. Email hello@frameinnovations.com instead.' }, 503);
  let d;
  try { d = await request.json(); } catch { return json({ error: 'Bad request.' }, 400); }
  if (d && d.website) return json({ ok: true });            // honeypot field: bots fill it, people never see it
  const email = clip(d.email, 254)?.toLowerCase();
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return json({ error: 'Add a valid email address.' }, 400);
  const printers = Number.parseInt(d.printers, 10);
  await ensureTable(env.DB);
  await env.DB.prepare(`INSERT INTO waitlist (email, name, type, printers, message, source, country)
      VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
      ON CONFLICT(email) DO UPDATE SET
        name = COALESCE(excluded.name, name), type = COALESCE(excluded.type, type),
        printers = COALESCE(excluded.printers, printers), message = COALESCE(excluded.message, message),
        updated_at = datetime('now')`)
    .bind(email, clip(d.name, 120), clip(d.type, 60), Number.isFinite(printers) && printers >= 0 && printers < 100000 ? printers : null,
          clip(d.message, 2000), clip(d.source, 20), request.cf?.country || null)
    .run();
  return json({ ok: true });
}

async function exportCsv(url, env) {
  if (!env.EXPORT_KEY || url.searchParams.get('key') !== env.EXPORT_KEY) return new Response('Not found', { status: 404 });
  if (!env.DB) return new Response('Database not bound', { status: 503 });
  await ensureTable(env.DB);
  const { results } = await env.DB.prepare('SELECT * FROM waitlist ORDER BY created_at').all();
  const cols = ['created_at', 'email', 'name', 'type', 'printers', 'message', 'source', 'country', 'updated_at'];
  const csv = [cols.join(','), ...results.map(r => cols.map(c => csvCell(r[c])).join(','))].join('\r\n');
  return new Response(csv, { headers: { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': 'attachment; filename="waitlist.csv"', 'cache-control': 'no-store' } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname === '/api/waitlist') {
        if (request.method !== 'POST') return json({ error: 'Method not allowed.' }, 405);
        return await addToWaitlist(request, env);
      }
      if (url.pathname === '/api/waitlist.csv') return await exportCsv(url, env);
    } catch (err) {
      console.error(err);
      return json({ error: 'Something went wrong. Try again in a minute.' }, 500);
    }
    return env.ASSETS.fetch(request);
  },
};
