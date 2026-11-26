"use client";

import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";
import type { EChartsOption } from "echarts";
import { Download } from "lucide-react";

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
  const chartRef = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const chart = echarts.init(el, undefined, { renderer: "svg" });
    chartRef.current = chart;

    const ro = new ResizeObserver(() => {
      chart.resize();
    });
    ro.observe(el);

    return () => {
      ro.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.setOption(option, { notMerge: true });
    }
  }, [option]);

  const handleExportSvg = () => {
    if (!chartRef.current) return;
    const url = chartRef.current.getDataURL({
      type: "svg",
      backgroundColor: "#080C14",
    });
    const a = document.createElement("a");
    a.href = url;
    a.download = `${exportName}.svg`;
    a.click();
  };

  return (
    <div className={`relative w-full ${className}`}>
      <button
        type="button"
        onClick={handleExportSvg}
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
