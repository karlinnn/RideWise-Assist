# Design Decisions

## 1. Three most important design decisions

**a) Access control enforced in code, not in the prompt.**
Role and `customer_id` come from the session. Customers get a fixed menu of parameterised queries with their own `customer_id` forced in; they never write SQL and the LLM never supplies the customer id. Agents use a separate query module, so the customer path cannot reach it. A prompt can be talked around; a function with the id hard-wired cannot. This protects the most attacked part of the system.

**b) Deterministic core, LLM at the edges.**
The LLM only interprets the question and phrases the reply. Policy version selection, [refund and penalty maths,] masking and status-code translation are plain code. This makes answers reproducible and testable, and avoids LLM arithmetic errors on money.

**c) Evidence-grounded answers with a Trust Check.**
Every answer is built from an evidence list (queries run, rows, policy document and section). After generation, code verifies that amounts and IDs in the reply exist in the evidence and that no other customer's ID appears. On failure it retries once, then falls back to a template. The user can see the evidence and trust results, which makes answers verifiable.

## 2. Alternatives considered and rejected

| Alternative | Why rejected |
|---|---|
| Free text-to-SQL for customers | Hard to make safe; one injected prompt could cross customer boundaries. Fixed queries are safer and tested. |
| Letting the LLM do refund and penalty arithmetic | Unreliable for money; deterministic code with a step trace is checkable. |
| Three independent autonomous agents | Coordination overhead and unpredictability for a 3-hour build. One graph with three nodes is simpler to explain and debug. |
| Putting both cancellation policies in one index and letting the LLM choose | Risk of mixing v1 and v2. Version is chosen by code from dates. |
| Vector embeddings for policy search | Only five small documents; BM25 is simpler, needs no extra service, and is easy to explain. |
| Full login system | Out of scope per the brief; replaced by a session role plus a staff access code. |

## 3. Where the assistant currently fails or behaves poorly

- **Staff authentication is a shared access code**, not per-agent login. A real deployment needs SSO and per-agent permissions. Agent turns are written to an audit log.
- **Customer "login" is just a `customer_id`**; anyone who knows an ID can start that session (accepted by the brief for evaluation).
- **Intent classification depends on the LLM.** Unusual phrasing can be misclassified, which leads to a clarification question or a refusal rather than a wrong data leak (access is enforced separately).
- **Ambiguous follow-ups** ("the other one") with several recent bookings may need a clarification question.
- **Policy parsing:** [describe any tables or sections that extracted poorly from the PDFs].
- **[Calculators / agent fleet queries / input guard] are [partial / not implemented]:** [state exactly what is missing].
- **Slow or unavailable LLM** produces a plain template answer with raw facts, not a natural reply.
- Policy search is keyword-based, so rare synonyms can be missed.

## 4. What I would build next with one more week

1. Real authentication (SSO) with per-agent roles and a full audit trail.
2. SQL AST validation (`sqlglot`) to give agents safe free-form analytics with table allowlists and column masking.
3. A stronger number-grounding verifier and an automated evaluation set (including adversarial and multi-turn cases) run on every commit.
4. Versioned, structured policy rules (YAML) linked to PDF clauses, so a new policy version needs no code change.
5. Hybrid retrieval (BM25 plus embeddings) with reranking.
6. Proactive handling of data-quality issues (inconsistent statuses and timestamps) with flags shown to agents.
7. Caching and rate-limit handling for the LLM, plus structured monitoring.
