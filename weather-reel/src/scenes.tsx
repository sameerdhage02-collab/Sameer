import React from 'react';
import {interpolate} from 'remotion';
import {
  Bg, Calendar, Clock, Cloud, Eyes, Fan, Heat, House, INK, IndiaGate, Snowflake, Snowman, Stamp, Sun, Sweat, Sweater, T, Thermo, YEL,
  col, pop, prog,
} from './parts';

export type SceneProps = {f: number; w: (i: number) => number; end: number};
export type SceneDef = {C: React.FC<SceneProps>; sfx: [number, string, number?][]; impacts: number[]};

const lerp = (p: number, a: number, b: number) => interpolate(p, [0, 1], [a, b]);
const decay = (f: number, at: number, k = 40) => (f < at ? 0 : Math.exp(-(f - at) / k));

const Flame: React.FC<{f: number; s?: number}> = ({f, s = 1}) => (
  <g transform={`scale(${s} ${s * (1 + Math.sin(f * 0.8) * 0.08)})`} filter="url(#sh)">
    <path d="M 0 0 C -70 -30 -45 -120 0 -180 C 10 -120 75 -100 60 -40 C 55 -10 25 0 0 0 Z" fill="#ff5a1f" stroke={INK} strokeWidth={8} strokeLinejoin="round" />
    <path d="M 0 -8 C -30 -20 -20 -70 2 -100 C 8 -70 35 -55 28 -30 C 24 -14 12 -8 0 -8 Z" fill={YEL} />
  </g>
);

// 1 — November, sweaters out? No: the fans are still spinning.
const S1: React.FC<SceneProps> = ({f, w}) => {
  const cal = pop(f, w(0));
  const tear = prog(f, w(2), w(2) + 16);
  const sun = pop(f, w(1), 12);
  const sw = pop(f, w(5), 7);
  const swing = Math.sin((f - w(5)) / 6) * 14 * decay(f, w(5));
  const fan = pop(f, w(10), 9);
  const blow = prog(f, w(13), w(13) + 22);
  const fanSpeed = 0.4 + prog(f, w(10), w(14)) * 1.2;
  return (
    <g>
      <Bg f={f} c1={col(f, w(10), w(15), '#5ec2ff', '#ffa94d')} c2={col(f, w(10), w(15), '#a8e2ff', '#ffd56b')} />
      <g transform={`translate(${lerp(sun, 1300, 870)} ${290 + Math.sin(f / 10) * 14}) rotate(${Math.sin(f / 15) * 8})`}>
        <Sun f={f} r={115} />
      </g>
      <g transform={`translate(470 600) scale(${cal}) rotate(${-4 + Math.sin(f / 14) * 3})`}>
        <Calendar month="NOV" />
        {tear < 1 && (
          <g transform={`translate(${tear * 520} ${-tear * 700}) rotate(${tear * 80})`}>
            <Calendar month="OCT" color="#ff9f1c" />
          </g>
        )}
      </g>
      {f >= w(12) && [0, 1, 2, 3, 4].map((i) => {
        const p = ((f + i * 7) % 20) / 20;
        return (
          <path key={i} d={`M ${640 - p * 520} ${960 + i * 50} l -170 0`} stroke="#fff" strokeWidth={14} strokeLinecap="round"
            opacity={Math.sin(p * Math.PI)} />
        );
      })}
      {f >= w(5) && (
        <g transform={`translate(${290 - blow * 800} ${lerp(sw, -400, 1100) - blow * 250}) rotate(${swing - blow * 260})`}>
          <Sweater />
        </g>
      )}
      <g transform={`translate(800 ${lerp(fan, 1700, 1080)})`}>
        <Fan f={f} speed={fanSpeed} />
      </g>
    </g>
  );
};

const LAND: [number, number, number, number, number][] = [
  [-180, -120, 120, 70, -20], [60, -170, 90, 50, 15], [-60, 150, 140, 60, 10], [240, 90, 80, 110, 0], [-330, 40, 70, 120, 0],
];

