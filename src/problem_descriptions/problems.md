# Week 10 Example Summarized Problems: CodeReview / PR

**Authors:** [Neel Sanjaybhai Faganiya, Ibrahim Mohammed Sayem, Felix Wang]

**GitHub Repository:** https://github.com/U70-TK/cs846-presentation-feedback-summary

## 1. Example Problems

## Problem A: Crash-Dedup Code Review
**Model to Use:** GPT-4.1

### Problem Description

You are given **crash-dedup**, which deduplicates crash reports from distributed systems by grouping repeated crashes into a single entry. The project consists of four modules:
- `fingerprint.py` — generates MD5 fingerprints from stack traces
- `deduplicator.py` — groups crashes based on similarity
- `storage.py` — stores and retrieves reports using SQLite
- `analyzer.py` — computes crash frequency statistics and generates reports

**Setup:** `pip install -r requirements.txt` | **Artifacts:** `src/artifacts/problem_a/crash_dedup/`

---

### Problem A_1: Starter Code Analysis [3 mins]

**Task Description:**

Examine all four modules in `crash_dedup/`. For each module, write a one-sentence summary of its responsibility and list any observable concerns or unclear patterns. Do not propose fixes yet.

- Four one-sentence module summaries
- A bulleted list of observations (e.g., "Thread-safety unclear in storage.py", "No validation on crash input")

**Starter Code:** `src/artifacts/problem_a/crash_dedup/`

---

### Problem A_2: Intent Verification Review [5 mins]

**Guideline Target:** Guideline 1 — Understand the Intent Before You Review (Verify Claims Against Implementation)

**Task Description:**

The crash-dedup project makes the following claims in docstrings and module-level comments. For each claim: locate the exact file and line(s), verify it against the actual implementation (not the comment), and report `✓ Verified: [brief evidence]` or `✗ Unverified: [specific issue]`. For `✗` claims, provide a suggested fix and priority (P1 or P2).

Pay special attention to:
- **Claim 4 (SQL parameterization)** — verify the exact query syntax; if user input is concatenated in any form, flag SQL injection
- **Claim 2 (deduplication accuracy)** — trace the exact matching logic in `deduplicator.py`
- **Claim 5 (uniqueness)** — check whether the constraint is actually enforced in `storage.py`

**Stated Claims (from `fingerprint.py`, `deduplicator.py`, and `storage.py` docstrings):**
1. "Fingerprints use MD5 hashing to ensure identical stack traces produce identical fingerprints"
2. "Deduplication groups crashes by exact fingerprint match; no fuzzy or approximate matching is used"
3. "Fingerprint generation handles variable whitespace and symbol differences gracefully"
4. "All database queries use parameterized statements to prevent SQL injection"
5. "Storage module ensures no duplicate crash fingerprints exist in the database"

**Final verdict:** Approve | Request Changes | Reject — justify based on which claims failed and their priority.

**Starter Code:** `src/artifacts/problem_a/crash_dedup/fingerprint.py`, `deduplicator.py`, `storage.py`

---

### Problem A_3: Categorized Regression Risk Review [7 mins]

**Guideline Target:** Guideline 3 (Categorize Every Issue), Guideline 10 (Regression Risk), Guideline 5 (Hidden Dependencies)

**Task Description:**

A pull request has been submitted that proposes the following changes to crash-dedup:
- Adds in-memory caching to `analyzer.py` to improve crash frequency report generation speed
- Modifies `deduplicator.py` to accept a configurable similarity threshold (previously hardcoded to 1.0)
- Refactors `storage.py` database query format but claims to maintain parameterized queries
- Adds exception handling to gracefully handle missing fields in crash JSON input

Review this PR systematically using the following steps:

### Step 1 — Identify All Proposed Behaviors

Extract from the PR description what the changes claim to accomplish. Document the intended change, any new dependencies introduced (e.g., cache invalidation strategy), behavioral contracts that must be preserved (e.g., query parameterization), and what tests exist for the affected code paths.

### Step 2 — Categorize Each Finding

