# Probability Decision Record — Worked Uncertain Case C030

Case: **C030** (true label hidden from agent at decision time; revealed only for scoring: Fraud).
Why this case: most uncertain fraud in the set — Bayesian posterior **36.13%** (neither
near 0 nor near 1), conflicting evidence (first-time + urgency point to fraud;
lookalike-No + tone-No point to genuine), callback not yet attempted, amount $7,662.
Policy: `bayesian_cost_sensitive` in `src/agent.py` (prior 0.10, VERIFY=$150, ESCALATE=$500).

## 1. Hidden states and prior belief (sums to 100%)

| Hidden state S | Meaning | Prior P(S) |
|---|---|---|
| Fraud | Request is not supplier intent (compromised/spoofed channel) | 10% |
| Genuine | Request is supplier's genuine intent | 90% |
| **Total** | | **100%** |

Prior 10% is an a priori base-rate assumption (not fitted to test labels).

## 2. Evidence available at decision time (label hidden)

| # | Evidence e | Observed | P(e\|Fraud) | P(e\|Genuine) | Likelihood ratio |
|---|---|---|---|---|---|
| E1 | callback_verification | Not Attempted | 0.35 | 0.28 | 1.250 |
| E2 | first_time_bank_change | Yes | 0.75 | 0.20 | 3.750 |
| E3 | urgency_language | Yes | 0.55 | 0.15 | 3.667 |
| E4 | reply_to_mismatch | No | 0.70 | 0.92 | 0.761 |
| E5 | lookalike_domain | No | 0.30 | 0.99 | 0.303 |
| E6 | tone_deviation | No | 0.50 | 0.92 | 0.543 |
| E7 | spf_dkim_dmarc_pass | No | 0.10 | 0.05 | 2.000 |
| E8 | above_materiality_5k | Yes ($7,662) | 0.65 | 0.55 | 1.182 |

Note E7: SPF=No has LR only 2.0 by design — email-auth is a weak signal (passes on full
mailbox compromise), so even the rare SPF failure moves belief little.

## 3. Sequential belief update: prior → posterior (each row sums to 100%)

Naive-Bayes: P(Fraud|e₁…eₖ) ∝ P(Fraud)·∏P(eᵢ|Fraud); same for Genuine; normalize.

| Step | Event | P(Fraud) | P(Genuine) | Sum |
|---|---|---|---|---|
| 0 | Prior | 10.00% | 90.00% | 100% |
| 1 | + E1 callback Not Attempted (LR 1.25) | 12.20% | 87.80% | 100% |
| 2 | + E2 first-time Yes (LR 3.75) | 34.25% | 65.75% | 100% |
| 3 | + E3 urgency Yes (LR 3.67) | 65.63% | 34.37% | 100% |
| 4 | + E4 reply-to No (LR 0.76) | 59.23% | 40.77% | 100% |
| 5 | + E5 lookalike No (LR 0.30) | 30.57% | 69.43% | 100% |
| 6 | + E6 tone No (LR 0.54) | 19.31% | 80.69% | 100% |
| 7 | + E7 SPF No (LR 2.00) | 32.37% | 67.63% | 100% |
| 8 | + E8 amount>5k Yes (LR 1.18) | **36.13%** | **63.87%** | **100%** |

Reading: urgency + first-time spike belief to ~66%; lookalike-No + tone-No pull it back
to ~19%; SPF + amount nudge to the final **36.13% / 63.87%**.

## 4. Actions, costs, policy, decision (initial)

| Action | Cost model (USD) | Expected cost at p=36.13%, amount $7,662 |
|---|---|---|
| APPROVE (pay) | p · amount if fraud, $0 if genuine | 0.3613 × 7662 = **$2,768** |
| VERIFY (out-of-band callback to known number) | $150 flat | **$150** |
| ESCALATE (controller hold + review) | $500 flat | **$500** |

