# PROGRESS.md

## Week 1 (2026-09-21 – 2026-09-27)
**Focus:** Setup git files & ML-KEM-DEMO with Liboqs

**Done:**
- Setup git on local device and made initial commit.
- Developed README.md skeleton
- Developed PROGRESS.md skeleton
- Developed procedural ML-KEM handshake script
- Updated handshake script into client & server
- Setup tests for handshake

**Didn't get to:**
- Split demo into sockets
- Setup integration test
- Merge PR
- Setup CI workflow

**Blocked / struggled with:**
- Setting up demo took longer than expected (doesn't help I kept expanding the scope).
- Nothing in particular took me too long to figure out just general development process always takes longer than expected.

**Decisions made (and why):**
- **SQLite for scan findings instead of raw JSON.** Two tables: `scan_runs` and `findings` (one-to-many).
Why: the findings are naturally relational, queries can track risk across scans, it's stdlib (no extra infra), and I get real SQL practice.
- **Ollama as the LLM backend.** Why: free, runs locally, no API key to leak. `.env` still used for config (host URL, model name) and gitignored; model weights stay in ~/.ollama, never in the repo.
- **pyproject.toml for dependencies, not requirements.txt.**
- **Sockets over an in-process client/server split for the ML-KEM refactor.** Why: learning value (framing, blocking I/O, connection lifecycle) vs ~4 hrs extra cost. Bonus: Potential reuse in project 2.
- **Client generates the ML-KEM keypair; server encapsulates.** Why: this matches TLS 1.3 hybrid key exchange (X25519MLKEM768).
- **Open the PR as a draft early on `feat/ml-kem-demo` and keep committing to it.** README changes on the feature branch rather than going straight to `main`.

**Time spent:** ~20 hrs so far (over the 10–12 target; Prioritised project over applications this week to develop portfolio. Pushed slightly ahead of schedule but lots of time went into learning ML-KEM algorithm and libraries).

**Next week:** Complete ML-KEM demo & tests. Merge PR. Setup CI workflow.

## Week 2 (2026-09-28 – 2026-10-04)
**Focus:** Finish ML-KEM-DEMO & merge branch.

**Done:**
- Completed ML-KEM handshake demo via client/server sockets
- Completed integration test
- Updated README.md
- Merged PR #1, tagged v0.1-foundations
- First release: v0.1 — ML-KEM foundations
- Test and program algorithm agnostic (change ALGORITHM in handshake.py)

**Didn't get to:**
- Set up CI workflow

**Blocked / struggled with:**
- Finishing demo due to scope creep

**Decisions made (and why):**
- Deleted ml-kem-demo.py to remove redundancy covered by integration test.
- Tests should derive sizes from liboqs so ALGORITHM is the single source of truth

**Time spent:** ~9 hrs (slightly under 10–12 target; focused more on applications this week)

**Next week:** 
- Set up CI workflow
- Learn how to create/use agents
- Set up scanner agent framework

## Week 3 (2026-10-05 – 2026-10-11)
**Focus:** Set up CI workflow. Start work on agents.

**Done:**
- Merged the refactor PR
- CI workflow refactor (formatting imports, etc)
- Set up CI workflow (and merged PR)
- Learnt AI agent basics (what an agent is & how to set up in python)
- Began using issues (v0.2 scanner agent milestone)

**Didn't get to:**
- Start on scanner agent

**Blocked / struggled with:**
- More time on setting up CI workflow than planned since some demo code needs refactoring
- Dedicated more time to applications

**Decisions made (and why):**
- **Merged PR #1 before CI existed; CI gets its own `ci/github-actions` branch.** Why: one purpose per PR, didn't want to hold the
  foundations release hostage to CI. Tagged `v0.1-foundations`.
- **Tests derive sizes from liboqs, so `ALGORITHM` in `handshake.py` is the single source of truth.** Why: tests keep working if the parameter set
  changes. Checked by swapping to ML-KEM-512 and ML-KEM-1024 and confirming
  everything still passes (mutation check).
- **Kept the algorithm-agnostic refactor in its own PR.** The branch was
  accidentally cut from the CI branch, so I rebased it onto `main` to drop
  the two CI commits. Why: one purpose per PR.
- **MIT licence** added, declared in pyproject.toml (`license = "MIT"`). Why: allows others to use, change, and distribute the software.
- **Confirmed Ollama use for the agent loop.** Why: runs locally on my device without any additional cost for API usage. Checked that ollama supports tool calling for the loop.
- **Using SQLite as shared state between agents.** Why: The findings are deterministic facts produced by static analysis. The LLM reasons over stored, verifiable records (file X, line Y). That cuts down on hallucinated findings and gives an audit trail. Open question of whether assessments go in their own table.
- **Planning the Scanner so other languages can be added later, without building that now.** Why: The main classical cryptography identification is done using python ast. I want to set up for efficient adjustments/improvements in the future (scans C, C++, etc files) without dedicating unnecessary time now.

**Time spent:** ~4.5 hrs (under 10–12 target; focused more on applications this week)

**Next week:** 
- Scanner agent design & decisions (regarding tools, scope, sqlite, etc)
- Create issues/work schedule for scanner agent
- Scanner agent file framework
- Scannar agent API
- Scanner agent fitted with basic tools

## Week 4 (2026-10-12 - 2026-10-18)
**Focus:** Scanner agent design and foundations

**Done:**
- Agent design
- SQLite schema
- Planning & issue/milestone creation
- README & PROGRESS update after design changes

**Didn't get to:**
- Complete scanner due to major design changes

**Blocked / struggled with:**
- Struggled to make progress whilst travelling. I had to find ways to stay productive — I did this by working on design choices which were more accessible offline. 

**Decisions made (and why):**
- **Moved the ML-KEM demo into `foundations/` (tests in `tests/foundations/`);
  `src/agentic_migration_adviser/` holds only the migration tool.** Kept the
  four modules separate rather than merging them, to preserve the
  framing/handshake mechanism-vs-policy split. Only config change:
  pytest `pythonpath = ["foundations"]`. Why: the demo was for learning ML-KEM and isn’t part of the tool itself. Keeping it separate stops it mixing with the product code.
- **Issue-driven workflow:** Issue → `gh issue develop` → commits → PR with
  `Closes #N` → CI green → merge. Labels and milestones map to release tags
  (v0.1.1, v0.2, v0.3, v0.4, v1.0).
- **[CHANGED] Three agents → deterministic core + one agent.** Scanner and
  risk scorer are rule-based; one hand-rolled Ollama loop runs a triage pass
  and a planning pass. Why: only triage and planning need judgment; rules
  are testable and defensible.
- **[CHANGED] Risk scoring is rule-based**, with rule IDs (Shor vs Grover,
  key exchange before signatures / HNDL, exposure, blast radius, migration
  difficulty). Any LLM adjustment capped at one tier, stored separately.
- **[NEW] LLM triage of low-confidence findings only.** Verdicts
  include/exclude/needs-human with evidence; nothing is deleted.
- **[NEW] SQLite is the only interface between stages, with safeguards:**
  pure stage functions, one data-access module with a schema version, one
  transaction per stage, validated agent write tools.
- **[CHANGED] Schema extended from 2 tables** to repos, scans, findings,
  risk scores, triage verdicts, plan_steps plus a link table. Scans record
  the commit SHA, versions and status, and findings are fingerprinted. This
  answers last week's open question: assessments get their own table.
- **[DEFERRED] Non-Python languages.** Language-neutral schema and scanner
  registry now; C/C++ parsing later.
- **[REFINED] Targets:** trustme (smoke), PyJWT (primary), paramiko
  (stretch), python-rsa (limitation demo), pinned by SHA.
- **[REFINED] MVP fallback is v0.3** (scanner + risk scorer, no LLM). Decide
  at the end of week 6 whether to build v0.4 or start Project 2.

**Time spent:** ~6.5 hrs (under 10–12 target; found it harder to complete work due to travel. Decided to focus on design which didn't require as much setup: laptop, wifi, etc).

**Next week:** 
- Scanner tool foundations

## Week 5 (2026-10-19 - 2026-10-25)
**Focus:** Networking & application test — no project development this week.

**Time spent:** ~0 hrs (under 10–12 target; this week I was focused on studying for a test I had to complete as part of a job application — I also had a day in London at a networking event).

**Next week:** 
- Scanner tool foundations

## Week 6 (2026-10-26 - 2026-11-01)
**Focus:** Scanner tool foundations

**Done:**
- 

**Didn't get to:**
- 

**Blocked / struggled with:**
- 

**Decisions made (and why):**
- 

**Time spent:** ~ hrs (under/achieved/over 10–12 target; why?).

**Next week:** 
-