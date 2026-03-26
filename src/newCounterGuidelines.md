# Week 10 Guidelines: CodeReview / PR

**Authors:** [Neel Sanjaybhai Faganiya, Ibrahim Mohammed Sayem, Felix Wang]




## 1. New given Guidelines




#Format of this document:
```
##Old guideline

---
---

## All the updated guideline different groups gave for this particular guideline (all guidelines seperated by  lots of ----------------------------------------)





---
---
---






##Old guideline

---
---

## All the updated guideline different groups gave for this particular guideline (all guidelines seperated by  lots of ----------------------------------------)





---
---
---
.
.
.
.
.
.
.
.
.
and so on and on

```

## Old Guideline 1: Create a structured instruction file

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated Guideline: [Diagnose first, patch later] (group 2)

**Prompt and Context:**

(no `instruction.md` is used)
This is an iterative debugging task. Do not propose code changes yet.
First explain the likely issue in the current code, what evidence supports it, and what is still uncertain.
Avoid refactoring or broad fixes until the cause is clear.

----------------------------------------------------

### Updated guideline: Discuss Merge Conflict with Copilot in Web App instead of through instructions file (group 6)

**Description:**
Github has a web app that allows copilot conversations with access to the git repo, and this is a much easier method to discuss merge conflicts and what will come of each possible choice.

**Reasoning:**
This is quicker and easier to deal with merge conflicts than setting them up locally and simply using the instructions file does not deal with them automatically.

#### Using New Guideline on Problem:
**Prompt and Context:**
For this solution, the copilot chat in the GitHub web app was used instead of the instructions file for the detailed review.

Please review the changes and identify merge conflicts, describing what each option would entail.

Please walk through each conflict section and spell out what ours vs theirs is for each conflicting file.

Please produce the 3-way merged chunks with step-by-step resolution ideas, for the merge into NewGuideline








---
---
---











## Old Guideline 3: Be Extra Cautious about Binary Executables

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated Guideline: Enforce Binary-Artifact Review Gates (Operationalized via Guideline 9)  (group 1)

**Description:**

To make Guideline 11 reliable in practice, operationalize it through Guideline 9 (structured instruction files).  
Without instruction files, Copilot often drifts into surface-level review and can underweight supply-chain risks.

The updated approach is:
- Define repo-wide review priorities and output structure in `.github/copilot-instructions.md`.
- Add path-specific TypeScript security/testing expectations in `.github/instructions/typescript.instructions.md`.
- Explicitly require binary-executable findings to block merge unless provenance, integrity, and necessity are documented.

**Prompt and Context:**  
```text
Use these review instructions:

Repo-wide (.github/copilot-instructions.md):
- Prioritize Security, Correctness, Error Handling, Testing, Maintainability.
- Report findings with file path, lines, category, finding, reasoning.
- Do not give generic PR summaries.

TypeScript path-specific (.github/instructions/typescript.instructions.md):
- Be extremely cautious with binary executables. Avoid by default.
- Require unit tests for exported logic.

Now review PR #10 (Usage Audit Feature) for problem_d.
Treat committed binary executables as high-risk supply-chain artifacts.
If any binary is committed and executed by backend logic, require:
1) provenance/source origin,
2) integrity evidence (checksum/signature),
3) reproducible build path,
otherwise mark as merge-blocking.
End with a merge decision.
```

------------------------------------------------------

### Updated Guideline: Enforce a Binary Executable Detection and Interrogation Protocol (group 4)

**Description:**  
When reviewing any pull request, the LLM must actively scan for binary or non-human-readable files in the diff (e.g., `.exe`, `.dll`, `.jar`, `.so`, `.dylib`, `.bin`, `.wasm`, or any file that cannot be rendered as text). When a binary is detected, the review must **immediately escalate** it as a high-severity finding and block the merge by default. The LLM must not evaluate the rest of the PR favorably until the binary is justified.

For each binary detected, the review must demand:

