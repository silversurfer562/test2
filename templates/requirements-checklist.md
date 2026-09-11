# AI system requirements checklist

Run this **before design starts**, not after. Every question here is cheap to
answer at requirements time and expensive to retrofit, and each one is drawn
from a real gap found in a shipped system — the sources are named so you can
see what it cost to skip them.

## How to run it

- **Timebox it to 45 minutes.** It is a gate, not a design session. If a
  question turns into an hour of debate, that's the finding: write down that
  it's unresolved and who owns resolving it.
- **Write the answers down.** An answer held in the room is not a requirement.
- **"Not applicable" is a valid answer, in writing, with the reason.** What is
  not valid is silence. Silence is how a requirement goes missing and then
  gets described later as a delivery problem.
- **Name an owner per answer.** A requirement with no name against it is a
  hope.
- Re-run it when scope changes materially — a new data source, a new
  autonomous action, a new tenant model.

---

## Part 1 — The five that always apply

### 1. What measures whether the output is correct, and who owns that number?

**Pass condition:** a named eval set with a source (production traces, not
imagination), a stated n, a grading method, and a person whose job it is to
report the number.

**A bad answer sounds like:** *"we have good test coverage."* Tests check that
the system runs. Evals check that it is right. A system can be at 90% coverage
and wrong on every clinical answer it produces — coverage measures the code,
and the model is not the code.

**What skipping it costs:** `deep-study-ai` ships patient education material,
discharge instructions, SBAR reports, and drug-interaction analysis, with 20+
test files and zero golden sets. The reliability requirement was written in a
docstring and built. The correctness requirement was never written, so nothing
was built.

---

### 2. What is the trust boundary for content we pull *in*?

**Pass condition:** every external content source is named, and for each you
can say where it lands in the prompt (system turn or user turn), how it's
delimited, and what the model is told about its status.

**A bad answer sounds like:** *"it's from a reputable source."* Reputable
sources serve content that other people wrote. The question is not whether
PubMed is trustworthy; it's whether an abstract's text can act as an
instruction once it's inside your prompt.

**What skipping it costs:** `claude_service.py:94` concatenates fetched FDA
label text and literature into the **system** message —
`system_message += f"\n\nContext: {context}"` — unfenced, untagged, with no
statement that it is data. The design specified *"No PHI stored"* and
clinician-review banners with real care. **Thorough requirements on the data
we send out, none on the data we pull in.** That asymmetry is the default,
because outbound risk is visible to everyone in the room and inbound risk
isn't.

**The cheap fix, specified up front:** external content goes in the user turn,
inside tagged delimiters, with one line in the system prompt saying that
tagged content is reference data and never instruction.

---

### 3. What resumes after a mid-run failure, and what does restarting cost?

**Pass condition:** you can name the checkpoint boundary, the idempotency key
on every side-effecting call, and the retry budget — a number, with a defined
behavior on exhaustion.

**A bad answer sounds like:** *"we retry on failure."* Retries without
idempotency are how one failure becomes two charges, two emails, or two
records.

**What skipping it costs:** the multi-wizard fan-out in `coach.py` has no
checkpointing, no resumption, and no idempotency keys. Circuit breakers
protect the single call; nothing protects the run. **Reliability that stops at
the request boundary looks like reliability right up until a multi-step job
dies at step seven.**

---

### 4. What is the cost per *successful* task, and when was the price table dated?

**Pass condition:** a target cost per successful task (not per call), the
current measured figure, and a price table with a date on it and an owner for
re-dating it.

**A bad answer sounds like:** *"we track spend."* Spend tells you what
happened. Cost per successful task tells you what the retry loop and the
re-retrieval are costing, which is the number an architecture decision
actually turns on.

**What skipping it costs:** the cost table in
`memdocs/empathy_llm_toolkit/providers.py` is hardcoded Claude 3-era pricing
with no date on it, and the model pins behind it are over a year old. An
undated price table doesn't fail loudly — it silently misprices every decision
made from it, and the decisions look well-reasoned the whole time.

---

### 5. What does deletion actually delete, and how do we prove it?

**Pass condition:** a named test that deletes a record, then queries for
something only that record could answer — and checks the derived artifacts
too: caches, embeddings, summaries, digests, exports, logs.

**A bad answer sounds like:** *"we delete from the database."* Derived
artifacts are the whole problem. A memory removed from the store and still
present in a consolidated summary is not deleted; it's hidden.

**What skipping it costs:** the two-layer memory protocol was ratified in July
2026 and no test proves the system honors it. Deletion is a commitment you
make to users, so it needs a test, not a code path.

---

## Part 2 — The conditional ones

Answer the header question first. If it's no, write "n/a" and move on.

### If the model gets tools

- **What can it do without a human?** Name the actions. The list should be
  short enough to read aloud.
- **What requires approval, and what does the approving human see?** An
  approval prompt that doesn't show the actual arguments is a rubber stamp.
- **What does each tool's error string tell the model to do next?**
  `"404"` teaches nothing. `"No user with id 'X'. Search by email with
  find_user first."` is control flow.
- **Can untrusted content reach a privileged tool?** If yes, that is the
  design's central problem and everything else is secondary.
- **What is the measured tool-error rate, and against which eval set?**

### If the system has memory

- **What gets written, and what is the admission rule?** Storage is cheap;
  retrieval contamination is not.
- **Does every record carry source, timestamp, and confidence?** Without
  provenance you cannot answer "why does it think that?" or handle staleness.
- **What happens when a new memory contradicts an old one?** Supersede with
  history, keep both with timestamps, or flag for confirmation — pick one.
  Last-writer-wins silently loses information you'll want back.
- **What decays, and on what schedule?**
- **What's the token budget at read time, and what wins a slot?**

### If the model's control flow is model-decided

- **Why is this an agent rather than a pipeline?** Name the variety you can't
  enumerate. If you *can* enumerate the paths, the pipeline is cheaper,
  faster, and debuggable at 2am.
- **What is the step budget, and what happens at exhaustion?**
- **What does the run-to-run variance look like?** An agent that averages
  better while swinging wildly is often the worse product.

### If there are multiple tenants or users

- **What isolates one user's data from another's at retrieval time?**
- **What in the prompt could leak across the boundary** — a cached prefix, a
  shared summary, a global memory?

---

## Sign-off

| # | Question | Answer written | Owner | Status |
|---|---|---|---|---|
| 1 | Output correctness measured | | | pass / gap / n/a |
| 2 | Inbound trust boundary | | | pass / gap / n/a |
| 3 | Mid-run resumption | | | pass / gap / n/a |
| 4 | Cost per successful task | | | pass / gap / n/a |
| 5 | Provable deletion | | | pass / gap / n/a |
| C1 | Tool surface | | | pass / gap / n/a |
| C2 | Memory | | | pass / gap / n/a |
| C3 | Model-decided control flow | | | pass / gap / n/a |
| C4 | Tenant isolation | | | pass / gap / n/a |

**Gaps are allowed. Unwritten gaps are not.** Every row marked *gap* gets a
line in the design doc saying what's missing, why you're shipping without it,
and what would change that. A gap you decided to accept is an engineering
decision; a gap nobody wrote down is the thing you find out about from a user.

---

## Revise this in Week 12

This version is built from one read of three repositories. After the quarter,
rewrite it from what the twelve weeks actually taught you — add the questions
whose absence bit you, cut the ones that never earned their 45 minutes. A
checklist that never changes is one nobody is running.
