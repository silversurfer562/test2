# The three capstones

They run *through* the weeks, not after them. Each one is a thread that picks
up several weeks' gates and ties them into something with a demo.

Given your week-0 baseline (`docs/baseline-week-00.md`), the weight is on
P1 and P3. P2 is largely built — its capstone is proving it, not building it.

---

## P1 — The instrumented agent (Weeks 1–7)

**Take one agent you actually run.** By Week 7 it should have:

- An eval suite scoring **task outcome**, not just retrieval — with n, spread,
  and cost per successful task
- Full tracing: a session reconstructible from the trace alone
- A ranked failure taxonomy built by hand from ~100 real failing sessions
- A measured workflow-vs-agent comparison on at least one feature
- A tool surface refactored against measured tool-error rates
- Durable execution: killed mid-run, resumes, no duplicated side effects
- A written trust boundary — what runs unattended, what needs approval, how
  untrusted content is isolated from privileged tools

**Demo:** kill it mid-run in front of someone. It comes back and finishes.

**Why this one matters most for you:** your memory layer exists to serve
agents, and four rubric dimensions covering agents have no evidence behind
them today.

---

## P2 — The memory service, proven (Weeks 8–10)

You have the architecture, the protocol, and the write path. The capstone is
not to build it again — it's to make it defensible.

- The two-layer protocol **red-teamed**, not reviewed. Someone whose job for
  an hour is to break it
- **Write precision measured**: sample 100 curated nodes, hand-label
  correct / redundant / wrong, improve the write path, re-measure on a fresh
  sample, report both
- **Multi-session eval scenarios**: a fact stated in session 1 and needed in
  session 5. Retrieval scored inside one session is context-window testing
- **Adversarial set**: facts that changed, facts that expired, equal-confidence
  contradictions, injected content in a stored memory
- **The deletion test**: delete a node, ask the question only it could answer.
  Check derived summaries, embeddings, caches, and the digest. Cosmetic
  deletion is a privacy failure, not a bug

**Demo:** the adversarial set passing at a rate you stated before you ran it,
and the deletion test green including derived artifacts.

---

## P3 — Small model, narrow job (Week 11)

One subtask moved off a frontier model onto a small trained one — or a
documented decision not to.

**The candidate that suggests itself:** the curation admission decision. You
have `review_verdict: keep | sharper` labels on curated nodes, applied by
human review against the 30-day test. That's a labelled dataset for the
admission classifier, generated as a byproduct of work you already did.

- Baseline 1: frontier model, prompted with the 30-day test
- Baseline 2: small model, prompted — the cheap option people skip
- Candidate: small model, LoRA fine-tuned on your review verdicts
- Held-out split with no overlap

**Deliverable:** the quality / cost / p95 / operational-burden table, and an
ADR that says ship or don't ship. *Don't ship* is a good outcome and is
frequently correct — the cost of owning a model is real and rarely counted
honestly right after a good eval result. Count it.

**Caveat worth surfacing now:** your verdict labels come from one reviewer
applying a policy that was itself still settling in July. Check for label
drift across the date range before you train on them.