// 2 — Blame a super El Niño: the Pacific is running a fever.
const S2: React.FC<SceneProps> = ({f, w}) => {
  const t1 = pop(f, w(2), 8);
  const t2 = pop(f, w(3), 8);
  const g = pop(f, w(5), 11);
  const hot = prog(f, w(10), w(12));
  const fever = prog(f, w(13), w(15) + 10);
  const shift = (f * 2.2) % 900;
  return (
    <g>
      <Bg f={f} c1={col(f, w(10), w(12), '#ff8a5c', '#ff4e50')} c2="#ffc371" cy={1000} />
      {f >= w(2) && <T x={540} y={300} size={160} s={t1} rot={-5} fill={YEL}>SUPER</T>}
      {f >= w(3) && <T x={540} y={470} size={175} s={t2} rot={3}>EL NIÑO</T>}
      {hot > 0 && <Heat f={f} x={540} y={700} n={4} gap={110} />}
      <g transform={`translate(540 990) scale(${g}) rotate(${Math.sin(f / 12) * 3})`}>
        <clipPath id="gc"><circle r={300} /></clipPath>
        <g filter="url(#sh)">
          <circle r={300} fill={col(f, w(10), w(12), '#3fa9f5', '#ff9a62')} stroke={INK} strokeWidth={10} />
        </g>
        <g clipPath="url(#gc)">
          {[0, -900].map((off) => (
            <g key={off} transform={`translate(${shift + off} 0)`}>
              {LAND.map(([x, y, rx, ry, r], i) => (
                <ellipse key={i} cx={x} cy={y} rx={rx} ry={ry} transform={`rotate(${r} ${x} ${y})`} fill="#59c96b" stroke={INK} strokeWidth={7} />
              ))}
              {LAND.map(([x, y, rx, ry, r], i) => (
                <ellipse key={'b' + i} cx={x + 450} cy={-y * 0.8} rx={rx * 0.8} ry={ry} transform={`rotate(${-r} ${x + 450} ${-y * 0.8})`} fill="#59c96b" stroke={INK} strokeWidth={7} />
              ))}
            </g>
          ))}
          <ellipse cx={0} cy={60} rx={260 * hot * (1 + Math.sin(f / 4) * 0.05)} ry={140 * hot} fill="#ff2e2e" opacity={0.75} />
          <ellipse cx={0} cy={60} rx={150 * hot} ry={80 * hot} fill={YEL} opacity={0.6} />
          <ellipse cx={-120} cy={-170} rx={110} ry={55} fill="#fff" opacity={0.25} transform="rotate(-30 -120 -170)" />
        </g>
        <circle r={300} fill="none" stroke={INK} strokeWidth={10} />
        <Eyes f={f} gap={85} r={36} y={-60} look={-0.3} />
        <circle cx={-150} cy={20} r={38} fill="#ff2e63" opacity={0.25 + hot * 0.5} />
        <circle cx={150} cy={20} r={38} fill="#ff2e63" opacity={0.25 + hot * 0.5} />
        {fever > 0 ? (
          <g>
            <ellipse cx={0} cy={95} rx={42} ry={30} fill="#7a1030" stroke={INK} strokeWidth={7} />
            <g transform={`translate(10 95) rotate(${-25 + Math.sin(f / 4) * 4})`}>
              <rect x={0} y={-16} width={230 * Math.min(1, fever * 3)} height={32} rx={16} fill="#fff" stroke={INK} strokeWidth={7} />
              <rect x={0} y={-8} width={(50 + fever * 150) * Math.min(1, fever * 3)} height={16} rx={8} fill="#ff2e2e" />
            </g>
          </g>
        ) : (
          <path d="M -50 80 Q 0 130 50 80" fill="none" stroke={INK} strokeWidth={9} strokeLinecap="round" />
        )}
        {hot > 0.5 && <><Sweat f={f} x={-250} y={-120} s={1.6} /><Sweat f={f} x={260} y={-90} s={1.6} seed={2} /></>}
      </g>
      {hot > 0 && (
        <g transform={`translate(540 1330) scale(${pop(f, w(10))})`}>
          <rect x={-250} y={-48} width={500} height={96} rx={48} fill="#fff" stroke={INK} strokeWidth={8} filter="url(#sh)" />
          <text textAnchor="middle" dominantBaseline="central" y={4} fontFamily="Luckiest" fontSize={56} fill={INK}>PACIFIC OCEAN</text>
        </g>
      )}
    </g>
  );
};

