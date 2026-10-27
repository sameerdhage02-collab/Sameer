const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path=require('path');
(async()=>{
  const mode=process.argv[2]||'test';
  const b=await chromium.launch();
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.resolve('reel/index.html'));
  await p.evaluate(()=>document.fonts.ready);
  await p.waitForTimeout(300);
  const total=await p.evaluate(()=>window.TOTAL);
  const el=await p.$('#stage');
  if(mode==='test'){
    const ts=process.argv.slice(3).map(Number);
    for(const t of ts){await p.evaluate(t=>render(t),t);await el.screenshot({path:`${process.env.TD||"test"}/t_${t}.png`});}
  } else {
    const fps=30,N=Math.round(total*fps);
    const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium','-movflags','+faststart','out/reel_silent.mp4'],{stdio:['pipe','inherit','inherit']});
    for(let i=0;i<N;i++){await p.evaluate(t=>render(t),i/fps);const buf=await el.screenshot({type:'jpeg',quality:95});
      if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(i%150===0)console.log('frame',i,'/',N);}
    ff.stdin.end(); await new Promise(r=>ff.on('close',r));
  }
  await b.close();
})();