1. **Provenance**: Where did this binary come from? Is the source code available?
2. **Reproducibility**: Can this binary be rebuilt from source? Provide build instructions.
3. **Integrity verification**: Is there a cryptographic hash (SHA-256) that matches a known-good artifact?
4. **Necessity justification**: Why must this be a committed binary rather than a build-time dependency?
5. **Scope of execution**: What does this binary do? What system resources does it access?

If the PR author cannot satisfy all five, the merge decision must be **Reject**.

**Reasoning:**

- Previous studies show that many known CVE vulnerabilities are embedded within precompiled binaries committed into repositories [13–15 from the guidelines references].
- Binary artifacts cannot be meaningfully reviewed, diffed, or statically analyzed using standard development workflows.
- The original Guideline 11 said "be cautious" but did not specify _what actions to take_ or _what evidence to demand_, which caused the LLM to skip the finding entirely.
- By framing the binary as a mandatory escalation with a five-point checklist, the LLM is forced to surface it regardless of how the PR is described.

**Prompt and Context:**

The following updated instruction was added to `.github/copilot-instructions.md`:

```markdown
# Copilot Code Review Instructions

You are assisting with pull request code review.
Your job is to identify meaningful issues in the changed code, not to summarize the PR.

In your code review, prioritize:

- Security
- Correctness
- Error handling
- Testing
- Maintainability

## Review output format

### `file path`

- **Lines:** `x-y`
- **Category:** `Security | Correctness | Error Handling | Testing | Maintainability | Performance | Design`
- **Finding:** concise issue statement
- **Reasoning:** brief concrete explanation

## Rules

- Always group findings under the file they belong to.
- Always include line numbers.
- Always assign one primary category.
- Keep reasoning brief, specific, and technical.
- Focus on actionable findings only.
- Do not summarize the PR unless no issues are found.

## CRITICAL: Binary Executable Detection

If ANY file in the diff is a binary executable or a non-text file that is invoked by code
(e.g., .exe, .dll, .jar, .so, .dylib, .bin, .wasm, or any file that cannot be rendered as
readable source code), you MUST:

1. **Immediately flag it as a BLOCKER-severity security finding.**
2. **State the file path and how it is invoked in the codebase.**
3. **Demand the following from the PR author before merge can proceed:**
   - Source code or build instructions to reproduce the binary from source.
   - A cryptographic hash (SHA-256) matching a known-good artifact from the vendor.
   - Explicit justification for why this must be a committed binary rather than a build-time
     dependency fetched from a trusted registry.
   - Documentation of what the binary does and what system resources it accesses.
4. **The merge decision MUST be Reject until all four items above are provided.**
5. **Do NOT evaluate the rest of the PR favorably until the binary is addressed.**

A binary committed to a repository is a blind spot for all reviewers — human and automated.
It cannot be diffed, linted, or statically analyzed. Treat it as a potential supply-chain attack
vector by default.
```

The following was added to `.github/instructions/typescript.instructions.md`:

```markdown
---
applyTo: "**/*.ts"
---

# TypeScript Coding Standards

## Security

- **Binary executables are blocked by default.** Any PR that introduces a binary executable
  (e.g., in a vendor/ directory) MUST be flagged as a BLOCKER. Require the PR author to
  provide: source code, build reproducibility steps, SHA-256 hash verification, and a written
  justification. Do not approve the PR until all are provided.
- Validate and sanitize all inputs passed to `child_process` functions (`exec`, `execFile`,
  `spawn`). Flag any use of these with unsanitized user input as a critical vulnerability.

## Error Handling

- Always handle promise rejections with `try/catch` or `.catch()`.
- Use custom error classes for application-specific errors.
- Never use bare `catch (error)` without typing the error parameter.

## Testing

- Write unit tests for all exported functions.
- Use Jest for all testing.
- Name test files as `<filename>.test.ts`.

## Example

// Good
interface AuditEvent {
id: number;
message: string;
timestamp: Date;
}

const writeAuditEvent = async (event: AuditEvent): Promise<void> => {
try {
// ... write logic using a library, NOT a binary
} catch (error: unknown) {
if (error instanceof Error) {
throw new AuditWriteError(error.message);
}
throw new AuditWriteError('Unknown error during audit write');
}
};

// Bad
const writeAuditEvent = async (message: any) => {
execFile('./vendor/audit_writer', [message]); // Binary! No validation! No error handling!
};
```