// 3 — The heat bends winds; India's monsoon came up short.
const S3: React.FC<SceneProps> = ({f, w}) => {
  const bend = prog(f, w(2), w(2) + 20);
  const ground = pop(f, w(7), 12);
  const cl = pop(f, w(9), 9);
  const dry = prog(f, w(11), w(13));
  return (
    <g>
      <Bg f={f} c1={col(f, w(11), w(13), '#36b3c9', '#e9a23b')} c2={col(f, w(11), w(13), '#7fe0e8', '#ffd27a')} cy={700} />
      {[260, 370, 480, 590].map((y, i) => {
        const d = `M -120 ${y} C 300 ${y} 520 ${y + bend * 260} 1200 ${y + bend * (i % 2 ? -140 : 200)}`;
        const appear = prog(f, i * 3, i * 3 + 14);
        return (
          <g key={i} opacity={appear}>
            <path d={d} fill="none" stroke={INK} strokeWidth={30} strokeLinecap="round" strokeDasharray="170 90" strokeDashoffset={-f * 16 - i * 60} />
            <path d={d} fill="none" stroke="#fff" strokeWidth={16} strokeLinecap="round" strokeDasharray="170 90" strokeDashoffset={-f * 16 - i * 60} />
          </g>
        );
      })}
      <g transform={`translate(0 ${lerp(ground, 800, 0)})`}>
        <path d="M -20 1270 Q 270 1235 540 1270 T 1100 1270 L 1100 1950 L -20 1950 Z" fill={col(f, w(11), w(13), '#6cc551', '#c9a24a')} stroke={INK} strokeWidth={10} />
        <g transform="translate(540 1275) scale(0.72)"><IndiaGate /></g>
        <g transform="translate(180 1275) scale(0.9)"><House c="#ffcf5c" /></g>
        <g transform="translate(900 1275) scale(0.9)"><House c="#8fd3ff" /></g>
      </g>
      {f >= w(9) && Array.from({length: 12}, (_, i) => {
        const p = ((f * 1.3 + i * 17) % 30) / 30;
        const x = 380 + ((i * 53) % 320);
        return (
          <path key={i} transform={`translate(${x} ${820 + p * 400})`} d="M 0 -22 Q 14 2 0 10 Q -14 2 0 -22 Z"
            fill="#3fa9f5" stroke={INK} strokeWidth={4} opacity={(1 - dry) * Math.min(1, cl) * (i % 3 === 0 || dry < 0.3 ? 1 : 1 - dry * 2)} />
        );
      })}
      <g transform={`translate(${540 + Math.sin(f / 9) * 20} 760) scale(${cl * (1.25 - dry * 0.55)})`}>
        <Cloud f={f} color={col(f, w(11), w(13), '#ffffff', '#c8ced4')} face={dry > 0.5 ? 'sad' : 'happy'} />
      </g>
      <g transform="translate(540 1050)"><Stamp f={f} at={w(12)} text="BELOW NORMAL" size={64} /></g>
    </g>
  );
};

const STARS = Array.from({length: 26}, (_, i) => [(i * 137) % 1040 + 20, (i * 89) % 820 + 160, (i % 3) + 1]);

