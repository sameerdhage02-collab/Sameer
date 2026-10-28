import React from 'react';
import {interpolate} from 'remotion';
import {Bg, INK, Stamp, Sweat, T, col, pop, prog} from './parts';
import {Aldo, Chain, Crown, Drop, Gauge, JGCell, Kidney, Liver, Lungs, Pac, Pill, Renin, Salt, Sparkles, Tag, Vessel} from './bio';

export type SceneProps = {f: number; w: (i: number) => number; end: number};
export type SceneDef = {C: React.FC<SceneProps>; sfx: [number, string, number?][]; impacts: number[]};

const lerp = (p: number, a: number, b: number) => interpolate(p, [0, 1], [a, b]);
const decay = (f: number, at: number, k = 20) => (f < at ? 0 : Math.exp(-(f - at) / k));
const SP = 58;

// 1 — BP drops; the kidney's alarm goes off.
const S1: React.FC<SceneProps> = ({f, w}) => {
  const g = pop(f, 0, 12);
  const drop = prog(f, w(2), w(4));
  const angle = lerp(drop, 2, -66) + Math.sin(f * 0.9) * (3 + 8 * decay(f, w(4)));
  const k = pop(f, w(5), 10);
  const siren = pop(f, w(10), 9);
  const flash = f >= w(10) && Math.sin(f / 2) > 0;
  return (
    <g>
      <Bg f={f} c1={col(f, w(2), w(4), '#5ec2ff', '#ff6b6b')} c2={col(f, w(2), w(4), '#a8e2ff', '#ffa69e')} />
      {flash && <rect width={1080} height={1920} fill="#ff1f3d" opacity={0.18} />}
      <g transform={`translate(540 600) scale(${g})`}><Gauge angle={angle} r={280} /></g>
      <g transform="translate(800 760)"><Stamp f={f} at={w(4)} text="LOW!" rot={8} size={70} /></g>
      {f >= w(5) && (
        <g transform={`translate(${540 + (siren > 0 ? Math.sin(f * 1.7) * 6 : 0)} ${lerp(k, 1800, 1140)})`}>
          <Kidney f={f} s={0.82} siren={siren} mood={f >= w(10) ? 'shock' : 'ok'} />
          {f >= w(10) && <><Sweat f={f} x={-190} y={-120} s={1.4} /><Sweat f={f} x={170} y={-150} s={1.4} seed={2} /></>}
        </g>
      )}
    </g>
  );
};

// 2 — JG cells in the afferent arteriole sense the drop and release renin.
const S2: React.FC<SceneProps> = ({f, w}) => {
  const v = prog(f, 0, 12);
  const alert = pop(f, w(6), 8);
  const rel = w(10);
  const xs = [200, 420, 660, 880];
  return (
    <g>
      <Bg f={f} c1="#ff9fb2" c2="#ffd0da" cy={1000} />
      <g opacity={v} transform={`translate(${lerp(v, -300, 0)} 0)`}>
        <Vessel f={f} y={620} h={260} speed={0.55} n={6} />
      </g>
      <g transform={`translate(540 390) scale(${pop(f, w(4))})`}><Tag text="AFFERENT ARTERIOLE" size={44} /></g>
      {xs.map((x, i) => (
        <g key={i} transform={`translate(${x} ${800}) scale(${pop(f, w(0) + i * 3)})`}>
          <JGCell f={f} seed={i} alert={f >= w(6) ? alert : 0} />
        </g>
      ))}
      {f < rel + 6 && <g transform={`translate(540 960) scale(${pop(f, w(1)) * (1 - prog(f, rel, rel + 6))})`}><Tag text="JG CELLS" fill="#9be15d" /></g>}
      {f >= rel && xs.map((x, i) => {
        const p = prog(f, rel + i * 3, rel + i * 3 + 18);
        const tx = lerp(p, x, 230 + i * 205);
        const ty = lerp(p, 800, 1090 + (i % 2) * 60);
        return (
          <g key={'r' + i} transform={`translate(${tx} ${ty}) rotate(${90 + Math.sin(f / 5 + i) * 20 + (1 - p) * 360}) scale(${0.2 + p * 0.3})`}>
            <Renin f={f + i * 5} />
          </g>
        );
      })}
      {f >= w(14) && <T x={540} y={1310} size={140} s={pop(f, w(14), 8)} rot={-3} fill="#ff9f1c">RENIN</T>}
    </g>
  );
};

