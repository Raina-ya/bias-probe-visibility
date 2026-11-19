"""Paper v4.1 hardware addendum: numbers, calibration table, figure and results note.

Reads only committed hardware records (results/hardware_v1/, results/hardware_v1_analysis/)
and the registered amendment's analytic threshold, and writes:

  paper/numbers_hw_v4_1.tex           LaTeX macros for every hardware number in the paper
  figures/hw_relevance_v4_1.svg       (a) rho_hat with intervals; (b) reported vs measured errors
  docs/results/hardware_readout_v1.md results note

Outputs are derived (overwritten deterministically); the records they read are
immutable.  The SVG is converted to PDF with headless Chromium (see build log).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "experiments" / "hardware"))

import hw_circuits_v1 as hc  # noqa: E402
import hw_stats_v1 as st  # noqa: E402

OUTPUTS = ("numbers_hw_v4_1.tex", "hw_relevance_v4_1.svg", "hardware_readout_v1.md")
RUN = REPO / "results" / "hardware_v1"
ANALYSIS = REPO / "results" / "hardware_v1_analysis" / "analysis_v1.json"
E5_MAX_TAU, E5_MARGINAL = 0.01, 0.10  # protocol v4 Section 3.1


def load() -> dict:
    return {
        "analysis": json.loads(ANALYSIS.read_text(encoding="utf-8")),
        "pilot": json.loads((RUN / "raw" / "pilot_job0.json").read_text(encoding="utf-8")),
        "main": json.loads((RUN / "raw" / "main_job0.json").read_text(encoding="utf-8")),
        "manifest": json.loads((RUN / "preflight" / "run_manifest.json").read_text(encoding="utf-8")),
        "allocation": json.loads((RUN / "allocation.json").read_text(encoding="utf-8")),
    }


def e5_ratio() -> float:
    return E5_MAX_TAU / st.c_star(E5_MARGINAL, E5_MARGINAL)


def numbers(d: dict | None = None) -> dict[str, tuple[str, str]]:
    d = d or load()
    a, pairs = d["analysis"], d["analysis"]["pairs"]
    ratios = [p["c_over_cstar"] for p in pairs]
    rhos = [p["rho_hat"] for p in pairs if p["rho_hat"] is not None]
    upper_ratio = max(p["c_interval_95"][1] / p["c_star"] for p in pairs)
    min_det_holm = min(p["detection_p_holm"] for p in pairs)
    pilot_s, main_s = float(d["pilot"]["usage_seconds"]), float(d["main"]["usage_seconds"])
    e5_rho = E5_MAX_TAU / (E5_MARGINAL * (1 - E5_MARGINAL))
    ci_excl = sum(1 for p in pairs if p["c_interval_95"][0] > 0 or p["c_interval_95"][1] < 0)
    return {
        "HwCiExcl": (str(ci_excl), "pair-preparations whose unadjusted 95% interval for c excludes 0"),
        "HwTests": (str(a["m_tests_per_family"]), "analysis.m_tests_per_family"),
        "HwRelRej": (str(a["relevance_rejections"]), "analysis.relevance_rejections"),
        "HwDetRej": (str(a["detection_rejections"]), "analysis.detection_rejections"),
        "HwShots": (f"{a['shots_per_circuit']['p4a_all0']:,}", "analysis.shots_per_circuit"),
        "HwPilotSec": (f"{pilot_s:.0f}", "raw/pilot_job0.usage_seconds"),
        "HwMainSec": (f"{main_s:.0f}", "raw/main_job0.usage_seconds"),
        "HwTotalSec": (f"{pilot_s + main_s:.0f}", "pilot + main usage_seconds"),
        "HwMaxRho": (f"{max(abs(x) for x in rhos):.3f}", "max |rho_hat| over pair-preparations"),
        "HwMaxRatio": (f"{max(ratios):.3f}", "max c_hat/c* over pair-preparations"),
        "HwMaxUpperRatio": (f"{upper_ratio:.3f}", "max (95% upper bound of c)/c*"),
        "HwMinDetHolm": (f"{min_det_holm:.2f}", "min Holm-adjusted detection p"),
        "HwMedianErr": (f"{100 * d['manifest']['median_readout_error']:.2f}",
                        "run_manifest.median_readout_error (percent)"),
        "HwSmin": (f"{d['allocation']['s_min']:,}", "allocation.s_min"),
        "EfiveRho": (f"{e5_rho:.2f}", "protocol v4 E5: tau 0.01 / (0.1 x 0.9)"),
        "EfiveRatio": (f"{e5_ratio():.2f}", "protocol v4 E5: tau 0.01 / c*(0.1, 0.1)"),
    }


def measured_rates(d: dict) -> dict[str, list[float]]:
    return d["analysis"]["flip_rates_per_logical_qubit"]


def md_table(d: dict) -> str:
    phys = d["manifest"]["selected_physical_qubits"]
    rep = d["manifest"]["selected_readout_errors"]
    m = measured_rates(d)
    lines = ["| Logical | Physical | Reported | Flip, all 0 | Flip, all 1 |", "|---:|---:|---:|---:|---:|"]
    lines += [f"| {k} | {q} | {100 * rep[k]:.2f} | {100 * m['p4a_all0'][k]:.2f} | {100 * m['p4a_all1'][k]:.2f} |"
              for k, q in enumerate(phys)]
    return "\n".join(lines)


def figure(d: dict) -> str:
    """Full-width SVG with two panels.

    (a) Estimated correlation coefficient rho_hat with 95% percentile bootstrap
        intervals (unadjusted) for 28 pairs x 2 preparations, on the scale of the
        data; the relevance threshold and the largest E5 setting lie far above
        the axis and are marked by arrows.
    (b) Reported calibration readout error versus measured flip rate per
        selected qubit, both preparations, with the line y = x.
    """

    a, m = d["analysis"], d["manifest"]
    pairs = a["pairs"]
    order = hc_pairs()
    W, H = 700, 252
    colors = {"p4a_all0": "#1f5fa8", "p4a_all1": "#c2571a"}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           'font-family="Helvetica, Arial, sans-serif">', f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    def text(x, y, t, size=9, anchor="start", fill="#333", weight="normal", rotate=None):
        tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate is not None else ""
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
                   f'fill="{fill}" font-weight="{weight}"{tr}>{t}</text>')

    # ---------------- panel (a)
    L, T, PW, PH = 52, 40, 400, 160
    ymin, ymax = -0.025, 0.025
    ya = lambda v: T + (ymax - v) / (ymax - ymin) * PH  # noqa: E731
    xa = lambda i, k: L + (i + 0.5) / len(order) * PW + (-2.6 if k == 0 else 2.6)  # noqa: E731
    text(8, 14, "a", 12, weight="bold", fill="#111")
    text(26, 14, "Measured pair correlations are about 1% or less", 10, fill="#111")
    for v in (-0.02, -0.01, 0.0, 0.01, 0.02):
        out.append(f'<line x1="{L}" y1="{ya(v):.1f}" x2="{L + PW}" y2="{ya(v):.1f}" '
                   f'stroke="{"#999" if v == 0 else "#e6e6e6"}" stroke-width="1"/>')
        text(L - 5, ya(v) + 3, f"{v:+.2f}".replace("+0.00", "0"), 8.5, "end", "#444")
    by = {(p["circuit"], tuple(p["pair"])): p for p in pairs}
    for i, pr in enumerate(order):
        for k, circ in enumerate(hc.CIRCUITS):
            p = by[(circ, pr)]
            den = (p["q_i"] * (1 - p["q_i"]) * p["q_j"] * (1 - p["q_j"])) ** 0.5
            lo, hi = (min(max(v / den, ymin), ymax) for v in p["c_interval_95"])
            cx = xa(i, k)
            out.append(f'<line x1="{cx:.1f}" y1="{ya(hi):.1f}" x2="{cx:.1f}" y2="{ya(lo):.1f}" '
                       f'stroke="{colors[circ]}" stroke-width="1" opacity="0.8"/>')
            out.append(f'<circle cx="{cx:.1f}" cy="{ya(p["rho_hat"]):.1f}" r="2" fill="{colors[circ]}"/>')
        text(L + (i + 0.5) / len(order) * PW + 2.5, T + PH + 6, f"{pr[0]}-{pr[1]}", 6.8, "end", "#444", rotate=-90)
    rho_star = min(p["c_star"] / ((p["q_i"] * (1 - p["q_i"]) * p["q_j"] * (1 - p["q_j"])) ** 0.5)
                   for p in pairs if p["q_i"] > 0 and p["q_j"] > 0)
    e5 = E5_MAX_TAU / (E5_MARGINAL * (1 - E5_MARGINAL))
    xx = L + 10
    out.append(f'<line x1="{xx:.1f}" y1="{T - 2}" x2="{xx:.1f}" y2="{T - 15}" stroke="#555" stroke-width="1"/>')
    out.append(f'<path d="M {xx - 3.5:.1f} {T - 12} L {xx:.1f} {T - 19} L {xx + 3.5:.1f} {T - 12} Z" fill="#555"/>')
    text(xx + 7, T - 13, f"Far above this axis: largest simulated E5 setting, ρ = {e5:.2f};", 8.3, "start", "#444")
    text(xx + 7, T - 3, f"threshold where tensored mitigation becomes worse than none, ρ* = {rho_star:.2f} or more", 8.3, "start", "#444")
    text(L + PW / 2, T + PH + 38, "logical qubit pair", 9, "middle", "#222")
    text(14, T + PH / 2, "correlation coefficient ρ", 9, "middle", "#222", rotate=-90)
    lx, ly = L + 8, T + PH - 22
    for k, (circ, lab) in enumerate((("p4a_all0", "prepared all 0"), ("p4a_all1", "prepared all 1"))):
        out.append(f'<circle cx="{lx + 98 * k}" cy="{ly}" r="2.4" fill="{colors[circ]}"/>')
        text(lx + 6 + 98 * k, ly + 3, lab, 8.5)

    # ---------------- panel (b)
    L2, T2, S = 520, 40, 160
    vmax = 7.0
    xb = lambda v: L2 + v / vmax * S  # noqa: E731
    yb = lambda v: T2 + (vmax - v) / vmax * S  # noqa: E731
    text(L2 - 44, 14, "b", 12, weight="bold", fill="#111")
    text(L2 - 26, 14, "Reported errors miss measured flip rates", 10, fill="#111")
    for v in range(0, 8):
        out.append(f'<line x1="{xb(v):.1f}" y1="{T2}" x2="{xb(v):.1f}" y2="{T2 + S}" stroke="#eeeeee" stroke-width="1"/>')
        out.append(f'<line x1="{L2}" y1="{yb(v):.1f}" x2="{L2 + S}" y2="{yb(v):.1f}" stroke="#eeeeee" stroke-width="1"/>')
        if v % 2 == 0:
            text(xb(v), T2 + S + 12, str(v), 8.5, "middle", "#444")
            text(L2 - 5, yb(v) + 3, str(v), 8.5, "end", "#444")
    out.append(f'<rect x="{L2}" y="{T2}" width="{S}" height="{S}" fill="none" stroke="#999" stroke-width="1"/>')
    out.append(f'<line x1="{xb(0):.1f}" y1="{yb(0):.1f}" x2="{xb(vmax):.1f}" y2="{yb(vmax):.1f}" '
               'stroke="#222" stroke-width="1" stroke-dasharray="4 3"/>')
    text(xb(5.9), yb(6.35), "y = x", 8.5, "end", "#222")
    rep = m["selected_readout_errors"]
    rates = a["flip_rates_per_logical_qubit"]
    for k, q in enumerate(m["selected_physical_qubits"]):
        ys = [100 * rates[c][k] for c in hc.CIRCUITS]
        out.append(f'<line x1="{xb(100 * rep[k]):.1f}" y1="{yb(min(ys)):.1f}" x2="{xb(100 * rep[k]):.1f}" '
                   f'y2="{yb(max(ys)):.1f}" stroke="#9a9a9a" stroke-width="1"/>')
        for circ in hc.CIRCUITS:
            out.append(f'<circle cx="{xb(100 * rep[k]):.1f}" cy="{yb(100 * rates[circ][k]):.1f}" r="2.6" '
                       f'fill="{colors[circ]}" opacity="0.9"/>')
        if max(abs(y - 100 * rep[k]) for y in ys) > 2.5:
            text(xb(100 * rep[k]) + (-5 if rep[k] > 0.05 else 5), yb(max(ys)) - 4, f"q{q}", 8,
                 "end" if rep[k] > 0.05 else "start", "#444")
    text(L2 + S / 2, T2 + S + 26, "reported readout error (%)", 9, "middle", "#222")
    text(L2 - 26, T2 + S / 2, "measured flip rate (%)", 9, "middle", "#222", rotate=-90)
    out.append("</svg>")
    return "\n".join(out) + "\n"


def hc_pairs():
    import itertools

    return list(itertools.combinations(range(hc.WIDTH), 2))


def note(d: dict, n: dict) -> str:
    v = {k: val for k, (val, _) in n.items()}
    a = d["analysis"]
    m = d["manifest"]
    return f"""# Hardware readout amendment v1: results