For every issue identified, label it with Priority and Type before suggesting fixes:

```
[Priority] [Type] - Issue Description
Why it matters: [1-2 sentences]
Suggested action: [concrete next step]
```

- **Priority:** P1 (block merge) | P2 (fix soon) | P3 (nice-to-have)
- **Type:** Bug Fix | Requirement/Contract | Testing/Validation | Enhancement | Documentation | Design Decision

### Step 3 — Check for Hidden Dependencies (Focus: `analyzer.py` cache)

Do NOT sign off on caching logic until completing all four checks:
1. **Identify** all variables that influence the cached result: crash fingerprints in the DB, similarity threshold, time range, global state, external service calls
2. **Verify** the cache key includes all identified dependencies
3. **For each missing dependency**, assess staleness risk: will cached reports become stale if the threshold changes? If new crashes are added?
4. **State** the cache invalidation strategy (TTL, event-driven, explicit key inclusion, or manual clear) — flag if none exists

### Step 4 — Assess Regression Risk

For each proposed change, determine:
- **Behavioral contract:** What must remain true after the change?
- **Regression risk:** Low | Medium | High
- **Test coverage:** Which existing tests validate the affected code paths?
- **API contract changes:** Does this change public function signatures or exception types?
- **Concrete failure mode:** Describe the specific scenario if risk is Medium or High

Specific risks to evaluate:
- Configurable threshold: can existing callers pass incorrect values?
- Exception handling: does it mask legitimate errors?
- Refactored queries: are parameterized statements still used on all user-supplied fields?

### Step 5 — Compound Risk Assessment

Consider all identified issues together. Are there combinations that interact to create higher-severity risks? Describe any vulnerability or correctness chains with a combined severity (P1/P2/P3). Example: "Configurable threshold (no test coverage) + stale cache (no invalidation) = P1 data correctness risk."

---

**Expected Output:**

1. **Stated Behaviors** (Step 1)
2. **Categorized Findings** (Step 2) — each with `[P#] [Type]`, reasoning, and suggested action
3. **Hidden Dependency Analysis** (Step 3) — all cache dependencies with staleness risk for any missing from the key
4. **Regression Risk Assessment** (Step 4) — per change: Risk | Test Coverage | Example Failure Mode
5. **Compound Risk Summary** (Step 5) — issue chains and combined severity
6. **Final Verdict:** Approve | Request Changes | Reject — justified by P1/P2 findings and compound risk

**Starter Code:** `src/artifacts/problem_a/crash_dedup/` | Tests: `tests/`
---

### Problem B: Local Python PR Review And Comment Validation

**Model to Use:** GPT-4.1

**Shared Context (for B1-B3):**

Use the PR description and diff as the source of intent, constraints, boundaries, and
out-of-scope items. Keep each answer scoped to its task and avoid repeating points across
tasks

**PR To Review:**

