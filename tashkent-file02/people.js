// Characters: 2D illustrated portraits + 3D figures with illustrated face decals.
import * as THREE from 'three';

// ---------- the cast (stylised illustrations, not photographs) ----------
export const PEOPLE = {
  shastri: { skin: '#c48a5a', hw: 112, hh: 132, jaw: .62, ear: 1.25, head: 'cap', top: '#f2eee4', jacket: '#3b2f27', bottom: '#f2eee4', age: .8, smile: .55, brow: '#2a2a2a', name: 'L.B. SHASTRI' },
  lalita: { skin: '#c99066', hw: 108, hh: 130, jaw: .64, ear: 1, head: 'saree', top: '#efe7d6', border: '#a8401c', bottom: '#efe7d6', bindi: true, age: .75, smile: .1, brow: '#2a2420', name: 'LALITA SHASTRI' },
  chugh: { skin: '#d49d6c', hw: 100, hh: 140, jaw: .58, ear: 1, head: 'hair', hair: '#2b2b2b', grey: .35, glasses: true, mustache: true, top: '#5b5f66', shirt: '#f2f0ea', tie: '#7a1c1c', bottom: '#4a4e55', age: .5, smile: .15, brow: '#222', name: 'DR. R.N. CHUGH' },
  ramnath: { skin: '#a8724a', hw: 102, hh: 136, jaw: .6, ear: 1.05, head: 'hair', hair: '#151110', mustache: true, top: '#b9a27a', bottom: '#e9e3d4', age: .35, smile: 0, brow: '#151110', name: 'RAM NATH' },
};

const shade = (hex, k) => { const c = new THREE.Color(hex); c.multiplyScalar(k); return '#' + c.getHexString(); };

