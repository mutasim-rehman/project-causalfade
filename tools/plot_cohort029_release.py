"""Create deterministic, model-free Cohort 029 SVG figures and figure data."""

import json
from pathlib import Path

from tools.cohort029_prepare import ROOT


BASE = ROOT / "experiments/cohort_029"


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def svg_document(body, title, description):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" '
            f'viewBox="0 0 960 540" role="img" aria-labelledby="title desc">'
            f'<title id="title">{title}</title><desc id="desc">{description}</desc>'
            '<rect width="960" height="540" fill="#fff"/>'
            '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#1c2733}'
            '.heading{font-size:26px;font-weight:700}.sub{font-size:17px}'
            '.tick{font-size:15px}.label{font-size:19px;font-weight:600}'
            '.note{font-size:14px;fill:#4b5661}</style>' + body + '</svg>\n')


def main():
    report = json.loads((BASE / "release/verification.json").read_text())
    if not report["passed"]:
        raise ValueError("Release verification must pass before plotting")
    primary = json.loads((BASE / "runs/confirmatory/analysis/primary.json").read_text())
    out = BASE / "release/figures"
    out.mkdir(parents=True, exist_ok=True)
    data = {
        "unit": "percentage points",
        "pair_fidelity": [
            {"task": "Causal", "correct": primary["causal"]["both_correct"],
             "scheduled": 512, "percent": 100 * primary["causal"]["fidelity"]},
            {"task": "Arithmetic", "correct": primary["control"]["both_correct"],
             "scheduled": 512, "percent": 100 * primary["control"]["fidelity"]},
        ],
        "difference": {"estimate": primary["delta_percentage_points"],
                       "approximate_t_95": [100*x for x in primary["interval_t"]],
                       "conservative_bounded_95": [100*x for x in primary["interval_bounded"]]},
        "source": "experiments/cohort_029/runs/confirmatory/analysis/primary.json",
    }
    write(out / "figure_data.json", data)
    p = data["pair_fidelity"]
    bars = []
    for item, y, color in ((p[0], 220, "#1d667e"), (p[1], 330, "#ad6025")):
        x_end = 250 + item["percent"] * 15
        bars.append(f'<text class="label" x="45" y="{y+27}">{item["task"]}</text>'
                    f'<rect x="250" y="{y}" width="{x_end-250:.3f}" height="45" '
                    f'fill="{color}"/>'
                    f'<text class="label" x="{x_end+12:.3f}" y="{y+29}">'
                    f'{item["correct"]}/{item["scheduled"]} ({item["percent"]:.2f}%)</text>')
    chart = ('<text class="heading" x="45" y="65">Target pair fidelity</text>'
             '<text class="sub" x="45" y="98">Transfer form · 512 scheduled pairs per task</text>'
             '<line x1="250" y1="405" x2="850" y2="405" stroke="#263744"/>'
             + ''.join(f'<line x1="{250+15*i}" y1="405" x2="{250+15*i}" y2="413" '
                       f'stroke="#263744"/><text class="tick" x="{244+15*i}" y="438">{i}%</text>'
                       for i in (0, 10, 20, 30, 40))
             + ''.join(bars)
             + '<text class="note" x="45" y="490">Pair success requires both target variants to be correct.</text>')
    (out / "primary_pair_fidelity.svg").write_text(svg_document(
        chart, "Cohort 029 target pair fidelity", "Causal 128 of 512; arithmetic 146 of 512."))

    delta = data["difference"]
    scale = lambda v: 480 + 12*v
    lo, hi = delta["approximate_t_95"]
    blo, bhi = delta["conservative_bounded_95"]
    interval_chart = ('<text class="heading" x="45" y="65">Causal minus arithmetic pair fidelity</text>'
                      '<text class="sub" x="45" y="98">Transfer form · percentage points · 128 families</text>'
                      '<line x1="120" y1="390" x2="840" y2="390" stroke="#263744"/>'
                      '<line x1="480" y1="155" x2="480" y2="390" stroke="#9aa6b0" stroke-dasharray="5 5"/>'
                      + ''.join(f'<line x1="{scale(i)}" y1="390" x2="{scale(i)}" y2="398" '
                                f'stroke="#263744"/><text class="tick" x="{scale(i)-15}" y="425">{i}</text>'
                                for i in (-30, -20, -10, 0, 10, 20, 30))
                      + f'<text class="label" x="45" y="215">Approximate t interval</text>'
                      + f'<line x1="{scale(lo):.3f}" y1="245" x2="{scale(hi):.3f}" y2="245" '
                        'stroke="#1d667e" stroke-width="6"/>'
                      + f'<circle cx="{scale(delta["estimate"]):.3f}" cy="245" r="9" fill="#1d667e"/>'
                      + f'<text class="sub" x="600" y="250">{delta["estimate"]:.3f} [{lo:.2f}, {hi:.2f}]</text>'
                      + '<text class="label" x="45" y="300">Conservative bound</text>'
                      + f'<line x1="{scale(blo):.3f}" y1="330" x2="{scale(bhi):.3f}" y2="330" '
                        'stroke="#ad6025" stroke-width="6"/>'
                      + f'<circle cx="{scale(delta["estimate"]):.3f}" cy="330" r="9" fill="#ad6025"/>'
                      + '<text class="note" x="45" y="485">The approximate interval crosses zero; this is not an equivalence result.</text>')
    (out / "primary_difference.svg").write_text(svg_document(
        interval_chart, "Cohort 029 primary contrast", "Difference minus 3.515625 percentage points with approximate and conservative intervals."))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
