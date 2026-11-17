// Usage: node render.js stills  -> contact sheet frames at scene midpoints
//        node render.js full [start] [end] -> frames/ JPEGs at 30fps
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2' };
const srv = http.createServer((q, r) => {
  let p = decodeURIComponent(q.url.split('?')[0]); if (p === '/') p = '/index.html';
  const f = path.join(__dirname, p);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(d); });
}).listen(+process.env.PORT || 8766);
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await b.newPage({ viewport: { width: 720, height: 1280 } });
  pg.on('pageerror', e => console.log('PAGEERR', e.message));
  pg.on('console', m => { if (m.type() === 'error') console.log('CONSOLE', m.text()); });
  await pg.goto(`http://localhost:${+process.env.PORT || 8766}/`);
  await pg.waitForFunction('window.ready', null, { timeout: 120000 });
  const total = await pg.evaluate('window.TOTAL');
  fs.writeFileSync('timeline.json', JSON.stringify(await pg.evaluate('({total: window.TOTAL, events: window.EVENTS, segs: window.SEGTIMES})'), null, 1));
  console.log('TOTAL', total.toFixed(2));
  const mode = process.argv[2] || 'stills';
  if (mode === 'stills') {
    const times = process.argv[3] ? process.argv[3].split(',').map(Number) : JSON.parse(fs.readFileSync('timeline.json')).segs.map(s => s.start + s.dur * .6);
    fs.mkdirSync('stills', { recursive: true });
    for (const [i, t] of times.entries()) { await pg.evaluate(t => window.renderAt(t), t); await pg.screenshot({ path: `stills/s${String(i).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 85 }); }
  } else {
    fs.mkdirSync('frames', { recursive: true });
    const N = Math.ceil(total * 30); const s = +(process.argv[3] || 0), e = Math.min(N, +(process.argv[4] || N));
    const t0 = Date.now();
    for (let i = s; i < e; i++) {
      await pg.evaluate(t => window.renderAt(t), i / 30);
      await pg.screenshot({ path: `frames/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 90 });
      if (i % 150 === 0) console.log(i, '/', N, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
  }
  await b.close(); srv.close();
})();
