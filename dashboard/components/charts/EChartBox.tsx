"use client";

import React, { useEffect, useRef, useState } from "react";
import type { EChartsOption } from "echarts";
import type { EChartsType } from "echarts/core";
import { Download } from "lucide-react";

const lightColors: Record<string, string> = {
  "#f1f5f9": "#0f172a", "#94a3b8": "#334155", "#64748b": "#475569",
  "#080c14": "#f8fafc", "#111827": "#ffffff", "#263142": "#cbd5e1", "#1e293b": "#cbd5e1",
  "#55d6be": "#056c5b", "#60a5fa": "#1b5cb0", "#a78bfa": "#6940b5",
  "#fbbf24": "#8d5703", "#f87171": "#aa2c36", "#34d399": "#05704d",
};

function applyLightPalette<T>(value: T): T {
  if (typeof value === "string") return (lightColors[value.toLowerCase()] ?? value) as T;
  if (Array.isArray(value)) return value.map(applyLightPalette) as T;
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, entry]) => [key, applyLightPalette(entry)])) as T;
  }
  return value;
}

export function EChartBox({
  option,
  height = 340,
  exportName = "causalfade-chart",
  className = "",
}: {
  option: EChartsOption;
  height?: number;
  exportName?: string;
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<EChartsType | null>(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    let cancelled = false;
    let resize: ResizeObserver | undefined;
    import("./chart-engine").then(({ init }) => {
      if (cancelled) return;
      const chart = init(el, undefined, { renderer: "svg" });
      chartRef.current = chart;
      resize = new ResizeObserver(() => chart.resize());
      resize.observe(el);
      setReady(true);
    }).catch(() => {
      if (!cancelled) setFailed(true);
    });

    return () => {
      cancelled = true;
      resize?.disconnect();
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!ready) return;
    const root = document.documentElement;
    const draw = () => {
      const themed = root.classList.contains("dark") ? option : applyLightPalette(option);
      chartRef.current?.setOption({
        ...themed,
        animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      }, { notMerge: true });
    };
    draw();
    const themeObserver = new MutationObserver(draw);
    themeObserver.observe(root, { attributes: true, attributeFilter: ["class"] });
    return () => themeObserver.disconnect();
  }, [option, ready]);

  const handleExportSvg = () => {
    if (!chartRef.current) return;
    const url = chartRef.current.getDataURL({
      type: "svg",
      backgroundColor: getComputedStyle(document.documentElement).getPropertyValue("--bg-app"),
    });
    const a = document.createElement("a");
    a.href = url;
    a.download = `${exportName}.svg`;
    a.click();
  };

  return (
    <div className={`relative min-w-0 w-full ${className}`}>
      {failed && <p role="alert" className="absolute left-2 top-2 text-sm text-sci-caution">The chart could not be loaded.</p>}
      <button
        type="button"
        onClick={handleExportSvg}
        disabled={!ready}
        title="Export SVG"
        className="no-print absolute right-1 top-1 z-10 inline-flex items-center gap-1 rounded border border-obs-border bg-obs-elevated/90 px-2 py-0.5 text-[11px] font-mono text-obs-secondary hover:border-sci-causal/60 hover:text-obs-text"
      >
        <Download className="h-3 w-3" />
        <span>SVG</span>
      </button>
      <div ref={containerRef} style={{ width: "100%", height }} />
    </div>
  );
}
