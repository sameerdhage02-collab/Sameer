const { chromium } = require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+path.resolve('reel/index.html'));
const r=await p.evaluate(()=>({total:TOTAL,starts:S.map(s=>s.start),big:S.flatMap(s=>[...s.topL,...s.botL].flat().filter(t=>t.k!=='s').flatMap(t=>t.ws.map(o=>s.start+o.t)))}));
console.log(JSON.stringify(r));await b.close();})();
