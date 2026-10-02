# LinkedIn Post 

link to the post - https://www.linkedin.com/posts/deepikaaupadhyaya_payments-fraudprevention-aiagents-activity-7511491908892962816-2b93?utm_source=social_share_send&utm_medium=member_desktop_web&rcm=ACoAACA4NUwBHCyuIAUIJGFwYzjAorIIMP2c0NM


Most bank-change fraud doesn't look like an attack. It looks like an email asking to update bank details.

When I started scoping this, I thought the problem was who sent it. Then I learned that in a compromised mailbox, the domain, SPF, DKIM and DMARC all pass. The sender checks out. The request can still be fraud.
 
So the uncertain thing is intent, not identity.

I'm building a small prototype agent around that idea: (simulated data for now)
* It reads 7 signals: first-time change, urgency, reply-to mismatch, lookalike domain, tone deviation, SPF/DKIM/DMARC, and amount.
* It holds a belief over two hidden states: Genuine vs Fraud.
* It chooses one of 3 actions: approve, verify by callback, or escalate to a human.

About 200 lines of Python. No LLM prompting, and every decision leaves a reasoning trail.

Over the next few posts I'll share how the belief updates, where it failed, the design decision that mattered most, and results.

In your payment flow today, who gets the final call on a bank details change: AP, finance, the system, or nobody?

hashtag#Payments hashtag#FraudPrevention hashtag#AIAgents