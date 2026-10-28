import React from 'react';
import {Eyes, INK, YEL, pop} from './parts';

export const Tag: React.FC<{text: string; size?: number; fill?: string; color?: string; s?: number}> = ({text, size = 46, fill = '#fff', color = INK, s = 1}) => {
  const w = text.length * size * 0.6 + 64;
  return (
    <g transform={`scale(${s})`} filter="url(#sh)">
      <rect x={-w / 2} y={-size * 0.95} width={w} height={size * 1.9} rx={size * 0.95} fill={fill} stroke={INK} strokeWidth={7} />
      <text textAnchor="middle" dominantBaseline="central" y={3} fontFamily="Luckiest" fontSize={size} fill={color} letterSpacing={2}>{text}</text>
    </g>
  );
};

const KIDNEY = 'M -20 -230 C 150 -250 210 -120 160 -60 C 110 -10 110 30 160 80 C 210 140 140 250 -20 230 C -190 210 -225 60 -222 0 C -220 -90 -170 -220 -20 -230 Z';
export const Kidney: React.FC<{f: number; mood?: 'ok' | 'shock' | 'happy'; siren?: number; hat?: number; s?: number}> = ({f, mood = 'ok', siren = 0, hat = 0, s = 1}) => (
  <g transform={`scale(${s})`}>
    {siren > 0 && (
      <g transform={`translate(-20 -235) scale(${siren})`}>
        <g transform={`rotate(${f * 14})`} opacity={0.35}>
          <path d="M 0 -60 L -260 -380 L -90 -420 Z" fill="#ff3b3b" />
          <path d="M 0 -60 L 260 300 L 90 340 Z" fill="#ff3b3b" />
        </g>
        <rect x={-70} y={-20} width={140} height={34} rx={8} fill="#9aa5b1" stroke={INK} strokeWidth={7} />
        <path d="M -52 -20 C -52 -110 52 -110 52 -20 Z" fill={Math.sin(f / 2) > 0 ? '#ff3b3b' : '#b3121f'} stroke={INK} strokeWidth={7} />
        <ellipse cx={-18} cy={-62} rx={10} ry={18} fill="#fff" opacity={0.7} />
      </g>
    )}
    {hat > 0 && (
      <g transform={`translate(0 ${-30 * (1 - hat)})`} opacity={Math.min(1, hat * 2)} filter="url(#sh)">
        <path d="M -150 -212 C -120 -330 70 -340 120 -232 C 40 -255 -60 -250 -150 -212 Z" fill="#ffcc4d" stroke={INK} strokeWidth={8} strokeLinejoin="round" />
        <Eyes f={f} gap={26} r={10} y={-268} seed={4} />
      </g>
    )}
    <g filter="url(#sh)">
      <path d={KIDNEY} fill="#e8506b" stroke={INK} strokeWidth={10} strokeLinejoin="round" />
      <path d="M -120 -160 C -170 -100 -175 -20 -160 30" fill="none" stroke="#ff8fa3" strokeWidth={22} strokeLinecap="round" />
      <path d="M 110 0 C 160 -10 200 -30 240 -40 M 110 20 C 160 40 200 50 240 70" fill="none" stroke={INK} strokeWidth={10} strokeLinecap="round" />
      <g transform="translate(-50 -20)">
        <Eyes f={f} gap={48} r={mood === 'shock' ? 30 : 24} y={-20} seed={1} />
        <circle cx={-85} cy={30} r={20} fill="#ff2e63" opacity={0.4} />
        <circle cx={85} cy={30} r={20} fill="#ff2e63" opacity={0.4} />
        {mood === 'shock' ? (
          <ellipse cy={55} rx={24} ry={30} fill="#7a1030" stroke={INK} strokeWidth={6} />
        ) : (
          <path d={mood === 'happy' ? 'M -36 40 Q 0 85 36 40 Z' : 'M -28 48 Q 0 66 28 48'} fill={mood === 'happy' ? '#7a1030' : 'none'} stroke={INK} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
        )}
      </g>
    </g>
  </g>
);