// ---------- 2D portrait illustration ----------
export function drawPortrait(c, w, h, p, { bg = true } = {}) {
  if (bg) {
    const g = c.createRadialGradient(w / 2, h * .38, 10, w / 2, h * .45, w * .85);
    g.addColorStop(0, '#d9c7a0'); g.addColorStop(1, '#5e4b33'); c.fillStyle = g; c.fillRect(0, 0, w, h);
    c.fillStyle = 'rgba(70,50,25,.18)';
    for (let y = 0; y < h; y += 9) for (let x = (y / 9) % 2 ? 4 : 0; x < w; x += 9) { const r = 1.6 + 1.4 * (y / h); c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); }
  }
  c.save(); c.translate(w / 2, h * .5); c.scale(w / 600, w / 600);
  c.lineJoin = 'round'; c.lineCap = 'round';
  const ink = '#2a170c', skin = p.skin, skinD = shade(p.skin, .78), cy = -70;
  const O = (lw = 4) => { c.strokeStyle = ink; c.lineWidth = lw; c.stroke(); };
  // clothes / shoulders
  c.beginPath(); c.moveTo(-300, 400); c.bezierCurveTo(-290, 220, -200, 170, -70, 150); c.lineTo(70, 150); c.bezierCurveTo(200, 170, 290, 220, 300, 400); c.closePath();
  c.fillStyle = p.top; c.fill(); O(5);
  const cg = c.createLinearGradient(-300, 0, 300, 0); cg.addColorStop(0, 'rgba(0,0,0,0)'); cg.addColorStop(1, 'rgba(40,20,0,.28)'); c.fillStyle = cg; c.fill();
  // neck
  c.beginPath(); c.moveTo(-46, 30); c.lineTo(-50, 165); c.quadraticCurveTo(0, 195, 50, 165); c.lineTo(46, 30); c.closePath(); c.fillStyle = skinD; c.fill(); O(4);
  if (p.jacket) { // white kurta collar + dark Nehru jacket
    c.beginPath(); c.moveTo(-58, 150); c.quadraticCurveTo(0, 185, 58, 150); c.lineTo(58, 172); c.quadraticCurveTo(0, 205, -58, 172); c.closePath(); c.fillStyle = p.top; c.fill(); O(3);
    for (const s of [-1, 1]) { c.beginPath(); c.moveTo(s * 60, 168); c.bezierCurveTo(s * 150, 175, s * 250, 230, s * 275, 400); c.lineTo(s * 12, 400); c.lineTo(s * 12, 230); c.quadraticCurveTo(s * 20, 185, s * 60, 168); c.closePath(); c.fillStyle = p.jacket; c.fill(); O(4); }
    c.fillStyle = '#c9b48a'; for (let i = 0; i < 4; i++) { c.beginPath(); c.arc(-24, 250 + i * 40, 6, 0, 7); c.fill(); }
  } else if (p.tie) { // suit: shirt V, tie, lapels
    c.beginPath(); c.moveTo(-60, 152); c.lineTo(0, 290); c.lineTo(60, 152); c.closePath(); c.fillStyle = p.shirt; c.fill(); O(3);
    c.beginPath(); c.moveTo(-14, 172); c.lineTo(14, 172); c.lineTo(22, 300); c.lineTo(0, 330); c.lineTo(-22, 300); c.closePath(); c.fillStyle = p.tie; c.fill(); O(3);
    for (const s of [-1, 1]) { c.beginPath(); c.moveTo(s * 62, 150); c.lineTo(s * 8, 330); c.lineTo(s * 70, 260); c.lineTo(s * 100, 190); c.closePath(); c.fillStyle = shade(p.top, .8); c.fill(); O(3); }
  } else if (p.head !== 'saree') { // kurta collar + placket
    c.beginPath(); c.moveTo(-58, 150); c.quadraticCurveTo(0, 185, 58, 150); c.lineTo(58, 172); c.quadraticCurveTo(0, 205, -58, 172); c.closePath(); c.fillStyle = shade(p.top, .92); c.fill(); O(3);
    c.beginPath(); c.moveTo(0, 190); c.lineTo(0, 330); O(3); c.fillStyle = '#e8dcc0'; for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(10, 215 + i * 38, 5, 0, 7); c.fill(); }
  }
  // ears
  for (const s of [-1, 1]) { c.beginPath(); c.ellipse(s * (p.hw - 4), cy + 15, 20 * p.ear, 34 * p.ear, s * .15, 0, 7); c.fillStyle = skin; c.fill(); O(4); c.beginPath(); c.ellipse(s * (p.hw - 2), cy + 15, 9 * p.ear, 20 * p.ear, s * .15, -1, 1.6); c.strokeStyle = skinD; c.lineWidth = 4; c.stroke(); }
  // head
  const head = () => { const hw = p.hw, hh = p.hh; c.beginPath(); c.moveTo(0, cy - hh);
    c.bezierCurveTo(hw * .78, cy - hh, hw, cy - hh * .55, hw, cy - hh * .05); c.bezierCurveTo(hw, cy + hh * .5, hw * p.jaw, cy + hh * .9, 0, cy + hh);
    c.bezierCurveTo(-hw * p.jaw, cy + hh * .9, -hw, cy + hh * .5, -hw, cy - hh * .05); c.bezierCurveTo(-hw, cy - hh * .55, -hw * .78, cy - hh, 0, cy - hh); };
  head(); c.fillStyle = skin; c.fill();
  c.save(); head(); c.clip(); const hg = c.createLinearGradient(-p.hw, 0, p.hw, 0); hg.addColorStop(0, 'rgba(255,230,200,.18)'); hg.addColorStop(.55, 'rgba(0,0,0,0)'); hg.addColorStop(1, 'rgba(60,25,5,.38)'); c.fillStyle = hg; c.fillRect(-300, -300, 600, 600);
  c.fillStyle = 'rgba(200,80,60,.12)'; for (const s of [-1, 1]) { c.beginPath(); c.ellipse(s * 58, cy + 40, 30, 18, 0, 0, 7); c.fill(); }
  c.restore(); head(); O(5);
  // hair / cap / saree
  if (p.head === 'hair') {
    c.beginPath(); c.moveTo(-p.hw - 3, cy - 10); c.bezierCurveTo(-p.hw - 8, cy - p.hh - 40, p.hw + 8, cy - p.hh - 45, p.hw + 3, cy - 10);
    c.bezierCurveTo(p.hw - 10, cy - 70, p.hw * .7, cy - p.hh * .72, p.hw * .2, cy - p.hh * .78); c.bezierCurveTo(-p.hw * .3, cy - p.hh * .6, -p.hw * .9, cy - p.hh * .6, -p.hw - 3, cy - 10);
    c.fillStyle = p.hair; c.fill(); O(4);
    if (p.grey) { c.strokeStyle = `rgba(200,200,200,${p.grey})`; c.lineWidth = 3; for (let i = 0; i < 14; i++) { c.beginPath(); const x = -p.hw + 20 + i * 14; c.moveTo(x, cy - p.hh * .8 - (i % 3) * 6); c.lineTo(x + 22, cy - p.hh - 10 + (i % 2) * 12); c.stroke(); } }
  } else if (p.head === 'cap') { // Gandhi cap
    c.save(); c.rotate(-.04);
    c.beginPath(); c.moveTo(-p.hw - 6, cy - p.hh * .52); c.lineTo(p.hw + 6, cy - p.hh * .52); c.bezierCurveTo(p.hw * .9, cy - p.hh - 30, p.hw * .3, cy - p.hh - 52, 0, cy - p.hh - 50);
    c.bezierCurveTo(-p.hw * .3, cy - p.hh - 52, -p.hw * .9, cy - p.hh - 30, -p.hw - 6, cy - p.hh * .52); c.closePath(); c.fillStyle = '#f7f5ef'; c.fill(); O(5);
    c.beginPath(); c.moveTo(-p.hw - 2, cy - p.hh * .52 - 30); c.quadraticCurveTo(0, cy - p.hh * .52 - 40, p.hw + 2, cy - p.hh * .52 - 30); c.strokeStyle = '#b9b3a3'; c.lineWidth = 5; c.stroke();
    c.beginPath(); c.moveTo(-10, cy - p.hh - 48); c.lineTo(-30, cy - p.hh * .52 - 36); c.strokeStyle = '#cfc9ba'; c.lineWidth = 4; c.stroke();
    c.restore();
    c.beginPath(); c.moveTo(-p.hw + 4, cy - p.hh * .5); c.quadraticCurveTo(-p.hw - 2, cy - 20, -p.hw + 6, cy - 10); c.strokeStyle = '#555'; c.lineWidth = 8; c.stroke();
    c.beginPath(); c.moveTo(p.hw - 4, cy - p.hh * .5); c.quadraticCurveTo(p.hw + 2, cy - 20, p.hw - 6, cy - 10); c.stroke();
  } else if (p.head === 'saree') {
    c.beginPath(); c.moveTo(-p.hw * .35, cy - p.hh * .78); c.quadraticCurveTo(0, cy - p.hh * .9, p.hw * .35, cy - p.hh * .78); c.lineTo(p.hw * .5, cy - p.hh * .55); c.quadraticCurveTo(0, cy - p.hh * .72, -p.hw * .5, cy - p.hh * .55); c.closePath(); c.fillStyle = '#1e1714'; c.fill();
    c.beginPath(); c.moveTo(-300, 400); c.bezierCurveTo(-280, 200, -p.hw - 50, 120, -p.hw - 30, cy - 20); c.bezierCurveTo(-p.hw - 30, cy - p.hh - 70, p.hw + 30, cy - p.hh - 70, p.hw + 30, cy - 20);
    c.bezierCurveTo(p.hw + 50, 120, 280, 200, 300, 400); c.lineTo(230, 400); c.bezierCurveTo(220, 240, p.hw + 10, 160, p.hw + 4, cy + 10);
    c.bezierCurveTo(p.hw * .85, cy - p.hh * .5, p.hw * .5, cy - p.hh * .82, 0, cy - p.hh * .84); c.bezierCurveTo(-p.hw * .5, cy - p.hh * .82, -p.hw * .85, cy - p.hh * .5, -p.hw - 4, cy + 10);
    c.bezierCurveTo(-p.hw - 10, 160, -220, 240, -230, 400); c.closePath(); c.fillStyle = p.top; c.fill(); O(5);
    c.beginPath(); c.moveTo(-p.hw - 4, cy + 10); c.bezierCurveTo(-p.hw * .85, cy - p.hh * .5, -p.hw * .5, cy - p.hh * .82, 0, cy - p.hh * .84); c.bezierCurveTo(p.hw * .5, cy - p.hh * .82, p.hw * .85, cy - p.hh * .5, p.hw + 4, cy + 10);
    c.strokeStyle = p.border; c.lineWidth = 14; c.stroke();
    c.beginPath(); c.moveTo(-230, 400); c.bezierCurveTo(-220, 240, -p.hw - 10, 160, -p.hw - 4, cy + 10); c.stroke(); c.beginPath(); c.moveTo(230, 400); c.bezierCurveTo(220, 240, p.hw + 10, 160, p.hw + 4, cy + 10); c.stroke();
    c.strokeStyle = 'rgba(80,60,30,.25)'; c.lineWidth = 5; for (let i = 0; i < 5; i++) { c.beginPath(); c.moveTo(130 + i * 25, 120 + i * 10); c.quadraticCurveTo(170 + i * 20, 250, 160 + i * 25, 400); c.stroke(); }
  }
  // brows
  c.strokeStyle = p.brow; c.lineWidth = 10;
  for (const s of [-1, 1]) { c.beginPath(); c.moveTo(s * 18, cy - 32); c.quadraticCurveTo(s * 45, cy - 48 - p.smile * 4, s * 74, cy - 34); c.stroke(); }
  // eyes
  for (const s of [-1, 1]) {
    const ex = s * 44, ey = cy + 2;
    c.beginPath(); c.moveTo(ex - 24, ey); c.quadraticCurveTo(ex, ey - 17, ex + 24, ey); c.quadraticCurveTo(ex, ey + 12, ex - 24, ey); c.fillStyle = '#f4ecdc'; c.fill();
    c.save(); c.clip(); c.beginPath(); c.arc(ex + 1, ey - 1, 11, 0, 7); c.fillStyle = '#2a1608'; c.fill(); c.beginPath(); c.arc(ex + 1, ey - 1, 5, 0, 7); c.fillStyle = '#000'; c.fill(); c.restore();
    c.beginPath(); c.arc(ex + 5, ey - 5, 3, 0, 7); c.fillStyle = '#fff'; c.fill();
    c.beginPath(); c.moveTo(ex - 26, ey + 1); c.quadraticCurveTo(ex, ey - 19, ex + 25, ey - 1); c.strokeStyle = ink; c.lineWidth = 5; c.stroke();
    c.beginPath(); c.moveTo(ex - 18, ey + 11); c.quadraticCurveTo(ex, ey + 15, ex + 17, ey + 8); c.strokeStyle = skinD; c.lineWidth = 3; c.stroke();
    if (p.age > .5) { c.beginPath(); c.moveTo(ex + s * 28, ey + 2); c.lineTo(ex + s * 38, ey + 8); c.moveTo(ex + s * 27, ey - 4); c.lineTo(ex + s * 38, ey - 6); c.strokeStyle = skinD; c.lineWidth = 2.5; c.stroke(); }
  }
  // nose
  c.beginPath(); c.moveTo(-8, cy + 2); c.quadraticCurveTo(-6, cy + 40, -20, cy + 58); c.quadraticCurveTo(-4, cy + 68, 0, cy + 62); c.quadraticCurveTo(6, cy + 68, 20, cy + 58); c.strokeStyle = ink; c.lineWidth = 4; c.stroke();
  c.fillStyle = 'rgba(60,25,10,.35)'; c.beginPath(); c.ellipse(10, cy + 34, 10, 22, 0, 0, 7); c.fill();
  // mouth
  const my = cy + 92;
  c.beginPath(); c.moveTo(-34, my); c.quadraticCurveTo(0, my + 10 + p.smile * 14, 34, my); c.quadraticCurveTo(0, my + 4, -34, my); c.fillStyle = shade(p.skin, .6); c.fill();
  c.beginPath(); c.moveTo(-36, my - 1 - p.smile * 4); c.quadraticCurveTo(0, my + 6 + p.smile * 10, 36, my - 1 - p.smile * 4); c.strokeStyle = ink; c.lineWidth = 4; c.stroke();
  c.beginPath(); c.moveTo(-22, my + 18); c.quadraticCurveTo(0, my + 26, 22, my + 18); c.strokeStyle = skinD; c.lineWidth = 3; c.stroke();
  if (p.age > .4) { c.strokeStyle = skinD; c.lineWidth = 3; for (const s of [-1, 1]) { c.beginPath(); c.moveTo(s * 30, cy + 54); c.quadraticCurveTo(s * 50, cy + 80, s * 46, my + 12); c.stroke(); } }
  if (p.age > .6) { c.strokeStyle = 'rgba(80,40,20,.35)'; c.lineWidth = 3; for (let i = 0; i < 2; i++) { c.beginPath(); c.moveTo(-50, cy - 70 - i * 14); c.quadraticCurveTo(0, cy - 78 - i * 14, 50, cy - 70 - i * 14); c.stroke(); } }
  if (p.mustache) { c.beginPath(); c.moveTo(-4, my - 22); c.bezierCurveTo(-30, my - 26, -46, my - 12, -44, my - 2); c.bezierCurveTo(-30, my - 8, -12, my - 8, 0, my - 10); c.bezierCurveTo(12, my - 8, 30, my - 8, 44, my - 2); c.bezierCurveTo(46, my - 12, 30, my - 26, 4, my - 22); c.closePath(); c.fillStyle = p.hair || '#222'; c.fill(); }
  if (p.bindi) { c.beginPath(); c.arc(0, cy - 44, 8, 0, 7); c.fillStyle = '#b3121b'; c.fill(); }
  if (p.glasses) {
    c.strokeStyle = '#141414'; c.lineWidth = 7;
    for (const s of [-1, 1]) { c.beginPath(); c.ellipse(s * 45, cy + 2, 33, 27, 0, 0, 7); c.stroke(); c.fillStyle = 'rgba(255,255,255,.08)'; c.fill(); }
    c.beginPath(); c.moveTo(-12, cy - 4); c.quadraticCurveTo(0, cy - 12, 12, cy - 4); c.stroke();
    c.beginPath(); c.moveTo(-78, cy - 4); c.lineTo(-p.hw + 2, cy - 8); c.moveTo(78, cy - 4); c.lineTo(p.hw - 2, cy - 8); c.stroke();
  }
  c.restore();
}

