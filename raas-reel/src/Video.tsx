import React, {useState} from 'react';
import {AbsoluteFill, Audio, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';
import voice from './voice.json';
import {SCENES} from './scenes';
import {Defs, INK, Overlay, YEL, prog} from './parts';

type Word = {w: string; s: number; e: number};
const LEAD = 8;
const TAIL = 12;
const LAST_HOLD = 55;
const lens = voice.map((v, i) => LEAD + Math.ceil(v.dur * 30) + (i === voice.length - 1 ? LAST_HOLD : TAIL));
const starts = lens.map((_, i) => lens.slice(0, i).reduce((a, b) => a + b, 0));
export const TOTAL = lens.reduce((a, b) => a + b, 0);

const wordFrame = (i: number) => (k: number) => {
  const ws = voice[i].words as Word[];
  return LEAD + Math.round(ws[Math.min(k, ws.length - 1)].s * 30);
};

const fontHandle = {h: 0};
const useFonts = () => {
  useState(() => {
    const h = delayRender('fonts');
    Promise.all([
      new FontFace('Luckiest', `url(${staticFile('LuckiestGuy-Regular.ttf')})`).load(),
      new FontFace('Lilita', `url(${staticFile('LilitaOne-Regular.ttf')})`).load(),
    ]).then((fs) => { fs.forEach((x) => (document.fonts as any).add(x)); continueRender(h); });
    fontHandle.h = h;
    return h;
  });
};

const Scene: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame();
  const def = SCENES[i];
  const w = wordFrame(i);
  const amp = def.impacts.reduce((a, k) => (f >= w(k) ? a + 22 * Math.exp(-(f - w(k)) / 5) : a), 0);
  const punch = interpolate(spring({frame: f, fps: 30, config: {damping: 14}}), [0, 1], [1.12, 1]);
  const zoom = punch * (1 + 0.05 * f / lens[i]);
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1080 1920" width={1080} height={1920}>
        <Defs f={f} />
        <g transform={`translate(${540 + Math.sin(f * 3.1) * amp} ${960 + Math.cos(f * 2.7) * amp}) scale(${zoom}) translate(-540 -960)`}>
          <def.C f={f} w={w} end={lens[i]} />
        </g>
        <Overlay />
      </svg>
    </AbsoluteFill>
  );
};

// Caption groups: up to 3 words, broken at punctuation.
const groups = voice.map((v) => {
  const out: Word[][] = []; let cur: Word[] = [];
  (v.words as Word[]).forEach((wd) => {
    cur.push(wd);
    if (cur.length === 3 || /[.,!?]$/.test(wd.w)) { out.push(cur); cur = []; }
  });
  if (cur.length) out.push(cur);
  return out;
});

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const i = starts.findIndex((s, k) => frame >= s && frame < s + lens[k]);
  if (i < 0) return null;
  const t = (frame - starts[i] - LEAD) / 30;
  const gs = groups[i];
  const gi = gs.findIndex((g, k) => t >= g[0].s - 0.05 && (k === gs.length - 1 ? t < g[g.length - 1].e + 0.35 : t < gs[k + 1][0].s - 0.05));
  if (gi < 0) return null;
  const g = gs[gi];
  const gStart = starts[i] + LEAD + Math.round(g[0].s * 30);
  const p = spring({frame: frame - gStart, fps: 30, config: {damping: 11, stiffness: 200, mass: 0.5}});
  return (
    <div style={{position: 'absolute', top: 1450, left: 50, right: 50, display: 'flex', flexWrap: 'wrap', justifyContent: 'center',
      gap: '0 46px', transform: `scale(${interpolate(p, [0, 1], [0.6, 1])}) rotate(${(gi % 2 ? 1 : -1) * 2}deg)`, opacity: Math.min(1, p * 2)}}>
      {g.map((wd, k) => {
        const active = t >= wd.s - 0.03;
        const now = active && t < wd.e + 0.05;
        return (
          <span key={k} style={{fontFamily: 'Luckiest', fontSize: Math.min(124, 1500 / Math.max(1, wd.w.length)), lineHeight: 1.12, color: active ? (now ? YEL : '#fff') : 'rgba(255,255,255,0.55)',
            WebkitTextStroke: `16px ${INK}`, paintOrder: 'stroke fill', textShadow: `0 12px 0 rgba(29,26,47,0.45)`,
            transform: `scale(${now ? 1.1 : 1}) translateY(${now ? -6 : 0}px)`, display: 'inline-block', letterSpacing: 2}}>
            {wd.w.toUpperCase()}
          </span>
        );
      })}
    </div>
  );
};

const Iris: React.FC = () => {
  const f = useCurrentFrame();
  const R = 1200;
  const b = starts.slice(1).find((B) => f >= B - 9 && f <= B + 11);
  if (b === undefined) return null;
  const ring = (o: number, inn: number, c: string) => (o - inn > 0.5 ? <circle cx={540} cy={960} r={(o + inn) / 2} fill="none" stroke={c} strokeWidth={o - inn} /> : null);
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1080 1920" width={1080} height={1920}>
        {ring(prog(f, b - 9, b - 1) * R, prog(f, b + 2, b + 11) * R, YEL)}
        {ring(prog(f, b - 6, b) * R, prog(f, b, b + 8) * R, '#ff5e62')}
      </svg>
    </AbsoluteFill>
  );
};

const Chrome: React.FC = () => {
  const f = useCurrentFrame();
  const blink = Math.sin(f / 4) > 0;
  const inP = spring({frame: f - 4, fps: 30, config: {damping: 12}});
  return (
    <AbsoluteFill>
      <svg viewBox="0 0 1080 1920" width={1080} height={1920}>
        <rect x={0} y={0} width={1080 * f / TOTAL} height={14} fill={YEL} stroke={INK} strokeWidth={4} />
        <g transform={`translate(540 ${interpolate(inP, [0, 1], [-80, 115])})`}>
          <rect x={-245} y={-42} width={490} height={84} rx={42} fill={INK} />
          <path d="M -210 18 L -185 -24 L -160 18 Z" fill={blink ? YEL : '#ff5e62'} stroke={YEL} strokeWidth={3} strokeLinejoin="round" />
          <text x={30} y={3} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={44} fill="#fff" letterSpacing={3}>PHYSIOLOGY 101</text>
        </g>
      </svg>
    </AbsoluteFill>
  );
};

export const Video: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{backgroundColor: INK}}>
      {SCENES.map((def, i) => (
        <Sequence key={i} from={starts[i]} durationInFrames={lens[i]}>
          <Scene i={i} />
          <Sequence from={LEAD}><Audio src={staticFile(voice[i].file)} /></Sequence>
          {def.sfx.map(([k, name, vol], j) => (
            <Sequence key={j} from={wordFrame(i)(k)}><Audio src={staticFile(`${name}.wav`)} volume={(vol ?? 1) * 0.55} /></Sequence>
          ))}
        </Sequence>
      ))}
      {starts.slice(1).map((B, j) => (
        <Sequence key={'w' + j} from={B - 10}><Audio src={staticFile('whoosh.wav')} volume={0.5} /></Sequence>
      ))}
      <Audio src={staticFile('music.wav')} volume={(f) => interpolate(f, [0, 15, TOTAL - 30, TOTAL], [0, 0.32, 0.32, 0], {extrapolateRight: 'clamp'})} />
      <Iris />
      <Captions />
      <Chrome />
    </AbsoluteFill>
  );
};