const pt = (r: number, a: number) => [r * Math.sin((a * Math.PI) / 180), -r * Math.cos((a * Math.PI) / 180)];
const arc = (r: number, a1: number, a2: number) => {
  const [x1, y1] = pt(r, a1); const [x2, y2] = pt(r, a2);
  return `M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`;
};
export const Gauge: React.FC<{angle: number; r?: number}> = ({angle, r = 260}) => (
  <g filter="url(#sh)">
    <path d={`M ${-r} 40 L ${-r} 0 A ${r} ${r} 0 0 1 ${r} 0 L ${r} 40 Z`} fill="#fff" stroke={INK} strokeWidth={10} strokeLinejoin="round" />
    <path d={arc(r * 0.8, -88, -38)} fill="none" stroke="#ff3b3b" strokeWidth={r * 0.2} />
    <path d={arc(r * 0.8, -38, 38)} fill="none" stroke="#3ccf6e" strokeWidth={r * 0.2} />
    <path d={arc(r * 0.8, 38, 88)} fill="none" stroke="#ff9f1c" strokeWidth={r * 0.2} />
    {[[-63, 'LOW'], [0, 'OK'], [63, 'HIGH']].map(([a, t]) => {
      const [x, y] = pt(r * 0.8, a as number);
      return <text key={t as string} x={x} y={y} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={r * 0.13} fill="#fff"
        stroke={INK} strokeWidth={6} paintOrder="stroke" transform={`rotate(${a} ${x} ${y})`}>{t}</text>;
    })}
    <g transform={`rotate(${angle})`}>
      <path d={`M -16 0 L 0 ${-r * 0.78} L 16 0 Z`} fill={INK} />
    </g>
    <circle r={30} fill="#ff4d6d" stroke={INK} strokeWidth={8} />
    <text y={-r * 0.36} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={r * 0.2} fill={INK}>BP</text>
  </g>
);

export const Vessel: React.FC<{f: number; y: number; h?: number; squeeze?: number; speed?: number; n?: number}> = ({f, y, h = 260, squeeze = 0, speed = 1, n = 9}) => {
  const top = y - h / 2; const bot = y + h / 2; const sq = squeeze * h * 0.32;
  const d = `M -40 ${top} Q 540 ${top + sq * 2} 1120 ${top} L 1120 ${bot} Q 540 ${bot - sq * 2} -40 ${bot} Z`;
  return (
    <g>
      <path d={d} fill="none" stroke={INK} strokeWidth={66} strokeLinejoin="round" />
      <path d={d} fill="none" stroke="#ffc2cf" strokeWidth={48} strokeLinejoin="round" />
      <path d={d} fill="#ff8da1" />
      {Array.from({length: n}, (_, i) => {
        const x = ((f * speed * 7 + i * 137) % 1300) - 110;
        const pinch = 1 - squeeze * 0.6 * Math.exp(-(((x - 540) / 300) ** 2));
        const jy = ((i * 53) % 5 - 2) * h * 0.13 * pinch;
        return (
          <g key={i} transform={`translate(${x} ${y + jy}) rotate(${(i * 37 + f * 2) % 360}) scale(${0.7 + 0.3 * pinch} 1)`}>
            <ellipse rx={38} ry={26} fill="#e0233d" stroke={INK} strokeWidth={6} />
            <ellipse rx={18} ry={11} fill="#b3121f" />
          </g>
        );
      })}
    </g>
  );
};

export const JGCell: React.FC<{f: number; seed?: number; alert?: number}> = ({f, seed = 0, alert = 0}) => (
  <g filter="url(#sh)">
    <circle r={70} fill="#9be15d" stroke={INK} strokeWidth={8} />
    {[[-35, 30], [30, 38], [0, 52], [45, 5], [-48, -5]].map(([x, yy], i) => (
      <circle key={i} cx={x} cy={yy} r={9} fill="#ff9f1c" stroke={INK} strokeWidth={3} />
    ))}
    <Eyes f={f} gap={24} r={alert ? 15 : 12} y={-18} seed={seed} look={0} />
    {alert > 0 && (
      <g transform={`translate(0 ${-115 - Math.abs(Math.sin(f / 3)) * 10}) scale(${alert})`}>
        <text textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={70} fill={YEL} stroke={INK} strokeWidth={10} paintOrder="stroke">!</text>
      </g>
    )}
  </g>
);

export const Renin: React.FC<{f: number; open?: number}> = ({f, open}) => {
  const a = open ?? 14 + 14 * Math.abs(Math.sin(f * 0.5));
  const half = (sgn: number) => (
    <g transform={`rotate(${sgn * a})`}>
      <path d={`M 0 ${-12 * sgn} L 175 ${-4 * sgn} Q 185 0 175 ${6 * sgn} L 0 ${12 * sgn} Z`} fill="#e6edf3" stroke={INK} strokeWidth={6} strokeLinejoin="round" />
      <g transform={`translate(-80 ${-8 * sgn})`}>
        <ellipse rx={50} ry={36} fill="#ff9f1c" stroke={INK} strokeWidth={7} />
        <ellipse rx={24} ry={14} fill="#fff3e0" stroke={INK} strokeWidth={5} />
      </g>
    </g>
  );
  return (
    <g filter="url(#sh)">
      {half(1)}
      {half(-1)}
      <circle r={30} fill="#ff9f1c" stroke={INK} strokeWidth={7} />
      <g transform="translate(-10 -62)"><Eyes f={f} gap={18} r={11} seed={5} /></g>
    </g>
  );
};