export function portraitTex(p, w = 512, h = 600) {
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  drawPortrait(cv.getContext('2d'), w, h, p);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}

// ---------- 3D face decal (features only, transparent) ----------
function faceTex(p) {
  const S = 512, cv = document.createElement('canvas'); cv.width = cv.height = S; const c = cv.getContext('2d');
  const ink = '#1d0f07', skinD = shade(p.skin, .7);
  c.lineCap = 'round'; c.lineJoin = 'round';
  const cx = S / 2, eyeY = 205, browY = 165, noseY = 285, mouthY = 352;
  c.strokeStyle = p.brow; c.lineWidth = 12;
  for (const s of [-1, 1]) { c.beginPath(); c.moveTo(cx + s * 26, browY + 4); c.quadraticCurveTo(cx + s * 58, browY - 10, cx + s * 92, browY + 4); c.stroke(); }
  for (const s of [-1, 1]) {
    const ex = cx + s * 60;
    c.beginPath(); c.moveTo(ex - 26, eyeY); c.quadraticCurveTo(ex, eyeY - 18, ex + 26, eyeY); c.quadraticCurveTo(ex, eyeY + 13, ex - 26, eyeY); c.fillStyle = '#efe4d0'; c.fill();
    c.save(); c.clip(); c.beginPath(); c.arc(ex, eyeY - 1, 12, 0, 7); c.fillStyle = '#20100a'; c.fill(); c.restore();
    c.beginPath(); c.arc(ex + 4, eyeY - 5, 3.5, 0, 7); c.fillStyle = '#fff'; c.fill();
    c.beginPath(); c.moveTo(ex - 28, eyeY + 1); c.quadraticCurveTo(ex, eyeY - 20, ex + 27, eyeY - 1); c.strokeStyle = ink; c.lineWidth = 6; c.stroke();
  }
  c.strokeStyle = skinD; c.lineWidth = 6;
  c.beginPath(); c.moveTo(cx - 6, eyeY + 10); c.quadraticCurveTo(cx - 4, noseY - 20, cx - 20, noseY); c.quadraticCurveTo(cx, noseY + 12, cx + 20, noseY); c.stroke();
  c.beginPath(); c.moveTo(cx - 40, mouthY - 2); c.quadraticCurveTo(cx, mouthY + 10 + p.smile * 14, cx + 40, mouthY - 2); c.quadraticCurveTo(cx, mouthY + 4, cx - 40, mouthY - 2); c.fillStyle = shade(p.skin, .55); c.fill();
  c.beginPath(); c.moveTo(cx - 42, mouthY - 2 - p.smile * 4); c.quadraticCurveTo(cx, mouthY + 8 + p.smile * 10, cx + 42, mouthY - 2 - p.smile * 4); c.strokeStyle = ink; c.lineWidth = 5; c.stroke();
  if (p.age > .4) { c.strokeStyle = skinD; c.lineWidth = 4; for (const s of [-1, 1]) { c.beginPath(); c.moveTo(cx + s * 34, noseY - 6); c.quadraticCurveTo(cx + s * 58, noseY + 30, cx + s * 52, mouthY + 14); c.stroke(); } }
  if (p.mustache) { const my = mouthY; c.beginPath(); c.moveTo(cx - 4, my - 26); c.bezierCurveTo(cx - 36, my - 30, cx - 54, my - 14, cx - 52, my - 2); c.bezierCurveTo(cx - 36, my - 10, cx - 14, my - 10, cx, my - 12); c.bezierCurveTo(cx + 14, my - 10, cx + 36, my - 10, cx + 52, my - 2); c.bezierCurveTo(cx + 54, my - 14, cx + 36, my - 30, cx + 4, my - 26); c.closePath(); c.fillStyle = p.hair || '#1a1a1a'; c.fill(); }
  if (p.bindi) { c.beginPath(); c.arc(cx, browY - 12, 9, 0, 7); c.fillStyle = '#b3121b'; c.fill(); }
  c.fillStyle = 'rgba(190,70,50,.14)'; for (const s of [-1, 1]) { c.beginPath(); c.ellipse(cx + s * 72, noseY + 10, 34, 22, 0, 0, 7); c.fill(); }
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}

