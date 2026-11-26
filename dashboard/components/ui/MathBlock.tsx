"use client";

import React, { useMemo } from "react";
import katex from "katex";

export function MathBlock({
  tex,
  display = false,
  className = "",
}: {
  tex: string;
  display?: boolean;
  className?: string;
}) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(tex, {
        displayMode: display,
        throwOnError: false,
        strict: false,
      });
    } catch {
      return tex;
    }
  }, [tex, display]);

  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
