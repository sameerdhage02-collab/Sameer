const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const srv = http.createServer((q, r) => {
  const f = path.join(__dirname, decodeURIComponent(q.url.split('?')[0]) === '/' ? 'index.html' : decodeURIComponent(q.url));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); return r.end(); }
    r.writeHead(200, {'Content-Type': f.endsWith('.js') ? 'text/javascript' : 'text/html'}); r.end(d); });
}).listen(8765);
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader','--enable-unsafe-swiftshader'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 720 } });
  pg.on('console', m => console.log(m.text())); pg.on('pageerror', e => console.log('ERR', e));
  await pg.goto('http://localhost:8765/');
  await pg.waitForFunction('window.ready');
  fs.mkdirSync('frames', { recursive: true });
  const N = +process.argv[2] || 150;
  for (let i = 0; i < N; i++) {
    await pg.evaluate(t => window.renderAt(t), i / 30);
    await pg.locator('canvas').screenshot({ path: `frames/f${String(i).padStart(4,'0')}.png` });
  }
  await b.close(); srv.close();
})();
