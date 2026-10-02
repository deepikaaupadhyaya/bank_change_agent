# Supplier Bank-Change Agent — Blinded Evaluation (40 Simulated Cases)

Decision problem: each supplier bank-change request is APPROVE, VERIFY (out-of-band callback),
or ESCALATE (human controller). Hidden state = Genuine vs Fraud. SPF/DKIM/DMARC is a
near-zero signal (passes on full mailbox compromise) and must not drive the decision.

## Test set (30–50 requirement: 40 cases used)
Source: `data/supplier_bank_change_simulated_dataset.xlsx`, sheet `Simulated_Cases`.
32 Genuine / 8 Fraud. Columns: `case_id`, `hidden_state_TRUE_LABEL` (ground truth —
hidden from the agent, used only for scoring), `callback_verification`
(Confirmed/Failed/Not Attempted), `first_time_bank_change`, `urgency_language`,
`reply_to_mismatch`, `lookalike_domain`, `tone_deviation`, `spf_dkim_dmarc_pass`,
`payment_amount_usd`, `above_materiality_threshold_5k`.
SIMULATED data only — proportions are directional assumptions from practitioner
discussions, not measured statistics.

## Cost model (stated assumptions, not industry facts)
- APPROVE genuine = $0; APPROVE fraud = full `payment_amount_usd` (wire lost, unrecoverable).
- VERIFY = $150 (callback labor + delay); ESCALATE = $500 (controller review + hold/friction).
- Rationale: r/Accounting counter-signature threshold ~$5k feeds materiality; r/AI_Agents
  "verification costs minutes, wrong approval costs the invoice."

## Policies tested (label is hidden at decision time)
1. `bayesian_cost_sensitive` (agent A): one-step Bayesian posterior (POMDP-inspired
   framing, NOT a sequential POMDP solver — see Limitations) with a priori likelihoods
   (`src/agent.py`, prior fraud 0.10, NOT fitted to test labels) + expected-cost rule:
   ESCALATE if p≥0.65 or (amount>20k and p≥0.25 and p·amount≥150); APPROVE if p·amount<150
   and p<0.35; else VERIFY.
2. `rule_checklist` (agent B): red-flag score (Failed callback +2, lookalike +2,
   first-time/urgency/reply-to/tone/amount>5k +1 each, Not Attempted +1, SPF weight 0);
   ≥4 ESCALATE, 2–3 VERIFY, ≤1 APPROVE.
3. `baseline_spf` (baseline): APPROVE iff `spf_dkim_dmarc_pass=Yes`, else VERIFY.
   Tests whether email-auth alone suffices (it does not).
Reference ceilings (review PP2, not competing policies): `always_approve` (fraud-loss
upper bound) and `always_verify` (review-load upper bound).

## Measurements (accuracy is NOT the only metric)
Confusion matrix, Precision, Recall, False-positive count, False-negative count,
Human-review rate ((VERIFY+ESCALATE)/N), Decision cost, Calibration (ECE + binned
mean-predicted vs empirical fraud rate). Flagged = VERIFY or ESCALATE.

## Results (from `results/metrics.json`)
| Policy | Confusion TP/FP/TN/FN | Prec | Rec | FP | FN | Review rate | Total cost |
|---|---|---|---|---|---|---|---|
| bayesian_cost_sensitive | 8/6/26/0 | 0.571 | 1.000 | 6 | 0 | 0.350 (8V+6E) | $4,200 ($0 fraud loss) |
| rule_checklist | 8/13/19/0 | 0.381 | 1.000 | 13 | 0 | 0.525 (12V+9E) | $6,300 ($0 fraud loss) |
| baseline_spf | 1/1/31/7 | 0.500 | 0.125 | 1 | 7 | 0.050 (2V+0E) | $143,374 ($143,074 fraud loss) |
| always_approve (ref) | 0/0/32/8 | 0.000 | 0.000 | 0 | 8 | 0.000 | $150,736 (all fraud lost) |
| always_verify (ref) | 8/32/0/0 | 0.200 | 1.000 | 32 | 0 | 1.000 (40V) | $6,000 ($0 fraud loss) |
Calibration ECE: bayesian 0.038 (well-calibrated), rule 0.205 (over-flags low bins),
baseline 0.127 with no high-confidence coverage. Accuracy alone would rank baseline
(0.80) near bayesian (0.85) and hide the $139k cost gap — hence the multi-metric table.

