export function fmtPct(ratio: number, digits = 2): string {
  return `${(ratio * 100).toFixed(digits)}%`;
}

export function fmtPP(pp: number, digits = 2, signed = true): string {
  const prefix = signed && pp > 0 ? "+" : "";
  return `${prefix}${pp.toFixed(digits)} pp`;
}

export function fmtCI(low: number, high: number, digits = 2, unit = "pp"): string {
  const f = (n: number) => (n > 0 ? `+${n.toFixed(digits)}` : n.toFixed(digits));
  return `[${f(low)}, ${f(high)}] ${unit}`;
}

export function fmtPValue(p: number): string {
  if (p < 1e-4) {
    return p.toExponential(2);
  }
  return p.toFixed(4);
}

export function fmtInt(n: number): string {
  return n.toLocaleString("en-US");
}
