# Guideline 10: Assess Regression Risk as Part of Every Review Decision

**[Consolidated from Group 1, 2, 4, 6, and 7 feedback]**

---

## Description

When reviewing any proposed fix, assess whether the change could break existing correct behavior or introduce new risk. Regression risk assessment is not a binary judgment — it requires understanding the behavioral contract of the code, identifying which behaviors must be preserved, evaluating test coverage, and distinguishing between regressions of correct behavior and intentional fixes to wrong contracts. For every fix, systematically report:

1. **The behavioral contract** — what the code is supposed to do
2. **Regression risk** — Low | Medium | High (relative to correct behavior only)
3. **Test coverage** — which existing tests validate the affected code path
4. **API contract changes** — whether the fix changes the public API, documented exception types, or return shapes
5. **Security criticality** — whether the fix addresses a known vulnerability class
6. **Combined risk** — how this fix interacts with other changes in the PR

Flag a fix as `HUMAN REVIEW REQUIRED` if and only if **any** of the following are true:

1. Regression risk is `High` **AND** no existing test covers the affected behavior, **OR**
2. The fix changes the **public API contract** — it changes which exception type is raised on a documented, already-tested path; changes the return type or shape of a public function; or removes a parameter that callers may depend on, **OR**
3. The fix addresses a **security-critical vulnerability** (SQL injection, auth bypass, hardcoded credentials, unsafe deserialization), **OR**
4. The fix introduces shared mutable state regressions, nested object aliasing, or cache invalidation issues across multiple calls, **OR**
5. Combined regression risk of all changes together exceeds what individual changes suggest.

**Do NOT flag a fix as `HUMAN REVIEW REQUIRED` solely because it adds or modifies exception handling.** A guard clause (`if x <= 0: raise ValueError`) that applies to an already-tested code path and does not change the function's documented behavior for valid inputs is Low risk and does not require human review.

---

## Reasoning

- **Up to 24.8% of AI-suggested code improvements introduce regressions**, breaking previously correct behaviors [7].

- **Exception handling is the most common regression source**, but not all exception changes are equally risky. Adding a guard clause to an already-tested code path is fundamentally different from changing which exception type is raised on that path. The original guideline conflated them, leading to high false-positive rates and reviewer fatigue.

- **Test coverage status is the most reliable predictor** of whether a regression will be caught automatically. A High-risk fix with full test coverage will surface failures in CI; the same fix with no tests will not. The original criterion ignores this distinction entirely.

- **Security vulnerabilities are invisible to regression-only analysis** — they introduce new risk rather than breaking existing behavior. SQL injection, auth bypass, and credential exposure are the highest-impact class of fix and must be flagged separately from behavioral regressions.

- **Shared state and caching bugs require cross-call analysis**, not local code inspection. A fix that mutates a default parameter, aliases a nested object, or invalidates a cache may affect multiple code paths and callers simultaneously. Single-function reviews miss these patterns.

- **Distinguishing correctness regressions from intentional contract fixes** is essential. If tests fail under a proposed fix, the question is: "Did we break something correct?" vs. "Did we stop doing something incorrect that tests accidentally enshrined?" These require different mitigation strategies.

- **Grounding each criterion in a concrete, answerable question** (Is there a test? Does the signature change? Is this a known vulnerability class?) gives the model a deterministic path to the right flag, rather than relying on surface pattern matching that leads to inconsistent decisions.

- **When multiple changes ship together, they can interact in unexpected ways.** Two Medium-risk fixes that are safe individually may combine to create a High-risk scenario. This compound risk must be assessed explicitly.

---

## Good Example: Comprehensive Regression-Aware Review Prompt

```markdown
Review all files in the problem_A/ directory.

**Step 1: State the behavioral contract**
Before suggesting fixes, state the intended contract of each affected function, including:
- Cache behavior (if any)
- Exception behavior and documented exception types
- Normalization rules and defaults
- Whether mutable state or shared references exist
- Whether repeated calls should produce independent results

**Step 2: For every fix you suggest, explicitly state:**

- **Issue & why it matters**: the specific bug or problem
- **Behavioral contract**: does this preserve the documented contract?
- **Regression risk to correct behavior**: Low | Medium | High
- **Test coverage**: which existing tests cover the affected code path? (cite the test name)
- **API contract change**: does this fix change the documented exception type, return type/shape, or parameter semantics on an already-tested path?
- **Security criticality**: is this fix addressing SQL injection, auth bypass, credentials, or input sanitization?
- **Shared state impact**: does this fix mutate defaults, create nested object aliases, or affect cross-call behavior?
- **Concrete failure path**: if regression risk is Medium or High, describe the specific code path and scenario that creates it
- **Test to catch regression**: provide one concrete test that would fail if the regression occurs

**Step 3: Flag a fix as HUMAN REVIEW REQUIRED if and only if:**

(a) Regression risk is High AND no existing test covers the affected behavior, **OR**
(b) The fix changes the public API contract as defined above, **OR**
(c) The fix addresses a security-critical vulnerability, **OR**
(d) The fix introduces shared mutable state or caching regressions, **OR**
(e) Combined with other changes in this PR, the risk profile changes.

**Do NOT flag a fix solely because it adds or modifies exception handling.** A guard clause that applies to an already-tested code path and does not change behavior for valid inputs is Low risk and does not require human review.

**Step 4: Assess combined regression risk**
After evaluating individual fixes, assume ALL changes in this PR ship together.
What is the worst-case scenario if these changes interact in an unintended way?
What is the combined regression risk?

**Step 5: End with a merge decision**
- Approve
- Request Changes
- Reject
- Human Review Required (with specific reasoning)
```

---

## Bad Example 1: OR-Based Criterion (inflates false positives)

```markdown
Review all files in the problem_A/ directory.

For every fix you suggest, explicitly state:
 - Regression risk: Low | Medium | High
 - Which currently-passing tests could break if this fix is applied?
 - Does this fix affect exception handling, shared state, or boundary conditions?

Flag any fix as HUMAN REVIEW REQUIRED if the regression risk is High
or if the fix affects shared state or exception handling.
```

**Why this is ineffective:**
- Any fix that touches exception handling triggers the flag, even trivially safe guard clauses
- No distinction between breaking correct behavior and fixing a wrong contract
- Ignores test coverage entirely — High-risk fixes with full CI coverage are treated the same as High-risk fixes with no tests
- Leads to reviewer fatigue and loss of signal when flags are ignored on safe changes

---

## Bad Example 2: No Regression Analysis at All

```markdown
Fix all the bugs you found in problem_a/ directory.
```

**Why this is dangerous:**
- Up to 24.8% of suggested fixes introduce regressions
- Without explicit regression analysis, AI systems reliably break previously correct behavior
- Silent failures in edge cases, exception paths, and shared state are never surfaced
- Tests may pass locally but fail in production under unanticipated conditions

---