Then, the following prompt was used with GPT-4.1:

```
I am reviewing Pull Request #10 on branch feat-audit.

PR Description: This change integrates a vendor-supplied audit component required by the
internal usage audit workflow. The underlying audit logic is encapsulated and not exposed
at the application layer.

[Include the full diff here]

Please review this PR following the instructions in .github/copilot-instructions.md and
.github/instructions/typescript.instructions.md.

For every finding:
1. Quote the specific line(s) of code that support your claim.
2. Explain the failure path using only those lines.
3. If you cannot point to a specific line, do not include the finding.

End with a merge decision: Approve, Request Changes, or Reject.
```

-------------------------------------------------------

### Updated guideline: Be Extra Cautious About Any Potential Malicious Behaviour (group 7)

**Guideline Definition**
Express to the LLM the need to err on the side of caution when deciding whether or not a PR should be merged into the repo. Malicious code can be embedded in files such as images and PDFs, be obfuscated in a binary file, or added directly in plaintext to files and merged into repos if not carefully reviewed.

**Prompt and Context:**  

Can you review this PR patch file and gauge whether or not the PR should be merged. Be wary of any potential malicious code. When in doubt, err on the side of caution, and don't approve the PR if it seems even a little bit malicious: 
From ef4da45ab510028b883e1a718ff00e2dd73a4af0 Mon Sep 17 00:00:00 2001
From: Greg French <g2french@uwaterloo.ca>
Date: Mon, 16 Mar 2026 21:36:51 -0400
Subject: [PATCH] Added text processor










---
---
---










## Old Guideline 4: Assess Regression Risk as Part of Every Review Decision

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated Guideline: Assess Regression Risk as Part of Every Review Decision (group1)

When reviewing any proposed fix, assess whether the change could break existing correct behavior or introduce new risk. For every fix, report:

- Regression risk: `Low | Medium | High`
- Are there existing tests that cover the affected code path?
- Does this fix change the **public API contract** — specifically the return type, parameter semantics, or the *documented* exception type on an already-tested path?
- Is this fix **security-critical** (SQL injection, authentication, credential handling, input sanitization)?

**Flag a fix as `HUMAN REVIEW REQUIRED` if and only if any of the following are true:**
1. Regression risk is `High` **AND** no existing test covers the affected behavior, **OR**
2. The fix changes the **public API contract** — it changes which exception type is raised on a documented, already-tested path; changes the return type or shape of a public function; or removes a parameter that callers may depend on, **OR**
3. The fix addresses a **security-critical vulnerability** (SQL injection, auth bypass, hardcoded credentials, unsafe deserialization).

**Do NOT flag a fix as `HUMAN REVIEW REQUIRED` solely because it adds or modifies exception handling.** A guard clause (`if x <= 0: raise ValueError`) that applies to an already-tested code path and does not change the function's documented behavior for valid inputs is Low risk and does not require human review.

**Reasoning**

- Security vulnerabilities (SQL injection, auth bypass, credential exposure) are the highest-impact class of fix and are completely invisible to regression-only analysis — they introduce new risk rather than breaking existing behavior, so exception/shared-state proxies will never catch them.

- A change to the exception type raised on an already-tested code path is a verifiable contract change: an existing test will fail, and a human must consciously decide to update it. This is categorically different from "any code that touches exception handling."

- Test coverage status is the most reliable predictor of whether a regression will be caught automatically. A High-risk fix with full test coverage will surface failures in CI; the same fix with no tests will not. The original guideline ignores this distinction entirely.

- The OR-based original criterion inflated false-positive rates in practice. When the `HUMAN REVIEW REQUIRED` flag fires on trivially safe guard clauses, reviewers learn to discount it — meaning the flag loses its value precisely when it matters most.

