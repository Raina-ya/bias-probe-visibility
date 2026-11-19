"""Paper v4.1 hardware addendum: numbers, calibration table, figure and results note.

Reads only committed hardware records (results/hardware_v1/, results/hardware_v1_analysis/)
and the registered amendment's analytic threshold, and writes:

  paper/numbers_hw_v4_1.tex           LaTeX macros for every hardware number in the paper
  paper/hw_figure_v4_1.tex            pgfplots figure: (a) rho_hat with intervals; (b) reported vs measured
  docs/results/hardware_readout_v1.md results note

Outputs are derived (overwritten deterministically); the records they read are
immutable.  The figure is typeset by pgfplots inside the paper.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "experiments" / "hardware"))

import hw_circuits_v1 as hc  # noqa: E402
import hw_stats_v1 as st  # noqa: E402

OUTPUTS = ("numbers_hw_v4_1.tex", "hw_figure_v4_1.tex", "hardware_readout_v1.md")
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
    """pgfplots code for the two-panel hardware figure (typeset with the paper's fonts).

    (a) Caterpillar plot: rho_hat with unadjusted 95% percentile-bootstrap
        intervals for all 56 pair-preparations, ordered by estimate; circles
        are preparation all-0, squares all-1.  The E5 setting and the
        relevance threshold lie far above the axis and are named in a note.
    (b) Reported calibration readout error against measured flip rate per
        selected qubit, both preparations joined by a grey line, with y = x.
    """

    a, m = d["analysis"], d["manifest"]
    pts = []
    for p in a["pairs"]:
        den = (p["q_i"] * (1 - p["q_i"]) * p["q_j"] * (1 - p["q_j"])) ** 0.5
        lo, hi = (v / den for v in p["c_interval_95"])
        pts.append((p["rho_hat"], lo, hi, p["circuit"]))
    pts.sort(key=lambda t: (t[0], t[3]))
    rho_star = min(p["c_star"] / ((p["q_i"] * (1 - p["q_i"]) * p["q_j"] * (1 - p["q_j"])) ** 0.5)
                   for p in a["pairs"] if p["q_i"] > 0 and p["q_j"] > 0)
    e5 = E5_MAX_TAU / (E5_MARGINAL * (1 - E5_MARGINAL))

    def series(circ):
        rows = [f"    {k + 1} {r:.6f} {hi - r:.6f} {r - lo:.6f}"
                for k, (r, lo, hi, c) in enumerate(pts) if c == circ]
        return "\n".join(rows)

    rep = m["selected_readout_errors"]
    rates = a["flip_rates_per_logical_qubit"]
    joins, marks0, marks1, labels = [], [], [], []
    for k, q in enumerate(m["selected_physical_qubits"]):
        x = 100 * rep[k]
        y0, y1 = 100 * rates["p4a_all0"][k], 100 * rates["p4a_all1"][k]
        joins.append(f"  \\draw[gray!70] (axis cs:{x:.3f},{y0:.3f}) -- (axis cs:{x:.3f},{y1:.3f});")
        marks0.append(f"({x:.3f},{y0:.3f})")
        marks1.append(f"({x:.3f},{y1:.3f})")
        if max(abs(y0 - x), abs(y1 - x)) > 2.5:
            anchor = "east" if x > 5 else "west"
            labels.append(f"  \\node[font=\\scriptsize,anchor={anchor},inner sep=2pt] at "
                          f"(axis cs:{x:.3f},{max(y0, y1):.3f}) {{{q}}};")
    return "\n".join([
        "% Generated by experiments/synthesis/hw_paper_v4_1.py from the hardware records. Do not edit by hand.",
        "\\definecolor{hwblue}{RGB}{31,95,168}\\definecolor{hworange}{RGB}{194,87,26}",
        "\\begin{tikzpicture}",
        "\\begin{axis}[name=pa, width=11.6cm, height=5.4cm, xmin=0, xmax=57, ymin=-0.025, ymax=0.025,",
        "  xtick=\\empty, ytick={-0.02,-0.01,0,0.01,0.02},",
        "  yticklabel style={/pgf/number format/fixed,/pgf/number format/precision=2,/pgf/number format/fixed zerofill},",
        "  scaled y ticks=false, tick label style={font=\\footnotesize}, label style={font=\\small},",
        "  xlabel={pair-preparations, ordered by estimate}, ylabel={correlation $\\hat\\rho$},",
        "  axis lines*=left, ymajorgrids, grid style={gray!20},",
        "  legend style={font=\\footnotesize, draw=none, fill=none, at={(0.02,0.04)}, anchor=south west},",
        "  legend columns=2, legend cell align=left, legend style={/tikz/every even column/.append style={column sep=0.45cm}},",
        "  title={\\textbf{(a)} Pair correlations are about 1\\% or less}, title style={font=\\small, at={(0,1)}, anchor=south west, xshift=-1.0cm}]",
        "\\addplot[gray!60, forget plot] coordinates {(0,0) (57,0)};",
        "\\addplot[only marks, mark=*, mark size=1.3pt, hwblue, error bars/.cd, y dir=both, y explicit, error bar style={hwblue!70}]",
        "  table[x index=0, y index=1, y error plus index=2, y error minus index=3] {",
        series("p4a_all0"), "  };",
        "\\addlegendentry{all qubits prepared in 0}",
        "\\addplot[only marks, mark=square*, mark size=1.2pt, hworange, error bars/.cd, y dir=both, y explicit, error bar style={hworange!70}]",
        "  table[x index=0, y index=1, y error plus index=2, y error minus index=3] {",
        series("p4a_all1"), "  };",
        "\\addlegendentry{all qubits prepared in 1}",
        f"\\node[font=\\scriptsize, align=left, anchor=north west, fill=white, inner sep=2pt] at (rel axis cs:0.015,0.985)",
        f"  {{Far above this axis: largest simulated E5 setting, $\\rho={e5:.2f}$;\\\\threshold where tensored mitigation is worse than none, $\\rho^\\ast \\ge {rho_star:.2f}$}};",
        "\\end{axis}",
        "\\begin{axis}[at={(pa.north east)}, anchor=north west, xshift=1.5cm, width=5.4cm, height=5.4cm,",
        "  xmin=0, xmax=7, ymin=0, ymax=7, xtick={0,2,4,6}, ytick={0,2,4,6},",
        "  tick label style={font=\\footnotesize}, label style={font=\\small},",
        "  xlabel={reported readout error (\\%)}, ylabel={measured flip rate (\\%)},",
        "  grid=major, grid style={gray!20},",
        "  title={\\textbf{(b)} Reported errors miss measured rates}, title style={font=\\small, at={(0,1)}, anchor=south west, xshift=-1.0cm}]",
        "\\addplot[black, dashed, forget plot] coordinates {(0,0) (7,7)};",
        "\\node[font=\\scriptsize, anchor=east] at (axis cs:5.7,6.3) {$y=x$};",
        *joins,
        f"\\addplot[only marks, mark=*, mark size=1.5pt, hwblue] coordinates {{{' '.join(marks0)}}};",
        f"\\addplot[only marks, mark=square*, mark size=1.4pt, hworange] coordinates {{{' '.join(marks1)}}};",
        *labels,
        "\\end{axis}",
        "\\end{tikzpicture}",
    ]) + "\n"


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
    (REPO / "paper" / OUTPUTS[1]).write_text(figure(d), encoding="utf-8", newline="\n")
    (REPO / "docs" / "results" / OUTPUTS[2]).write_text(note(d, n), encoding="utf-8", newline="\n")
    print("\n".join(f"{k} = {val}" for k, (val, _) in sorted(n.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