// 4 — October hotter than normal; even the nights refuse to cool.
const S4: React.FC<SceneProps> = ({f, w}) => {
  const night = prog(f, w(12), w(12) + 16);
  const cal = pop(f, w(1));
  const level = lerp(prog(f, w(3), w(7)), 0.22, 0.97);
  const moon = pop(f, w(14), 9);
  const H = 600;
  const normY = -0.6 * (H - 40);
  return (
    <g>
      <Bg f={f} c1={col(f, w(12), w(12) + 16, '#ff8a3d', '#1b1f4b')} c2={col(f, w(12), w(12) + 16, '#ffc46b', '#3a2c7a')} cx={720} cy={700} />
      {night > 0 && STARS.map(([x, y, s], i) => (
        <path key={i} transform={`translate(${x} ${y}) scale(${s * 0.5 * (0.7 + 0.3 * Math.sin(f / 5 + i))})`}
          d="M 0 -20 L 6 -6 L 20 0 L 6 6 L 0 20 L -6 6 L -20 0 L -6 -6 Z" fill="#fff6b0" opacity={night} />
      ))}
      <g transform={`translate(290 530) scale(${cal * (1 - night)}) rotate(-6)`} opacity={1 - night}>
        <Calendar month="OCT" color="#ff9f1c" w={340} />
        <g transform="translate(150 -230)"><Flame f={f} s={0.7} /></g>
      </g>
      {moon > 0 && (
        <g transform={`translate(290 470) scale(${moon}) rotate(${Math.sin(f / 10) * 6})`} filter="url(#sh)">
          <circle r={140} fill="#fff1a8" stroke={INK} strokeWidth={9} />
          <circle cx={-60} cy={-70} r={22} fill="#f0d76a" />
          <circle cx={70} cy={60} r={16} fill="#f0d76a" />
          <circle cx={-80} cy={40} r={12} fill="#f0d76a" />
          <Eyes f={f} gap={45} r={22} y={-20} seed={3} />
          <ellipse cx={0} cy={55} rx={30} ry={22} fill="#7a1030" stroke={INK} strokeWidth={6} />
          <Sweat f={f} x={-120} y={-60} s={1.3} />
          <Sweat f={f} x={125} y={-30} s={1.3} seed={2} />
          <g transform={`translate(150 90) rotate(${Math.sin(f * 0.9) * 25})`}>
            <path d="M 0 0 L -40 -110 Q 0 -140 40 -110 Z" fill="#ff6b9a" stroke={INK} strokeWidth={7} strokeLinejoin="round" />
          </g>
        </g>
      )}
      <g transform="translate(760 1060)">
        <Thermo level={level} h={H} f={f} />
        <path d={`M -170 ${normY} L 170 ${normY}`} stroke={INK} strokeWidth={8} strokeDasharray="22 14" />
        <g transform={`translate(-200 ${normY})`}>
          <rect x={-150} y={-38} width={180} height={76} rx={38} fill="#fff" stroke={INK} strokeWidth={7} filter="url(#sh)" />
          <text x={-60} textAnchor="middle" dominantBaseline="central" y={3} fontFamily="Luckiest" fontSize={40} fill={INK}>NORMAL</text>
        </g>
        {level > 0.85 && <g transform={`translate(0 ${-H - 10}) scale(${pop(f, w(7))})`}><Flame f={f} s={0.9} /></g>}
      </g>
      {[[150, '#ffcf5c'], [400, '#8fd3ff']].map(([x, c], i) => (
        <g key={i} transform={`translate(${x} 1420) scale(0.85)`}><House c={c as string} lit={night > 0.5} /></g>
      ))}
      {night > 0.3 && <><Heat f={f} x={150} y={1230} n={2} gap={60} c="#ff9a62" /><Heat f={f} x={400} y={1230} n={2} gap={60} c="#ff9a62" /></>}
    </g>
  );
};

const MONTHS = ['JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC', 'JAN', 'FEB'];
const CURVE = [845, 820, 765, 690, 605, 530, 570, 660];