- Grounding each criterion in a concrete, answerable question (Is there a test? Does the signature change? Is this a known vulnerability class?) gives the model a deterministic path to the right flag, rather than relying on surface pattern matching.

**Good Example: Regression-Aware Review Prompt (Updated)**

```
Review all files in the problem_code/ directory.
For every fix you suggest, explicitly state:
 - Regression risk: Low | Medium | High
 - Are there existing tests that cover the affected code path? (cite the test name)
 - Does this fix change the public API contract — specifically the documented exception type
   on an already-tested path, the return type/shape, or any parameter callers depend on?
 - Is this fix security-critical (SQL injection, auth bypass, credentials, input sanitization)?
Flag a fix as HUMAN REVIEW REQUIRED only if:
(a) Regression risk is High AND no existing test covers the affected behavior, OR
(b) The fix changes the public API contract as defined above, OR
(c) The fix addresses a security-critical vulnerability.
Do NOT flag a fix solely because it adds or modifies exception handling.
A guard clause that applies to an already-tested code path and does not change behavior
for valid inputs is Low risk and does not require human review.
```

**Bad Example: OR-Based Criterion (the original prompt)**

```
Review all files in the problem_code/ directory.
For every fix you suggest, explicitly state:
 - Regression risk: Low | Medium | High
 - Which currently-passing tests could break if this fix is applied?
 - Does this fix affect exception handling, shared state, or boundary conditions?
Flag any fix as HUMAN REVIEW REQUIRED if the regression risk is High
or if the fix affects shared state or exception handling.
```

-------------------------------------------------

### Updated Guideline: [State the full behavior contract before judging regression risk.] (group 2)

**Prompt and Context:**

Review the full module in load_user_settings.py, focusing on load_user_settings(...) and every helper function it depends on.

Before suggesting fixes, first state the intended behavioral contract of the module, including:

- cache behavior
- exception behavior
- normalization rules
- whether defaults, audit templates, settings_db entries, and cached values may be mutated
- whether each call should produce independent audit log entries and independent returned settings objects

Then review the code and suggest fixes only if they preserve that contract.

For every fix you suggest, explicitly include:

- Issue
- Why it is a problem
- Regression risk: Low | Medium | High
- Which existing behaviors or tests could break
- Whether it changes exception handling
- Whether it changes shared mutable state
- Whether it could affect later calls through caching, defaults, nested objects, or audit logging
- Whether human review is required

Do not mark a fix as safe unless you explicitly checked for:

- shared mutable default aliasing
- nested object aliasing
- cache regressions across multiple calls
- reused audit-log objects
- silent behavior changes caused by fallback defaults or coercion

If a fix changes exception behavior, shared state, or cross-call behavior, mark it as not safe to apply automatically.

-----------------------------------------------------

### Updated Guideline: In Review, Distinguish Correctness Regressions from Intentional Contract Changes (group 4)

When you assess regression risk, separate _regressions of correct behavior_ from _intentional behavior changes to correct a wrong contract_.

If tests fail under a proposed fix, treat it as a question:

- “Did we break something correct?” vs
- “Did we stop doing something incorrect that tests accidentally enshrined?”

---

**Copilot Conversation (Prompts and Outputs)**

##### User Prompt # 1

```
Review the files in the old and new directory under week10-counter.
old has the original files and new has the updated files with some fixes. These correspond to the new PR I created. I want you to review the PR (that is, review the fixes made in the new directory)

For every change you suggest, explicitly state:

- Behavior change: None | Bug-fix (contract preserved) | Contract change (intentional)
- Regression risk to _correct behavior_: Low | Medium | High
- If tests would break: are those tests validating correct behavior, or enshrining a bug/unsafe contract?
- Does this change affect exception handling, shared state, or boundary conditions? If yes, what failure modes could be masked or newly introduced?
- Mitigation: what targeted tests should be added/updated, and is a deprecation/versioning note needed?

Flag HUMAN REVIEW REQUIRED if:

- regression risk to correct behavior is High
```

-------------------------------------------------------

### Updated Guideline: Extract Behavioral Contract and Execution Paths Before Assigning Regression Risk (group 4)