Policy rule (`src/agent.py`): ESCALATE if p ≥ 0.65; APPROVE if E[approve] < $150 AND
p < 0.35; else VERIFY. High-value guard: amount > $20k and p ≥ 0.25 also escalates
(not triggered here: $7,662).
Comparison: $2,768 ≫ $150 → APPROVE rejected; p = 36.13% < 65% → ESCALATE rejected.
**Decision: VERIFY** — matches `results/predictions.csv` (C030, bayesian_cost_sensitive,
p=0.3613, VERIFY). Audit: flagged=True (VERIFY counts as flagged), correct=True
(truth is Fraud; verification is the fraud-catching action).

## 5. New evidence → updated belief → new action

Event: agent executes VERIFY — calls the vendor's pre-established known number.
Outcome observed: **callback FAILED** (contact denies the change / number unreachable).
This replaces E1 (Not Attempted, LR 1.25) with E1′ (Failed: P=0.60|Fraud, 0.02|Genuine, LR 30.0);
all other evidence unchanged. Treat posterior 36.13% as the new prior and apply LR 30/1.25 = 24× update:

| Step | Event | P(Fraud) | P(Genuine) | Sum |
|---|---|---|---|---|
| 8 | Belief before callback (carried prior) | 36.13% | 63.87% | 100% |
| 9 | + callback FAILED (LR 30.0, replaces LR 1.25) | **93.14%** | **6.86%** | **100%** |

Recomputed expected costs: E[APPROVE] = 0.9314 × 7662 = **$7,136** vs VERIFY $150 vs ESCALATE $500.
Threshold comparison: p = 93.14% ≥ 65% → **new action: ESCALATE** (hold payment, route to
controller with callback-failure transcript). Fraud loss of $7,662 avoided for $500.

Counterfactual recorded: had the callback instead come back **Confirmed**
(LR 0.05/0.70 ≈ 0.071), posterior would be **3.13% / 96.87%** (sums 100%),
E[APPROVE] = $240 > $150 → policy still says **VERIFY** (hold + second check), not APPROVE —
first-time + urgency + $7,662 amount keep it above the approve bar. This is intentional:
one Confirmed call downgrades but does not single-handedly clear a first-time change.

## 6. Audit data to log (per decision)

Log for both decision points (initial + post-callback): case_id C030, timestamp,
policy name + version (`bayesian_cost_sensitive`, prior 0.10, costs 150/500),
evidence snapshot (E1–E8, then E1′), prior → posterior with normalization check (=100%),
likelihood ratios used, expected-cost comparison ($2,768 / then $7,136 vs $150 vs $500),
threshold branch taken, action (VERIFY → ESCALATE), callback transcript reference,
reviewer id on escalation, and scoring fields kept separate (true label used only in
`experiments/run_experiment.py`, never passed to the policy).

---

# Probability Decision Record — Prospective Case C041 (correct state NOT known)

New live request received 2026-10-01. No ground truth exists — this is a decision under
uncertainty, not a scoring exercise. Truth will only be known after the callback/escalation
outcome. Case id **C041-prospective** (no row in the simulated dataset).

## Required-items table

| Item | Content for C041 |
|---|---|
| Evidence | callback=Not Attempted; first-time=Yes; urgency=Yes; reply-to=No; lookalike=No; SPF pass=Yes; amount $18,400 (>5k Yes); tone report PENDING at decision time |
| Hidden states | Fraud (unsafe: request is not supplier intent) vs Genuine (safe: request is supplier intent) |
| Beliefs | Prior 10% Fraud / 90% Genuine → posterior after initial evidence **33.02% / 66.98%** (sums 100%; stepwise table below) |
| Event | The Fraud hidden state is the safety-critical event for the user (an approved fraud is an irreversible wire loss); the Genuine state matters as the cost of needless friction |
| Actions | APPROVE (pay $18,400) · VERIFY (out-of-band callback to known number, $150) · ESCALATE (controller hold + review, $500) |
| Costs | APPROVE: $0 if genuine, $18,400 lost if fraud · VERIFY: $150 · ESCALATE: $500 (assumed; see README cost model) |
| Policy | `bayesian_cost_sensitive` v1 (`src/agent.py`): ESCALATE if p ≥ 0.65; APPROVE if E[approve]=p·amount < $150 AND p < 0.35; else VERIFY |
| Decision | **VERIFY** — E[APPROVE]=0.3302×18400=**$6,076** ≫ $150 rejects APPROVE; p=33.02% < 65% rejects ESCALATE |
| Audit data | Time 2026-10-01 (prospective) · data version: simulated dataset v1 (`Simulated_Cases`, 40 rows; C041 not in it) · model `src/agent.py` bayesian v1 (prior fraud 0.10, a priori likelihoods) · policy v1 (thresholds 0.35/0.65, costs 150/500) · truth UNKNOWN at decision time |

