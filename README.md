# Agentic PQC Migration Adviser

> **Status:** v0.1-foundations. This release contains the ML-KEM (FIPS 203)
> key-exchange groundwork. The agent is planned for v0.4, not yet built.

## The problem
Organisations face hard post-quantum migration deadlines. US federal systems
must migrate key establishment by 2030 and signatures by 2031. The UK NCSC
roadmap sets planning by 2028, high-priority upgrades by 2031, and full
migration by 2035. Most teams don't know where classical cryptography lives
in their codebases, or which usages to fix first.

This tool will scan a codebase, flag classical crypto usage, and produce a
risk-ranked migration roadmap mapped to NIST's PQC standards.

## Planned architecture
```mermaid
flowchart LR
    subgraph rules [Deterministic rules]
        S[Scan<br/>ast · regex · deps] --> R[Score risk<br/>rule IDs: Shor, Grover, HNDL]
    end
    subgraph agent [One agent loop, two passes]
        T[Triage<br/>low-confidence findings only] --> P[Plan<br/>ordered fix steps, verified by rescan]
    end
    R --> T
    DB[(SQLite: the only interface between stages)]
    S <--> DB
    R <--> DB
    T <--> DB
    P <--> DB
```

Stage | Rules or LLM | What it does | Output | Milestone
|---|---|---|---|---|
| Scanner | Rules | The design has three layers: Python call sites through ast (high confidence), declared and locked dependencies (medium), and regex over text and config files (low). | Findings with file, detection rule, fingerprint, line, key size, confidence, etc; stored in SQLite | v0.2 |
| Risk Scorer | Rules | Risk-rank findings mapped to ML-KEM / ML-DSA / SLH-DSA. High confidence findings (from python modules) are sequenced deterministically | RSA/ECC → critical (Shor's algorithm); symmetric → lower priority (Grover's algorithm) | v0.3 |
| Findings Triage | LLM | Decides whether low confidence findings are real violations and sequences them accordingly | Prioritised roadmap | v0.4 |
| Migration planner | LLM | Takes roadmap and develops plan? | Full migration plan | v0.4 |

The orchestration is hand-rolled, without an agent framework. It uses a local
LLM through Ollama, so no API keys leave the machine.

# Findings database: schema design

Status: design for issue #5, updated 26 Oct. Nine tables, built up across milestones. Based on decision 11 in the 14 Oct design briefing, plus `files` (needed for 3NF) and `risk_rule_hits` (rule-level queries).

## ER diagram (target: v0.4)

```mermaid
erDiagram
    repos ||--o{ scans : "scanned in"
    scans ||--o{ files : "discovers"
    files ||--o{ findings : "contains"
    findings ||--o| risk_scores : "scored by"
    risk_scores ||--|{ risk_rule_hits : "explained by"
    findings ||--o| triage_verdicts : "triaged by"
    scans ||--o{ plan_steps : "planned in"
    plan_steps ||--|{ plan_step_findings : "fixes"
    findings ||--o{ plan_step_findings : "fixed by"

    repos {
        INTEGER id PK
        TEXT name UK "e.g. jpadilla/pyjwt"
        TEXT url
        TEXT local_path "clone under targets/"
        TEXT created_at
    }

    scans {
        INTEGER id PK
        INTEGER repo_id FK
        TEXT commit_sha "pinned target SHA"
        TEXT scanner_version
        TEXT rules_version "version of the rules file used"
        TEXT status "pending|scanned|scored|triaged|planned|failed"
        TEXT error_message "nullable, set only when failed"
        TEXT started_at
        TEXT finished_at
    }

    files {
        INTEGER id PK
        INTEGER scan_id FK
        TEXT path "relative to repo root"
        TEXT language "python, text, config, ..."
        INTEGER is_test_path "0/1"
        INTEGER is_doc_path "0/1"
    }

    findings {
        INTEGER id PK
        INTEGER file_id FK
        TEXT fingerprint "unique per file, so unique per scan"
        INTEGER line
        TEXT detection_rule_code "e.g. DET-PY-007, from the rules file"
        TEXT detection_method "ast|dependency|text, snapshot"
        TEXT primitive "RSA, ECDSA, ECDH, ..., snapshot"
        TEXT operation "key_exchange, signature, ..., snapshot"
        INTEGER key_size "nullable, e.g. 2048"
        TEXT curve "nullable, e.g. secp256r1"
        TEXT confidence "high|medium|low"
        TEXT snippet "the matched line"
    }

    risk_scores {
        INTEGER id PK
        INTEGER finding_id FK "unique: one score per finding"
        TEXT base_tier "critical|high|medium|low"
        INTEGER llm_adjustment "nullable, -1, 0 or +1"
        TEXT llm_adjustment_reason "nullable"
        TEXT llm_evidence_lines "nullable"
    }

    risk_rule_hits {
        INTEGER risk_score_id PK, FK
        TEXT rule_code PK "e.g. RISK-SHOR-01, from the rules file"
    }

    triage_verdicts {
        INTEGER id PK
        INTEGER finding_id FK "unique: one verdict per finding"
        TEXT verdict "include|exclude|needs_human"
        TEXT reason
        TEXT evidence_lines
        TEXT model "which Ollama model decided"
        TEXT created_at
    }

    plan_steps {
        INTEGER id PK
        INTEGER scan_id FK
        INTEGER step_order "unique within a scan"
        TEXT action "what to change"
        TEXT target_algorithm "from get_replacement"
        TEXT rationale "why this position in the order"
        TEXT snippet "nullable liboqs draft"
        INTEGER verified "0/1, set by rescan_file"
        TEXT model
        TEXT created_at
    }

    plan_step_findings {
        INTEGER plan_step_id PK, FK
        INTEGER finding_id PK, FK
    }
```

