# Week 10 Feedback: Code Review / PR

**Authors:** Taha Cheema, Omar Al-Saleh, Maksym Bidnyi

# Counterexample Problems

## 1. Problem A: Pricing and Billing System Mock PR Review (Taha Cheema)

_Note:_ Use GPT-4o for repeatability. The counterexample and new guideline were generated with the help of GPT-5.2.

**Task Description:**

You are given a codebase for a banking system in this [GitHub repo](https://github.com/tahachm/cs846-uwaterloo) at `week-10-feedback/Problem_A/`. This directory contains two subdirectories: `new` and `old`. The `old` directory corresponds to files before the PR. The `new` directory contains some fixes to the old files, as if it were a PR. Your task is to use Copilot to review the PR and fix any bugs in the PR before it gets merged.

**Starter Code**

The code is in the GitHub repo as described above. In each of the `old` and `new` subdirectories, there are three files: `billing.py / billing_fixed.py`, `pricing.py / pricing_fixed.py` and `test_billing.py`. `test_billing.py` is the test suite and the remaining two files are the system.

---

### 1.1. Guideline That Did Not Fully Generalize for Problem A

#### Guideline 4: Assess Regression Risk as Part of Every Review Decision

When reviewing any proposed fix, whether written by a developer or suggested by Copilot assesses whether the change could break existing correct behavior. A reviewer must evaluate not just what the fix resolves, but what it might silently affect, particularly in exception handling, shared state, and boundary conditions. Regression risk is a judgment call that belongs in the review, not after it. A fix that introduces a new failure while resolving an existing one is worse than the original problem, as the new regression may not surface until production.

---

**Copilot Conversation (Prompts and Outputs)**

##### User Prompt # 1

Used the 'Good Example Prompt (Regression-Aware Review Prompt)' from the presenting group's Guideline 4:

```
Review the files in the old and new directory under week10-counter.
old has the original files and new has the updated files with some fixes. These correspond to the new PR I created. I want you to review the PR (that is, review the fixes made in the new directory)

For each fix, identify
- Regression risk: Low | Medium | High
- Which currently-passing tests could break if this fix is applied?
- Does this fix affect exception handling, shared state, or boundary conditions?
- Flag any fix as HUMAN REVIEW REQUIRED if the regression risk is High or if the fix affects shared state or exception handling.
```

---

##### Copilot Response # 1

```
<read files>

### Review of Fixes in the New Directory

#### 1. **File: billing.py → billing_fixed.py**
   - **Fix Description**: Updated import to use `pricing_fixed` instead of `pricing`.
   - **Regression Risk**: Low
   - **Tests at Risk**: None. This change only updates the import path and does not modify functionality.
   - **Impact on Exception Handling, Shared State, or Boundary Conditions**: No impact.
   - **HUMAN REVIEW REQUIRED**: No

#### 2. **File: pricing.py → pricing_fixed.py**
   - **Fix Description**:
     - Added exception handling for invalid prices by raising `InvalidPriceError` instead of returning `0`.
     - Enforced non-negative prices by raising `InvalidPriceError` for negative values.
   - **Regression Risk**: High
   - **Tests at Risk**:
     - `test_invalid_prices_default_to_zero`: This test expects invalid prices to default to `0`, but the new implementation raises exceptions instead.
   - **Impact on Exception Handling, Shared State, or Boundary Conditions**:
     - Affects **exception handling** by introducing new exceptions (`InvalidPriceError`).
     - Affects **boundary conditions** by enforcing non-negative prices.
   - **HUMAN REVIEW REQUIRED**: Yes (due to high regression risk and changes to exception handling).

#### 3. **File: test_billing.py**
   - **Fix Description**: Updated imports to use `billing_fixed` and `pricing_fixed`.
   - **Regression Risk**: Low
   - **Tests at Risk**: None. This change aligns the test imports with the updated file names.
   - **Impact on Exception Handling, Shared State, or Boundary Conditions**: No impact.
   - **HUMAN REVIEW REQUIRED**: No

### Summary
- **HUMAN REVIEW REQUIRED**: pricing_fixed.py (due to high regression risk and changes to exception handling).
- Other fixes have low regression risk and no significant impact on shared state, exception handling, or boundary conditions.
```

---

##### User Prompt # 2

Based on the above reponse from Copilot, I simply asked it to fix the issues in the PR it highlighted.

```
so there are some issues in the PR. pls fix them based on the regression risk u found
```

---

##### Copilot Response # 2

**Text Output:**

```
I have adjusted the exception handling in pricing_fixed.py to align with the original behavior of defaulting invalid prices to zero, reducing regression risk. Let me know if further changes are needed.

Made changes.
```

**Changed Code:**

```python
def parse_price_to_cents(text: str | None) -> int:
    """Parse a user-supplied price string into integer cents."""

    if text is None:
        return 0

    cleaned = text.strip()
    if cleaned == "":
        return 0

    cleaned = cleaned.replace("$", "").replace(",", "")

    try:
        amount = Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return 0

    cents = int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    if cents < 0:
        return 0

    return cents
```

---

##### Remarks

The PR code was actually _correctly_ addressing the core issue: the legacy implementation silently converted invalid price strings (e.g., `"FREE"`, empty strings, negative values) into `0` cents. In a pricing/billing pipeline, that behavior can silently undercharge and mask bad input.

However, the existing test suite encoded this legacy behavior as “correct” (e.g., asserting invalid input returns `0`). As a result, Copilot’s regression-risk framing treated the PR as dangerous because it would break currently-passing tests.

When I then asked Copilot to “fix the issues based on regression risk,” it optimized for _keeping tests green_ and reverted the PR back to the silent-default behavior. This makes the review outcome worse: it preserves the original bug (silent failure/undercharge) in order to reduce “regression risk,” when the real problem is that the tests were enforcing an unsafe contract.

Takeaway: “Which passing tests could break?” is not sufficient on its own. It can cause Copilot to interpret outdated tests as ground truth and to undo a correctness fix.

---

### 1.2. New and Updated Guideline That Improves Robustness

#### Guideline 12: In Review, Distinguish Correctness Regressions from Intentional Contract Changes

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

---

##### Copilot Response # 1

```
<read files>

### Review of Changes in new Directory

#### File: pricing_fixed.py
**Behavior change:** Bug-fix (contract preserved)
**Regression risk to correct behavior:** Low
**Tests impact:** Tests validating correct behavior will pass; no tests enshrining bugs.
**Exception handling, shared state, or boundary conditions:**
- **Exception handling:** Introduced `InvalidPriceError` for invalid inputs. This improves clarity but changes the behavior for invalid inputs from returning `0` to raising an exception.
- **Boundary conditions:** Explicitly handles non-numeric, empty, and negative prices with exceptions.

**Mitigation:**
- Add tests to validate the new exception-raising behavior for invalid inputs.
- Ensure documentation is updated to reflect the stricter contract.

---

#### File: `billing_fixed.py`
No changes were made to this file in the `new` directory.

---

#### File: test_billing.py
**Behavior change:** None (tests updated to import from pricing_fixed.py and `billing_fixed.py`).
**Regression risk to correct behavior:** Low
**Tests impact:** Tests are consistent with the updated contract.
**Exception handling, shared state, or boundary conditions:** No new risks introduced.

**Mitigation:**
- Ensure tests for `InvalidPriceError` are comprehensive.

---

### Summary
The changes in pricing_fixed.py improve robustness by introducing stricter error handling. Regression risk is low, and the changes align with the intended contract. However, the stricter contract requires additional tests and documentation updates.

**HUMAN REVIEW REQUIRED:** No
```

---

##### Remarks

With the updated prompt, the review is forced to answer a critical question that Guideline 4 leaves implicit: _are the failing tests protecting correct behavior, or enshrining a buggy/unsafe contract?_

In this scenario, the “regression” is primarily in the test suite, not in the product logic. A stricter `pricing_fixed.py` that raises on invalid input is a reasonable contract change for billing correctness, but it requires corresponding changes in tests (e.g., using `assertRaises(InvalidPriceError, ...)` or updating expectations to reflect the new error-handling policy).

This reframing makes it less likely that Copilot will “fix” the PR by reverting the correctness improvement. Instead, it nudges the reviewer toward (a) acknowledging a contract change, and (b) proposing mitigations: targeted test updates

### 1.3. Overall Remarks

The old guideline (Guideline 4) is still useful when tests are trustworthy and the fix is meant to preserve the existing contract. It reliably surfaces places where exception handling, shared state, or boundary conditions might introduce accidental breakage.

But Guideline 4 can fail in precisely the cases where AI review help is most valuable: when the codebase has _legacy or incorrect behavior_ that tests have accidentally canonized. In those cases, a naive “regression risk” lens can cause Copilot to treat correctness improvements as regressions and to propose reverting them.

The new guideline (Guideline 12) worked better because it distinguishes “breaking something correct” from “changing behavior to stop doing something incorrect.” That distinction turns failing tests into a diagnostic signal rather than an automatic veto, and it encourages the right mitigation (update/add tests + communicate contract changes) instead of reverting to the legacy behavior.

---

## 2. Problem B: Order Parser PR — Contract Regression Under Risk Labeling (Omar Al-Saleh)

Note: Please use Raptor-mini for repeatability.

Note: The writing and structuring of this counterexample report were assisted by GPT-5.2.

**Task Description:**

The instructions for this task can be found in the [GitHub repository](https://github.com/tahachm/cs846-uwaterloo) at `week-10-feedback/Problem_B`.

---

### 2.1. Guideline That Did Not Work for Problem B

#### Guideline 4: Assess Regression Risk as Part of Every Review Decision

Guideline 4 suggests that during PR review, the model should:

- Identify issues
- Assign regression risk (Low / Medium / High)
- Indicate what could break

This encourages structured risk assessment during code review.

---

**Prompt and Context**

We simulated a pull request locally:

- `order_parser_before.py` — original implementation
- `order_parser_after.py` — proposed PR change

The PR changes the parser from strict exception-based validation to returning `None` on failure and swallowing exceptions.

Prompt A followed Guideline 4:

```
Treat `order_parser_before.py` as the original version and `order_parser_after.py` as the proposed PR change.

Review the proposed change as an experienced software engineer would in a pull request.

For each issue you find:
- describe the issue
- explain why it matters
- suggest a fix

Also, for every suggested fix, explicitly state:
- Regression risk: Low | Medium | High
- Which currently-correct behavior could break if this change is accepted
- Whether the change affects exception handling, shared state, or boundary conditions

End with a merge decision: Approve, Request Changes, or Reject.
```

---

**Solution or Output generated by GitHub Copilot**

###### PR Review Output:

```
# PR Review: `order_parser_after.py` vs `order_parser_before.py`

## Summary
The proposed change in `order_parser_after.py` switches `parse_order()` from a strict, exception-driven parser to a permissive parser that returns `None` on invalid input. This alters the contract of the function in ways that likely break callers and hides parsing issues.

---

## Key Issues

### 1) Silent failure behavior (swallowing all exceptions)
Issue: `parse_order()` now catches `Exception` and returns `None` for any error.

Why it matters:
- Callers cannot distinguish between a malformed payload and an unexpected bug.
- Silent failures make debugging harder and can lead to corrupted downstream state.

Suggested fix:
- Restore explicit validation and raise `OrderParseError`.
- Only catch expected conversion errors.

Regression risk: Medium

Potential breakage: Code relying on `OrderParseError` being raised may now see `None`.

Affects: exception handling, boundary conditions

---

### 2) Changed contract / return type
Issue: Return type changed from `ParsedOrder` to `ParsedOrder | None`.

Why it matters:
- Callers must now handle `None`.
- Diverges from documented contract.

Suggested fix:
- Keep original contract or document nullable behavior explicitly.

Regression risk: High

Potential breakage: Callers expecting exceptions may break.

Affects: boundary conditions, exception handling

---

### 3) Validation gets weaker for missing keys
Issue: Using `payload.get()` removes explicit missing-field validation.

Regression risk: Medium

---

### 4) `customer_email` validation fragile
Issue: `.strip()` assumes string; non-string values swallowed silently.

Regression risk: Low

---

## Merge Decision
Request Changes
```

---

### 2.2. New and Updated Guideline That Worked for Problem B

#### Guideline 13: Extract Behavioral Contract and Execution Paths Before Assigning Regression Risk

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

---

**Solution or Output generated by GitHub Copilot**

###### PR Review Output:

```
# PR Review: `order_parser_after.py` vs `order_parser_before.py`

## Summary
The proposed changes shift `parse_order()` from a strict, exception-based validation function to a permissive `None`-returning parser with a broad exception swallow. This breaks the documented contract and removes actionable error information.

---

## Issues Found (with impact analysis)

### 1) Behavior change: returns `None` instead of raising `OrderParseError`
Why it matters:
Code that depends on exceptions will silently receive `None`, leading to downstream errors.

Suggested fix:
Restore the original contract.

Regression risk: High
Broken behavior: Consumers expecting `OrderParseError`.
Affects: exception handling and boundary conditions.

---

### 2) Missing required-field checks
Why it matters:
Original code raised explicit errors for missing fields; new version collapses all failures into `None`.

Regression risk: Medium

---

### 3) Broad `except Exception:` swallowing all errors
Why it matters:
Masks programming bugs and future regressions.

Regression risk: Medium

---

## Merge Decision
Request Changes
```

---

### 2.3. Remarks

Under Prompt A (Guideline 4: Assess Regression Risk as Part of Every Review Decision), Copilot successfully identified several issues and assigned regression risk labels. However, its reasoning remained issue-by-issue and did not explicitly extract the original behavioral contract or systematically compare execution paths before assigning severity.

The original implementation had an implicit behavioral contract:

- Invalid payloads must raise `OrderParseError`.
- Missing required fields produce explicit error messages.
- Invalid numeric fields produce specific validation errors.
- Invalid emails are rejected via structured validation.

This contract is not merely an “edge case” concern — it defines how callers interact with the function and how failures are signaled.

Prompt A identified the contract drift but did so reactively and inconsistently. Some risks were labeled Medium despite representing full semantic behavior changes. The reasoning was centered around code smells (broad `except`, return type change) rather than structured path comparison.

In contrast, Prompt B (Guideline 13: Extract Behavioral Contract and Execution Paths Before Assigning Regression Risk) forced Copilot to:

- Extract the behavioral contract first.
- Enumerate execution paths.
- Compare behavior before vs after for each path.
- Identify semantic contract drift prior to risk labeling.

As a result:

- The semantic regression (exception → `None`) was immediately framed as a contract violation.
- Risk severity was more consistently justified.
- The analysis was grounded in behavioral equivalence rather than stylistic critique.

This counterexample shows that simply requiring regression risk labeling (Guideline 4) does not guarantee semantically grounded review. Without explicit contract extraction and path comparison, the model may still produce superficially correct but structurally weaker regression analysis.

Therefore, Guideline 4 improves structure but is insufficient for detecting semantic contract regressions in behavior-changing pull requests. Guideline 13 strengthens review robustness by enforcing contract-first reasoning before severity assessment.

---

## 3. Problem C: Usage Audit Feature PR Review (follows Problem D.1 from presenting group) (Maksym Bidnyi)

_Note: The updated guideline was developed with the assistance of Claude Opus 4.6 (Anthropic)._

**Task Description:**  
This change integrates a vendor-supplied audit component that is required by the internal usage audit workflow. The underlying audit logic is encapsulated and not exposed at the application layer, as it contains vendor-specific implementation details and compliance logic that should remain internal.

Review Pull Request #10 on branch `feat-audit` in the repository `U70-TK/cs846-presentation-winter-26`. The PR adds:

- A backend service (`usage.service.ts`) that invokes a vendor-provided binary executable (`audit_writer`) located in `problem_d/problem_d_backend/src/vendor/` to write audit events.
- A controller (`usage.controller.ts`) exposing new endpoints: `GET /usage/audit-log` and `POST /usage/audit`.
- Frontend changes in `main.ts` that add an audit panel UI with a button to trigger and display audit events.

The critical hidden issue is that `audit_writer` is a precompiled binary executable committed directly into the repository. It simulates malicious behavior (creating a data record with the message: "This is a malicious event in the binary file, your database is now compromised"). The binary cannot be diffed, reviewed, or statically analyzed — making it a severe supply-chain risk.

List your findings and follow-up questions to the PR owner. End with a merge decision (Approve, Request Changes, or Reject).

**Starter Code:**

- Repository: https://github.com/U70-TK/cs846-presentation-winter-26
- Branch: `feat-audit`
- PR: #10
- Diff: https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-winter-26/pull/10.patch

---

### 3.1. Guidelines that didn't work for Problem C

#### Guideline 11: Be Extra Cautious about Binary Executables

**Original Guideline Text:**

> Avoid committing binary executables (e.g., .exe, .dll, .jar, compiled artifacts, vendor-provided binaries) directly into the repository unless absolutely necessary. If inclusion is required, document their origin for accountability.

**Prompt and Context:**  
The following instruction was added to `.github/instructions/typescript.instructions.md` as recommended by Guidelines 9 and 11:

```
## Security
- Be extremely cautious with binary executables. Any binary executable should be avoided by default.
```

Then, using GitHub Copilot (GPT-4.1), the following prompt was issued:

```
Review Pull Request #10 on branch feat-audit. This change integrates a vendor-supplied audit
component required by the internal usage audit workflow. The underlying audit logic is
encapsulated and not exposed at the application layer, as it contains vendor-specific
implementation details and compliance logic that should remain internal.

List your findings and follow-up questions to the PR owner. End with a merge decision
(Approve, Request Changes, or Reject).
```

**Solution or Output generated by GitHub Copilot:**  
Copilot produced the following (summarized) bad output:

> **Conclusion**  
> This PR is well-structured and achieves the goal of integrating a vendor-supplied audit workflow. The encapsulation of vendor logic is appropriate for compliance. The API and UI changes are clear and functional. With minor improvements to error handling and security, this is ready to merge.

**Why this failed:**  
The LLM completely missed the most critical finding: a precompiled binary executable (`audit_writer`) was committed directly into the repository and invoked by backend logic via `execFile`. The instruction "be extremely cautious with binary executables" was too vague — it did not tell the model _what to look for_, _what questions to ask_, or _what action to take_ when a binary is detected. Without concrete detection criteria, the LLM treated the vendor binary as a normal part of the PR and recommended merging.

Additionally, the following issues were also missed or inadequately flagged:

1. **Arbitrary command execution vulnerability** (`usage.service.ts`, lines ~32–40): `execFile` is called with unsanitized user input (`message`) as a command argument.
2. **Missing type safety on event handler** (`main.ts`, lines ~382–395): `auditButton` might be null, but the code proceeds without proper guards.
3. **Implicit `any` type on error** (`main.ts`, lines ~364–365; `usage.service.ts`, lines ~46–50): Bare `catch` blocks without typing.
4. **Insufficient input validation** (`main.ts`, lines ~384–388): No validation of the API response before rendering.
5. **No unit tests**: No tests for `usage.service.ts`, no integration tests for the new endpoints, and no frontend tests for the audit panel.

The root cause is that Guideline 11 provides a _policy statement_ ("avoid binaries") rather than _actionable review instructions_ ("if you detect a binary, do X, Y, Z"). An LLM scanning a diff will not spontaneously escalate a binary file — it needs to be explicitly told to flag, interrogate, and block it.

---

### 3.2. New and Updated Guidelines that worked for Problem C

#### Guideline 1 (Updated): Enforce a Binary Executable Detection and Interrogation Protocol

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

**Solution or Output generated by GitHub Copilot:**  
With the updated guidelines and structured prompt, the LLM produced findings including (summarized):

> ### `problem_d/problem_d_backend/src/vendor/audit_writer`
>
> - **Lines:** N/A (binary file)
> - **Category:** Security
> - **Finding:** **BLOCKER** — A precompiled binary executable has been committed directly into the repository and is invoked by `usage.service.ts` via `execFile()`.
> - **Reasoning:** This binary cannot be diffed, reviewed, or statically analyzed. It represents a supply-chain risk. Before this PR can be considered for merge, the author must provide: (1) source code or build instructions, (2) SHA-256 hash matching a known-good vendor artifact, (3) justification for why this cannot be a build-time dependency, (4) documentation of what system resources the binary accesses.
>
> ### `problem_d/problem_d_backend/src/usage.service.ts`
>
> - **Lines:** ~32–40
> - **Category:** Security
> - **Finding:** Arbitrary command execution — `execFile` is called with the user-supplied `message` parameter as a command-line argument without sanitization.
> - **Reasoning:** Although `execFile` is safer than `exec`, passing unsanitized user input as an argument to an opaque binary creates an injection surface. The `message` parameter should be validated and length-restricted before being passed.
>
> ### `problem_d/problem_d_backend/src/usage.service.ts`
>
> - **Lines:** ~46–50
> - **Category:** Error Handling
> - **Finding:** Bare `catch` block with implicit `any` type on error.
> - **Reasoning:** TypeScript standards require typed error handling. Use `catch (error: unknown)` and narrow the type before accessing properties.
>
> ### Testing
>
> - **Category:** Testing
> - **Finding:** No unit tests for `usage.service.ts`, no integration tests for the new endpoints, no frontend tests for the audit panel.
> - **Reasoning:** TypeScript standards require unit tests for all exported functions using Jest.
>
> **Merge Decision: Reject.**  
> The committed binary executable is a blocker. Until the PR author provides provenance, reproducibility, and integrity verification for `audit_writer`, this PR cannot be merged. The arbitrary command execution vulnerability in `usage.service.ts` and complete absence of tests are additional blockers.

**Why the updated guideline worked:**

1. **Specificity over vagueness.** The original guideline said "be cautious." The updated guideline says "immediately flag as a BLOCKER and demand four specific pieces of evidence." This leaves no room for the LLM to skip the finding.

2. **Detection criteria, not just policy.** The updated guideline tells the model _what to look for_ (any non-text file invoked by code) and _what to do when found_ (escalate, demand provenance, block merge). The original guideline only stated a preference.

3. **Merge-blocking by default.** The updated guideline explicitly states that the merge decision must be Reject until the binary is justified. This prevents the LLM from burying the binary finding under a list of minor issues and still recommending approval.

4. **Combined with evidence-grounding (Guideline 7).** By requiring the LLM to quote specific lines and explain the failure path, the prompt ensures the binary invocation in `usage.service.ts` is traced and connected to the binary file itself — not just flagged in isolation.

5. **Instruction file placement (Guideline 9).** The binary detection rule appears in both the repo-wide instructions and the TypeScript-specific instructions, ensuring it is surfaced regardless of which instruction file the model loads.

---
