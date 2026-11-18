import { useEffect, useMemo, useRef, useState } from 'react';
import {
  type Point,
  type ValueFormat,
  formatValue,
  interpolate,
  sliceCurve,
  wrapText,
} from './math';

export interface BellCurveProps {
  /** Curve points (any order, any number). x = value axis, y = density. */
  points: Point[];
  /** Shaded band + bracket + intersection markers. Both must be set for the band to render. */
  shadeFrom?: number;
  shadeTo?: number;
  /** Text above the bracket, e.g. "80% of flows". */
  bandLabel?: string;
  /** Vertical dashed reference line (e.g. a redemption gate). */
  referenceX?: number;
  /** Text for the reference line; defaults to the formatted value. */
  referenceLabel?: string;
  /** Probability mass sitting at/below the curve's left edge, as a fraction 0–1 (drawn as a gray bar). */
  pointMass?: number;
  pointMassLabel?: string;
  format: ValueFormat;
  decimals: number;
  curveColor: string;
  shadeColor: string;
  referenceColor: string;
  yAxisLabel?: string;
}

const FONT = 'Inter, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif';
const INK = '#1f2328';
const MUTED = '#6b7280';
const TICKS = 6;

function useSize<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [size, setSize] = useState({ w: 0, h: 0 });
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setSize({ w: Math.round(width), h: Math.round(height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, size] as const;
}

export function BellCurve(props: BellCurveProps) {
  const [ref, { w, h }] = useSize<HTMLDivElement>();
  return (
    <div ref={ref} style={{ position: 'relative', width: '100%', height: '100%', minHeight: 160, overflow: 'hidden' }}>
      {w > 0 && h > 0 && <Chart {...props} width={w} height={h} />}
    </div>
  );
}

function Chart(p: BellCurveProps & { width: number; height: number }) {
  const { width, height, points, format, decimals } = p;
  const fmt = (v: number) => formatValue(v, format, decimals);

  const hasMass = p.pointMass !== undefined && p.pointMass > 0;
  const massLines = hasMass && p.pointMassLabel ? wrapText(p.pointMassLabel, 24) : [];
  const gutter = hasMass ? 62 : 0;
  const m = {
    top: 14,
    right: 26,
    bottom: 28 + (hasMass ? 18 + massLines.length * 14 : 0),
    left: 34 + gutter,
  };
  const plotW = Math.max(10, width - m.left - m.right);
  const plotH = Math.max(10, height - m.top - m.bottom);

  const model = useMemo(() => {
    if (points.length < 2) return undefined;
    const xMin = points[0].x;
    const xMax = points[points.length - 1].x;
    const yMax = Math.max(...points.map((q) => q.y)) * 1.08 || 1;
    return { xMin, xMax, yMax };
  }, [points]);

  if (!model) {
    return (
      <svg width={width} height={height} role="img" aria-label="Bell curve">
        <text x={width / 2} y={height / 2} textAnchor="middle" fontFamily={FONT} fontSize={13} fill={MUTED}>
          Select a source, an X column and a density column in the editor panel.
        </text>
      </svg>
    );
  }

  const { xMin, xMax, yMax } = model;
  const sx = (x: number) => m.left + ((x - xMin) / (xMax - xMin)) * plotW;
  const sy = (y: number) => m.top + plotH - (y / yMax) * plotH;
  const baseY = sy(0);

  const line = points.map((q, i) => `${i ? 'L' : 'M'}${sx(q.x).toFixed(2)},${sy(q.y).toFixed(2)}`).join('');

  // Shaded band: clamp to curve domain, accept bounds in either order.
  let band: { lo: number; hi: number } | undefined;
  if (p.shadeFrom !== undefined && p.shadeTo !== undefined) {
    const lo = Math.max(xMin, Math.min(p.shadeFrom, p.shadeTo));
    const hi = Math.min(xMax, Math.max(p.shadeFrom, p.shadeTo));
    if (hi > lo) band = { lo, hi };
  }
  const bandPath = band
    ? (() => {
        const s = sliceCurve(points, band.lo, band.hi);
        return (
          s.map((q, i) => `${i ? 'L' : 'M'}${sx(q.x).toFixed(2)},${sy(q.y).toFixed(2)}`).join('') +
          `L${sx(band.hi).toFixed(2)},${baseY}L${sx(band.lo).toFixed(2)},${baseY}Z`
        );
      })()
    : undefined;
  // Bracket sits at the curve height of the lower intersection so it never floats above the curve.
  // Clamped so the value labels under it never run into the x-axis ticks.
  const bracketY = band
    ? Math.min(sy(Math.min(interpolate(points, band.lo), interpolate(points, band.hi))), baseY - 40)
    : 0;

  const ticks = Array.from({ length: TICKS }, (_, i) => xMin + ((xMax - xMin) * i) / (TICKS - 1));
  const refInRange = p.referenceX !== undefined && p.referenceX >= xMin && p.referenceX <= xMax;
  const refX = refInRange ? sx(p.referenceX as number) : 0;

  const text = (extra: object) => ({ fontFamily: FONT, fontSize: 11, fill: INK, ...extra });

  return (
    <svg width={width} height={height} role="img" aria-label="Bell curve distribution">
      {/* y axis + label */}
      <line x1={m.left} x2={m.left} y1={m.top} y2={baseY} stroke="#9ca3af" />
      <text {...text({ fill: MUTED, fontSize: 10 })} transform={`translate(11 ${m.top + plotH / 2}) rotate(-90)`} textAnchor="middle">
        {p.yAxisLabel ?? 'density'}
      </text>

      {/* shading under the curve */}
      {bandPath && <path d={bandPath} fill={p.shadeColor} />}

      {/* curve */}
      <path d={line} fill="none" stroke={p.curveColor} strokeWidth={1.5} strokeLinejoin="round" />

      {/* x axis */}
      <line x1={m.left} x2={m.left + plotW} y1={baseY} y2={baseY} stroke="#9ca3af" />
      {ticks.map((t) => (
        <text key={t} {...text({ fill: MUTED, fontSize: 10 })} x={sx(t)} y={baseY + 15} textAnchor="middle">
          {fmt(t)}
        </text>
      ))}

      {/* reference line (e.g. gate) */}
      {refInRange && (
        <g>
          <line x1={refX} x2={refX} y1={m.top} y2={baseY} stroke={p.referenceColor} strokeWidth={1.25} strokeDasharray="4 3" />
          <text {...text({ fontSize: 10 })} x={refX} y={baseY - 6} textAnchor="middle">
            {p.referenceLabel || fmt(p.referenceX as number)}
          </text>
        </g>
      )}

      {/* bracket + intersection points */}
      {band && (
        <g>
          <line x1={sx(band.lo)} x2={sx(band.hi)} y1={bracketY} y2={bracketY} stroke={INK} strokeWidth={1.5} />
          <line x1={sx(band.lo)} x2={sx(band.lo)} y1={bracketY - 5} y2={bracketY + 5} stroke={INK} strokeWidth={1.5} />
          <line x1={sx(band.hi)} x2={sx(band.hi)} y1={bracketY - 5} y2={bracketY + 5} stroke={INK} strokeWidth={1.5} />
          {p.bandLabel && (
            <text {...text({})} x={(sx(band.lo) + sx(band.hi)) / 2} y={bracketY - 9} textAnchor="middle">
              {p.bandLabel}
            </text>
          )}
          {(() => {
            // Narrow bands: labels would collide, so push the upper label outside the bracket
            // (and onto a second line when the band is only a few pixels wide).
            const bw = sx(band.hi) - sx(band.lo);
            const narrow = bw < 64;
            return (
              <>
                <text {...text({})} x={sx(band.lo) + 3} y={bracketY + 16} textAnchor="start">
                  {fmt(band.lo)}
                </text>
                <text
                  {...text({})}
                  x={narrow ? sx(band.hi) + 5 : sx(band.hi) - 3}
                  y={bracketY + (bw < 30 ? 30 : 16)}
                  textAnchor={narrow ? 'start' : 'end'}
                >
                  {fmt(band.hi)}
                </text>
              </>
            );
          })()}
        </g>
      )}

      {/* probability mass at the left edge */}
      {hasMass && (
        <g>
          <rect
            x={m.left - 52}
            y={baseY - Math.min(1, p.pointMass as number) * plotH}
            width={44}
            height={Math.min(1, p.pointMass as number) * plotH}
            fill="#c8c8c8"
          />
          <text {...text({ fontSize: 10 })} x={m.left - 30} y={baseY - Math.min(1, p.pointMass as number) * plotH + 14} textAnchor="middle">
            {formatValue(p.pointMass as number, 'percent-fraction', decimals)}
          </text>
          <g stroke={INK} strokeWidth={1.25} fill="none">
            <line x1={m.left - 30} x2={m.left - 30} y1={baseY + 34} y2={baseY + 20} />
            <polyline points={`${m.left - 34},${baseY + 24} ${m.left - 30},${baseY + 19} ${m.left - 26},${baseY + 24}`} />
          </g>
          {massLines.map((l, i) => (
            <text key={i} {...text({ fontSize: 10 })} x={m.left - 52} y={baseY + 48 + i * 13} textAnchor="start">
              {l}
            </text>
          ))}
        </g>
      )}
    </svg>
  );
}