// 5 — El Niño peaks around December, so winter comes late and weak.
const S5: React.FC<SceneProps> = ({f, w}) => {
  const card = pop(f, 0, 12);
  const draw = prog(f, w(0), w(5));
  const flag = pop(f, w(5), 8);
  const runIn = prog(f, w(9), w(11) + 6);
  const clock = pop(f, w(11));
  const weak = prog(f, w(14), w(15) + 8);
  const X = (i: number) => 165 + i * 107;
  const pts = CURVE.map((y, i) => [X(i), y]);
  let d = `M ${pts[0][0]} ${pts[0][1]}`;
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1]; const [x1, y1] = pts[i]; const mx = (x0 + x1) / 2;
    d += ` C ${mx} ${y0} ${mx} ${y1} ${x1} ${y1}`;
  }
  const area = `${d} L ${X(7)} 880 L ${X(0)} 880 Z`;
  return (
    <g>
      <Bg f={f} c1="#9b8cff" c2="#c8bfff" />
      <g transform={`translate(540 620) scale(${card}) translate(-540 -620)`}>
        <rect x={80} y={250} width={920} height={740} rx={50} fill="#fff" stroke={INK} strokeWidth={10} filter="url(#sh)" />
        <text x={540} y={340} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={62} fill={INK}>EL NIÑO STRENGTH</text>
        <path d={area} fill="#ff7a45" opacity={0.35 * draw} />
        <path d={d} fill="none" stroke="#ff4d1f" strokeWidth={16} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - draw} />
        <path d={`M 120 880 L 960 880`} stroke={INK} strokeWidth={8} strokeLinecap="round" />
        {MONTHS.map((m, i) => (
          <text key={m} x={X(i)} y={930} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={38}
            fill={i === 5 ? '#ff4d1f' : i === 3 ? '#3f6cf5' : INK}>{m}</text>
        ))}
        {draw > 0.55 && (
          <g transform={`translate(${X(3)} ${CURVE[3]})`}>
            <circle r={22 + Math.sin(f / 4) * 5} fill="#3f6cf5" opacity={0.3} />
            <circle r={14} fill="#3f6cf5" stroke={INK} strokeWidth={6} />
            <g transform="translate(0 -70)">
              <rect x={-65} y={-30} width={130} height={60} rx={30} fill="#3f6cf5" stroke={INK} strokeWidth={6} />
              <text textAnchor="middle" dominantBaseline="central" y={3} fontFamily="Luckiest" fontSize={34} fill="#fff">NOW</text>
            </g>
          </g>
        )}
        {f >= w(5) && (
          <g transform={`translate(${X(5)} ${CURVE[5]}) scale(${flag})`}>
            <path d="M 0 0 L 0 -140" stroke={INK} strokeWidth={10} strokeLinecap="round" />
            <path d={`M 0 -140 L 150 ${-115 + Math.sin(f / 3) * 8} L 0 -80 Z`} fill="#ff4d1f" stroke={INK} strokeWidth={7} strokeLinejoin="round" />
            <text x={60} y={-110} textAnchor="middle" dominantBaseline="central" fontFamily="Luckiest" fontSize={36} fill="#fff">PEAK</text>
          </g>
        )}
      </g>
      {f >= w(9) && (
        <g transform={`translate(${lerp(runIn, -250, 340)} ${1250 + (runIn < 1 ? Math.abs(Math.sin(f * 0.9)) * -25 : 0)}) rotate(${runIn < 1 ? 12 : 0})`}>
          <Snowflake f={f} s={1 - weak * 0.45} run={runIn < 1 ? 1 : 0} sad={weak} />
          <Sweat f={f} x={90} y={-90} s={1.2} />
        </g>
      )}
      {f >= w(11) && <g transform={`translate(780 1230) scale(${clock}) rotate(${Math.sin(f) * 6})`}><Clock f={f} /></g>}
      <g transform="translate(780 1060)"><Stamp f={f} at={w(12)} text="LATE" rot={8} /></g>
      <g transform="translate(330 1040)"><Stamp f={f} at={w(15)} text="WEAK" color="#3f6cf5" rot={-6} /></g>
    </g>
  );
};

