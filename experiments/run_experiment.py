"""Run blinded evaluation: hide label, apply policies, save predictions + metrics.

Usage:
    python3 experiments/run_experiment.py
Reads:  data/supplier_bank_change_simulated_dataset.xlsx (sheet Simulated_Cases)
Writes: results/predictions.csv, results/metrics.json, results/metrics.md
"""
import csv
import json
import sys
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))

from agent import (  # noqa: E402
    ESCALATE_COST,
    PRIOR_FRAUD,
    VERIFY_COST,
    policy_baseline_spf,
    policy_bayesian_cost_sensitive,
    policy_rule_checklist,
)
from metrics import calibration, confusion, decision_cost, prf, review_rates  # noqa: E402

def policy_always_approve(evidence: dict) -> tuple[str, float]:
    """Reference ceiling: pay everything. Fraud-loss upper bound (review PP2)."""
    return "APPROVE", PRIOR_FRAUD


def policy_always_verify(evidence: dict) -> tuple[str, float]:
    """Reference ceiling: callback on everything. Review-load upper bound (PP2)."""
    return "VERIFY", 0.50  # maximal uncertainty: no discrimination claimed


POLICIES = {
    "bayesian_cost_sensitive": policy_bayesian_cost_sensitive,
    "rule_checklist": policy_rule_checklist,
    "baseline_spf": policy_baseline_spf,
    "always_approve": policy_always_approve,
    "always_verify": policy_always_verify,
}

DATA = BASE / "data" / "supplier_bank_change_simulated_dataset.xlsx"
OUT_PRED = BASE / "results" / "predictions.csv"
OUT_JSON = BASE / "results" / "metrics.json"
OUT_MD = BASE / "results" / "metrics.md"


def load_cases():
    wb = openpyxl.load_workbook(DATA, data_only=True)
    ws = wb["Simulated_Cases"]
    rows = list(ws.iter_rows(values_only=True))
    header = [str(h) for h in rows[0]]
    cases = [dict(zip(header, r)) for r in rows[1:] if r[0] is not None]
    assert 30 <= len(cases) <= 50, f"need 30-50 cases, got {len(cases)}"
    return cases


def case_cost(action: str, true_label: str, amount: float) -> float:
    if action == "APPROVE" and true_label == "Fraud":
        return float(amount)  # wire lost
    if action == "VERIFY":
        return VERIFY_COST
    if action == "ESCALATE":
        return ESCALATE_COST
    return 0.0  # APPROVE genuine


def main():
    cases = load_cases()
    records = []
    for case in cases:
        true_label = str(case["hidden_state_TRUE_LABEL"])
        amount = float(case.get("payment_amount_usd") or 0)
        # HIDE label: build evidence dict without it
        evidence = {k: v for k, v in case.items() if k != "hidden_state_TRUE_LABEL"}
        for pname, pfn in POLICIES.items():
            action, p = pfn(evidence)  # policy never sees true_label
            flagged = action in ("VERIFY", "ESCALATE")
            correct = (flagged and true_label == "Fraud") or (action == "APPROVE" and true_label == "Genuine")
            records.append({
                "case_id": case["case_id"],
                "true_label": true_label,
                "policy": pname,
                "action": action,
                "p_fraud": round(float(p), 4),
                "flagged": flagged,
                "correct": correct,
                "cost_usd": case_cost(action, true_label, amount),
                "payment_amount_usd": amount,
            })

    OUT_PRED.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PRED, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    summary = {}
    for pname in POLICIES:
        recs = [r for r in records if r["policy"] == pname]
        c = confusion(recs)
        summary[pname] = {
            "n": len(recs),
            "confusion": c,
            **{k: round(v, 3) for k, v in prf(c).items()},
            "false_positives": c["FP"],
            "false_negatives": c["FN"],
            **review_rates(recs),
            **decision_cost(recs),
            "calibration": calibration(recs),
        }

    with open(OUT_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    lines = ["# Metrics (40 simulated cases; 32 Genuine / 8 Fraud)", ""]
    for pname, m in summary.items():
        lines += [f"## {pname} (n={m['n']})",
                  f"- Confusion: TP={m['confusion']['TP']} FP={m['confusion']['FP']} "
                  f"TN={m['confusion']['TN']} FN={m['confusion']['FN']}",
                  f"- Accuracy={m['accuracy']} Precision={m['precision']} Recall={m['recall']} F1={m['f1']}",
                  f"- False positives={m['false_positives']} False negatives={m['false_negatives']}",
                  f"- Human-review rate={m['human_review_rate']:.3f} "
                  f"(verify={m['verify']}, escalate={m['escalate']})",
                  f"- Total decision cost=${m['total_cost_usd']:,.0f} "
                  f"(fraud loss=${m['fraud_loss_usd']:,.0f}, avg=${m['avg_cost_per_case_usd']:,.0f}/case)",
                  f"- Calibration ECE={m['calibration']['ece']}; bins={m['calibration']['bins']}", ""]
    OUT_MD.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {OUT_PRED}, {OUT_JSON}, {OUT_MD}")


if __name__ == "__main__":
    main()