Before labeling regression severity:

1. Extract the behavioral contract of the original implementation.
2. Enumerate main execution paths (valid, missing fields, invalid numeric, invalid email).
3. Compare behavior of each path before vs after.
4. Identify semantic contract drift prior to assigning risk.

This shifts from **issue-first risk labeling** to **contract-first semantic comparison**.

---

**Prompt and Context**

We reused the same repository and files.

The only change was modifying the instruction:

```
Treat `order_parser_before.py` as the original version and `order_parser_after.py` as the proposed PR change.

Review the proposed change as an experienced software engineer would in a pull request.

Before assigning regression risk, do this first:

1. Extract the behavioral contract of the original implementation.
2. Enumerate execution paths:
   - valid payload
   - missing required fields
   - invalid numeric fields
   - invalid email
3. Compare how each path behaves before vs after.
4. Explicitly identify semantic behavior changes.

Then provide review findings with:
- location
- what changed
- why it matters
- suggested fix
- regression risk

End with a merge decision.
```

-------------------------------------------------------

### Updated Guideline: Assess Individual AND Cross-Issue Regression Risk (group 6)

**Original Guideline 4:** Assess regression risk per issue (Low / Medium / High).

**Updated Guideline 4:** After assessing individual regression risks, add: *"Assess the combined regression risk assuming ALL changes in this PR ship together. What is the worst-case scenario if these changes interact in an unintended way?"*

**Prompt and Context:**
```
For each issue, assess individual regression risk (Low / Medium / High).

Then provide a Combined Regression Assessment:
Assume all changes in this PR ship together. What is the worst-case
scenario if these changes interact in an unintended way? What is the
combined regression risk?
```

----------------------------------------------------

### Updated guideline: Assess Regression Risk with Concrete Failure Paths and Preserved Behaviors (group 7)

**Guideline Definition**
When reviewing a proposed fix, require the LLM to do more than assign a risk label. It must identify the exact currently correct behaviors that must remain true after the fix, explain any new failure paths introduced by the change, and point to the specific code that creates the regression risk. If the fix changes exception handling, shared state, or boundary behavior, the model should explicitly state what can now fail silently and what tests should be added to catch that regression.

**Prompt and Context:**  
```
Review this fix for ProblemC.

Do not only say whether the fix works. Also check whether it introduces regression risk.

For your review, you must provide:

1. What original bug the fix solves.
2. What currently correct behaviors must still remain true after the fix.
3. Any new failure path introduced by the fix.
4. Whether exception handling, shared state, or boundary behavior changed.
5. At least one concrete test that would catch the regression if it exists.
6. Final verdict: APPROVE | REQUEST CHANGES | HUMAN REVIEW REQUIRED

Be specific. If you claim regression risk, explain the exact code path that creates it.
```











---
---
---










    
## Old Guideline 6: Explicitly State Assumptions and Non-Goals

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated Guideline: Explicitly State Assumptions, Non-Goals, and Review Boundaries (group 1)

**Reasoning:**
The updated guideline works better because it sets clear review boundaries while allowing the model to flag issues that directly result from the code in the PR. This keeps the review focused and ensures that real defects are not overlooked.

**Prompt and Context:**  
*Review this PR. 
@week10/src/problem_C/profile_service_before.py  is the codebase before PR.
@week10/src/problem_C/profile_service_after.py is the codebase after PR. 
Assume authentication, request validation, and database persistence layers work correctly and are out of scope. Do not suggest broader architectural redesigns or changes to unrelated modules. However, still flag any correctness, consistency, or maintainability issues that arise as a direct consequence of the logic in this code, including interactions visible in the shown functions.e and keep the review within PR boundaries.*










---
---
---










    
## Old Guideline 7: Understand the Intent Before You Review

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated Guideline: Treat Docstrings as Claims to Verify, Not as Ground Truth (group1)

**Description:**

The original guideline assumes the docstring is a reliable statement of intent. But docstrings can be aspirational, stale or just plain wrong — especially around security properties. When Copilot is told "here is what the code should do" and the description is incorrect, it validates against a false specification and approves code it should reject.

