# Reading list

Organized by week, with the question to read for. Three hours a week — that's
two or three items, not ten. Skip anything that doesn't serve the week's gate.

**On citations:** titles and authors are given without URLs on purpose, so
that a moved link doesn't become a dead end. Search the title. Where a date
matters (benchmarks, pricing, model behavior), check the publication date
before you rely on a number — several of these predate the models you run.

---

## Week 1 — Baseline & eval harness

- **"Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"** — Zheng et al., 2023.
  *Read for:* where judge/human agreement breaks down, and the position and
  verbosity biases you'll need to control for in your own judge prompts.
- **Anthropic Engineering, "Building effective agents."**
  *Read for:* the workflow-vs-agent distinction. You'll act on it in Week 4;
  read it now so Week 1's eval design anticipates it.
- **Your own production traces.** Two hours, reading actual sessions end to end.
  *Read for:* what your users really do, as opposed to what the demo does.

## Week 2 — Context as a budget

- **"Lost in the Middle: How Language Models Use Long Contexts"** — Liu et al., 2023.
  *Read for:* position effects on retrieval accuracy. Dated — check whether it
  still reproduces on your current model before you design around it. Running
  that check is itself a good use of the week.
- **Anthropic Engineering, "Effective context engineering for AI agents."**
  *Read for:* context as a finite budget allocated across system prompt, tools,
  history, and retrieved material.
- **Your model provider's prompt-caching documentation.**
  *Read for:* what invalidates a cache prefix. This determines how you order
  your context, which is an architectural decision disguised as a formatting one.

## Week 3 — Failure taxonomy

- **"Reflexion: Language Agents with Verbal Reinforcement Learning"** — Shinn et al., 2023.
  *Read for:* self-correction as a control-flow pattern — and its cost. Note
  what it does not fix.
- ***Designing Data-Intensive Applications*** — Kleppmann, ch. 1 and 8.
  *Read for:* the vocabulary of partial failure. It transfers to agents almost
  unchanged, and it's better vocabulary than the agent literature has.

## Week 4 — Workflow vs agent

- **"ReAct: Synergizing Reasoning and Acting in Language Models"** — Yao et al., 2022.
  *Read for:* the original interleaved reason/act loop — the ancestor of most
  agent loops you've used.
- **"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"** — Wei et al., 2022.
  *Read for:* historical grounding. Much of this is now trained into the models;
  read it to see which parts have been absorbed and which are still your job.
- **Anthropic Engineering, "Building effective agents"** — reread, now with the
  Week 1 numbers in hand. It reads differently.

## Week 5 — Tool interface design

- **Anthropic Engineering, "Writing tools for agents."**
  *Read for:* tool descriptions as documentation for a fallible reader, and
  error strings as control flow.
- **"Toolformer: Language Models Can Teach Themselves to Use Tools"** — Schick et al., 2023.
  *Read for:* what makes a tool call learnable at all.
- **The Model Context Protocol specification.**
  *Read for:* how a tool boundary gets standardized, and what the spec chose to
  make explicit.

## Week 6 — Delegation & multi-agent

- **Anthropic Engineering, "How we built our multi-agent research system."**
  *Read for:* the token cost of delegation, stated honestly, and the tasks
  where it paid.
- **"Generative Agents: Interactive Simulacra of Human Behavior"** — Park et al., 2023.
  *Read for:* the reflection loop — an agent summarizing its own history into
  higher-level memories. This is also your Week 8 warm-up.

## Week 7 — Durable agents

- **Temporal's documentation on durable execution and idempotency.**
  *Read for:* a mature model of the problem you're about to hit. Not an
  endorsement of the tool — an endorsement of the vocabulary.
- **DDIA ch. 11** — Kleppmann.
  *Read for:* exactly-once as an illusion built from idempotency plus retries.

## Week 8 — Memory reference architecture

- **"MemGPT: Towards LLMs as Operating Systems"** — Packer et al., 2023.
  *Read for:* paging between a small fast context and a large slow store; the
  OS analogy, and where it breaks.
- **"Generative Agents"** — Park et al. (reread).
  *Read for:* the retrieval score — recency, importance, relevance, combined.
  Three axes, weighted. Your read path in Week 10 needs all three.
- **"Voyager: An Open-Ended Embodied Agent with Large Language Models"** — Wang et al., 2023.
  *Read for:* the skill library as *procedural* memory — the memory type most
  systems skip entirely.

## Week 9 — Memory write path

- **DDIA ch. 5** — Kleppmann, on conflict resolution and last-writer-wins.
  *Read for:* why "just overwrite it" loses information you'll want back.
- **Any recent survey on memory in LLM agents.** Search for one published in
  the last year; the field moves and a 2023 survey is an artifact now.
  *Read for:* a taxonomy to argue with, not one to adopt.

## Week 10 — Memory read path

- **"Retrieval-Augmented Generation for Large Language Models: A Survey"** — Gao et al., 2023.
  *Read for:* the read-path design space. Skim the taxonomy; dwell on the
  evaluation section.
- **"Lost in the Middle"** — Liu et al. (reread, retrieval angle).
  *Read for:* what ordering does to your retrieved memories, not just documents.

## Week 11 — Model layer

- **"LoRA: Low-Rank Adaptation of Large Language Models"** — Hu et al., 2021.
  *Read for:* why adaptation got cheap, and what rank actually trades off.
- **"QLoRA: Efficient Finetuning of Quantized LLMs"** — Dettmers et al., 2023.
  *Read for:* the memory math that decides what you can train on hardware you
  can rent.
- **"Distilling the Knowledge in a Neural Network"** — Hinton et al., 2015.
  *Read for:* the original argument. Your Week 11 build is this paper, with
  your own traces as the transfer set.
- **"Training Compute-Optimal Large Language Models"** — Hoffmann et al., 2022.
  *Read for:* data-vs-parameters intuition. Enough to know how much data your
  fine-tune actually needs.

## Week 12 — Design review

- **"Documenting Architecture Decisions"** — Michael Nygard, 2011.
  *Read for:* the ADR form. It is one page long and it is the whole idea.
- **Chapters on architecture decisions and trade-off analysis** in Richards &
  Ford, *Fundamentals of Software Architecture*.
  *Read for:* how to present a decision so that a reviewer can attack the
  reasoning rather than the conclusion.

---

## Standing sources

Check weekly, in the short sessions, not the deep ones:

- Anthropic's engineering blog and the Claude documentation
- Your model providers' changelogs — model behavior changes under you, and a
  design tuned to a deprecated model is a maintenance debt
- One practitioner writing on evals whose numbers you trust. One. Not a feed.