export const Liver: React.FC<{f: number}> = ({f}) => (
  <g filter="url(#sh)">
    <path d="M -210 -40 C -200 -150 130 -160 215 -95 C 250 -60 190 40 60 95 C -40 135 -220 80 -210 -40 Z" fill="#b5653a" stroke={INK} strokeWidth={10} strokeLinejoin="round" />
    <path d="M -150 -90 C -60 -125 60 -125 140 -90" fill="none" stroke="#d58a5c" strokeWidth={18} strokeLinecap="round" />
    <Eyes f={f} gap={42} r={20} y={-20} seed={6} />
    <path d="M -24 30 Q 0 52 24 30" fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" />
  </g>
);

export const Lungs: React.FC<{f: number}> = ({f}) => {
  const b = 1 + Math.sin(f / 9) * 0.04;
  const lobe = 'M -35 -120 C -130 -170 -240 -40 -230 120 C -225 210 -120 230 -45 185 C -25 100 -22 0 -35 -120 Z';
  return (
    <g filter="url(#sh)">
      <path d="M -20 -290 L 20 -290 L 20 -150 L 60 -110 L 40 -95 L 0 -130 L -40 -95 L -60 -110 L -20 -150 Z" fill="#ffd6e2" stroke={INK} strokeWidth={8} strokeLinejoin="round" />
      <g transform={`scale(${b})`}>
        <path d={lobe} fill="#ff8fb1" stroke={INK} strokeWidth={10} />
        <path d={lobe} transform="scale(-1 1)" fill="#ff8fb1" stroke={INK} strokeWidth={10} />
        <path d="M -160 -20 C -175 40 -170 100 -140 150" fill="none" stroke="#ffc2d6" strokeWidth={18} strokeLinecap="round" />
      </g>
      <g transform="translate(-125 30)"><Eyes f={f} gap={0.1} r={24} seed={7} /></g>
      <g transform="translate(125 30)"><Eyes f={f} gap={0.1} r={24} seed={7} /></g>
      <path d="M -150 110 Q -125 130 -100 110 M 100 110 Q 125 130 150 110" fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" />
    </g>
  );
};

export const Pac: React.FC<{f: number; r?: number; chomp?: number; label?: string; dead?: number}> = ({f, r = 140, chomp = 1, label = 'ACE', dead = 0}) => {
  const m = ((6 + 32 * Math.abs(Math.sin(f * 0.45)) * chomp) * Math.PI) / 180;
  const ux = -r * Math.cos(m); const uy = -r * Math.sin(m);
  return (
    <g filter="url(#sh)">
      <path d={`M 0 0 L ${ux} ${uy} A ${r} ${r} 0 1 1 ${ux} ${-uy} Z`} fill="#3f6cf5" stroke={INK} strokeWidth={9} strokeLinejoin="round" />
      {dead ? (
        <g transform={`translate(${r * 0.05} ${-r * 0.48})`} stroke={INK} strokeWidth={8} strokeLinecap="round">
          <path d="M -16 -16 L 16 16 M 16 -16 L -16 16" />
        </g>
      ) : (
        <g transform={`translate(${r * 0.05} ${-r * 0.48})`}>
          <circle r={r * 0.15} fill="#fff" stroke={INK} strokeWidth={6} />
          <circle cx={-r * 0.05} r={r * 0.08} fill={INK} />
        </g>
      )}
      <text x={r * 0.25} y={r * 0.38} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={r * 0.38} fill="#fff" stroke={INK} strokeWidth={6} paintOrder="stroke">{label}</text>
    </g>
  );
};

export const BEADS = ['#ff6b6b', '#ffd23f', '#4ecdc4', '#a78bfa', '#ff9f1c', '#3fa9f5', '#ff8fb1', '#7bd389', '#f4a261', '#c084fc', '#9aa5b1', '#9aa5b1', '#9aa5b1', '#9aa5b1'];