Evidence type: hardware-derived (IBM Quantum backend {m['backend']}), exploratory with
respect to protocol v4 endpoints. Registered before any hardware data at OSF
[wh5rs](https://osf.io/wh5rs/) (package commit 88ae3a6, manifest SHA-256 ec1c54da...).
Generated by `experiments/synthesis/hw_paper_v4_1.py` from the immutable records.

**H-R1: {a['H_R1']}.** Relevance rejections: {v['HwRelRej']} of {v['HwTests']}
(Holm, alpha 0.05). Detection rejections: {v['HwDetRej']} of {v['HwTests']}; the
smallest Holm-adjusted detection p-value was {v['HwMinDetHolm']}.

- Backend {m['backend']}, calibration {m['calibration_timestamp']}; logical qubits 0-7 on
  physical qubits {m['selected_physical_qubits']}.
- Pilot: 2 x 1,000 shots, {v['HwPilotSec']} reported QPU s (job {d['pilot']['job_id']}).
  Median reported readout error {v['HwMedianErr']}% -> grid 0.01, S_min {v['HwSmin']}; GO.
- Main: one job, {v['HwShots']} shots per circuit, {v['HwMainSec']} reported QPU s
  (job {d['main']['job_id']}). Total {v['HwTotalSec']} of the 360-second cap.
- Largest |rho_hat| {v['HwMaxRho']}; largest c_hat/c* {v['HwMaxRatio']}; largest 95% upper
  bound of c divided by c* {v['HwMaxUpperRatio']}. For comparison, the largest E5 grid
  setting in simulation has rho {v['EfiveRho']} and c/c* {v['EfiveRatio']}.
- {v['HwCiExcl']} of {v['HwTests']} pair-preparations have an unadjusted 95% interval for c that
  excludes 0 (all with |rho| at most {v['HwMaxRho']}); none survives Holm correction.

Reported calibration readout error versus measured flip rate (percent):

{md_table(d)}

Independent recomputation (separate code, SciPy Fisher test, separate Holm and
bootstrap): tables 56/56, covariances 56/56, Fisher p-values 56/56 (largest relative
difference 2.5e-10), Holm decisions 56/56, and no relevance rejection with a different
bootstrap seed. Limitations: one backend, one day, preparations 00 and 11 only, qubits
chosen for low reported readout error (amendment Section 8).
"""


def main() -> int:
    d = load()
    n = numbers(d)
    lines = ["% Generated by experiments/synthesis/hw_paper_v4_1.py. Do not edit by hand."]
    lines += [f"\\newcommand{{\\num{k}}}{{{val}}} % {src}" for k, (val, src) in sorted(n.items())]
    (REPO / "paper" / OUTPUTS[0]).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (REPO / "figures" / OUTPUTS[1]).write_text(figure(d), encoding="utf-8", newline="\n")
    (REPO / "docs" / "results" / OUTPUTS[2]).write_text(note(d, n), encoding="utf-8", newline="\n")
    print("\n".join(f"{k} = {val}" for k, (val, _) in sorted(n.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

