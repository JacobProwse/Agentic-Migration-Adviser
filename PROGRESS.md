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

**Next week:** Complete ML-KEM demo & tests. Merge PR. Setup CI workflow. Begin Risk Assessor Agent/Agentic Architecture.

## Week 2 (2026-09-28 – 2026-10-04)
**Focus:** Finish ML-KEM-DEMO & merge branch. Setup CI workflow. Start work on agents.

**Done:**
- Completed ML-KEM handshake demo via client/server sockets
- Completed integration test
- Updated README.md
- Merged feature branch
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