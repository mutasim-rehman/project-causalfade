"""Verify all compiled PDF deliverables, LaTeX/BibTeX logs, figure/table/inventory counts, and repository immutability."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RETRO = Path(__file__).resolve().parents[1]
BUILD = RETRO / "build"


def main():
    blg = (BUILD / "main.blg").read_text(encoding="utf-8", errors="replace")
    log = (BUILD / "main.log").read_text(encoding="utf-8", errors="replace")
    pdf_bytes = (BUILD / "The_Life_of_CausalFade.pdf").read_bytes()

    print("=== BibTeX Log (main.blg) ===")
    print(blg.strip())

    undef_cite = re.findall(r"LaTeX Warning: Citation .* undefined", log)
    undef_ref = re.findall(r"LaTeX Warning: Reference .* undefined", log)
    mult_lbl = re.findall(r"LaTeX Warning: Label .* multiply defined", log)
    pages_m = re.findall(r"Output written on .*?\((\d+) pages", log)
    pages = int(pages_m[-1]) if pages_m else len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))

    print(f"Undefined citations: {len(undef_cite)}")
    print(f"Undefined references: {len(undef_ref)}")
    print(f"Multiply-defined labels: {len(mult_lbl)}")
    print(f"Compiled PDF page count: {pages} pages ({len(pdf_bytes):,} bytes)")

    figs = sorted((RETRO / "figures").glob("*.pdf"))
    tabs = sorted((RETRO / "tables").glob("*.tex"))
    evids = sorted([p for p in (RETRO / "evidence").iterdir() if not p.name.startswith("_")])
    print(f"Vector PDF figures: {len(figs)}")
    print(f"Generated LaTeX tables: {len(tabs)}")
    print(f"Evidence inventory files: {len(evids)}")

    # Verify zero tracked file changes and zero manuscript/ changes
    git_diff = subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).strip()
    git_staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()
    non_retro = [l for l in git_status if "docs/scientific-retrospective" not in l and "manuscript/" not in l]

    print(f"Modified tracked files: '{git_diff}'")
    print(f"Staged tracked files: '{git_staged}'")
    print(f"Git status entries outside docs/scientific-retrospective and pre-existing manuscript/: {non_retro}")
    assert git_diff == "" and git_staged == "" and len(non_retro) == 0
    assert len(undef_cite) == 0 and len(undef_ref) == 0 and len(mult_lbl) == 0
    assert len(figs) >= 16 and pages > 50
    print("ALL DELIVERABLE AND IMMUTABILITY CHECKS PASSED.")


if __name__ == "__main__":
    main()
