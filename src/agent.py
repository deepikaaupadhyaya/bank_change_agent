"""Bank-change agent policies — POMDP-inspired ONE-STEP decision (review PP3).

One-step only: Bayesian belief update over {Genuine, Fraud} + expected-cost action.
No sequential planning, belief-space solver, or value iteration is implemented;
"POMDP" here means the framing (hidden state, observations, costs), not a solver.
All policies take ONLY observable evidence (no true label).
Hidden state: genuine vs fraud. Actions: APPROVE, VERIFY, ESCALATE.
"""

PRIOR_FRAUD = 0.10  # assumed base rate, set a priori (not fitted to test set)

VERIFY_COST = 150.0    # USD: ~5-min callback + delay/friction
ESCALATE_COST = 500.0  # USD: controller review + vendor friction + hold

# Likelihood tables: P(feature_value | Fraud), P(feature_value | Genuine).
# Set A PRIORI from practitioner-discussion direction (README), not learned
# from test labels, to avoid train-on-test leakage.
# SPF nuance (review PB4): the "weak signal" claim concerns the PASS outcome
# (LR 0.90/0.95 = 0.947 ~= 1, i.e. near-non-informative, as on a fully
# compromised mailbox). The rare No outcome carries weak-moderate signal
# (LR 2.0) by assumption; magnitude flagged for sensitivity review.
LIKELIHOODS = {
    "callback_verification": {
        "Failed": (0.60, 0.02),
        "Confirmed": (0.05, 0.70),
        "Not Attempted": (0.35, 0.28),
    },
    "first_time_bank_change": {"Yes": (0.75, 0.20), "No": (0.25, 0.80)},
    "urgency_language": {"Yes": (0.55, 0.15), "No": (0.45, 0.85)},
    "reply_to_mismatch": {"Yes": (0.30, 0.08), "No": (0.70, 0.92)},
    "lookalike_domain": {"Yes": (0.70, 0.01), "No": (0.30, 0.99)},
    "tone_deviation": {"Yes": (0.50, 0.08), "No": (0.50, 0.92)},
    "spf_dkim_dmarc_pass": {"Yes": (0.90, 0.95), "No": (0.10, 0.05)},
    "above_materiality_threshold_5k": {"Yes": (0.65, 0.55), "No": (0.35, 0.45)},
}

EVIDENCE_COLS = list(LIKELIHOODS.keys())


def posterior_fraud(evidence: dict) -> float:
    """Naive-Bayes posterior P(fraud | evidence). Evidence dict has no label."""
    prior_f, prior_g = PRIOR_FRAUD, 1 - PRIOR_FRAUD
    lik_f, lik_g = prior_f, prior_g
    for col in EVIDENCE_COLS:
        val = str(evidence.get(col, ""))
        table = LIKELIHOODS[col]
        if val not in table:
            continue
        pf, pg = table[val]
        lik_f *= pf
        lik_g *= pg
    return lik_f / (lik_f + lik_g) if (lik_f + lik_g) > 0 else prior_f


def policy_bayesian_cost_sensitive(evidence: dict) -> tuple[str, float]:
    """Policy A (agent): Bayesian posterior + expected-cost thresholds.

    E[cost APPROVE] = p(fraud) * amount. VERIFY=$150, ESCALATE=$500.
    Escalate directly on very high posterior or high-value uncertain cases.
    """
    p = posterior_fraud(evidence)
    try:
        amount = float(evidence.get("payment_amount_usd", 0) or 0)
    except (TypeError, ValueError):
        amount = 0.0
    exp_approve_cost = p * amount
    if p >= 0.65:
        return "ESCALATE", p
    if amount > 20000 and p >= 0.25 and exp_approve_cost >= VERIFY_COST:
        return "ESCALATE", p
    if exp_approve_cost < VERIFY_COST and p < 0.35:
        return "APPROVE", p
    return "VERIFY", p


def policy_rule_checklist(evidence: dict) -> tuple[str, float]:
    """Policy B (agent): deterministic red-flag checklist. SPF weight = 0."""
    score = 0
    cb = str(evidence.get("callback_verification", ""))
    if cb == "Failed":
        score += 2
    elif cb == "Not Attempted":
        score += 1
    if str(evidence.get("first_time_bank_change")) == "Yes":
        score += 1
    if str(evidence.get("urgency_language")) == "Yes":
        score += 1
    if str(evidence.get("reply_to_mismatch")) == "Yes":
        score += 1
    if str(evidence.get("lookalike_domain")) == "Yes":
        score += 2
    if str(evidence.get("tone_deviation")) == "Yes":
        score += 1
    if str(evidence.get("above_materiality_threshold_5k")) == "Yes":
        score += 1
    # SPF deliberately ignored (weak signal per research)
    if score >= 4:
        action = "ESCALATE"
    elif score >= 2:
        action = "VERIFY"
    else:
        action = "APPROVE"
    pseudo_p = min(0.05 + score * 0.12, 0.95)  # for calibration comparison only
    return action, pseudo_p


def policy_baseline_spf(evidence: dict) -> tuple[str, float]:
    """Baseline B0: naive email-auth heuristic. APPROVE iff SPF/DKIM/DMARC pass."""
    if str(evidence.get("spf_dkim_dmarc_pass")) == "Yes":
        return "APPROVE", 0.05
    return "VERIFY", 0.50
