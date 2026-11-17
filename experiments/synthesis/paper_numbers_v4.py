"""Generate paper/numbers_v4.tex: every result number printed in the manuscript.

Each LaTeX macro is computed from a committed result file, so a number is given
in one place and can be traced to its source (claim ledger).  The manuscript
uses only these macros for results.  Run after all result files exist; the
output is overwritten deterministically (it is derived, not raw data).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "paper" / "numbers_v4.tex"
SOURCES = {
    "primary": "results/holdout_v4/primary_endpoint_v4.json",
    "secondary": "results/holdout_v4/secondary_endpoints_v4.json",
    "synthesis": "results/synthesis/boundary_synthesis_v4.json",
    "prop1": "results/prop1/prop1_scoring_v4.json",
}


def f(x: float | None, d: int = 3) -> str:
    return "n/a" if x is None else f"{x:.{d}f}"


def s(x: float, d: int = 4) -> str:
    return f"{x:+.{d}f}"


def numbers() -> dict[str, tuple[str, str]]:
    j = {
        k: json.loads((REPO / v).read_text(encoding="utf-8"))
        for k, v in SOURCES.items()
    }
    pm = j["primary"]["primary_designated"]["main"]
    pp = j["primary"]["primary_designated"]["per_structure"]
    p2 = j["primary"]["secondary_structure_agnostic_P2"]["main"]
    sec = j["secondary"]
    cov, pooled = sec["coverage"], sec["coverage_pooled"]
    ag = sec["visibility"]["agreement"]
    flip = sec["flip_subset"]
    cert = sec["readout_certificate"]
    syn = j["synthesis"]
    q = j["prop1"]["summary"]
    graphs = j["prop1"]["graphs"]
    causes = {}
    for c in syn["cells"]:
        if c["cause"]:
            causes[c["cause"]] = causes.get(c["cause"], 0) + 1
    n = {
        "dFC": (s(pm["dFC"]), "primary.main.dFC"),
        "dFClo": (s(pm["dFC_lower_2.5"]), "primary.main.dFC_lower_2.5"),
        "dFChi": (s(pm["dFC_upper_97.5"]), "primary.main.dFC_upper_97.5"),
        "FCzero": (f(pm["FC_R0_pooled"], 4), "primary.main.FC_R0_pooled"),
        "FCzeroUp": (f(pm["FC_R0_upper_97.5"], 4), "primary.main.FC_R0_upper_97.5"),
        "CovLoss": (f(pm["coverage_loss_pooled"]), "primary.main.coverage_loss_pooled"),
        "CovLossLo": (
            f(pooled["R1"]["loss_ci"][0]),
            "secondary.coverage_pooled.R1.loss_ci[0]",
        ),
        "CovLossHi": (
            f(pooled["R1"]["loss_ci"][1]),
            "secondary.coverage_pooled.R1.loss_ci[1]",
        ),
        "InterPooled": (
            f(pooled["R1"]["interception"]),
            "secondary.coverage_pooled.R1.interception",
        ),
        "InterUnits": (
            str(pooled["R1"]["interception_units"]),
            "secondary.coverage_pooled.R1.interception_units",
        ),
        "PtwodFC": (s(p2["dFC"]), "primary.P2.dFC"),
        "PtwodFClo": (s(p2["dFC_lower_2.5"]), "primary.P2.dFC_lower_2.5"),
        "PtwodFChi": (s(p2["dFC_upper_97.5"]), "primary.P2.dFC_upper_97.5"),
        "PtwoLoss": (
            f(pooled["R1_P2"]["loss"]),
            "secondary.coverage_pooled.R1_P2.loss",
        ),
        "PtwoLossLo": (
            f(pooled["R1_P2"]["loss_ci"][0]),
            "secondary.coverage_pooled.R1_P2.loss_ci[0]",
        ),
        "PtwoLossHi": (
            f(pooled["R1_P2"]["loss_ci"][1]),
            "secondary.coverage_pooled.R1_P2.loss_ci[1]",
        ),
        "PtwoInter": (
            f(pooled["R1_P2"]["interception"]),
            "secondary.coverage_pooled.R1_P2.interception",
        ),
        "AgInv": (
            f(ag["invariant"]["point"]),
            "secondary.visibility.agreement.invariant.point",
        ),
        "AgInvLo": (
            f(ag["invariant"]["ci"][0]),
            "secondary.visibility.agreement.invariant.ci[0]",
        ),
        "AgInvHi": (
            f(ag["invariant"]["ci"][1]),
            "secondary.visibility.agreement.invariant.ci[1]",
        ),
        "AgSen": (
            f(ag["sensitive"]["point"]),
            "secondary.visibility.agreement.sensitive.point",
        ),
        "AgSenLo": (
            f(ag["sensitive"]["ci"][0]),
            "secondary.visibility.agreement.sensitive.ci[0]",
        ),
        "AgSenHi": (
            f(ag["sensitive"]["ci"][1]),
            "secondary.visibility.agreement.sensitive.ci[1]",
        ),
        "AgInvN": (
            str(round(ag["invariant"]["point"] * 23)),
            "secondary agreement x 23",
        ),
        "AgSenN": (
            str(round(ag["sensitive"]["point"] * 19)),
            "secondary agreement x 19",
        ),
        "AgInvSmall": (
            str(sec["visibility"]["agreement_smallest_strength"]["invariant"]),
            "secondary.agreement_smallest_strength.invariant",
        ),
        "AgSenSmall": (
            str(sec["visibility"]["agreement_smallest_strength"]["sensitive"]),
            "secondary.agreement_smallest_strength.sensitive",
        ),
        "DevHoldSame": (
            str(syn["dev_holdout_label_agreement"]),
            "synthesis.dev_holdout_label_agreement",
        ),
        "PfiveEonePower": (
            f(sec["visibility"]["cells"]["P5/E1"]["power"]),
            "secondary.cells.P5/E1.power",
        ),
        "PtwoEfpPower": (
            f(sec["visibility"]["cells"]["P2/E5'"]["power"]),
            "secondary.cells.P2/E5'.power",
        ),
        "PtwoEfpFA": (
            f(sec["visibility"]["cells"]["P2/E5'"]["false_alarm"]),
            "secondary.cells.P2/E5'.false_alarm",
        ),
        "PoneEonePower": (
            f(sec["visibility"]["cells"]["P1/E1"]["power"], 2),
            "secondary.cells.P1/E1.power",
        ),
        "PthreeEthreePower": (
            f(sec["visibility"]["cells"]["P3/E3"]["power"], 2),
            "secondary.cells.P3/E3.power",
        ),
        "PfourbEfivePower": (
            f(sec["visibility"]["cells"]["P4b/E5"]["power"]),
            "secondary.cells.P4b/E5.power",
        ),
        "EoneFlipped": (
            str(flip["E1"]["flipped_graphs"]),
            "secondary.flip_subset.E1.flipped_graphs",
        ),
        "EoneFlipAlarm": (
            f(flip["E1"]["flipped"]["alarm_rate"]),
            "secondary.flip_subset.E1.flipped.alarm_rate",
        ),
        "EoneNoFlipAlarm": (
            f(flip["E1"]["not_flipped"]["alarm_rate"]),
            "secondary.flip_subset.E1.not_flipped.alarm_rate",
        ),
        "EthreeFlipped": (
            str(flip["E3"]["flipped_graphs"]),
            "secondary.flip_subset.E3.flipped_graphs",
        ),
        "EthreeFlipAlarm": (
            f(flip["E3"]["flipped"]["alarm_rate"]),
            "secondary.flip_subset.E3.flipped.alarm_rate",
        ),
        "EthreeNoFlipAlarm": (
            f(flip["E3"]["not_flipped"]["alarm_rate"]),
            "secondary.flip_subset.E3.not_flipped.alarm_rate",
        ),
        "EtwoFlipAlarm": (
            f(flip["E2"]["flipped"]["alarm_rate"]),
            "secondary.flip_subset.E2.flipped.alarm_rate",
        ),
        "EtwoNoFlipAlarm": (
            f(flip["E2"]["not_flipped"]["alarm_rate"]),
            "secondary.flip_subset.E2.not_flipped.alarm_rate",
        ),
        "CertEfourUnres": (
            f(cert["P4a/E4"]["certificate"]["unresolved"]),
            "secondary.readout_certificate.P4a/E4.certificate.unresolved",
        ),
        "CertEfourRzero": (
            f(cert["P4a/E4"]["R0"]["unresolved"]),
            "secondary.readout_certificate.P4a/E4.R0.unresolved",
        ),
        "CertEfiveUnres": (
            f(cert["P4b/E5"]["certificate"]["unresolved"]),
            "secondary.readout_certificate.P4b/E5.certificate.unresolved",
        ),
        "CertEfiveRzero": (
            f(cert["P4b/E5"]["R0"]["unresolved"]),
            "secondary.readout_certificate.P4b/E5.R0.unresolved",
        ),
        "PoneHits": (str(q["hits"]), "prop1.summary.hits"),
        "PoneRate": (f(q["hit_rate"], 2), "prop1.summary.hit_rate"),
        "PoneLo": (f(q["wilson_95"][0]), "prop1.summary.wilson_95[0]"),
        "PoneHi": (f(q["wilson_95"][1]), "prop1.summary.wilson_95[1]"),
        "PoneTies": (str(q["ties"]), "prop1.summary.ties"),
        "PoneZneBetter": (
            str(q["zne_better_observed"]),
            "prop1.summary.zne_better_observed",
        ),
        "PoneTieZero": (
            str(sum(g["tie"] and g["error_rate_raw"] == 0 for g in graphs)),
            "prop1.graphs: ties with zero errors",
        ),
        "PoneErrRaw": (
            f(sum(g["error_rate_raw"] for g in graphs) / len(graphs)),
            "prop1.graphs mean error_rate_raw",
        ),
        "PoneErrZne": (
            f(sum(g["error_rate_zne"] for g in graphs) / len(graphs)),
            "prop1.graphs mean error_rate_zne",
        ),
        "PoneSep": (
            str(q["by_reason"]["raw_separated"]["graphs"]),
            "prop1.by_reason.raw_separated.graphs",
        ),
        "PoneUnc": (
            str(q["by_reason"]["uncertified_raw_default"]["graphs"]),
            "prop1.by_reason.uncertified_raw_default.graphs",
        ),
        "PoneUnr": (
            str(q["by_reason"]["unresolved_anchor"]["graphs"]),
            "prop1.by_reason.unresolved_anchor.graphs",
        ),
        "CauseResources": (
            str(causes.get("resources", 0)),
            "synthesis.cells cause=resources",
        ),
        "CauseModel": (str(causes.get("model", 0)), "synthesis.cells cause=model"),
        "CauseMethod": (str(causes.get("method", 0)), "synthesis.cells cause=method"),
        "CauseDesign": (str(causes.get("design", 0)), "synthesis.cells cause=design"),
        "PonebEone": (f(syn["p1b_exploratory_power"]["E1"], 2), "synthesis.p1b.E1"),
        "PonebEthree": (f(syn["p1b_exploratory_power"]["E3"], 2), "synthesis.p1b.E3"),
    }
    for stratum, key in (("invariant", "DevAgInv"), ("sensitive", "DevAgSen")):
        n[key] = (
            str(sum(c["development"] == c["predicted"] for c in syn["cells"] if c["stratum"] == stratum)),
            f"synthesis.cells development==predicted, {stratum}",
        )
    n["FCGraphs"] = (
        str(sum(v["R0_false_cert_graphs"] for v in pp.values())),
        "primary.per_structure sum of R0_false_cert_graphs",
    )
    for st in ("E1", "E2", "E3"):
        key = st.replace("E1", "Eone").replace("E2", "Etwo").replace("E3", "Ethree")
        n[f"{key}FCzero"] = (f(pp[st]["FC_R0"], 4), f"primary.per_structure.{st}.FC_R0")
        n[f"{key}FCone"] = (f(pp[st]["FC_R1"], 4), f"primary.per_structure.{st}.FC_R1")
        n[f"{key}Graphs"] = (
            str(pp[st]["R0_false_cert_graphs"]),
            f"primary.per_structure.{st}.R0_false_cert_graphs",
        )
        n[f"{key}Certs"] = (
            str(pp[st]["R0_false_certifications"]),
            f"primary.per_structure.{st}.R0_false_certifications",
        )
        n[f"{key}Inter"] = (
            f(cov[st]["interception_R1"]),
            f"secondary.coverage.{st}.interception_R1",
        )
        n[f"{key}Czero"] = (f(cov[st]["C_R0"]), f"secondary.coverage.{st}.C_R0")
        n[f"{key}Cone"] = (f(cov[st]["C_R1"]), f"secondary.coverage.{st}.C_R1")
        n[f"{key}PtwoInter"] = (
            f(cov[st]["interception_R1_P2"])
            if cov[st]["interception_R1_P2"] is not None
            else "n/a",
            f"secondary.coverage.{st}.interception_R1_P2",
        )
    return n


def main() -> int:
    n = numbers()
    lines = [
        "% Generated by experiments/synthesis/paper_numbers_v4.py. Do not edit by hand."
    ]
    for path in SOURCES.values():
        lines.append(f"% source: {path}")
    for name, (value, source) in sorted(n.items()):
        lines.append(f"\\newcommand{{\\num{name}}}{{{value}}} % {source}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(n)} macros to {OUT.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
