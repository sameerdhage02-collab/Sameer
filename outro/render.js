const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{const mode=process.argv[2]||'full';const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('console',m=>console.log('PAGE',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/index.html');await p.waitForTimeout(500);
const dur=await p.evaluate(()=>window.DUR);
if(mode==='stills'){const ts=process.argv.slice(3).map(Number);for(const t of ts){const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.85)},t);require('fs').writeFileSync(`still_${t}.jpg`,Buffer.from(d.split(',')[1],'base64'));}await b.close();return;}
const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','outro_silent.mp4'],{stdio:['pipe','ignore','inherit']});
const N=Math.round(dur*30);for(let f=0;f<N;f++){const d=await p.evaluate(t=>{render(t);return document.getElementById('c').toDataURL('image/jpeg',.92)},f/30);ff.stdin.write(Buffer.from(d.split(',')[1],'base64'));if(f%90==0)console.log('frame',f,'/',N);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();})();