// A peptide as a string of beads; bead i keeps its colour through the cascade.
export const Chain: React.FC<{f: number; n: number; from?: number; sp?: number; show?: number; gold?: number; seedOff?: number}> = ({f, n, from = 0, sp = 60, show = 99, gold = 0, seedOff = 0}) => {
  const idx = Array.from({length: n}, (_, k) => from + k);
  const P = idx.map((i, k) => [k * sp, Math.sin(f / 6 + (i + seedOff) * 0.8) * 9]);
  const vis = idx.filter((_, k) => k < show);
  const line = P.slice(0, vis.length).map(([x, y], k) => `${k ? 'L' : 'M'} ${x} ${y}`).join(' ');
  return (
    <g filter="url(#sh)">
      {vis.length > 1 && <path d={line} fill="none" stroke={INK} strokeWidth={10} strokeLinecap="round" />}
      {vis.map((i, k) => {
        const s = Math.min(1, Math.max(0, show - k));
        return (
          <g key={i} transform={`translate(${P[k][0]} ${P[k][1]}) scale(${s})`}>
            {gold > 0 && <circle r={36 + Math.sin(f / 3 + k) * 4} fill={YEL} opacity={0.55 * gold} />}
            <circle r={26} fill={BEADS[i]} stroke={gold > 0.5 ? '#b8860b' : INK} strokeWidth={6} />
            <circle cx={-8} cy={-8} r={7} fill="#fff" opacity={0.6} />
          </g>
        );
      })}
    </g>
  );
};

export const Crown: React.FC<{f: number}> = ({f}) => (
  <g filter="url(#sh)" transform={`rotate(${Math.sin(f / 6) * 8})`}>
    <path d="M -55 0 L -66 -66 L -28 -34 L 0 -82 L 28 -34 L 66 -66 L 55 0 Z" fill={YEL} stroke={INK} strokeWidth={7} strokeLinejoin="round" />
    {[-66, 0, 66].map((x) => <circle key={x} cx={x} cy={x === 0 ? -86 : -70} r={10} fill="#ff4d6d" stroke={INK} strokeWidth={4} />)}
  </g>
);

export const Sparkles: React.FC<{f: number; r?: number; n?: number}> = ({f, r = 260, n = 7}) => (
  <g>
    {Array.from({length: n}, (_, i) => {
      const p = ((f + i * 9) % 30) / 30;
      const a = (i / n) * Math.PI * 2 + i;
      return (
        <path key={i} transform={`translate(${Math.cos(a) * r * (0.6 + p * 0.5)} ${Math.sin(a) * r * 0.5 * (0.6 + p * 0.5)}) scale(${Math.sin(p * Math.PI) * 1.2})`}
          d="M 0 -24 L 7 -7 L 24 0 L 7 7 L 0 24 L -7 7 L -24 0 L -7 -7 Z" fill={YEL} stroke={INK} strokeWidth={3} />
      );
    })}
  </g>
);

export const Salt: React.FC = () => (
  <g filter="url(#sh)">
    <path d="M -30 -20 L 0 -36 L 30 -20 L 0 -4 Z" fill="#ffffff" stroke={INK} strokeWidth={5} strokeLinejoin="round" />
    <path d="M -30 -20 L 0 -4 L 0 32 L -30 16 Z" fill="#dfe8f0" stroke={INK} strokeWidth={5} strokeLinejoin="round" />
    <path d="M 30 -20 L 0 -4 L 0 32 L 30 16 Z" fill="#c4d2de" stroke={INK} strokeWidth={5} strokeLinejoin="round" />
  </g>
);

export const Drop: React.FC<{s?: number}> = ({s = 1}) => (
  <g transform={`scale(${s})`} filter="url(#sh)">
    <path d="M 0 -40 Q 28 0 0 22 Q -28 0 0 -40 Z" fill="#3fa9f5" stroke={INK} strokeWidth={5} />
    <ellipse cx={-7} cy={2} rx={5} ry={9} fill="#fff" opacity={0.7} />
  </g>
);

export const Aldo: React.FC = () => (
  <g filter="url(#sh)">
    <path d="M 26 0 L 13 22 L -13 22 L -26 0 L -13 -22 L 13 -22 Z" fill="#c6f432" stroke={INK} strokeWidth={6} strokeLinejoin="round" />
    <circle r={7} fill={INK} />
  </g>
);

export const Pill: React.FC = () => (
  <g filter="url(#sh)">
    <path d="M 0 -48 L -72 -48 A 48 48 0 0 0 -72 48 L 0 48 Z" fill="#fff" stroke={INK} strokeWidth={8} />
    <path d="M 0 -48 L 72 -48 A 48 48 0 0 1 72 48 L 0 48 Z" fill="#ff4d6d" stroke={INK} strokeWidth={8} />
    <ellipse cx={-70} cy={-22} rx={30} ry={9} fill="#fff" opacity={0.7} />
  </g>
);

export {pop};
