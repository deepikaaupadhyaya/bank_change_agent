# Failure Analysis — 6 examined incorrect decisions

Dataset: 40 simulated cases (32 Genuine / 8 Fraud). Flagged = VERIFY or ESCALATE.
Costs: APPROVE fraud = full amount lost; VERIFY = $150; ESCALATE = $500; APPROVE genuine = $0.

## F1 — "Stolen-Callback Confirmation" (C034, Fraud, $54,729)
Evidence: callback=Confirmed, first_time=Yes, urgency=Yes, lookalike=Yes, SPF pass=Yes.
Baseline SPF: APPROVE → $54,729 loss (false negative). Both agents: ESCALATE (correct).
Lesson: a Confirmed callback on a fraud case means the verification channel itself was
compromised/answered by the attacker or a stale number was used. No single signal is trusted alone.

## F2 — "Urgency-Free Sleeper" (C009, Fraud, $56,875 — largest loss)
Evidence: callback=Failed, first_time=Yes, urgency=No, lookalike=Yes, tone=Yes, SPF pass=Yes.
Baseline SPF: APPROVE → $56,875 loss. Both agents: ESCALATE (correct).
Lesson: calm, non-urgent fraud (cf. r/AI_Agents "sat in the mailbox for weeks") evades
urgency-only heuristics; correlation of first-time + lookalike + failed callback is what fires.

## F3 — "Repeat-Vendor Camouflage" (C002, Fraud, $8,814)
Evidence: callback=Not Attempted, first_time=No, urgency=Yes, lookalike=Yes, tone=Yes, SPF pass=Yes.
Baseline SPF: APPROVE → $8,814 loss. Both agents: VERIFY/ESCALATE (correct).
Lesson: first_time=No does not clear a case; repeat-vendor status is weak evidence when
lookalike + tone + urgency co-occur. SPF passes clean on full mailbox compromise.

## F4 — "Stale-Contact False Alarm" (C020, Genuine, $5,998)
Evidence: callback=Failed, all other flags No, SPF pass=Yes.
Bayesian: VERIFY ($150 waste). Rule: VERIFY. Truth: genuine — vendor missed the call /
number on file was stale.
Lesson: treating Failed callback as deterministic fraud over-fires; genuine operational
failures produce the same observation. Cost is bounded ($150), unlike a missed fraud.

## F5 — "Legitimate-Urgency Over-Triage" (C026, Genuine, $37,528)
Evidence: callback=Not Attempted, first_time=Yes, urgency=Yes, amount $37,528, SPF pass=Yes.
Bayesian: VERIFY ($150). Rule: ESCALATE ($500). Truth: genuine first-time change with real deadline.
Lesson: stacked weak signals (first-time + urgency + large amount + no callback yet) push
score-based policies to escalate; this is the price of cost-sensitive caution on high amounts.

## F6 — "Benign Anomaly Coincidence" (C014, Genuine, $17,322)
Evidence: callback=Confirmed, reply_to=Yes, tone=Yes, rest No, SPF pass=Yes.
Bayesian + rule: VERIFY ($150). Truth: genuine — reply-to drift + formality shift with innocent cause.
Lesson: behavioral anomalies (reply-to, tone) occur in genuine traffic; Confirmed callback
correctly downgrades but amount + two flags still trigger VERIFY under expected-cost math.

## Which error has the highest cost?
FALSE APPROVE of a fraud case (false negative / false acceptance) — e.g. F1 ($54,729),
F2 ($56,875), F3 ($8,814). Baseline total fraud loss = $143,074 across 7 missed frauds.

## Why this error has the highest cost
1. Magnitude asymmetry: ~$3k–$57k per miss (mean ~$20k in this set) vs $150 (VERIFY)
   or $500 (ESCALATE) per false alarm — a 20×–380× ratio.
2. Irreversibility: a wired payment to an attacker-controlled account is rarely recovered;
   a delayed genuine payment is resolved by one callback.
3. Control failure: approving fraud defeats segregation-of-duties and out-of-band
   verification simultaneously; a false positive merely spends human time (the "expensive
   rubber stamp" failure from r/AI_Agents is real but bounded — $4,200–$6,300 total here
   vs $143,074 for the permissive baseline).
Hence the Bayesian policy is tuned for Recall = 1.0 (0 false negatives) at the price of
6 bounded false positives.
