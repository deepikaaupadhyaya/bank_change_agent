# LinkedIn Post (draft — 1 post for the week; attach paper/preprint.pdf on publish)

A supplier emails new bank details. You pay — or a scammer does. Email
authentication passes even on a fully compromised mailbox, so it can't tell the
difference. That's the problem in one sentence.

Why this agent design: the hidden state (genuine intent vs. compromised channel)
demands *action under uncertainty*, not a chatbot answer — so the agent does one of
three things per request: APPROVE, VERIFY via out-of-band callback, or ESCALATE to
a human controller. High-cost uncertainty goes to a person by policy, not by luck.

Why this probability model: the costs are violently asymmetric — approving one
fraud loses the full wire ($3k–$57k here), a check costs $150–$500. So beliefs
(posteriors summing to 100%) convert directly into expected-cost decisions instead
of accuracy-styleose predictions.

One result: on 40 blinded simulated cases, the Bayesian policy caught 8/8 frauds
for $4,200 total; the email-auth baseline caught 1/8 for $143,374. Accuracy says
0.85 vs. 0.80 — a near-tie that hides a $139k gap. (Scariest failure: a calm,
no-urgency $56,875 fraud no urgency heuristic would catch.)

One design change from public discussion: practitioners convinced me to weight
email authentication at ~zero (r/sysadmin: every check passes on a real
compromise) and to treat bank-verification APIs as a supplement that never replaces
the callback (r/fintechdev).

Largest known limitation, stated plainly: everything is 40 simulated cases with
assumed likelihoods and costs, and 35–52% review rates no real team could sustain.

My specific ask: if you run AP or payments — how many bank-change reviews per week
can your team genuinely do *well*? I'm using that number as the human-capacity
budget that should set the decision threshold, and I need real figures.

Preprint PDF attached. All amounts simulated; methods and limitations inside.