// 3 — Renin cuts angiotensinogen (from the liver) into angiotensin I (10 beads).
const S3: React.FC<SceneProps> = ({f, w}) => {
  const C = w(9);
  const x0 = 165; const y0 = 850;
  const reveal = prog(f, w(2), w(2) + 22) * 14;
  const sIn = prog(f, w(0), w(0) + 14);
  const open = f < C - 8 ? undefined : f < C ? 38 : f < C + 6 ? 2 : undefined;
  const move = prog(f, C + 2, C + 18);
  const rest = prog(f, C + 2, C + 24);
  const cutX = x0 + 9.5 * SP;
  return (
    <g>
      <Bg f={f} c1="#6fd3a0" c2="#b9f0cf" />
      <g transform={`translate(250 520) scale(${pop(f, w(2)) * 0.85})`}><Liver f={f} /></g>
      {f >= w(8) && <g transform={`translate(250 330) scale(${pop(f, w(8))})`}><Tag text="LIVER" fill="#ffd9c2" /></g>}
      {f >= w(2) && (
        <>
          <g transform={`translate(${lerp(move, x0, 540 - 4.5 * SP)} ${lerp(move, y0, 1150)})`}>
            <Chain f={f} n={10} sp={SP} show={Math.min(10, reveal)} />
          </g>
          {reveal > 10 && (
            <g transform={`translate(${x0 + 10 * SP + rest * 300} ${y0 + rest * rest * 500}) rotate(${rest * 50})`} opacity={1 - rest}>
              <Chain f={f} n={4} from={10} sp={SP} show={reveal - 10} />
            </g>
          )}
        </>
      )}
      {f >= w(2) && f < C + 4 && (
        <g transform={`translate(540 1000) scale(${pop(f, w(2)) * (1 - prog(f, C, C + 4))})`}><Tag text="ANGIOTENSINOGEN" size={44} /></g>
      )}
      <g transform={`translate(${lerp(sIn, 1300, cutX)} ${y0 - 215}) rotate(90) scale(0.85)`}>
        <Renin f={f} open={open} />
      </g>
      {f >= C && f < C + 10 && (
        <g transform={`translate(${cutX} ${y0}) scale(${1 + (f - C) * 0.25})`} opacity={1 - (f - C) / 10}>
          {Array.from({length: 8}, (_, i) => (
            <path key={i} transform={`rotate(${i * 45})`} d="M 0 -40 L 0 -80" stroke={INK} strokeWidth={8} strokeLinecap="round" />
          ))}
        </g>
      )}
      {f >= w(10) && <g transform={`translate(540 1290) scale(${pop(f, w(10))})`}><Tag text="ANGIOTENSIN I" size={52} fill="#a78bfa" color="#fff" /></g>}
    </g>
  );
};

// 4 — In the lungs, ACE trims two more: angiotensin II, the power player.
const S4: React.FC<SceneProps> = ({f, w}) => {
  const slide = prog(f, 0, 16);
  const pac = pop(f, w(3), 10);
  const eat = prog(f, w(4), w(4) + 12);
  const gold = prog(f, w(8), w(9) + 6);
  const crown = pop(f, w(11), 8);
  const cx = 230;
  const pacX = f < w(4) ? 910 : interpolate(f, [w(4), w(4) + 8, w(6), w(6) + 10], [910, 830, 830, 910], {extrapolateRight: 'clamp'});
  return (
    <g>
      <Bg f={f} c1="#9b8cff" c2="#c8bfff" />
      <g transform={`translate(540 560) scale(${pop(f, 0, 12) * 0.95})`}><Lungs f={f} /></g>
      <g transform={`translate(${lerp(slide, -700, cx)} 1060)`}>
        {gold > 0 && <g transform={`translate(${3.5 * SP} 0)`}><Sparkles f={f} r={300} n={8} /></g>}
        <Chain f={f} n={10} sp={SP} show={10 - eat * 2} gold={gold} />
        {f >= w(11) && <g transform={`translate(${3.5 * SP} ${-60}) scale(${crown})`}><Crown f={f} /></g>}
      </g>
      {f >= w(3) && <g transform={`translate(${pacX} 1060) scale(${pac})`}><Pac f={f} r={120} chomp={f < w(7) ? 1 : 0.3} /></g>}
      <g transform={`translate(540 1270) scale(${1 - prog(f, w(8) - 4, w(8))})`}><Tag text="ANGIOTENSIN I" size={48} fill="#a78bfa" color="#fff" /></g>
      {f >= w(8) && <g transform={`translate(540 1270) scale(${pop(f, w(8), 9)})`}><Tag text="ANGIOTENSIN II" size={54} fill="#ffd23f" /></g>}
    </g>
  );
};