## Tables, and what breaks without each one

| Table | Written by | Milestone | What breaks without it |
|---|---|---|---|
| `repos` | Setup / CLI | v0.2 | Repo name and URL repeat on every scan (a 3NF violation). |
| `scans` | Scanner; each stage updates `status` | v0.2 | No commit SHA, versions or status, so no cross-scan tracking. |
| `files` | Scanner (file discovery) | v0.2 | Language and test/doc flags repeat on every finding in a file. |
| `findings` | Scanner | v0.2 | The core data. Rows are never deleted. |
| `risk_scores` | Risk scorer, plus an optional LLM adjustment | v0.3 | The scorer would edit the scanner's output, and re-scoring would need a rescan. |
| `risk_rule_hits` | Risk scorer | v0.3 | "Which findings did rule X fire on?" can't be answered, and mutation checks can't query it. |
| `triage_verdicts` | Agent loop, triage pass | v0.4 | Triage can't be measured on its own, and verdicts would overwrite findings. |
| `plan_steps` | Agent loop, planning pass | v0.4 | The plan becomes an unqueryable blob. |
| `plan_step_findings` | Agent loop, planning pass | v0.4 | Without it there's no way to record that one step fixes many findings. |

## Rules stay out of the database

The rules file in git is the single source of truth for detection rules, risk rules and the FIPS replacement mapping. The database records only which rules were used:

- `scans.rules_version` is the rules file version for the run.
- `findings.detection_rule_code` and `risk_rule_hits.rule_code` are codes from that file.
- `get_replacement` reads the FIPS mapping from the rules file.

Reasons:

- Rule changes show up as diffs in a PR.
- Mutation checks are simple: delete a rule from the file and confirm a test fails.
- Stage functions and their tests run without a database.
- There's no second copy of the rules to drift out of sync.

The trade-off is that rule codes are plain text, not foreign keys. A code is always read against the scan's `rules_version`.

## Normalisation: 3NF, with deliberate exceptions

- **Snapshot columns on `findings`** (`primitive`, `operation`, `detection_method`): the rule code implies these values, so storing them is a transitive dependency. They are kept on purpose, in the same way an order line stores the price at the time of sale. A finding records what the scanner found under the rules in force then. If a later rules version re-maps a pattern, old findings don't silently change. This also lets SQL group findings by primitive without needing the rules file.
- **`findings.fingerprint`** is derived from other values. It's stored because it's the cross-scan matching key and needs an index.
- **`risk_scores.base_tier`** could be recomputed from the rule hits. It's stored as the scorer's recorded output for that rules version.
- **The final risk tier** (base tier plus LLM adjustment) is not stored. It's computed at query time.

## Constraints

- `UNIQUE(scan_id, path)` on `files`
- `UNIQUE(file_id, fingerprint)` on `findings`, which means unique per scan because the fingerprint includes the path
- `UNIQUE(finding_id)` on `risk_scores` and on `triage_verdicts`
- `UNIQUE(scan_id, step_order)` on `plan_steps`
- `CHECK` constraints on the status, tier, confidence and verdict values

## Notes

- The schema version is stored in SQLite's built-in `PRAGMA user_version` and goes up at each milestone (v0.2 → 1, v0.3 → 2, v0.4 → 3).
- Foreign keys are off by default in SQLite, so turn them on for each connection.
- Timestamps are ISO 8601 TEXT.