// ---------- 3D character ----------
const V2 = (x, y) => new THREE.Vector2(x, y);
export function makeChar(p, { envMap = null, silhouette = false, seated = false } = {}) {
  const mat = (col, o = {}) => silhouette ? new THREE.MeshStandardMaterial({ color: 0x050505, roughness: 1 }) : new THREE.MeshStandardMaterial({ color: col, roughness: .85, ...o });
  const skinM = mat(p.skin, { roughness: .55 }), topM = mat(p.top), botM = mat(p.bottom || p.top), shoeM = mat('#2a1a10', { roughness: .4 });
  const M = (geo, m, x = 0, y = 0, z = 0) => { const o = new THREE.Mesh(geo, m); o.position.set(x, y, z); o.castShadow = true; o.receiveShadow = true; return o; };
  const cap = (r, l) => new THREE.CapsuleGeometry(r, l, 6, 16);
  const g = new THREE.Group(), hips = new THREE.Group(); hips.position.y = .95; g.add(hips);
  { const pv = M(cap(.15, .08), botM); pv.scale.z = .7; hips.add(pv); }
  const torso = new THREE.Group(); hips.add(torso);
  const lathe = (pts, m, sz = .72) => { m.side = THREE.DoubleSide; const o = M(new THREE.LatheGeometry(pts.map(([x, y]) => V2(x, y)), 32), m); o.scale.z = sz; return o; };
  torso.add(lathe([[.0, -.06], [.17, -.06], [.19, .12], [.21, .36], [.235, .5], [.2, .58], [.1, .64], [.05, .66]], topM));
  if (p.jacket) {
    const jm = mat(p.jacket); const j = lathe([[.0, -.02], [.18, -.02], [.2, .14], [.222, .36], [.245, .5], [.205, .58], [.12, .62], [.0, .62]], jm, .74); torso.add(j);
    torso.add(M(new THREE.BoxGeometry(.06, .5, .02), topM, 0, .3, .172));
  }
  if (p.tie) {
    torso.add(M(new THREE.BoxGeometry(.12, .2, .02), mat(p.shirt), 0, .5, .168));
    const tie = M(new THREE.BoxGeometry(.045, .3, .015), mat(p.tie), 0, .42, .18); torso.add(tie);
  }
  // skirt (kurta hem / saree) hangs from hips
  let skirt = null;
  if (p.head === 'saree') skirt = lathe([[.2, .1], [.24, -.2], [.3, -.6], [.36, -.93], [0, -.93]], topM, .85);
  else if (!p.tie) skirt = lathe([[.19, .02], [.22, -.2], [.25, -.42], [.0, -.42]], topM, .8);
  if (skirt) { hips.add(skirt); if (p.border) { const b = M(new THREE.TorusGeometry(.355, .02, 6, 40), mat(p.border)); b.rotation.x = Math.PI / 2; b.scale.y = .85; b.position.y = -.9; hips.add(b); } }
  torso.add(M(new THREE.CylinderGeometry(.055, .065, .12), skinM, 0, .68));
  // head
  const head = new THREE.Group(); head.position.y = .82; torso.add(head);
  const hs = new THREE.Vector3(1, 1.15, 1.05);
  const skull = M(new THREE.SphereGeometry(.13, 32, 24), skinM); skull.scale.copy(hs); head.add(skull);
  if (!silhouette) {
    const Lp = Math.PI * .9;
    const face = new THREE.Mesh(new THREE.SphereGeometry(.1336, 48, 32, Math.PI / 2 - Lp / 2, Lp, .22 * Math.PI, .58 * Math.PI),
      new THREE.MeshStandardMaterial({ map: faceTex(p), transparent: true, roughness: .6, polygonOffset: true, polygonOffsetFactor: -2 }));
    face.scale.copy(hs); head.add(face);
    const nose = M(new THREE.SphereGeometry(.022, 12, 10), skinM, 0, -.012, .138); nose.scale.set(.9, 1.3, 1); head.add(nose);
  }
  for (const s of [-1, 1]) { const e = M(new THREE.SphereGeometry(.03, 10, 8), skinM, s * .13, 0, -.005); e.scale.set(.5, 1.1, .9); head.add(e); }
  if (p.head === 'hair') { const hr = M(new THREE.SphereGeometry(.139, 32, 16, 0, Math.PI * 2, 0, Math.PI * .45), mat(p.hair, { roughness: .9 })); hr.scale.copy(hs); hr.rotation.x = -.42; hr.position.y = .005; head.add(hr); }
  if (p.head === 'cap') {
    const geo = new THREE.BoxGeometry(.27, .1, .27, 1, 4, 1); const pa = geo.attributes.position;
    for (let i = 0; i < pa.count; i++) { const y = pa.getY(i); const k = 1 - .85 * Math.max(0, Math.min(1, (y + .05) / .1)) ** 1.3; pa.setX(i, pa.getX(i) * k); }
    geo.computeVertexNormals();
    const capM = M(geo, mat('#f7f5ef', { roughness: .95 }), 0, .128, -.012); capM.rotation.x = -.12; capM.rotation.z = .04; head.add(capM);
    const hr = M(new THREE.SphereGeometry(.137, 24, 12, 0, Math.PI * 2, Math.PI * .3, Math.PI * .3), mat('#4a4a4a')); hr.scale.copy(hs); hr.rotation.x = -1.2; head.add(hr);
  }
  if (p.head === 'saree') {
    const sm = mat(p.top, { side: THREE.DoubleSide });
    const hood = M(new THREE.SphereGeometry(.152, 32, 16, 0, Math.PI * 2, 0, Math.PI * .58), sm); hood.scale.set(1.05, 1.15, 1.08); hood.rotation.x = -.62; hood.position.set(0, .01, -.012); head.add(hood);
    const drape = M(new THREE.CylinderGeometry(.14, .22, .55, 24, 1, true, Math.PI * .55, Math.PI * .9), sm, 0, -.24, -.04); head.add(drape);
    const rim = M(new THREE.TorusGeometry(.155, .012, 6, 40, Math.PI * 1.1), mat(p.border)); rim.rotation.set(-.62 + Math.PI / 2, 0, -Math.PI * .05 + Math.PI * -.0); rim.position.set(0, .02, .02); rim.rotation.z = -Math.PI * .05 + Math.PI; head.add(rim);
  }
  if (p.glasses && !silhouette) {
    const gm = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: .3, metalness: .5 });
    for (const s of [-1, 1]) { const r = M(new THREE.TorusGeometry(.033, .006, 8, 24), gm, s * .05, .022, .146); head.add(r); }
    const br = M(new THREE.CylinderGeometry(.004, .004, .03), gm, 0, .028, .15); br.rotation.z = Math.PI / 2; head.add(br);
  }
  // limbs
  const legs = [], arms = [];
  for (const s of [1, -1]) {
    const hip = new THREE.Group(); hip.position.set(s * .095, -.05, 0); hips.add(hip);
    hip.add(M(cap(.078, .3), botM, 0, -.22));
    const knee = new THREE.Group(); knee.position.y = -.44; hip.add(knee);
    knee.add(M(cap(.066, .3), botM, 0, -.2));
    const foot = M(new THREE.BoxGeometry(.11, .07, .26), shoeM, 0, -.44, .06); knee.add(foot);
    legs.push({ hip, knee });
    const sh = new THREE.Group(); sh.position.set(s * .255, .55, 0); torso.add(sh);
    sh.add(M(cap(.07, .22), topM, 0, -.15));
    const el = new THREE.Group(); el.position.y = -.31; sh.add(el);
    el.add(M(cap(.054, .19), p.tie ? topM : (p.head === 'saree' ? skinM : topM), 0, -.13));
    el.add(M(new THREE.SphereGeometry(.05, 12, 10), skinM, 0, -.29));
    arms.push({ sh, el });
  }
  g.scale.setScalar(p === PEOPLE.shastri ? .93 : 1);
  const api = {
    g, head, torso, hips, arms, legs, skirt,
    walk(t, period = 1.1) {
      const ph = t / period * Math.PI * 2;
      legs.forEach((l, i) => { const q = ph + i * Math.PI; l.hip.rotation.x = -.42 * Math.sin(q); l.knee.rotation.x = .85 * Math.max(0, Math.sin(q - 1.1)) ** 1.5 + .05; });
      arms.forEach((a, i) => { const q = ph + (1 - i) * Math.PI; a.sh.rotation.x = .35 * Math.sin(q); a.sh.rotation.z = (i ? -1 : 1) * .05; a.el.rotation.x = -.3; });
      hips.position.y = .95 + .03 * Math.cos(2 * ph); torso.rotation.y = -.1 * Math.sin(ph); hips.rotation.x = 0;
    },
    stand(bow = 0, armX = .05, elX = -.15) {
      legs.forEach(l => { l.hip.rotation.x = 0; l.knee.rotation.x = .02; });
      arms.forEach((a, i) => { a.sh.rotation.x = armX; a.sh.rotation.z = (i ? -1 : 1) * .07; a.el.rotation.x = elX; });
      torso.rotation.x = bow * .6; head.rotation.x = bow; hips.position.y = .95;
    },
    sit(lean = .1) {
      hips.position.y = .55; legs.forEach(l => { l.hip.rotation.x = -Math.PI / 2; l.knee.rotation.x = Math.PI / 2; });
      if (skirt && p.head !== 'saree') skirt.visible = false;
      torso.rotation.x = lean; arms.forEach((a, i) => { a.sh.rotation.x = -.9; a.sh.rotation.z = (i ? -1 : 1) * .12; a.el.rotation.x = -.7; });
    },
  };
  if (seated) api.sit(); else api.stand();
  return api;
}