// 5 — Angiotensin II: squeezes vessels, triggers aldosterone, kidneys keep salt + water.
const S5: React.FC<SceneProps> = ({f, w}) => {
  const boss = pop(f, 0, 12);
  const vIn = prog(f, w(2) - 6, w(2) + 6);
  const sq = prog(f, w(2), w(5));
  const kid = pop(f, w(7), 10);
  const hat = prog(f, w(9), w(10) + 6);
  const KX = 290; const KY = 1150;
  const gulp = [w(20), w(21), w(22), w(22) + 6].reduce((a, t) => a + 0.06 * decay(f, t + 14, 6), 0);
  return (
    <g>
      <Bg f={f} c1="#ffb347" c2="#ffd56b" cy={900} />
      <g transform={`translate(540 300) scale(${boss * 0.72})`}>
        <Sparkles f={f} r={280} n={6} />
        <g transform={`translate(${-3.5 * 60} 0)`}><Chain f={f} n={8} sp={60} gold={1} /></g>
        <g transform="translate(0 -62)"><Crown f={f} /></g>
      </g>
      <g opacity={vIn} transform={`translate(0 ${lerp(vIn, 60, 0)})`}>
        <Vessel f={f} y={640} h={230} squeeze={sq} speed={1.4} n={8} />
        {sq > 0 && [-1, 1].map((d) => (
          <g key={d} transform={`translate(540 ${640 + d * (215 - sq * 30 + Math.sin(f / 2) * 6)}) rotate(${d > 0 ? 180 : 0})`} opacity={Math.min(1, sq * 2)}>
            <path d="M -26 -60 L 26 -60 L 26 -20 L 52 -20 L 0 30 L -52 -20 L -26 -20 Z" fill="#ff4d6d" stroke={INK} strokeWidth={7} strokeLinejoin="round" />
          </g>
        ))}
      </g>
      {f >= w(5) && f < w(9) + 6 && <g transform={`translate(540 855) scale(${pop(f, w(5)) * (1 - prog(f, w(9), w(9) + 6))})`}><Tag text="VASOCONSTRICTION" size={42} /></g>}
      {f >= w(7) && (
        <g transform={`translate(${KX} ${lerp(kid, 1800, KY)}) scale(${1 + gulp})`}>
          <Kidney f={f} s={0.6} hat={hat} mood={f >= w(17) ? 'happy' : 'ok'} />
        </g>
      )}
      {f >= w(12) && Array.from({length: 7}, (_, i) => {
        const p = ((f - w(12) + i * 6) % 34) / 34;
        const dir = i % 2 ? 1 : -1;
        return (
          <g key={i} transform={`translate(${KX - 20 + dir * Math.sin(p * Math.PI) * (120 + i * 12)} ${KY - 200 + p * 200 - Math.sin(p * Math.PI) * 50}) rotate(${f * 4 + i * 40}) scale(${Math.sin(p * Math.PI) * 1.1})`}>
            <Aldo />
          </g>
        );
      })}
      {f >= w(13) && <g transform={`translate(740 990) scale(${pop(f, w(13))})`}><Tag text="ALDOSTERONE" size={46} fill="#c6f432" /></g>}
      {f >= w(20) && [0, 1, 2, 3, 4, 5].map((i) => {
        const t0 = (i < 3 ? w(20) : w(22)) + (i % 3) * 5;
        const p = prog(f, t0, t0 + 16);
        if (f < t0 || p >= 1) return null;
        const sx = 1160; const sy = 1120 + (i % 3) * 90;
        return (
          <g key={i} transform={`translate(${lerp(p, sx, KX + 30)} ${lerp(p, sy, KY) - Math.sin(p * Math.PI) * 120}) scale(${1.3 - p * 0.6})`}>
            {i < 3 ? <Salt /> : <Drop s={1.3} />}
          </g>
        );
      })}
      {f >= w(20) && <g transform={`translate(760 1290) scale(${pop(f, w(20))})`}><Tag text="SALT + WATER" size={44} fill="#9be3ff" /></g>}
    </g>
  );
};

