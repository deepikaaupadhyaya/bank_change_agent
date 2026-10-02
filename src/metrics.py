"""Metrics: confusion, precision/recall, FP/FN, review rate, cost, calibration."""
from __future__ import annotations


def confusion(records: list[dict]) -> dict:
    # flagged = VERIFY or ESCALATE treated as "predict fraud"
    tp = sum(1 for r in records if r["flagged"] and r["true_label"] == "Fraud")
    fp = sum(1 for r in records if r["flagged"] and r["true_label"] == "Genuine")
    tn = sum(1 for r in records if not r["flagged"] and r["true_label"] == "Genuine")
    fn = sum(1 for r in records if not r["flagged"] and r["true_label"] == "Fraud")
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn}


def prf(c: dict) -> dict:
    precision = c["TP"] / (c["TP"] + c["FP"]) if (c["TP"] + c["FP"]) else 0.0
    recall = c["TP"] / (c["TP"] + c["FN"]) if (c["TP"] + c["FN"]) else 0.0
    acc = (c["TP"] + c["TN"]) / max(1, c["TP"] + c["FP"] + c["TN"] + c["FN"])
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}


def review_rates(records: list[dict]) -> dict:
    n = len(records)
    verify = sum(1 for r in records if r["action"] == "VERIFY")
    escalate = sum(1 for r in records if r["action"] == "ESCALATE")
    return {
        "n": n,
        "verify": verify,
        "escalate": escalate,
        "human_review_rate": (verify + escalate) / n if n else 0.0,  # any human touch
        "escalate_only_rate": escalate / n if n else 0.0,
    }


def decision_cost(records: list[dict], verify_cost=150.0, escalate_cost=500.0) -> dict:
    total = sum(r["cost_usd"] for r in records)
    fraud_loss = sum(r["cost_usd"] for r in records if r["true_label"] == "Fraud" and r["action"] == "APPROVE")
    return {"total_cost_usd": total, "fraud_loss_usd": fraud_loss,
            "avg_cost_per_case_usd": total / len(records) if records else 0.0}


def calibration(records: list[dict], bins=((0.0, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 1.01))) -> dict:
    out = []
    ece_num = 0.0
    n = len(records)
    for lo, hi in bins:
        b = [r for r in records if lo <= r["p_fraud"] < hi]
        if not b:
            out.append({"bin": [lo, hi], "n": 0, "mean_pred": None, "empirical_rate": None})
            continue
        mean_pred = sum(r["p_fraud"] for r in b) / len(b)
        emp = sum(1 for r in b if r["true_label"] == "Fraud") / len(b)
        out.append({"bin": [lo, hi], "n": len(b), "mean_pred": round(mean_pred, 3),
                    "empirical_rate": round(emp, 3)})
        ece_num += len(b) / n * abs(mean_pred - emp)
    return {"bins": out, "ece": round(ece_num, 3)}