## Initial belief update (prior → posterior, each row sums to 100%)

| Step | Event | P(Fraud) | P(Genuine) | Sum |
|---|---|---|---|---|
| 0 | Prior (assumed base rate) | 10.00% | 90.00% | 100% |
| 1 | + callback Not Attempted (LR 1.25) | 12.20% | 87.80% | 100% |
| 2 | + first-time Yes (LR 3.75) | 34.25% | 65.75% | 100% |
| 3 | + urgency Yes (LR 3.67) | 65.63% | 34.37% | 100% |
| 4 | + reply-to No (LR 0.76) | 59.23% | 40.77% | 100% |
| 5 | + lookalike No (LR 0.30) | 30.57% | 69.43% | 100% |
| 6 | + SPF Yes (LR 0.95) | 29.44% | 70.56% | 100% |
| 7 | + amount>5k Yes (LR 1.18) | **33.02%** | **66.98%** | **100%** |

Borderline VERIFY: just below the 35% approve-consideration band, far above the $150
approve bar ($6,076), well below the 65% escalate bar.

## Comparable historical cases (recent, not the easy large group)

Deliberately NOT fitted on all 40 rows. Reference set: **recent (C020–C041 era, i.e. the
second half of the simulation) AND comparable (first-time bank change = Yes, as in C041)** —
9 cases: C026, C029, C030, C032, C033, C034, C037, C039, C040. Evidence searched for
BOTH states: safe (Genuine n=3: C026, C032, C037) and unsafe (Fraud n=6: C029, C030,
C033, C034, C039, C040). Relevant finding for the pending signal: tone-deviation Yes
appears in **1/6 fraud comparables (C040, a $11,291 fraud)** and **0/3 genuine comparables**
(smoothed 0.25 vs 0.20, direction LR > 1). The small n is reported honestly — it supports
the direction of the policy's a priori tone LR (0.50/0.08 = 6.25) without pretending to
measure it precisely; the 6.25 magnitude remains an assumption flagged for review, consistent
with the r/cybersecurity tone-profiling finding.

## One new item of evidence → updated belief → new action

1. **Prior probability** (carried forward): P(Fraud)=33.02%, P(Genuine)=66.98%.
2. **New evidence**: late-arriving behavioral report — **tone_deviation = Yes** (vendor's
   writing profile deviates from history; cf. discussion-record tone-profiling thread).
3. **Likelihood for each important hidden state**: P(tone Yes|Fraud)=0.50,
   P(tone Yes|Genuine)=0.08 (policy a priori; comparable-set check above: only observed
   tone-Yes in the 9 comparables is the fraud case C040, zero in genuine — same direction).
4. **Posterior**: prior odds (0.3302/0.6698) × LR 6.25 → **P(Fraud)=75.50%, P(Genuine)=24.50%**
   (sums 100%). E[APPROVE] = 0.7550 × 18400 = **$13,891**.
5. **Threshold comparison**: 75.50% ≥ 65% escalate bar (and $13,891 ≫ $150).
6. **New action recorded: ESCALATE** — hold the $18,400 payment, route to controller with
   the tone-deviation transcript plus callback task; VERIFY callback still executed as the
   evidence-gathering step inside escalation. Prior action VERIFY is superseded, both
   logged with timestamps per the audit fields above.