// 6 — The calendar says winter; the weather says summer. Seasons rewritten.
const S6: React.FC<SceneProps> = ({f, w, end}) => {
  const calP = pop(f, w(1));
  const X = f < w(5) ? 1250 : interpolate(f, [w(5), w(5) + 12, w(7), w(7) + 14], [1250, 640, 640, 330], {extrapolateRight: 'clamp'});
  const melt = prog(f, w(7), w(8) + 12);
  const sunP = pop(f, w(5), 10);
  const t1 = pop(f, w(9), 8);
  const t2 = pop(f, w(11), 8);
  const ul = prog(f, w(12), w(12) + 14);
  const tag = pop(f, end - 40, 12);
  return (
    <g>
      <rect width={1080} height={1920} fill="#7fd3ff" />
      <Bg f={f} c1="#69c3ff" c2="#bdeaff" cx={300} cy={700} />
      {Array.from({length: 16}, (_, i) => {
        const y = ((f * (2 + (i % 3)) + i * 140) % 1500) + 150;
        return <circle key={i} cx={(i * 71) % 620 + 20 + Math.sin(f / 10 + i) * 20} cy={y} r={8 + (i % 3) * 4} fill="#fff" stroke={INK} strokeWidth={3} />;
      })}
      <g transform={`translate(300 560) scale(${calP * 0.85}) rotate(-5)`}>
        <Calendar month="WINTER" color="#3f6cf5" w={420} sub="CALENDAR" />
      </g>
      <g transform="translate(300 1150)"><Snowman f={f} melt={melt} /></g>
      <clipPath id="sum"><path d={`M ${X + 90} -10 L 1200 -10 L 1200 1940 L ${X - 90} 1940 Z`} /></clipPath>
      <g clipPath="url(#sum)">
        <Bg f={f} c1="#ff9a3c" c2="#ffd36b" cx={780} cy={650} />
        <g transform={`translate(${lerp(prog(f, w(7), w(7) + 14), 790, 620)} 640) scale(${sunP})`}><Sun f={f} r={160} hot={1} /></g>
        <Heat f={f} x={700} y={1250} n={4} gap={120} />
      </g>
      <path d={`M ${X + 90} -10 L ${X - 90} 1940`} stroke={INK} strokeWidth={14} />
      {f >= w(9) && <T x={540} y={1040} size={150} s={t1} rot={-4} fill={YEL}>SEASONS</T>}
      {f >= w(11) && <T x={540} y={1200} size={130} s={t2} rot={2}>REWRITTEN</T>}
      {ul > 0 && (
        <path d="M 170 1300 C 380 1270 650 1335 910 1280" fill="none" stroke="#ff3b3b" strokeWidth={18} strokeLinecap="round"
          pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - ul} />
      )}
      {f >= end - 40 && (
        <g transform={`translate(540 1600) scale(${tag})`}>
          <rect x={-330} y={-50} width={660} height={100} rx={50} fill={INK} filter="url(#sh)" />
          <text textAnchor="middle" dominantBaseline="central" y={4} fontFamily="Luckiest" fontSize={50} fill={YEL} letterSpacing={2}>SUPER EL NIÑO · 2026</text>
        </g>
      )}
    </g>
  );
};

export const SCENES: SceneDef[] = [
  {C: S1, sfx: [[0, 'pop'], [2, 'whoosh', 0.5], [1, 'pop'], [5, 'boing'], [10, 'pop'], [13, 'whoosh', 0.6]], impacts: [10]},
  {C: S2, sfx: [[2, 'boom'], [3, 'boom'], [5, 'pop'], [10, 'ding'], [13, 'boing']], impacts: [2, 3]},
  {C: S3, sfx: [[2, 'whoosh', 0.6], [7, 'pop'], [9, 'pop'], [12, 'boom', 0.8]], impacts: [12]},
  {C: S4, sfx: [[1, 'pop'], [3, 'whoosh', 0.4], [7, 'ding'], [12, 'whoosh', 0.5], [14, 'boing']], impacts: [7]},
  {C: S5, sfx: [[0, 'whoosh', 0.4], [5, 'boing'], [9, 'whoosh', 0.5], [11, 'pop'], [12, 'boom', 0.8], [15, 'boom', 0.8]], impacts: [12, 15]},
  {C: S6, sfx: [[1, 'pop'], [5, 'whoosh', 0.6], [7, 'boom', 0.7], [9, 'boom'], [11, 'boom'], [12, 'ding']], impacts: [7, 9, 11]},
];