## Repository layout
`foundations/` holds the v0.1 ML-KEM handshake groundwork, meaning the handshake, framing, client and server modules, with their tests in `tests/foundations/`.\
`src/agentic_migration_adviser/` is the actual migration tool, where the Scanner, Risk Assessor and Planner will live.\
I split them since the demo was for learning ML-KEM and isn’t part of the tool itself. Keeping it separate stops it mixing with the product code.

foundations/                  # v0.1: ML-KEM handshake demo\
tests/foundations/\
src/agentic_migration_adviser/  # the migration tool (Scanner onwards)\
tests/scanner/                # coming in v0.2\

## What's in this release
- `foundations/handshake.py`: the algorithm is set by the ALGORITHM constant (currently ML-KEM-768, tests adapt accordingly) KeyGen → Encaps → Decaps using liboqs-python.
- `foundations/client.py`/`foundations/server.py`: Handshake split over TCP sockets. The client
  generates the keypair and the server encapsulates, mirroring how TLS 1.3
  hybrid key exchange (X25519MLKEM768) carries the public key in the
  ClientHello and returns the ciphertext in the ServerHello.
- `tests/foundations/test_framing.py`: round trips, message boundaries, fragmented delivery, early disconnects, oversized headers
- `tests/foundations/test_handshake.py`: matching shared secrets, implicit rejection of tampered ciphertext, key/ciphertext/secret sizes checked against liboqs, wrong-size input errors, fresh keypair per client
- `tests/foundations/test_socket_handshake.py`: matching secrets over TCP, server rejecting a wrong-size public key, client failing fast with no server, server timing out a silent client

## Quick start
Requires Python >=3.10 and
[uv](https://docs.astral.sh/uv/). On macOS, liboqs needs `brew install cmake ninja`.

    git clone https://github.com/JacobProwse/Agentic-Migration-Adviser.git
    cd Agentic-Migration-Adviser
    uv sync
    uv run python foundations/server.py & sleep 1 && uv run python foundations/client.py
    uv run pytest -q

## Example output

```text

Server listening on ('127.0.0.1', 65432)
Connected to server at 127.0.0.1:65432
Connection from: ('127.0.0.1', 63012)
Server hashed shared secret snippet: ba1a49dc2b7b70bc...
Client hashed shared secret snippet: ba1a49dc2b7b70bc...
21 passed in 0.54s

```

For reference, FIPS 203 specifies these ML-KEM-768 (current set algorithm) sizes: public key 1184 B,
ciphertext 1088 B, shared secret 32 B.

## Design decisions
- **pyproject.toml + uv** over requirements.txt, for a lock file and reproducible installs.
- **Sockets rather than an in-process split:** I chose to prioritise learning value (framing, blocking I/O, connection lifecycle) over ~4 hrs extra cost. Bonus: Potential reuse in project 2.
- **Client generates the keypair, server encapsulates:** this matches the real TLS 1.3 hybrid flow (however I only used ML-KEM not hybrid).

## What I learned
- Where a rule should live matters as much as the rule itself. I initially considered enforcing the exact public key size in the framing layer. Instead, the framing layer checks against a generic 1 MiB cap, on both send and receive, whilst the handshake layer checks the exact public key. The revision came from the principle that lower layers should provide mechanism, whilst higher layers decide policy. The principle ensures that the behaviour of lower layers is independent of the process which sits above it. If the algorithm changes in later development the framing module doesn't need adjusting.
- A test that can't fail gives false confidence. I thought running two handshakes and asserting their secrets differ would ensure that each client generates a fresh keypair. Then, I realised that the test would have passed even if the client reused its keypair, because encaps adds its own randomness. Instead, I produced a unit test that directly compares the public keys of two Client instances. Now, before trusting a test, I make sure to try at least one mutation check to make sure that a test really can fail; using git restore to make sure the deliberate break never gets committed.
- The liboqs library handles the maths, not the protocol. It made generating keys & ciphertexts easy for running a basic procedural program. However, I had to provide the framework by splitting protocol roles between the client/server sockets, verifying implicit rejection of a tampered ciphertext (since decaps returns a wrong secret with no exception) and more.

## Limitations & roadmap
- This is a key-exchange demo, not TLS. The handshake is unauthenticated,
  and a real deployment would need signatures such as ML-DSA.
- GitHub Actions CI (pytest + ruff)
- [ ] Scanner Tool + SQLite findings store
- [ ] Risk Assessor Rules
- [ ] Migration Planner Agent + orchestrator
- [ ] Dockerfile for one-command setup
- [ ] Support for codebases beyond Python

## Tech stack
Used: python, liboqs-python (Open Quantum Safe), NIST ML-KEM, uv, GitHub Actions.\
Planned: SQLite, Ollama, Docker.
