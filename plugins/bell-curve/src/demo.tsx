// Standalone preview with the three scenarios from the design mock-ups. Not used inside Sigma.
import { createRoot } from 'react-dom/client';
import { BellCurve } from './BellCurve';
import type { Point } from './math';

const normal = (mu: number, sd: number, lo: number, hi: number): Point[] =>
  Array.from({ length: 200 }, (_, i) => {
    const x = lo + ((hi - lo) * i) / 199;
    return { x, y: Math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * Math.sqrt(2 * Math.PI)) };
  });
const expo = (rate: number, hi: number): Point[] =>
  Array.from({ length: 200 }, (_, i) => ({ x: (hi * i) / 199, y: rate * Math.exp((-rate * hi * i) / 199) }));
const gamma = (k: number, theta: number, hi: number): Point[] =>
  Array.from({ length: 200 }, (_, i) => {
    const x = (hi * i) / 199;
    return { x, y: (0.45 + Math.pow(x / theta, k - 1)) * Math.exp(-x / theta) };
  });

const common = { decimals: 1, curveColor: '#4f5bd5', shadeColor: '#dfe3f7', referenceColor: '#e0524d' };
const card = { width: 420, height: 300, border: '1px solid #e5e7eb', borderRadius: 8, padding: 8, background: '#fff' };

createRoot(document.getElementById('root')!).render(
  <div style={{ display: 'flex', gap: 16, padding: 16, flexWrap: 'wrap', background: '#f6f7f9' }}>
    <div style={card}>
      <BellCurve {...common} format="percent-fraction" points={normal(0.029, 0.105, -0.42, 0.477)}
        shadeFrom={-0.116} shadeTo={0.172} bandLabel="80% of flows" />
    </div>
    <div style={card}>
      <BellCurve {...common} format="percent-fraction" points={expo(80, 0.075)}
        shadeFrom={0} shadeTo={0.014} bandLabel="80% of flows"
        referenceX={0.05} referenceLabel="gate 5%" pointMass={0.597}
        pointMassLabel="Probability of a non-material redemptions" />
    </div>
    <div style={card}>
      <BellCurve {...common} format="percent-fraction" points={gamma(2, 0.02, 0.199).map((p) => ({ x: p.x, y: p.y }))}
        shadeFrom={0} shadeTo={0.081} bandLabel="80% of flows" pointMass={0.229}
        pointMassLabel="Probability of non-material subscriptions" />
    </div>
  </div>,
);
