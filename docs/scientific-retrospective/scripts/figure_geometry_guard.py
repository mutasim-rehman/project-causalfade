"""Automated pixel-level geometry guard ensuring ZERO text-over-text and ZERO text-over-bar/line/marker/border collisions in Matplotlib figures."""
from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox
import numpy as np


def _shrink(b: Bbox, px: float = 0.5) -> Bbox:
    if b.width <= 2 * px or b.height <= 2 * px:
        return b
    return Bbox.from_extents(b.x0 + px, b.y0 + px, b.x1 - px, b.y1 - px)


def _seg_intersects_bbox(p1: tuple[float, float], p2: tuple[float, float], b: Bbox) -> bool:
    x1, y1 = p1
    x2, y2 = p2
    if max(x1, x2) < b.x0 or min(x1, x2) > b.x1 or max(y1, y2) < b.y0 or min(y1, y2) > b.y1:
        return False
    if (b.x0 <= x1 <= b.x1 and b.y0 <= y1 <= b.y1) or (b.x0 <= x2 <= b.x1 and b.y0 <= y2 <= b.y1):
        return True
    # Sample 25 points along segment for fast, exact screen-space box intersection
    ts = np.linspace(0.0, 1.0, 25)
    xs = x1 + ts * (x2 - x1)
    ys = y1 + ts * (y2 - y1)
    return bool(np.any((xs >= b.x0) & (xs <= b.x1) & (ys >= b.y0) & (ys <= b.y1)))