The fix is a small but important shift, as far as I think, instead of feeding the docstring to Copilot as ground truth, it is better to treat it as a list of claims that need to be checked against the actual implementation. For any security-relevant claim — constant-time comparison, parameterised queries, input sanitisation — explicitly tell Copilot to verify the claim rather than assume it.

**Prompt and Context:**  
```
Review the authenticate_user() function in auth.py.

The docstring makes these claims about the implementation:
  1. Passwords are stored as SHA-256 hashes
  2. Hash comparison is constant-time to prevent timing attacks
  3. Returns True on success, False otherwise

Do not take these claims at face value — verify each one against the actual code.

For claim 2: find the exact line where hashes are compared and check whether
it is actually constant-time in CPython. If not, explain how an attacker could
exploit this and suggest the correct fix.

Also check any database queries in the function — if user input is being
inserted directly into a query string, flag it as SQL injection even if the
docstring doesn't mention it.

If the code doesn't deliver on a security claim made in the docstring, treat
that as BUG FIX / P1. A false security claim in documentation is dangerous
on its own because it makes reviewers trust code they shouldn't.

Format each finding as: [Category | Priority] Location → What → Why → Fix
```

-------------------------------------------------------

### Updated guideline: Scrutinize claims and comments in pull requests (group 8)

**Description:**
Before merging code claims about the code should be confirmed and code itself scrutinized.

**Reasoning:**
A pull request claiming to solve an existing problem won't necessarily be the best or even an adequate solution. Code
quality must to be checked and validity of claims scrutinized. As was seen multiple times before, LLMs have a tendency
to take input as truth and conform response to it but it has to take an adversarial role and interrogate whether the
claims and code match, and whether the code should be merged or not.

**Prompt and Context:**

Context Given: B_1/diff.patch

> The calculate_grades.py file takes in a JSON containing grades and calculates final grades and statistics.
> Review the pull request with message "This PR fixes a divide by 0 bug in the code and implements the students sorting
> functionality while overall updating the code to improve development of future features. This commit passes all
> existing
> tests and does not break existing functionality." and difference in diff.patch.
> Scrutinize the pull request to confirm any claims are reflected in code, then analyze the code to ensure it is of good
> quality and should be merged.
> Provide a concrete verdict (Approve / Request Changes / Reject).

-------------------------------------------------------

### Updated guideline: (group 8)

To improve the review quality, the guidelines were refined in the following way:

- Guideline 1 should require that the reviewer explicitly understand and state the intended behavior of the code before
  evaluating correctness.
- Guideline 4 should require the reviewer to assess whether the proposed change introduces regression risk, especially
  in security-sensitive logic such as authentication or access control.

Providing this context helps the model analyze the code more accurately.

**Description**

The reviewer must understand the intended behavior of the function before evaluating whether the code is correct.
In addition, the reviewer must assess whether the proposed change introduces regression risk, particularly in
security-critical logic such as authentication or access control.

**Reasoning**

Providing the intent of the function helps the model understand how the system is expected to behave.
Requesting regression-risk analysis ensures that changes are evaluated not only for correctness but also for potential
side effects that could weaken security.

### Prompt and Context

**Improved Prompt:**
Review the pull request modifying is_token_valid() in download_access_pr.py.

Intent:
The function validates download tokens for access control.
If token validation fails or throws an exception, access must be denied.

For each finding provide:

Location -> What -> Why it matters -> Suggested fix

Also assess regression risk for the proposed change:
Low / Medium / High.

Focus especially on exception handling and whether the change
introduces a fail-open security behavior.

At the end provide a final verdict:
Approve / Request Changes / Reject.













---
---
---










## Old Guideline 9: Categorize Every Issue Before Suggesting a Fix

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated guideline: Categorize Issues AND Assess Compound Risk Across Changes (group 6)

**Original Guideline 3:** Categorize each issue individually by type and priority.

