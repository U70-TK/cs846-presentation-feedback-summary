# Week 10 Updated Problem A: CodeReview of Crash-Dedup Project

**Authors:** [Neel Sanjaybhai Faganiya, Ibrahim Mohammed Sayem, Felix Wang]

**GitHub Repository:** https://github.com/U70-TK/cs846-presentation-feedback-summary

---

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

## Problem A_1: Starter Code Analysis [3 mins]

**Task Description:**

Examine all four modules in `crash_dedup/`. For each module, write a one-sentence summary of its responsibility and list any observable concerns or unclear patterns. Do not propose fixes yet.

- Four one-sentence module summaries
- A bulleted list of observations (e.g., "Thread-safety unclear in storage.py", "No validation on crash input")

**Starter Code:** `src/artifacts/problem_a/crash_dedup/`

---

## Problem A_2: Intent Verification Review [5 mins]

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

## Problem A_3: Categorized Regression Risk Review [7 mins]

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

---
