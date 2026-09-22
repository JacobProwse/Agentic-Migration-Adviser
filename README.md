#Agentic PQC Migration Advisor Project

Problem Statement:
- Organizations facing 2030–2031 PQC migration deadlines don't know where their classical cryptography actually lives in their codebases, or which instances are most urgent to fix first.
- This tool scans a codebase, flags classical crypto usage, and produces a risk-ranked migration roadmap mapped to NIST's PQC standards.

Agentic Architecture:
- Scanner → Risk Assessor → Migration Planner.

How to run (#EXAMPLE#):
- git clone.
- docker compose up, or pip install -r requirements.txt.
- python main.py --target ./sample-repo.

What it does (concrete example):
- paste a snippet of a scanned file and the resulting risk-ranked finding.

Design decisions / why it's built this way:
- This section is curated highlights pulled from PROGRESS.md's "Decisions made" entries.

What I learned:
- One or two honest, specific technical takeaways.

What's next / limitations:
- Make generic for any code base
- ...

Tech Stack:
- liboqs-python, NIST algorithms (ML-KEM/ML-DSA/SLH-DSA), Docker, GitHub Actions, etc.
