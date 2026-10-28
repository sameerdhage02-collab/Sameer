import React from 'react';
import {Easing, interpolate, interpolateColors, spring} from 'remotion';

export const INK = '#1d1a2f';
export const YEL = '#ffd23f';
export const FPS = 30;

const ease = Easing.bezier(0.2, 0.8, 0.2, 1);
export const prog = (f: number, a: number, b: number) =>
  interpolate(f, [a, b], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
export const pop = (f: number, at: number, damping = 10) =>
  spring({frame: f - at, fps: FPS, config: {damping, stiffness: 170, mass: 0.6}});
export const col = (f: number, a: number, b: number, c1: string, c2: string) =>
  interpolateColors(prog(f, a, b), [0, 1], [c1, c2]);

// Hard cartoon drop shadow + animated paper grain, defined once per scene SVG.
export const Defs: React.FC<{f: number}> = ({f}) => (
  <defs>
    <filter id="sh" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="12" stdDeviation="0" floodColor={INK} floodOpacity="0.3" />
    </filter>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={Math.floor(f / 2) % 50} />
      <feColorMatrix type="saturate" values="0" />
    </filter>
    <radialGradient id="vig" cx="50%" cy="45%" r="75%">
      <stop offset="60%" stopColor="#000" stopOpacity="0" />
      <stop offset="100%" stopColor="#000" stopOpacity="0.35" />
    </radialGradient>
  </defs>
);

export const Bg: React.FC<{f: number; c1: string; c2: string; cx?: number; cy?: number}> = ({f, c1, c2, cx = 540, cy = 760}) => (
  <g>
    <rect width={1080} height={1920} fill={c1} />
    <g transform={`translate(${cx} ${cy}) rotate(${f * 0.25})`}>
      {Array.from({length: 18}, (_, i) => (
        <path key={i} transform={`rotate(${i * 20})`} d="M 0 0 L -170 -2400 L 170 -2400 Z" fill={c2} opacity={0.35} />
      ))}
    </g>
    <circle cx={cx} cy={cy} r={520} fill={c2} opacity={0.25} />
  </g>
);

export const Overlay: React.FC = () => (
  <g pointerEvents="none">
    <rect width={1080} height={1920} fill="url(#vig)" />
    <rect width={1080} height={1920} filter="url(#grain)" opacity={0.09} style={{mixBlendMode: 'multiply'}} />
  </g>
);

export const T: React.FC<{
  x: number; y: number; size: number; fill?: string; sw?: number; rot?: number; s?: number; children: React.ReactNode; ls?: number;
}> = ({x, y, size, fill = '#fff', sw = 16, rot = 0, s = 1, children, ls = 2}) => (
  <g transform={`translate(${x} ${y}) rotate(${rot}) scale(${s})`} filter="url(#sh)">
    <text textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={size} fill={fill}
      stroke={INK} strokeWidth={sw} paintOrder="stroke" strokeLinejoin="round" letterSpacing={ls}>
      {children}
    </text>
  </g>
);

export const Eyes: React.FC<{f: number; gap: number; r: number; y?: number; look?: number; seed?: number}> = ({f, gap, r, y = 0, look = 0, seed = 0}) => {
  const ph = (f + seed * 37) % 95;
  const blink = ph < 5 ? Math.abs(ph - 2.5) / 2.5 : 1;
  return (
    <g transform={`translate(0 ${y})`}>
      {[-1, 1].map((d) => (
        <g key={d} transform={`translate(${d * gap} 0) scale(1 ${Math.max(0.08, blink)})`}>
          <ellipse rx={r} ry={r * 1.15} fill="#fff" stroke={INK} strokeWidth={6} />
          <circle cx={look * r * 0.4} cy={r * 0.15} r={r * 0.55} fill={INK} />
          <circle cx={look * r * 0.4 - r * 0.2} cy={-r * 0.1} r={r * 0.18} fill="#fff" />
        </g>
      ))}
    </g>
  );
};

export const Sweat: React.FC<{f: number; x: number; y: number; s?: number; seed?: number}> = ({f, x, y, s = 1, seed = 0}) => {
  const p = ((f + seed * 13) % 40) / 40;
  return (
    <g transform={`translate(${x} ${y + p * 70}) scale(${s})`} opacity={1 - p}>
      <path d="M 0 -26 Q 18 4 0 14 Q -18 4 0 -26 Z" fill="#7fd6ff" stroke={INK} strokeWidth={5} />
    </g>
  );
};

export const Sun: React.FC<{f: number; r?: number; shades?: boolean; hot?: number}> = ({f, r = 150, shades = true, hot = 0}) => (
  <g filter="url(#sh)">
    {Array.from({length: 12}, (_, i) => {
      const len = r * 0.42 + Math.sin(f / 5 + i) * r * 0.08;
      return (
        <path key={i} transform={`rotate(${i * 30 + f * 1.2})`}
          d={`M ${-r * 0.17} ${-r * 1.12} L 0 ${-r * 1.12 - len} L ${r * 0.17} ${-r * 1.12} Z`}
          fill={hot ? '#ff7a1a' : '#ffb300'} stroke={INK} strokeWidth={7} strokeLinejoin="round" />
      );
    })}
    <circle r={r} fill={hot ? '#ffb52e' : YEL} stroke={INK} strokeWidth={9} />
    <circle cx={-r * 0.55} cy={r * 0.28} r={r * 0.15} fill="#ff6b6b" opacity={0.6} />
    <circle cx={r * 0.55} cy={r * 0.28} r={r * 0.15} fill="#ff6b6b" opacity={0.6} />
    {shades ? (
      <g>
        <path d={`M ${-r * 0.75} ${-r * 0.22} L ${r * 0.75} ${-r * 0.22}`} stroke={INK} strokeWidth={10} />
        {[-1, 1].map((d) => (
          <g key={d}>
            <path d={`M ${d * r * 0.08} ${-r * 0.28} L ${d * r * 0.62} ${-r * 0.28} Q ${d * r * 0.62} ${r * 0.12} ${d * r * 0.35} ${r * 0.12} Q ${d * r * 0.08} ${r * 0.12} ${d * r * 0.08} ${-r * 0.28} Z`}
              fill={INK} />
            <path d={`M ${d * r * 0.18} ${-r * 0.18} L ${d * r * 0.3} ${-r * 0.18}`} stroke="#fff" strokeWidth={8} strokeLinecap="round" opacity={0.8} />
          </g>
        ))}
      </g>
    ) : (
      <Eyes f={f} gap={r * 0.35} r={r * 0.17} y={-r * 0.15} />
    )}
    <path d={`M ${-r * 0.42} ${r * 0.32} Q 0 ${r * 0.85} ${r * 0.42} ${r * 0.32} Z`} fill="#c2185b" stroke={INK} strokeWidth={7} strokeLinejoin="round" />
  </g>
);

const CLOUD = [[-110, 20, 80], [-30, -40, 105], [80, -20, 90], [140, 35, 65], [20, 45, 90], [-150, 50, 55]];
export const Cloud: React.FC<{f: number; color?: string; face?: 'happy' | 'sad' | 'none'; seed?: number}> = ({f, color = '#fff', face = 'happy', seed = 0}) => (
  <g filter="url(#sh)">
    {CLOUD.map(([x, y, r], i) => <circle key={'o' + i} cx={x} cy={y} r={r} fill={INK} stroke={INK} strokeWidth={18} />)}
    {CLOUD.map(([x, y, r], i) => <circle key={'i' + i} cx={x} cy={y} r={r} fill={color} />)}
    {face !== 'none' && (
      <g transform="translate(0 20)">
        <Eyes f={f} gap={45} r={18} y={-10} seed={seed} />
        {face === 'happy' ? (
          <path d="M -26 30 Q 0 55 26 30" fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" />
        ) : (
          <path d="M -26 48 Q 0 22 26 48" fill="none" stroke={INK} strokeWidth={7} strokeLinecap="round" />
        )}
      </g>
    )}
  </g>
);

export const Thermo: React.FC<{level: number; h?: number; f: number}> = ({level, h = 520, f}) => {
  const lv = Math.max(0, Math.min(1.05, level));
  const wob = Math.sin(f / 3) * 4 * (lv > 0.85 ? 1 : 0);
  return (
    <g filter="url(#sh)">
      <rect x={-55} y={-h} width={110} height={h + 40} rx={55} fill="#fff" stroke={INK} strokeWidth={9} />
      <circle cy={60} r={95} fill="#ff3b3b" stroke={INK} strokeWidth={9} />
      <rect x={-28} y={-lv * (h - 40) + wob} width={56} height={lv * (h - 40) + 70 - wob} rx={28} fill="#ff3b3b" />
      <circle cx={-30} cy={35} r={20} fill="#fff" opacity={0.6} />
      {Array.from({length: 8}, (_, i) => (
        <path key={i} d={`M 55 ${-h + 70 + i * 55} L ${i % 2 ? 80 : 95} ${-h + 70 + i * 55}`} stroke={INK} strokeWidth={7} strokeLinecap="round" />
      ))}
    </g>
  );
};

export const Fan: React.FC<{f: number; speed?: number}> = ({f, speed = 1}) => (
  <g filter="url(#sh)">
    <path d="M -20 120 L -30 330 L 30 330 L 20 120 Z" fill="#9fb3c8" stroke={INK} strokeWidth={8} strokeLinejoin="round" />
    <rect x={-130} y={320} width={260} height={50} rx={25} fill="#5b7a99" stroke={INK} strokeWidth={8} />
    <circle r={185} fill="#dff3ff" stroke={INK} strokeWidth={9} />
    <g transform={`rotate(${f * 38 * speed})`}>
      {[0, 120, 240].map((a) => (
        <path key={a} transform={`rotate(${a})`} d="M 0 0 C 60 -40 150 -60 155 -10 C 150 30 70 30 0 0 Z" fill="#3fa9f5" stroke={INK} strokeWidth={7} />
      ))}
    </g>
    {Array.from({length: 10}, (_, i) => (
      <path key={i} transform={`rotate(${i * 36})`} d="M 0 -45 L 0 -180" stroke={INK} strokeWidth={4} opacity={0.5} />
    ))}
    <circle r={185} fill="none" stroke={INK} strokeWidth={9} />
    <circle r={38} fill="#ff6b6b" stroke={INK} strokeWidth={8} />
  </g>
);

export const Sweater: React.FC = () => (
  <g filter="url(#sh)">
    <path d="M -95 -125 L 0 -185 L 95 -125" fill="none" stroke={INK} strokeWidth={9} strokeLinejoin="round" />
    <path d="M 0 -185 Q 0 -215 22 -215" fill="none" stroke={INK} strokeWidth={9} strokeLinecap="round" />
    <path d="M -95 -115 L -40 -135 Q 0 -100 40 -135 L 95 -115 L 175 -10 L 125 25 L 92 -25 L 92 150 L -92 150 L -92 -25 L -125 25 L -175 -10 Z"
      fill="#e63946" stroke={INK} strokeWidth={9} strokeLinejoin="round" />
    <path d="M -92 30 L -62 5 L -31 30 L 0 5 L 31 30 L 62 5 L 92 30" fill="none" stroke="#fff" strokeWidth={12} strokeLinejoin="round" />
    <path d="M -92 75 L 92 75" stroke="#fff" strokeWidth={10} />
    <rect x={-92} y={125} width={184} height={25} fill="#b71c2c" stroke={INK} strokeWidth={7} />
  </g>
);

export const Calendar: React.FC<{month: string; sub?: string; color?: string; w?: number}> = ({month, sub = '2026', color = '#ff4d6d', w = 380}) => (
  <g filter="url(#sh)">
    <rect x={-w / 2} y={-220} width={w} height={420} rx={36} fill="#fff" stroke={INK} strokeWidth={9} />
    <path d={`M ${-w / 2} -130 L ${-w / 2} -184 Q ${-w / 2} -220 ${-w / 2 + 36} -220 L ${w / 2 - 36} -220 Q ${w / 2} -220 ${w / 2} -184 L ${w / 2} -130 Z`}
      fill={color} stroke={INK} strokeWidth={9} strokeLinejoin="round" />
    {[-1, 1].map((d) => <rect key={d} x={d * 90 - 14} y={-250} width={28} height={70} rx={14} fill="#c9d3dd" stroke={INK} strokeWidth={7} />)}
    <text y={-170} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={44} fill="#fff">{sub}</text>
    <text y={50} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={month.length > 4 ? 92 : 140} fill={INK}>{month}</text>
  </g>
);

export const Snowman: React.FC<{f: number; melt?: number}> = ({f, melt = 0}) => (
  <g filter="url(#sh)">
    <ellipse cy={175} rx={150 + melt * 90} ry={20 + melt * 10} fill="#bfe9ff" stroke={INK} strokeWidth={7} opacity={0.4 + melt * 0.6} />
    <g transform={`translate(0 170) scale(${1 + melt * 0.15} ${1 - melt * 0.55}) translate(0 -170)`}>
      <circle cy={90} r={95} fill="#fff" stroke={INK} strokeWidth={9} />
      <circle cy={-50} r={70} fill="#fff" stroke={INK} strokeWidth={9} />
      <path d="M -70 0 Q 0 30 70 0 L 75 30 Q 0 60 -75 30 Z" fill="#3f8efc" stroke={INK} strokeWidth={7} />
      <g transform="translate(0 -60)">
        <Eyes f={f} gap={24} r={11} y={-12} />
        <path d="M 0 5 L 55 18 L 0 22 Z" fill="#ff8c1a" stroke={INK} strokeWidth={5} strokeLinejoin="round" />
        <path d={melt > 0.3 ? 'M -18 42 Q 0 30 18 42' : 'M -18 34 Q 0 46 18 34'} fill="none" stroke={INK} strokeWidth={6} strokeLinecap="round" />
      </g>
      <rect x={-55} y={-170} width={110} height={70} rx={8} fill={INK} />
      <rect x={-80} y={-110} width={160} height={18} rx={9} fill={INK} />
    </g>
  </g>
);

export const Snowflake: React.FC<{f: number; s?: number; run?: number; sad?: number}> = ({f, s = 1, run = 0, sad = 0}) => {
  const arms = Array.from({length: 6}, (_, i) => i * 60);
  const leg = Math.sin(f * 0.9) * 30 * run;
  const arm = (w: number, c: string) => arms.map((a) => (
    <g key={a + c} transform={`rotate(${a})`}>
      <path d="M 0 0 L 0 -150 M 0 -95 L -38 -128 M 0 -95 L 38 -128" stroke={c} strokeWidth={w} strokeLinecap="round" fill="none" />
    </g>
  ));
  return (
    <g transform={`scale(${s})`} filter="url(#sh)">
      <g transform={`translate(0 120)`}>
        {[-1, 1].map((d) => (
          <path key={d} d={`M ${d * 25} 0 L ${d * 25 + leg * d} 90`} stroke={INK} strokeWidth={14} strokeLinecap="round" />
        ))}
      </g>
      <g transform={`rotate(${f * (run ? 4 : 1)})`}>
        {arm(34, INK)}
        {arm(18, '#e8f8ff')}
      </g>
      <circle r={62} fill="#bfeaff" stroke={INK} strokeWidth={8} />
      <Eyes f={f} gap={22} r={12} y={-10} look={run ? 0.8 : 0} />
      <path d={sad > 0.5 ? 'M -18 32 Q 0 18 18 32' : 'M -18 22 Q 0 38 18 22'} fill="none" stroke={INK} strokeWidth={6} strokeLinecap="round" />
    </g>
  );
};

export const Clock: React.FC<{f: number}> = ({f}) => (
  <g filter="url(#sh)">
    {[-1, 1].map((d) => <circle key={d} cx={d * 50} cy={-78} r={26} fill="#ff4d6d" stroke={INK} strokeWidth={7} />)}
    <circle r={85} fill="#fff" stroke={INK} strokeWidth={9} />
    <path d={`M 0 0 L 0 -58`} stroke={INK} strokeWidth={9} strokeLinecap="round" transform={`rotate(${f * 24})`} />
    <path d={`M 0 0 L 40 0`} stroke={INK} strokeWidth={9} strokeLinecap="round" transform={`rotate(${f * 2})`} />
    <circle r={10} fill={INK} />
  </g>
);

export const IndiaGate: React.FC = () => (
  <g filter="url(#sh)">
    <path d="M -115 0 L -115 -270 L 115 -270 L 115 0 L 52 0 L 52 -150 Q 0 -225 -52 -150 L -52 0 Z" fill="#f2a65a" stroke={INK} strokeWidth={9} strokeLinejoin="round" />
    <rect x={-140} y={-310} width={280} height={44} rx={6} fill="#e08a3c" stroke={INK} strokeWidth={9} />
    <rect x={-70} y={-350} width={140} height={44} rx={6} fill="#f2a65a" stroke={INK} strokeWidth={9} />
    <path d="M -45 -350 Q 0 -400 45 -350 Z" fill="#e08a3c" stroke={INK} strokeWidth={9} />
  </g>
);

export const House: React.FC<{c: string; lit?: boolean; w?: number; h?: number}> = ({c, lit = false, w = 170, h = 170}) => (
  <g filter="url(#sh)">
    <rect x={-w / 2} y={-h} width={w} height={h} fill={c} stroke={INK} strokeWidth={8} />
    <path d={`M ${-w / 2 - 20} ${-h} L 0 ${-h - 85} L ${w / 2 + 20} ${-h} Z`} fill="#c0392b" stroke={INK} strokeWidth={8} strokeLinejoin="round" />
    <rect x={-w / 4 - 22} y={-h + 35} width={44} height={44} rx={6} fill={lit ? YEL : '#9be3ff'} stroke={INK} strokeWidth={6} />
    <rect x={w / 4 - 22} y={-h + 35} width={44} height={44} rx={6} fill={lit ? YEL : '#9be3ff'} stroke={INK} strokeWidth={6} />
    <rect x={-22} y={-62} width={44} height={62} rx={6} fill="#7a4b2a" stroke={INK} strokeWidth={6} />
  </g>
);

export const Heat: React.FC<{f: number; x: number; y: number; n?: number; gap?: number; c?: string}> = ({f, x, y, n = 3, gap = 70, c = '#fff'}) => (
  <g transform={`translate(${x} ${y})`}>
    {Array.from({length: n}, (_, i) => {
      const p = ((f + i * 12) % 36) / 36;
      return (
        <path key={i} transform={`translate(${(i - (n - 1) / 2) * gap} ${-p * 80})`} opacity={Math.sin(p * Math.PI)}
          d="M 0 0 C 20 -20 -20 -40 0 -60 C 20 -80 -20 -100 0 -120" fill="none" stroke={c} strokeWidth={10} strokeLinecap="round" />
      );
    })}
  </g>
);

export const Stamp: React.FC<{f: number; at: number; text: string; color?: string; rot?: number; size?: number}> = ({f, at, text, color = '#ff3b3b', rot = -8, size = 78}) => {
  const p = pop(f, at, 12);
  if (f < at) return null;
  const s = interpolate(p, [0, 1], [2.4, 1]);
  const w = text.length * size * 0.62 + 70;
  return (
    <g transform={`rotate(${rot}) scale(${s})`} opacity={Math.min(1, p * 1.5)} filter="url(#sh)">
      <rect x={-w / 2} y={-size * 0.8} width={w} height={size * 1.6} rx={20} fill={color} stroke={INK} strokeWidth={9} />
      <rect x={-w / 2 + 14} y={-size * 0.8 + 14} width={w - 28} height={size * 1.6 - 28} rx={12} fill="none" stroke="#fff" strokeWidth={5} strokeDasharray="14 10" />
      <text textAnchor="middle" dominantBaseline="central" y={4} fontFamily="Luckiest" fontSize={size} fill="#fff" letterSpacing={3}>{text}</text>
    </g>
  );
};