## Failure analysis (6 named conditions, see `results/failure_analysis.md`)
F1 Stolen-Callback Confirmation (C034 fraud $54,729, baseline approved); F2 Urgency-Free
Sleeper (C009 fraud $56,875); F3 Repeat-Vendor Camouflage (C002 fraud $8,814);
F4 Stale-Contact False Alarm (C020 genuine, $150 waste); F5 Legitimate-Urgency Over-Triage
(C026 genuine, $150–$500); F6 Benign Anomaly Coincidence (C014 genuine, $150).
Highest-cost error: FALSE APPROVE of fraud (false negative) — $3k–$57k irreversible loss
per miss vs $150–$500 per false alarm — because wires are unrecoverable while delays are
resolved by one callback.

## Repeat instructions
1. Requirements: Python 3.14.3, `pip install openpyxl==3.1.5` (only dependency).
2. From this folder (`bank_change_agent/`):
   ```
   python3 experiments/run_experiment.py
   ```
   The script loads `data/supplier_bank_change_simulated_dataset.xlsx`, strips
   `hidden_state_TRUE_LABEL` before calling each policy in `src/agent.py` (label hiding
   is enforced in code: `evidence = {k:v ... if k != "hidden_state_TRUE_LABEL"}`),
   computes costs/metrics via `src/metrics.py`, and writes:
   - `results/predictions.csv` — one row per case×policy (40×5=200 rows): case_id,
     true_label, policy, action, p_fraud, flagged, correct, cost_usd, payment_amount_usd.
   - `results/metrics.json` + `results/metrics.md` — confusion, precision/recall/F1,
     FP/FN, review rates, decision costs, calibration bins + ECE.
3. Verify: check `results/predictions.csv` has 200 rows; `metrics.json` matches the table
   above (bayesian $4,200/0 FN, rule $6,300/0 FN, baseline $143,374/7 FN,
   always_approve $150,736, always_verify $6,000); `results/failure_analysis.md`
   documents ≥5 named failures; `review-record.md` logs all three AI reviews.
4. Re-tune (optional): edit likelihoods/thresholds in `src/agent.py`, re-run step 2,
   compare `total_cost_usd` and `false_negatives` — do not fit likelihoods to test labels.

## Limitations & sensitivity (from `review-record.md` AI reviews — read before deploying)

- **Assumed costs, not measured (PR1/PB6):** VERIFY=$150, ESCALATE=$500, fraud loss =
  full amount (zero recovery). Re-tune from local labor rates and use
  loss = amount × (1 − recovery rate); hold cost should scale with amount/terms (PR5).
- **Prior vs prevalence (PB1):** agent prior P(Fraud)=0.10 is a priori; test prevalence is
  0.20. ECE is conditional on this gap. Sensitivity: re-run with prior 0.05/0.20 and
  confirm the zero-FN policy survives.
- **Invented likelihoods + independence (PB2/PB3):** all LRs are directional assumptions;
  naive Bayes double-counts correlated pairs (first-time∧urgency, lookalike∧tone).
  Sensitivity: perturb each LR ±50% (halve Failed-callback 30→15) and re-check recall.
- **Hand-picked thresholds (PB5):** 0.35/0.65 + $20k guard were not swept. Next version:
  sweep thresholds on a separate validation split against total cost.
- **Small-n calibration (PB7):** ECE bins hold n=1–3 cases — indicative only, not precise.
- **One-step, not sequential (PP3):** no POMDP solver or value iteration; claims are
  worded as POMDP-inspired accordingly.
- **Single 40-case split (PP4):** no holdout/replication; results could be demo-luck.
- **Capacity (PR4):** 35–52% review rates exceed realistic human budgets (~10 deep
  reviews/week) and risk rubber-stamping. Thresholds must be set downstream of a stated
  capacity budget.
- **Stale master data (PR3):** the "known number" is trusted but never verified (see
  failures F1/F4). Number changes need a separate authorization path.
- **Missing stakeholders (PR2):** supplier (delay harm), bank (recall window), auditor
  (segregation evidence) — per-decision audit fields are specified in
  `decisions/probability-decision-record.md` §6.
- **Ethics (PP5):** all cases are SIMULATED; amounts must never be quoted as real fraud data.

## File map
`src/agent.py`, `src/metrics.py`, `experiments/run_experiment.py`,
`data/supplier_bank_change_simulated_dataset.xlsx`, `results/predictions.csv`,
`results/metrics.json`, `results/metrics.md`, `results/failure_analysis.md`,
`decisions/probability-decision-record.md`, `paper/`, `social/`.
