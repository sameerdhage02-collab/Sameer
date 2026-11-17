const { chromium } = require('playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const T={'.html':'text/html','.js':'text/javascript','.json':'application/json','.woff2':'font/woff2','.mp3':'audio/mpeg'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]);const f=path.join(__dirname,p);fs.readFile(f,(e,d)=>{if(e){r.writeHead(404);return r.end();}r.writeHead(200,{'Content-Type':T[path.extname(f)]||'application/octet-stream'});r.end(d);});}).listen(8799);
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});const pg=await b.newPage({viewport:{width:+process.argv[3],height:+process.argv[4]}});
pg.on('pageerror',e=>console.log('ERR',e.message));await pg.goto('http://localhost:8799/'+process.argv[2]);await pg.waitForFunction('window.done',null,{timeout:60000});
await pg.screenshot({path:process.argv[5]});await b.close();srv.close();})();
