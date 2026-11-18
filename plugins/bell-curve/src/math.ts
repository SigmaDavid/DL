export interface Point {
  x: number;
  y: number;
}

export type ValueFormat = 'percent-fraction' | 'percent-points' | 'number';

/** Coerce a Sigma cell value to a finite number, or undefined. */
export function toNumber(v: unknown): number | undefined {
  if (v === null || v === undefined || v === '') return undefined;
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : undefined;
}

/** Zip two columns into clean points sorted by x. Rows with a non-numeric x or y are dropped. */
export function buildPoints(xs: unknown[] = [], ys: unknown[] = []): Point[] {
  const out: Point[] = [];
  const n = Math.min(xs.length, ys.length);
  for (let i = 0; i < n; i++) {
    const x = toNumber(xs[i]);
    const y = toNumber(ys[i]);
    if (x !== undefined && y !== undefined) out.push({ x, y });
  }
  return out.sort((a, b) => a.x - b.x);
}

/** Linear interpolation of the curve at x (clamped to the curve's end values). `pts` must be sorted. */
export function interpolate(pts: Point[], x: number): number {
  if (pts.length === 0) return 0;
  if (x <= pts[0].x) return pts[0].y;
  const last = pts[pts.length - 1];
  if (x >= last.x) return last.y;
  let lo = 0;
  let hi = pts.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (pts[mid].x <= x) lo = mid;
    else hi = mid;
  }
  const a = pts[lo];
  const b = pts[hi];
  const t = b.x === a.x ? 0 : (x - a.x) / (b.x - a.x);
  return a.y + t * (b.y - a.y);
}

/** The curve restricted to [lo, hi], with interpolated points at both boundaries. */
export function sliceCurve(pts: Point[], lo: number, hi: number): Point[] {
  if (pts.length === 0 || hi <= lo) return [];
  const inner = pts.filter((p) => p.x > lo && p.x < hi);
  return [{ x: lo, y: interpolate(pts, lo) }, ...inner, { x: hi, y: interpolate(pts, hi) }];
}

export function formatValue(v: number, format: ValueFormat, decimals: number): string {
  const scaled = format === 'percent-fraction' ? v * 100 : v;
  const text = Math.abs(scaled).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  const sign = scaled < 0 && Number(text.replace(/,/g, '')) !== 0 ? '−' : '';
  return `${sign}${text}${format === 'number' ? '' : '%'}`;
}

/** Greedy word-wrap on character count (good enough for short SVG captions). */
export function wrapText(text: string, maxChars: number): string[] {
  const lines: string[] = [];
  let line = '';
  for (const word of text.split(/\s+/).filter(Boolean)) {
    if (line && (line + ' ' + word).length > maxChars) {
      lines.push(line);
      line = word;
    } else {
      line = line ? line + ' ' + word : word;
    }
  }
  if (line) lines.push(line);
  return lines;
}
