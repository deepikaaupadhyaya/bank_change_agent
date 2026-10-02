# X Thread (draft — post with paper/preprint.pdf attached; one post per line)

1/ The problem: a supplier emails new bank details. Pay — or a scammer does.
Email auth passes even on a fully compromised mailbox, so it can't decide.
Agent must APPROVE, VERIFY (callback), or ESCALATE. Full writeup + PDF below.

2/ The test: 40 simulated labeled cases (32 genuine / 8 fraud), true label hidden
at decision time. Two agent policies (Bayesian cost-sensitive, rule checklist) vs.
an email-auth baseline. Scored on cost, recall, review rate — not just accuracy.

3/ The result: Bayesian policy caught 8/8 frauds for $4,200 total. Baseline caught
1/8 for $143,374. Accuracy said 0.85 vs 0.80 — a near-tie hiding a $139k gap.
Cost, not accuracy, is the metric that matters here.

4/ Scariest failure: a calm $56,875 fraud with zero urgency language. Any
urgency-based rule waves it through. What caught it: first-time change +
lookalike domain + failed callback firing together.

5/ Honest limitation: all 40 cases are simulated, likelihoods assumed, and
35–52% review rates would crush a real team into rubber-stamping. Treat this as
a tested prototype, not a deployment guide.

6/ Open question for payments/AP folks: how many bank-change reviews per week can
your team genuinely do well? I want that number to set the policy's review
budget. PDF attached — methods, failures, and repeat instructions inside.
