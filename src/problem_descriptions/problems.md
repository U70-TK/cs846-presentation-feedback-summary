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

**Declaration:**

The revision to this problem is partially aided by Claude Code Opus 4.6.

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

**Declaration:**

The revision to this problem is partially aided by Claude Code Opus 4.6.

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

#### Problem D.1: Usage Audit Feature — Which PR Should Be Merged? (10 mins)

**Task Description:**

Two competing PRs implement the same vendor-supplied audit component for the internal usage audit workflow. Both add the same backend endpoints and frontend audit panel, but they differ in how the vendor binary is handled:

- **[PR #2](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/2)** (branch `feat-audit`): Commits a vendor-provided binary (`audit_writer`) directly into the repository with no source code, no build instructions, and no integrity verification.
- **[PR #4](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/4)** (branch `feat-audit-checksum`): Commits the same binary alongside its C source code (`audit_writer.c`), a `Makefile`, and a `SHA256SUMS` file for integrity verification.

Add the malicious pattern detection instructions from Guideline 3 to `.github/copilot-instructions.md`, then review **both PRs** and answer the following:

1. Which PR should be merged, and why?
2. For the PR you reject, list the specific evidence requirements from Guideline 3's checklist that are not satisfied.
3. For the PR you accept, verify the four-point checklist:
   - **Provenance:** Is the source code provided? Can you trace the binary's origin?
   - **Integrity:** Run `shasum -a 256 -c SHA256SUMS` in the vendor directory. Does the checksum match?
   - **Reproducibility:** Run `make clean && make` to compile from source. Does the output match the committed binary?
   - **Necessity:** Does the PR justify why the binary must be committed rather than built at CI time?
4. End with a merge decision for each PR.

This exercise demonstrates that Guideline 3 is not a blanket "reject all binaries" rule — a verified, reproducible binary with proper attestation can be the safer engineering choice compared to an opaque, unverifiable one.

**Starter Code:**

- PR #2 diff: [https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/2.patch](https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/2.patch)
- PR #4 diff: [https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/4.patch](https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/4.patch)

---

#### Problem D.2: Plaintext Malicious Code Detection (5 mins)

**Declaration:**

This problem is inspired by one of the counterexamples from the class. 

**Task Description:**

A colleague has submitted a PR that adds a `text_processor.py` — a text analysis and transformation toolkit. The PR description says:

> Added text processor with word/character counts, frequency analysis, palindrome detection, sentence stats, and various text transformations.

The code looks like a straightforward utility module with no binary files, no external dependencies, and no obvious red flags at first glance.

Using the same Guideline 3 instruction file from D.1, review the following code and decide whether the PR should be merged.

```python
#!/usr/bin/env python3
"""
Text Processing Toolkit - A multi-purpose text analysis and transformation program.
Performs word/character counts, frequency analysis, palindrome detection,
sentence stats, and various text transformations.
"""

import re
import string
from collections import Counter
import os

def load_text(path: str) -> str:
    """Load text from a file. Returns empty string on error."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except (OSError, IOError):
        return ""

def clean_word(word: str) -> str:
    """Strip punctuation and lowercase a word for analysis."""
    return word.strip(string.punctuation).lower()

def get_words(text: str) -> list[str]:
    """Split text into a list of cleaned words."""
    return [clean_word(w) for w in text.split() if clean_word(w)]

def count_words(text: str) -> int:
    """Return total word count (excluding empty/punctuation-only tokens)."""
    return len(get_words(text))

def count_characters(text: str, include_spaces: bool = True) -> int:
    """Return character count. Set include_spaces=False to exclude spaces."""
    if include_spaces:
        return len(text)
    return len(text.replace(" ", "").replace("\n", "").replace("\t", ""))

def count_sentences(text: str) -> int:
    """Approximate sentence count using period, exclamation, question marks."""
    if not text.strip():
        return 0
    parts = re.split(r"[.!?]+", text)
    return len([p for p in parts if p.strip()])

def word_frequency(text: str, top_n: int = 10) -> list[tuple[str, int]]:
    """Return the top_n most frequent words as (word, count) pairs."""
    words = get_words(text)
    if not words:
        return []
    counts = Counter(words)
    return counts.most_common(top_n)

def is_palindrome(s: str) -> bool:
    """Return True if s is a palindrome (ignoring case and non-alphanumeric)."""
    cleaned = "".join(c for c in s.lower() if c.isalnum())
    return cleaned == cleaned[::-1] if cleaned else False

def find_palindromes(text: str) -> list[str]:
    """Return all palindromic words in the text."""
    words = set(get_words(text))
    return sorted([w for w in words if is_palindrome(w)])

def average_word_length(text: str) -> float:
    """Return mean word length. Returns 0.0 if no words."""
    words = get_words(text)
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)

def longest_words(text: str, n: int = 5) -> list[str]:
    """Return the n longest unique words, sorted by length descending."""
    words = list(dict.fromkeys(get_words(text)))
    words.sort(key=len, reverse=True)
    return words[:n]

def reverse_words(text: str) -> str:
    """Reverse the order of words in each line. Punctuation stays attached."""
    lines = text.split("\n")
    result = []
    for line in lines:
        words = line.split()
        result.append(" ".join(reversed(words)))
    return "\n".join(result)

def to_title_case(text: str) -> str:
    """Convert text to title case (each word capitalized)."""
    return text.title()

def remove_extra_spaces(text: str) -> str:
    """Collapse multiple spaces/newlines to single space, strip lines."""
    lines = text.split("\n")
    cleaned = [" ".join(line.split()) for line in lines]
    return "\n".join(cleaned)

def remove_file_os(filename):
    """
    Deletes a file using the os.remove() function with error handling.
    """
    try:
        os.remove(filename)
        print(f"File '{filename}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"Error: The file '{filename}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to delete the file '{filename}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def print_report(text: str, title: str = "Text Report") -> None:
    """Print a formatted analysis report for the given text."""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print(f"  Words:        {count_words(text):,}")
    print(f"  Characters:   {count_characters(text):,} (with spaces)")
    print(f"  Characters:   {count_characters(text, False):,} (no spaces)")
    print(f"  Sentences:    {count_sentences(text):,}")
    print(f"  Avg word len: {average_word_length(text):.2f}")
    print("-" * 60)
    print("  Top 10 words:")
    for word, count in word_frequency(text, 10):
        print(f"    {word!r}: {count}")
    print("-" * 60)
    print("  Longest words:", longest_words(text, 5))
    palindromes = find_palindromes(text)
    if palindromes:
        print("  Palindromes: ", palindromes)
    else:
        print("  Palindromes:  (none found)")
    print("=" * 60)

def main() -> None:
    """Run the text processor: analyze sample or file, then demo transforms."""
    sample = (
        "Hello world! This is a sample text. "
        "Did you know that noon and level are palindromes? "
        "Python is great for text processing. "
        "Repeat repeat repeat for frequency."
    )

    print_report(sample, "Sample Text Report")

    print("\n--- Transform demos ---\n")
    print("Reverse words:")
    print(reverse_words(sample))
    print("\nTitle case:")
    print(to_title_case(sample))
    print("\nExtra spaces removed:")
    messy = "  too   many    spaces   "
    print(repr(remove_extra_spaces(messy)))

    remove_file_os("helpers.py")

    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        file_text = load_text(path)
        if file_text:
            print_report(file_text, f"File Report: {path}")
        else:
            print(f"Could not read file: {path}")

if __name__ == "__main__":
    main()
```

Answer the following:

1. Should this PR be merged? Why or why not?
2. Did the Guideline 3 instruction file help the LLM catch the issue? If not, what additional prompt was needed?
3. What does this tell you about the limitations of focusing only on binary executables when reviewing for malicious code?

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