// 6 — BP back to normal; ACE inhibitors block the cascade.
const S6: React.FC<SceneProps> = ({f, w, end}) => {
  const rise = prog(f, w(0), w(4));
  const angle = lerp(rise, -66, 0) + Math.sin(f * 0.9) * 6 * decay(f, w(4), 10);
  const pac = pop(f, w(5), 10);
  const pill = prog(f, w(10), w(11));
  const blocked = f >= w(11);
  const tag = pop(f, end - 40, 12);
  return (
    <g>
      <Bg f={f} c1={col(f, w(1), w(4), '#ff8a80', '#4fd17f')} c2={col(f, w(1), w(4), '#ffc2bb', '#b5f2c8')} />
      <g transform="translate(540 540) scale(0.85)"><Gauge angle={angle} r={280} /></g>
      {f >= w(4) && <g transform={`translate(540 660) scale(${pop(f, w(4))})`}><Tag text="NORMAL" fill="#4fd17f" color="#fff" /></g>}
      {f >= w(5) && (
        <g transform={`translate(${600 + (blocked ? Math.sin(f * 2) * 4 * decay(f, w(11)) * 5 : 0)} 1060) scale(${pac})`}>
          <Pac f={f} r={140} chomp={blocked ? 0.25 : 1} dead={blocked ? 1 : 0} />
        </g>
      )}
      {f >= w(10) && (
        <g transform={`translate(${lerp(pill, 1250, 440)} ${lerp(pill, 700, 1060) - Math.sin(pill * Math.PI) * 120}) rotate(${lerp(pill, -200, 0)})`}>
          <Pill />
        </g>
      )}
      {f >= w(11) && <g transform={`translate(540 860) scale(${pop(f, w(11), 9)})`}><Tag text="ACE INHIBITOR" size={50} fill="#ff4d6d" color="#fff" /></g>}
      <g transform="translate(540 1270)"><Stamp f={f} at={w(12)} text="BLOCKED" rot={-6} size={70} /></g>
      {f >= end - 40 && (
        <g transform={`translate(540 1600) scale(${tag})`}>
          <rect x={-340} y={-50} width={680} height={100} rx={50} fill={INK} filter="url(#sh)" />
          <text textAnchor="middle" dominantBaseline="central" y={4} fontFamily="Luckiest" fontSize={48} fill="#ffd23f" letterSpacing={2}>RAAS · KIDNEY PHYSIOLOGY</text>
        </g>
      )}
    </g>
  );
};

export const SCENES: SceneDef[] = [
  {C: S1, sfx: [[0, 'pop'], [2, 'whoosh', 0.5], [4, 'boom'], [5, 'pop'], [10, 'boing'], [11, 'ding', 0.6]], impacts: [4, 10]},
  {C: S2, sfx: [[0, 'pop'], [4, 'pop', 0.6], [6, 'boing'], [10, 'whoosh', 0.6], [14, 'boom', 0.8]], impacts: [14]},
  {C: S3, sfx: [[0, 'whoosh', 0.5], [2, 'pop'], [8, 'pop', 0.6], [9, 'boom'], [10, 'ding', 0.6]], impacts: [9]},
  {C: S4, sfx: [[0, 'whoosh', 0.4], [3, 'pop'], [4, 'boing'], [8, 'ding'], [11, 'boom', 0.8]], impacts: [11]},
  {C: S5, sfx: [[0, 'ding', 0.5], [2, 'whoosh', 0.5], [5, 'pop'], [7, 'pop'], [9, 'boing'], [13, 'pop'], [20, 'pop'], [22, 'pop']], impacts: [2]},
  {C: S6, sfx: [[0, 'whoosh', 0.4], [4, 'ding'], [5, 'pop'], [10, 'whoosh', 0.6], [11, 'boom'], [12, 'boom', 0.7]], impacts: [11, 12]},
];