**Updated Guideline 3:** After categorizing each issue individually, add a **Compound Risk Assessment** step. Explicitly ask the LLM: *"Now consider all identified issues together. Are there any combinations of changes that, when taken together, create a higher-severity risk than any individual issue? Describe any vulnerability chains."*

**Prompt and Context:**
```
You are a senior code reviewer. Review the following PR diff for auth_middleware.py.

Step 1 — For each issue, categorize it:
- Type: Bug Fix | Enhancement | Documentation
- Priority: P1 (Critical) | P2 (Major) | P3 (Minor)

Step 2 — Compound Risk Assessment:
After listing individual issues, consider ALL changes together as a whole.
Are there any combinations of these changes that, when chained together,
create a security vulnerability or correctness problem that is MORE severe
than any single issue alone? Describe any vulnerability chains you identify
and assign a combined severity.

Here is the diff:
[full diff from BEFORE to AFTER pasted here]
```

-----------------------------------------------------

### Update guideline: Categorize Every Issue Before Suggesting a Fix (group 7)

**Guideline Definition**
Before suggesting a fix, first assign each review finding a priority and a type.
Priority says whether it blocks merge:
● P1 block merge
● P2 fix soon
● P3 nice to have
Type says what kind of issue it is:
● Bug Fix
● Requirement/Contract,
● Testing/Validation,
● Enhancement,
● Documentation
This keeps critical correctness, missing-spec, and missing-test issues from being buried under minor improvements.

**Prompt and Context:**

Context: (above)

Review the Python code and identify all issues.

For each finding, label it with:
- Priority: P1 (block merge), P2 (fix soon), or P3 (nice to have)
- Type: Bug Fix, Requirement/Contract, Testing/Validation, Enhancement, or Documentation

For each finding, use this format:
[Priority] [Type] - Finding
Why it matters: ...
Suggested action: ...

Focus especially on whether the expected behavior is clearly defined, whether the code can be verified as correct, and whether tests are missing for important edge cases.

------------------------------------------------------

### Updated guideline: Flag Design Decision Issues and Escalate (group 8)

**Description:**

When a finding genuinely spans more than one category (BUG FIX, ENHANCEMENT, DOCUMENTATION) — because the right fix
depends on which artefact (code or contract) is treated as the source of truth — do not force a single label. Instead
mark the issue as requiring a design decision.

**Reasoning:**

The single-label taxonomy is effective for genuinely independent findings (a standalone
off-by-one, a missing docstring on an unrelated function). It breaks down when the
category itself is the thing under debate, because premature labelling misdirects the fix
rather than clarifying it. Recognizing Design-Decision issues and surfacing the design
question first prevents the incomplete-fix failure mode described before.

**Prompt and Context:**

Context Given: `parse_date.py`

> Review `parse_date.py`, a small Python date-parsing utility that exposes a public API for
> parsing user-supplied date strings. The file contains two functions:

> - `parse_date(date_string, fmt)` — parses a string into a `datetime` object.
> - `days_until(date_string, fmt)` — calls `parse_date` and computes the delta to today.

> Perform a code review and suggest all improvements.

> For each finding:
> - If the finding reflects a mismatch between requirements, documentation, and code, mark it as a design decision and
    list the competing interpretations.
> - If the finding fits cleanly into exactly one category (Bug Fix / Enhancement / Documentation), label it with that
    category and a priority (P1 / P2 / P3), then suggest a fix.










---
---
---










    
## Old Guideline 11: Issues That Require Human Judgment

---
---

## IMPROVED GUIDELINES FOR THE ABOVE GUIDELINE

### Updated Guideline: [**Explicitly Check Hidden Dependencies in Cached Computations**] (group 2)

**Prompt and Context:**

Updat the guideline to explicitly require checking **hidden dependencies such as global variables or external configuration** when reviewing caching logic.

```jsx
Review the following Python code.

Focus specifically on hidden dependencies in cached computations.

When reviewing caching logic:
1. Identify all variables that influence the computation result.
2. Check whether the cache key includes all those variables.
3. If a computation depends on global state or configuration, determine whether the cache may become stale.
```