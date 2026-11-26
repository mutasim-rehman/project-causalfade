import { ImageResponse } from "next/og";

export const size = { width: 32, height: 32 };
export const contentType = "image/png";
export const dynamic = "force-static";

export default function Icon() {
  return new ImageResponse(
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 32, height: 32, borderRadius: 6, background: "#111827" }}>
      <div style={{ width: 12, height: 12, borderRadius: 6, background: "#55D6BE" }} />
    </div>,
    size,
  );
}