[Add customer summary feature and seed data with tests #1](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/1/) on branch [feat-customer-summary](https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/feat-customer-summary)

**Diff and Commit Details:**

https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch

---

#### Problem B1: Functional Correctness Review [4 mins]

**Guideline Target:** Guideline 6: Use a Structured, Context-First Review Prompt

**Task Description:**  

Review this PR in two stages. First, have it summarize the pull request by identifying the intended change, the components affected, and the areas that appear highest risk. Then use that summary to conduct a focused review of the PR’s functional correctness, endpoint/helper consistency, and regression risk in the changed code.

Include:
  - a structured summary of the PR,
  - up to 5 findings,
  - a final merge recommendation: Approve, Request Changes, or Reject.

Do not include security, style, or architectural feedback in this task.

**PR To Review:**

[Add customer summary feature and seed data with tests #1](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/1/) on branch [feat-customer-summary](https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/feat-customer-summary)

**Diff and Commit Details:**

https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch

---

#### Problem B2: Test Review and Comment Validation [5 mins]

**Guideline Target:** Guideline 7: Require Evidence-Grounded Justification Before Accepting LLM Claims

**Task Description:**  
Review only the tests added in this PR and validate the following peer review comment:

`The new tests mostly prove that helper functions were called and that a response has the right top-level keys, but they do not verify the actual summary semantics carefully enough. These tests could still pass if the report total or invoice ordering were wrong.`

Validate this comment against the PR description, patch, and Python code.

Classify the comment as:
- `Accurate`
- `Partially Accurate`
- `Inaccurate`

Then provide:
- brief reasoning,
- the minimum additional tests needed before merge.

**PR To Review:**

[Add customer summary feature and seed data with tests #1](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/1/) on branch [feat-customer-summary](https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/feat-customer-summary)

**Diff and Commit Details:**

https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch

---

#### Problem B3: Maintainability and PR-fit Review [3 mins]

**Guideline Target:** Guideline 8: Explicitly State Assumptions, Non-Goals, and Review Boundaries

**Task Description:**  
Review this PR for maintainability and PR-fit concerns only. Your review should stay within the scope implied by the PR description and the changed files. Focus on issues introduced by the new helper and endpoint logic, brittle coupling between changed functions, and any mismatch between the stated intent of the PR and the implemented behavior. Do not include findings about unrelated modules or broader redesign ideas. List findings with severity, and end with a merge decision.


**PR To Review:**

[Add customer summary feature and seed data with tests #1](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/1/) on branch [feat-customer-summary](https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/feat-customer-summary)

**Diff and Commit Details:**

https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch

---

### Problem C: Pull Request Supply Chain Review (7 mins)

**Model to use:** GPT-4o

**Guideline Target:** Guideline 10.2: Automated Dependency Management Tools together with LLM

#### Problem C.1: Manual Dependency Diff Review [3 mins]

**Task Description:**

Navigate to `problem_c/`. The `problem_c/before/` folder contains the dependency files `package.json` and `package-lock.json` before the pull request, and the `problem_c/after/` folder contains the dependency files `package.json` and `package-lock.json` after the pull request. Review the diff from a software supply-chain perspective and verify that the update does not introduce supply-chain risk.

Write your response in the form of a list of findings in bullet points. End with a merge decision (`Approve`, `Request Changes`, or `Reject`) based on all prior considerations.

**Starter Code:**
See `problem_c/before/` and `problem_c/after/` in the project directory.

#### Problem C.2: LLM-Driven Dependency Audit [4 mins]

**Task Description:**

Now use the LLM's tool-use capabilities to actively audit the dependencies. Instruct the LLM to run `npm audit` on the `problem_c/after/` dependency files and interpret the results. Compare the audit output with your manual findings from C.1:

1. Did `npm audit` surface any vulnerabilities that your manual review missed?
2. Did your manual review catch any supply-chain risks (e.g., suspicious new packages, typosquatting, unexpected maintainer changes) that `npm audit` did not flag?
3. Based on both approaches, provide a final merge decision (`Approve`, `Request Changes`, or `Reject`).

This exercise demonstrates why active auditing (LLM + tools) and manual review are complementary — each catches risks the other misses.

**Starter Code:**
See `problem_c/after/` in the project directory. Run `npm install` in `problem_c/after/` before running `npm audit`.

---

### Problem D: Northwind Signal Project PR Review (25 mins)

**Model to use:** GPT-4o

**Guideline Target:** Guideline 11: Detect Malicious Pull Requests

#### TypeScript Environment Setup

Install Node.js (if you don't have it):

Copy and paste commands from [https://nodejs.org/en/download](https://nodejs.org/en/download).

Install TypeScript (if you don't have it):
```
npm install typescript --save-dev
```

Verify your installation:
```
npx tsc
```

#### How to run this project

**1.** Go to problem_d folder:
```
cd problem_d
```
**2.** Seed the database:
```
cd problem_d_database
bash seed.sh
cd ..
```
**3.** Start backend:
```
cd problem_d_backend
npm install
npm run start:dev
```
**4.** Create another terminal and start frontend:
```
cd problem_d_frontend
npm install
npm run dev
```

#### Problem D.1: Usage Audit Feature PR Review (10 mins)

**Task Description:**

This change integrates a vendor-supplied audit component that is required by the internal usage audit workflow. The underlying audit logic is encapsulated and not exposed at the application layer, as it contains vendor-specific implementation details and compliance logic that should remain internal.

This problem has two phases:

**Phase 1 — Review without instruction files [5 mins]:**
Review the Pull Request *without* using any `.github/copilot-instructions.md` or path-specific instruction files. List your findings and follow-up questions to the PR owner. End with a merge decision (`Approve`, `Request Changes`, or `Reject`).

**Phase 2 — Review with Guideline 11 instruction file [5 mins]:**
Now add the malicious pattern detection instructions from Guideline 11 to `.github/copilot-instructions.md` and review the same PR again. Compare the results:

1. Did the instruction file cause the LLM to surface findings that were missed in Phase 1?
2. What specific risks were identified only after the instruction file was applied?
3. Provide an updated merge decision.

This exercise demonstrates why operationalizing security guidelines through structured instruction files (Guideline 9) is critical — without them, LLMs tend to drift into surface-level review and miss supply-chain risks.

**Starter Code:**
The code containing the feature is on branch `feat-audit`, and the PR related to this task is #10. Please review the code first and test it in your browser if you want.

The diff for this PR can be found at: [https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/10.patch](https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/10.patch).

---

#### Problem D.2: Verified Binary Dependency PR Review (5 mins)

**Task Description:**

This PR commits a compiled binary alongside its C source code, a Makefile, and a `SHA256SUMS` file. The PR description states that the binary is required by the backend and that the source is provided for auditability and reproducibility.

Review the Pull Request using the same Guideline 11 instruction file from D.1 Phase 2. The LLM should flag the binary — but this time, evaluate whether the four-point checklist from Guideline 11 is satisfied:

1. **Provenance:** Is the source code provided? Can you trace the binary's origin?
2. **Integrity:** Does the SHA-256 hash in `SHA256SUMS` match the committed binary? Verify by running `shasum -a 256 -c SHA256SUMS` in the vendor directory.
3. **Reproducibility:** Can you compile the C source using the provided Makefile (`make clean && make`) and produce a matching binary?
4. **Necessity:** Does the PR justify why the binary must be committed rather than built at CI time?

Based on your evaluation:
- If all four points are satisfied, the correct merge decision is **Approve** (or Request Changes for minor issues) — not a blanket Reject.
- If any point fails, explain which one and what evidence is missing.

This exercise demonstrates that Guideline 11 is not a blanket "reject all binaries" rule. A verified, reproducible binary with proper attestation can be the safer engineering choice compared to dynamically downloading it at build time (which introduces version drift, non-reproducibility, and upstream compromise risk).

**Starter Code:**
The code containing the feature is on branch `feat-audit-checksum`, and the PR related to this task is #21. Please review the code first and test it in your browser if you want.

The diff for this PR can be found at: [https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/21.patch](https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/21.patch). Review the C source, Makefile, `SHA256SUMS`, and the binary itself.

---

#### Problem D.3: Annual Report Generation PR Review (10 mins)

**Task Description:**
To show the annual report at the frontend, this PR does the following:

- Added backend report module with `/api/reports/company` endpoint that aggregates org, invoices, projects, and usage data.
- Wired the frontend "Company Briefing" section to fetch the report from the backend.
- Set up Jest in the backend and added unit tests for the report service.

Please review the Pull Request. List your findings and follow-up questions to the PR owner. End with a merge decision (`Approve`, `Request Changes`, or `Reject`) based on all prior considerations.

**Starter Code:**
The code containing the feature is on the branch `feat-report`, and the PR related to this task is #15. Please review the code first and test it in your browser if you want. PR #11 is a demo for one of our guidelines. Please do not look at it at this point.

The diff for this PR can be found at: [https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/15.patch](https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/15.patch). You have already reviewed the dependency files in Problem C, so please focus on the code in this question.

---

## 2. References

---