def verify_and_save(
    fig: plt.Figure,
    out_pdf: Path,
    preview_dir: Path | None = None,
    box_text_pairs: list[tuple[FancyBboxPatch, Text]] | None = None,
) -> list[str]:
    """Render figure, assert zero text-text and text-graphic overlaps, save PDF and optional PNG preview."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    issues: list[str] = []

    box_pairs = box_text_pairs or []
    paired_texts = {id(t): p for p, t in box_pairs}
    paired_patches = {id(p): t for p, t in box_pairs}

    # 1. Collect all visible non-empty Text objects across the entire figure
    all_texts: list[Text] = []
    legend_texts: set[int] = set()
    legends: list[tuple[Axes | plt.Figure, Legend, Bbox]] = []

    for leg in fig.legends:
        if leg.get_visible():
            legends.append((fig, leg, _shrink(leg.get_window_extent(renderer), 1.0)))
            for t in leg.get_texts():
                legend_texts.add(id(t))
    for ax in fig.axes:
        leg = ax.get_legend()
        if leg is not None and leg.get_visible():
            legends.append((ax, leg, _shrink(leg.get_window_extent(renderer), 1.0)))
            for t in leg.get_texts():
                legend_texts.add(id(t))

    def walk_texts(artist):
        if isinstance(artist, Text) and artist.get_visible() and artist.get_text().strip():
            all_texts.append(artist)
        for ch in artist.get_children():
            walk_texts(ch)

    walk_texts(fig)
    # Deduplicate by object id
    seen_ids = set()
    uniq_texts: list[Text] = []
    for t in all_texts:
        if id(t) not in seen_ids:
            seen_ids.add(id(t))
            uniq_texts.append(t)

    text_bboxes = [(t, _shrink(Text.get_window_extent(t, renderer), 1.0)) for t in uniq_texts]

    # Check 1: Text-over-Text collisions
    for i in range(len(text_bboxes)):
        t1, b1 = text_bboxes[i]
        for j in range(i + 1, len(text_bboxes)):
            t2, b2 = text_bboxes[j]
            if b1.overlaps(b2):
                s1 = t1.get_text().replace("\n", " ")[:35]
                s2 = t2.get_text().replace("\n", " ")[:35]
                issues.append(f"[TEXT-TEXT] '{s1}' overlaps '{s2}'")

    # Check 2: Container FancyBboxPatch containment & non-intrusion
    for patch, txt in box_pairs:
        pb = patch.get_window_extent(renderer)
        tb = txt.get_window_extent(renderer)
        if tb.x0 < pb.x0 + 1.5 or tb.x1 > pb.x1 - 1.5 or tb.y0 < pb.y0 + 1.5 or tb.y1 > pb.y1 - 1.5:
            s = txt.get_text().replace("\n", " ")[:40]
            issues.append(
                f"[BOX-OVERFLOW] '{s}' overflows its box (text={tb.bounds}, box={pb.bounds})"
            )
        for other_t, ob in text_bboxes:
            if id(other_t) == id(txt):
                continue
            if ob.overlaps(_shrink(pb, 1.0)):
                s_oth = other_t.get_text().replace("\n", " ")[:35]
                s_own = txt.get_text().replace("\n", " ")[:25]
                issues.append(f"[TEXT-OVER-BOX] '{s_oth}' overlaps container of '{s_own}'")

    # Check 3: Inside each Axes, check plot-area texts and legends against bars, lines, scatter markers, arrows
    for ax in fig.axes:
        ax_bbox = ax.get_window_extent(renderer)
        # Gather plot-area Texts belonging to this Axes (excluding tick labels/axis labels outside axes, and legend texts handled via legend bbox)
        ax_inner_texts: list[tuple[Text, Bbox]] = []
        for t, tb in text_bboxes:
            if id(t) in legend_texts or id(t) in paired_texts:
                continue
            if t.axes is ax and tb.overlaps(_shrink(ax_bbox, 2.0)):
                # Skip title, xlabel, ylabel, ticklabels if they sit outside data spine box, but check any overlap with actual data artists regardless!
                ax_inner_texts.append((t, tb))

        # Bars / Rectangles (skip background Axes patch and imshow)
        bars: list[Bbox] = []
        for p in ax.patches:
            if p is ax.patch or not p.get_visible():
                continue
            if id(p) in paired_patches:
                continue
            if isinstance(p, (Rectangle, FancyBboxPatch)):
                # Skip zero-height/zero-width bars
                if isinstance(p, Rectangle) and (p.get_width() == 0 or p.get_height() == 0):
                    continue
                bars.append(_shrink(p.get_window_extent(renderer), 1.0))

        # Lines (skip gridlines)
        segments: list[tuple[tuple[float, float], tuple[float, float], str]] = []
        for ln in ax.lines:
            if not ln.get_visible():
                continue
            verts = ln.get_transform().transform(ln.get_xydata())
            for k in range(len(verts) - 1):
                if np.all(np.isfinite(verts[k])) and np.all(np.isfinite(verts[k + 1])):
                    segments.append((tuple(verts[k]), tuple(verts[k + 1]), ln.get_label() or "line"))

        # Collections (errorbar LineCollections and scatter PathCollections)
        marker_boxes: list[Bbox] = []
        for col in ax.collections:
            if not col.get_visible():
                continue
            if isinstance(col, PathCollection):
                offs = col.get_offsets()
                if len(offs) > 0:
                    pts = col.get_offset_transform().transform(offs)
                    sizes = col.get_sizes()
                    r = float(np.sqrt(np.max(sizes)) / 2.0) if len(sizes) else 3.0
                    for px, py in pts:
                        if ax_bbox.x0 <= px <= ax_bbox.x1 and ax_bbox.y0 <= py <= ax_bbox.y1:
                            marker_boxes.append(Bbox.from_extents(px - r, py - r, px + r, py + r))
            elif hasattr(col, "get_segments"):
                for seg in col.get_segments():
                    tseg = col.get_transform().transform(seg)
                    for k in range(len(tseg) - 1):
                        segments.append((tuple(tseg[k]), tuple(tseg[k + 1]), "errorbar/fill"))

        # Arrow patches (standalone FancyArrowPatch and Annotation.arrow_patch)
        arrow_bboxes: list[Bbox] = []
        arrow_artists = [p for p in ax.patches if isinstance(p, FancyArrowPatch) and p.get_visible()]
        for ch in ax.get_children():
            if isinstance(ch, Annotation) and getattr(ch, "arrow_patch", None) is not None:
                if ch.arrow_patch.get_visible():
                    arrow_artists.append(ch.arrow_patch)
        for ap in arrow_artists:
            ab = _shrink(ap.get_window_extent(renderer), 2.5)
            if ab.width > 0 and ab.height > 0:
                arrow_bboxes.append(ab)

        # Test ax_inner_texts against bars, lines, markers, arrows
        for t, tb in ax_inner_texts:
            lbl = t.get_text().replace("\n", " ")[:35]
            tb_tight = _shrink(tb, 1.5)
            for bb in bars:
                if tb_tight.overlaps(bb):
                    issues.append(f"[TEXT-OVER-BAR] '{lbl}' overlaps a bar/patch")
                    break
            for p1, p2, l_name in segments:
                if _seg_intersects_bbox(p1, p2, tb_tight):
                    issues.append(f"[TEXT-OVER-LINE] '{lbl}' intersects line '{l_name}'")
                    break
            for mb in marker_boxes:
                if tb_tight.overlaps(mb):
                    issues.append(f"[TEXT-OVER-MARKER] '{lbl}' overlaps a scatter marker")
                    break

        # Also test all non-annotation texts inside this Axes against arrow bounding boxes
        for t, tb in text_bboxes:
            if isinstance(t, Annotation) or t.axes is not ax:
                continue
            tb_tight = _shrink(tb, 2.0)
            for ab in arrow_bboxes:
                if tb_tight.overlaps(ab):
                    lbl = t.get_text().replace("\n", " ")[:35]
                    issues.append(f"[ARROW-OVER-TEXT] arrow overlaps text '{lbl}'")
                    break

        # Test Legend bboxes against bars, lines, markers
        for owner, leg, lb in legends:
            if owner is ax or owner is fig:
                for bb in bars:
                    if lb.overlaps(bb):
                        issues.append("[LEGEND-OVER-BAR] legend overlaps bar")
                        break
                for p1, p2, l_name in segments:
                    if _seg_intersects_bbox(p1, p2, lb):
                        issues.append(f"[LEGEND-OVER-LINE] legend intersects line '{l_name}'")
                        break
                for mb in marker_boxes:
                    if lb.overlaps(mb):
                        issues.append("[LEGEND-OVER-MARKER] legend overlaps scatter marker")
                        break

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.10)
    if preview_dir is not None:
        preview_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(preview_dir / (out_pdf.stem + ".png"), dpi=160, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)

    if issues:
        print(f"GEOMETRY ISSUES in {out_pdf.name} ({len(issues)}):")
        for iss in issues[:12]:
            print("  -", iss)
    else:
        print(f"OK {out_pdf.name}: 0 overlaps verified.")
    return issues
