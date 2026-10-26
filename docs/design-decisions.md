# Design decisions

Record of the Project 1 design review (14 Oct 2026) and refinements since.
The pipeline diagram and stage table live in the [README](../README.md); the
findings database is specified in [schema.md](schema.md) (issue #5).

## Summary

The original brief (21 Sep) described three LLM agents: Scanner, Risk
Assessor and Migration Planner. Design review showed only two jobs need
judgment: triaging ambiguous findings and planning the migration. Detection
and risk scoring became deterministic rules, so they can be tested,
reproduced and defended.

**Guiding principle:** rules where correctness matters, LLM where judgment is
needed, and every LLM decision stored with its evidence.

**Pipeline:** Scan → Score risk → Triage → Plan. Each stage reads from and
writes to SQLite, and the scan status moves pending → scanned → scored →
triaged → planned. Scan and Score alone form v0.3: a ranked report with no
LLM dependency. The target is v0.4, the full pipeline.

## Decisions vs the original brief

| # | Decision | Original brief | Now, and why | Vs brief |
|---|---|---|---|---|
| 1 | LLM backend | Ollama, local | Same. Native ollama package with a tool-capable model (Qwen or Llama 3.x family). | Unchanged |
| 2 | Orchestration | Hand-rolled, no framework | Same, adapted to Ollama's message shapes. | Unchanged |
| 3 | Agent architecture | Three agents | Deterministic scanner and risk scorer, then one agent loop run as two passes: triage, then planning. Only these two jobs need judgment. | Changed |
| 4 | Scanner implementation | Agent calls ast or tree-sitter | Plain deterministic tool, no LLM. Layers: imports, alias resolution, calls, parameter extraction, regex text fallback, dependency scan. | Refined |
| 5 | Scanner coverage | Not specified | Python call sites via known crypto APIs (high confidence), declared and locked dependencies (medium), text and config files (low). Pure-Python crypto implementations are out of scope. | Refined |
| 6 | Non-Python languages | tree-sitter for multi-language | Deferred. Prepared with a language column, a language-neutral primitive taxonomy and scanners registered by file type. | Deferred |
| 7 | Risk assessment | LLM agent classifies findings | Deterministic rules with rule IDs: primitive (Shor vs Grover), operation (key exchange before signatures, harvest-now-decrypt-later), exposure, blast radius, migration difficulty. Optional LLM adjustment capped at one tier, stored separately. | Changed |
| 8 | LLM triage | None | Low-confidence findings only. Verdict include / exclude / needs-human with reason and evidence lines. Nothing is deleted; excluded findings stay in the report. | New |
| 9 | Tool routing | Implied LLM choice | By file extension, shebang and filename rules. No judgment involved. | New |
| 10 | Interface between stages | Agent hand-offs | SQLite is the interface. No prose summaries between stages, since a summary is a lossy copy. | New |
| 11 | Database schema | Two tables | repos, scans, files, findings, risk scores and rule hits, triage verdicts, plan steps and a step-to-finding link table. Plans are queryable, not a blob. | Changed |
| 12 | Cross-scan tracking | Not specified | Scans record target commit SHA, scanner and rules versions, and status. Findings carry a fingerprint because line numbers shift. | New |
| 13 | Planner tools | Not specified | get_findings (filtered, paginated), read_context, get_replacement (deterministic FIPS lookup), rescan_file (verifies a fix), save_plan_step. | New |
| 14 | Testing strategy | A handful of unit tests per component | Fixture folder with an expected-findings answer key, negatives for false positives, and mutation checks on every rule. | Refined |
| 15 | Target codebases | One real, smallish codebase | trustme (smoke), PyJWT (primary), paramiko (stretch), python-rsa (limitation demo). Pinned SHAs, cloned to a gitignored targets/. | Refined |
| 16 | Standards mapping | Map to FIPS 203 / 204 / 205 | Same, held as a deterministic lookup table rather than model recall. | Unchanged |
| 17 | MVP fallback | A working Scanner alone | Scanner plus risk scorer (v0.3): a ranked report without any LLM. The target is v0.4 (see Schedule). | Refined |
| 18 | Positioning | "Agentic" three-agent pipeline | Deterministic core, one agent where judgment is needed. | Changed |
| 19 | Database safeguards | Not specified | Stages are pure functions wrapped by a thin I/O layer; all SQL in one data-access module with a schema version; each stage writes in one transaction with its status update; agent write tools validate their arguments. Contains schema coupling, keeps unit tests database-free, prevents partial writes. | New |

## Refinements (18 Oct)

- **Score before triage.** Scoring is deterministic and costs nothing, so
  scoring a false positive wastes nothing. Scores let the report flag
  excluded findings that would have been critical for human review, which is
  the most dangerous error the tool can make. v0.3 already has to score
  untriaged findings, so triage stays a pure add-on in v0.4.
- **The outer pipeline is a workflow; agency lives inside planning.** Running
  scan and score in a different order never changes the result, so the order
  isn't a judgment call. A fixed loop guarantees every file is scanned and
  every finding scored, and keeps the v0.3 fallback LLM-free. Inside the
  planning pass, the LLM chooses which tool to call next, bounded by a step
  cap.
- **"Triage" keeps its name.** In security tooling it is the standard term
  for reviewing scanner results as true or false positives, which is exactly
  what the stage does.

## Schedule

The full plan is about 59 hours against the 30–36 the brief left for
Project 1. The briefing recommended committing to v0.3 and deciding at the
end of week 6 whether to build v0.4 or start Project 2.

**Decision (26 Oct): build through v0.4 before considering Project 2.** Why:
one thorough project is a stronger portfolio piece than two half-finished
ones, and the agent loop is where the project's hardest design questions
live. v0.3 remains a milestone, and the fallback if time runs out.

## Open questions

- Which Ollama model? Pick after issue 15 by testing tool-call reliability
  on two candidates.
- Is the bounded LLM risk adjustment worth building, or does v0.4 ship with
  triage and planning only?
- Is triage a single classification call per finding, or an agent with tools
  to investigate further? Decide in issue 17; describe it honestly either way.
- Where does module sensitivity come from: an optional user config file, or
  left out of v1.0?
- Does the planning pass draft liboqs snippets for every step, or only for
  the top-risk ones?
