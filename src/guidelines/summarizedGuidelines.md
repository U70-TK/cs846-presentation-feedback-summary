# Week 10 Summarized Guidelines: CodeReview / PR

**Authors:** [Neel Sanjaybhai Faganiya, Ibrahim Mohammed Sayem, Felix Wang]

**Readings Assigned:**  
- Accountability in Code Review: The Role of Intrinsic Drivers and the Impact of LLMs [1]
- Prompting and Fine-tuning Large Language Models for Automated Code Review Comment Generation [2]
- Rethinking Code Review Workflows with LLM Assistance: An Empirical Study [3]
- The Impact of Large Language Models (LLMs) on Code Review Process [4]
- LLMs as Code Review Agents: A Rapid Review [5]
- Evaluating Large Language Models for Code Review [6]
- Automated Code Review In Practice [7]
- GitHub blog: Code review in the age of AI [8] 
- Unlocking the full power of Copilot code review: Master your instructions files [9]
- Using GitHub Copilot code review [10]
- uReview: Scalable, Trustworthy GenAI for Code Review at Uber [11] 
- Detecting malicious pull requests at scale with LLMs [12]

> *Note: The following document contains the summarized guidelines for those guidelines where the class provided counterarguments, and the rest of the guidelines are put as they were during our presentation (Guidelines: 2, 6, 7, 10.1, 10.3)*

## Relevant Guidelines per Problem
| Question |          Guidelines               |
|----------|-----------------------------------|
| A.1 | random test |
| A.2 | 1, 2 |
| A.3 | 3, 4, 5 |
| B.1 | 6 |
| B.2 | 7 |
| B.3 | 8 |
| C.1 | 10.2 |
| C.2 | 10.2 |
| D.1 | 9, 10.2, 11 |
| D.2 | 9, 11 | 
| D.3 | 9, 10.1, 10.3 | 



## 1. Summarized guidelines (contains summarized counter as well as perfectly working guidelines)


> **Note:** Guidelines should be actionable, specific, and usable during real coding tasks.


### Guideline 1: Understand the Intent Before You Review [7] — Verify Claims Against Implementation

**Description**

Before judging any code, establish what it is supposed to do by reading the docstring, inline comments, function signature, and surrounding context. However, **do not treat these claims as ground truth**. Instead, verify each claim — especially security-related claims — against the actual implementation. If the intended behavior is unclear or if documentation contradicts the code, flag that mismatch as a finding. When using an LLM as part of your review, include both the claimed intent and explicit instructions to verify the claims rather than assume them. This approach ensures reviewers and models catch code that runs but either does the wrong thing or makes false security promises.

---

**Reasoning**

- **Docstrings can be aspirational, stale, or wrong**, especially around security properties. Simply accepting docstring claims as ground truth leads reviewers and LLMs to approve code that violates those claims.
- **Code correction ratio improves by up to 23 percentage points** when intent is included in the review prompt, but only if that intent is actively verified rather than passively accepted.
- **False security claims are dangerous**. If code claims to use constant-time comparison but doesn't, or claims to use parameterized queries but concatenates user input, that mismatch is a P1 bug regardless of whether the code "works."
- **GPT-4o assessed code correctness 68.5% of the time when given a problem description** [7], dropping significantly without it. However, if the problem description itself is incorrect, the model validates against the wrong spec and approves dangerous code.
- **Missing, misleading, or incorrect documentation directly reduces review accuracy** more than generic syntactic or stylistic issues, because it shapes what both human reviewers and LLM models consider "correct."
- **Claims without proof are placeholders for bugs**. A pull request message claiming "this PR fixes a divide-by-zero bug" doesn't mean it actually does. Reviewers must verify that the claimed fix is present in the code and that the fix is sound.

---

**Good Example: Intent Stated and Claims Verified**

```text
Review the authenticate_user() function in auth.py.

Stated Intent (from docstring and PR description):
 - Passwords are stored as SHA-256 hashes
 - Hash comparison is constant-time to prevent timing attacks
 - Returns True on success, False on invalid credentials
 - Validates tokens against a database

For each stated claim, verify it against the actual code:

Claim 1 (SHA-256 hashing):
  → Find the exact line where the hash is computed and verify the algorithm

Claim 2 (Constant-time comparison):
  → Find the exact line where stored and provided hashes are compared
  → Verify it uses a constant-time comparison function (e.g., hmac.compare_digest)
  → If it uses == or string comparison, explain how timing attacks could leak password info

Claim 3 (Exception behavior):
  → Does a missing user throw an exception or return False?
  → Does an invalid token throw an exception or return False?
  → If exceptions leak information about which check failed, flag it as a security issue

Claim 4 (Database queries):
  → Check all database queries; if user input is concatenated into query strings,
    flag as SQL injection even if the docstring doesn't mention it

Flag as HUMAN REVIEW REQUIRED if:
 - Any security claim (timing-resistant, parameterized queries, input sanitization) 
   is not actually implemented in the code
 - Code works but delivers a weaker security promise than documented

Format findings as: [Category | Priority] Location → Claim → Actual Behavior → Consequence → Fix

Provide final verdict: Approve | Request Changes | Reject
```

---

**Bad Example: Intent Accepted Without Verification**

```text
Review the authenticate_user() function in auth.py.

The docstring states that this function uses constant-time hash comparison
to prevent timing attacks. Check if the code is correct.
```

**Problem with this example:**
- Does not instruct the reviewer (or LLM) to verify the constant-time claim against the code
- Assumes the docstring is accurate and complete
- Will not catch code that claims to be secure but isn't
- May approve a simple string comparison (`if hash1 == hash2`) without flagging the timing attack vulnerability
- Does not require the reviewer to check for other unclaimed issues (e.g., SQL injection in the same function)

---

**Bad Example: Claims Accepted Without Scrutiny**

```text
Review the PR with this message: "This PR fixes a divide-by-zero bug and implements sorting."
The diff is in changes.patch. Let me know if it's safe to merge.
```

**Problem with this example:**
- Takes the PR message at face value without verifying the claim is true
- Does not require checking whether the divide-by-zero is actually fixed
- Does not require checking whether the "fix" introduces new bugs
- Does not ask the reviewer to verify that existing tests pass with the changes
- Does not require a concrete verdict; invites a summary rather than a judgment

---

### Guideline 2: Write Structured Review Comments [2]

**Description:**

Every issue you find should be reported in a consistent format that includes the location of the problem, its description, the reason it matters, and the steps to resolve it. A vague comment like this looks unsafe is not actionable. A reviewer reading your report, or a developer receiving your feedback, needs all four pieces to understand and act on the finding. Use this template for every finding:
[Location] → [What] → [Why_it_matters] → [Suggested_fix]

---

**Reasoning:**
 - Practitioners rate review comments on three dimensions: Relevance, Information completeness, and Explanation clarity [2].
 - Comments missing any one of these three dimensions are considered low quality by real developers.
 - Structured comments reduce back-and-forth between reviewer and author; the fix is self-contained.
 - When asking Copilot to review code, requesting this format in your prompt directly improves the quality of its output.

 *Example:*
storage.py: search_by_error_type(), line 79
→ SQL string interpolated with f-string
→ Attacker-controlled input reaches the database query unchanged (SQL Injection)
→ Replace with parameterized query: conn.execute("SELECT * FROM crashes WHERE error_type =?", (error_type,))


---

**Examples:**

**Good Example: Structured Review:**

```text
 - Ask Copilot to report every issue using a consistent format: location, what, why, and fix 
 - Specify the exact output format so every finding is self-contained and actionable 
 - Group findings under clear headings so critical issues are not buried alongside minor ones 
 - Ask for a severity (Critical / High / Medium / Low) label on each finding so issues can be triaged by importance 
 - Request a concrete verdict at the end to force an overall judgment on the code

```

**Bad Example: Not Strutured**

```text
Can you check the crash_dedup code and tell me if there are any problems?
```

---

### Guideline 3: Categorize Every Issue [4], Then Triage Interactions and Escalate Design Decisions

**Description:**

Before suggesting fixes, require the LLM to label every review finding with a Type and Priority so critical issues don’t get buried under minor improvements. Extend the taxonomy to cover common “review gaps” (requirements/contracts and testing/validation), add an explicit Design Decision label for ambiguous source-of-truth conflicts, and finish with a Compound Risk Assessment step that looks for issue combinations (or change interactions) that create higher-severity risks than any single finding.

- Types: Bug Fix | Requirement/Contract | Testing/Validation | Enhancement | Documentation | Design Decision
- Priorities: P1 (block merge) | P2 (fix soon) | P3 (nice-to-have)

**Reasoning:**

Unstructured reviews often conflate severity and urgency, causing real defects to be lost among stylistic notes. A type+priority taxonomy forces explicit triage and makes the review actionable.

The extended version improves the original by addressing common failure modes:

- Missing or unclear expected behavior is not just “documentation”—it’s a Requirement/Contract risk.
- Lack of tests for edge cases is often the main merge risk—so Testing/Validation deserves its own bucket.
- Some findings can’t be correctly fixed until the team decides whether code or contract/docs is the source of truth, labeling these as Design Decision prevents “confident but wrong” fixes.
- Individual issues may look minor alone but become serious when chained—Compound Risk Assessment catches vulnerability/correctness chains across changes.

**Examples:**

**Good Example:**

```
You are a senior code reviewer. Review this PR diff.

Step 1 — Scope:
Focus only on issues supported by the diff and the shown code. Prefer high-signal findings.

Step 2 — Categorize EACH finding before suggesting fixes:
For each finding, output exactly:
[Priority] [Type] - Finding
Why it matters: ...
Suggested action: ...

Priority:
- P1 (block merge) | P2 (fix soon) | P3 (nice-to-have)

Type:
- Bug Fix | Requirement/Contract | Testing/Validation | Enhancement | Documentation

Design-decision rule:
If the “right” fix depends on what the intended behavior is (e.g., mismatch between requirements/docs/tests vs code),
DO NOT force a single label. Use:
[P?] [Design Decision] - <issue>
Competing interpretations: (A) ... (B) ...
Decision needed: ...
Then suggest next steps (e.g., clarify contract, add tests) rather than a single definitive code change.

Step 3 — Compound Risk Assessment:
Now consider ALL findings and ALL changes together.
Do any combinations of changes/issues interact to create a higher-severity security or correctness risk than any single item alone?
Describe any vulnerability/correctness chains and assign a combined severity (P1/P2/P3).

Here is the diff:
[paste full diff BEFORE -> AFTER]
```

**Bad Example:**

```
Review this PR and suggest improvements.
```

---

### Guideline 4: Assess Regression Risk as Part of Every Review Decision [7]

**[Consolidated from Group 1, 2, 4, 6, and 7 feedback]**

---

**Description**

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

**Reasoning**

- **Up to 24.8% of AI-suggested code improvements introduce regressions**, breaking previously correct behaviors [7].

- **Exception handling is the most common regression source**, but not all exception changes are equally risky. Adding a guard clause to an already-tested code path is fundamentally different from changing which exception type is raised on that path. The original guideline conflated them, leading to high false-positive rates and reviewer fatigue.

- **Test coverage status is the most reliable predictor** of whether a regression will be caught automatically. A High-risk fix with full test coverage will surface failures in CI; the same fix with no tests will not. The original criterion ignores this distinction entirely.

- **Security vulnerabilities are invisible to regression-only analysis** — they introduce new risk rather than breaking existing behavior. SQL injection, auth bypass, and credential exposure are the highest-impact class of fix and must be flagged separately from behavioral regressions.

- **Shared state and caching bugs require cross-call analysis**, not local code inspection. A fix that mutates a default parameter, aliases a nested object, or invalidates a cache may affect multiple code paths and callers simultaneously. Single-function reviews miss these patterns.

- **Distinguishing correctness regressions from intentional contract fixes** is essential. If tests fail under a proposed fix, the question is: "Did we break something correct?" vs. "Did we stop doing something incorrect that tests accidentally enshrined?" These require different mitigation strategies.

- **Grounding each criterion in a concrete, answerable question** (Is there a test? Does the signature change? Is this a known vulnerability class?) gives the model a deterministic path to the right flag, rather than relying on surface pattern matching that leads to inconsistent decisions.

- **When multiple changes ship together, they can interact in unexpected ways.** Two Medium-risk fixes that are safe individually may combine to create a High-risk scenario. This compound risk must be assessed explicitly.

---

**Good Example: Comprehensive Regression-Aware Review Prompt**

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

**Bad Example 1: OR-Based Criterion (inflates false positives)**

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

**Bad Example 2: No Regression Analysis at All**

```markdown
Fix all the bugs you found in problem_a/ directory.
```

**Why this is dangerous:**
- Up to 24.8% of suggested fixes introduce regressions
- Without explicit regression analysis, AI systems reliably break previously correct behavior
- Silent failures in edge cases, exception paths, and shared state are never surfaced
- Tests may pass locally but fail in production under unanticipated conditions

---

### Guideline 5: Issues That Require Human Judgment — Mitigated by Explicit Dependency Verification [2][7][13][14]

**Description**

LLMs have well-documented limitations in code correctness assessment. Research shows LLMs fail to correctly assess code correctness in roughly 1 in 3 cases (Cihan et al. [7]), and achieve only 60-68% agreement with subject-matter experts on domain-specific tasks (Szymanski et al. [13]). Rather than treating all unmapped issues as inherently unmappable, this guideline identifies a concrete, highly-prevalent failure mode: **hidden dependencies in cached computations** — where LLMs systematically miss state variables, configuration parameters, or external factors that should influence cache keys but do not.

The updated approach shifts from a reactive stance (wait for the LLM to fail, then manually debug) to a proactive stance (explicitly train the LLM to surface and verify hidden dependencies before it signs off on caching logic).

---

**Reasoning**

1. **LLMs miss invisible dependencies:** Caching bugs arise when a computation depends on state (e.g., a global variable, configuration flag, or external service) that is never included in the cache key. LLMs often fail to trace these dependencies because they do not appear in the immediate function scope or call chain.

2. **Concrete, operationalizable criteria work better than generic guidelines:** Rather than saying "human judgment required," we provide a specific, checkable procedure for LLMs to follow when they encounter caching logic. This reduces false negatives.

3. **Staleness is often invisible in unit tests:** A cache that always returns stale data may never trigger a test failure if the test runs only once or if the external state is mocked. LLMs cannot infer staleness from code structure alone; they must be explicitly prompted to reason about it.

4. **Low cost, high confidence:** Asking the LLM to enumerate variables, cross-check the cache key, and justify staleness risk adds roughly 10% overhead to review time but catches a class of bugs that slip through otherwise.

---

**Good Example: Explicit Dependency Verification in Caching Review**

**Prompt:**

```
Review the following Python code for caching logic.

Focus specifically on hidden dependencies in cached computations.

For each caching operation:

1. Identify all variables that influence the computation result:
   - Local variables in the function
   - Function parameters
   - Class attributes and mutable fields
   - Global variables
   - Environment variables
   - External service state (database, file system, network)
   - Configuration files or singletons

2. State the current cache key and verify it includes all identified dependencies.

3. For each dependency NOT in the cache key, determine:
   - Is this a bug (cache may become stale)?
   - Is this intentional (e.g., we always want the cached value regardless of that state)?
   - If intentional, explicitly justify why staleness is acceptable.

4. If a computation depends on global state or configuration, determine whether the cache may 
   become stale and suggest how to invalidate it (TTL, event-driven, or explicit key inclusion).

Do not sign off on caching logic until you have answered all four checks.

---

Code to review:

[code snippet here]
```

**When applied to real code:**

```python
# Example: cache with hidden dependency

config = {"discount_rate": 0.1}

def calculate_price(item_id):
    # Hidden dependency: config["discount_rate"]
    item = db.get_item(item_id)
    price = item.base_price * (1 - config["discount_rate"])
    
    # Cache key does NOT include config
    cache[item_id] = price
    return price
```

**Good review output:**

```
Finding: Hidden dependency in cache key

Location: calculate_price() line 8

Identified dependencies:
1. item_id (parameter) — included in cache key ✓
2. db.get_item() result (external call) — NOT in cache key ✗
3. config["discount_rate"] (global state) — NOT in cache key ✗

Issue: If config["discount_rate"] changes, cached prices remain stale.

Examples of staleness:
- Admin updates discount_rate to 0.15; existing cached prices still reflect 0.1
- Item is updated in database; cached price may not reflect new base_price

Suggested fix:
- Include discount_rate in cache key: cache[(item_id, config["discount_rate"])] = price
- OR implement TTL-based invalidation (e.g., cache expires every 1 hour)
- OR invalidate cache when config changes (e.g., on_config_change.register(clear_cache))
- OR document that this cache intentionally ignores config changes and why that is safe

Regression risk: Medium — changing cache behavior could affect dependent services.
```

---

**Bad Example: Generic "Human Judgment Required" Flag Without Specificity**

**Prompt:**

```
Review this code and flag any issues that require human judgment.
```

**Output:**

```
Finding: Cache logic present
Regression risk: Medium
Note: This requires human judgment. LLMs have been shown to miss caching bugs.
Status: HUMAN REVIEW REQUIRED
```

**Why this is ineffective:**

1. **No actionable guidance:** The reviewer doesn't know what to look for. Are we worried about staleness? Correctness? Memory leaks?
2. **Unclear triage:** "Human judgment required" on every caching function creates alert fatigue. Reviewers learn to ignore the flag.
3. **No specificity:** The LLM didn't attempt to find the issue; it just punted to humans.
4. **Missed concrete checks:** We never asked the LLM to enumerate dependencies or verify cache keys. Even if an LLM cannot guarantee correctness, it can follow a procedure that surfaces concrete risks.

---

**Integration with Code Review Workflow**

**When to apply this guideline:**

- Any function that stores results in a cache (Redis, memcached, in-memory dict, class-level cache)
- Any decorator like `@lru_cache` or `@cache`
- Memoization patterns

**Checklist for reviewers:**

When an LLM flags caching logic:
1. ✓ Did it enumerate all variables that influence the result?
2. ✓ Did it check whether all those variables are in the cache key?
3. ✓ Did it identify potential staleness scenarios?
4. ✓ Did it justify why any missing dependencies are intentional and safe?

If any check is missing, ask the LLM to re-review with the explicit dependency procedure.

---

### Guideline 6: Use a Structured, Context-First Review Prompt [3][7]

**Description:**

When prompting an LLM for code review, first have it produce a structured summary of the pull request (intent, affected components, and high-risk areas). Then, give explicitly scoped review criteria (for example, correctness, security, and performance) as clear bullet-point instructions.

**Reasoning:**

Effective LLM-assisted code review requires context understanding before issue detection. Developers preferred AI-led summaries first to reduce cognitive load and improve contextual understanding before diving into findings [3]. Jumping straight to issue detection without grounding the model in the PR's intent produces unfocused, noisy feedback — which increases PR closure time and reduces reviewer trust over time [7]. Structuring the prompt itself with headings and bullet points further improves consistency and reduces ambiguity in LLM outputs.

Together, these findings converge on the same principle: the model needs to understand the change before it can review it well, and the prompt structure is what enforces that order.

**Examples:**

**Good Example:**

```
Ask the LLM to summarize the PR's intent first and identify high-risk areas, then instruct it to review only for a specific, named set of concerns.
```

**Bad Example:**

```
Review this pull request and suggest improvements.
```

----

### Guideline 7: Require Evidence-Grounded Justification Before Accepting LLM Claims [3]
**Description:**

When prompting an LLM to evaluate tests or validate a reviewer comment, explicitly instruct it to cite specific line numbers, function names, or test cases as evidence before reaching a conclusion. Do not accept a finding unless the model can point to the exact code that supports it.

**Reasoning:**

LLMs reviewing code tend to produce confident-sounding but loosely grounded outputs, asserting that a test is missing or a security risk exists without pointing to the specific code that demonstrates it. Empirical studies on code review workflows show that developers only act on and trust LLM feedback when it is tied to concrete code artifacts rather than general observations [3]. Practitioner guidance on writing effective LLM instructions similarly emphasizes requiring the model to cite locations as a key technique for improving precision and reducing hallucinated architectural criticism.

Requiring evidence-grounded justification addresses all of these failure modes in a single instruction: it forces the model to anchor every claim in the actual diff before surfacing it.

**Examples:**

**Good Example:**

```
For each finding, you must:
1. Quote the specific line(s) of code that support your claim.
2. Explain the failure path using only those lines.
3. If you cannot point to a specific line, do not include the finding.
```

**Bad Example:**

```
Review the tests and identify what's missing.
```

----

### Guideline 8: Explicitly State Assumptions, Non-Goals, and Review Boundaries

**Description:**

When prompting an LLM for code review, explicitly state (a) what assumptions it should make about surrounding systems, (b) what is out of scope (non-goals), and (c) what the review boundaries are. Crucially, add a boundary rule that still allows the model to flag issues that arise directly from the PR code (including interactions visible in the provided functions), so the review stays focused without missing real defects.

**Reasoning:**

Even with code context, LLMs often overreach by:

- Assuming missing system components or unknown requirements
- Critiquing hypothetical architectures and proposing redesigns
- Flagging issues that are handled elsewhere (auth/validation/persistence)
- Drifting into unrelated modules or “best practices” not relevant to the PR

By explicitly stating assumptions, non-goals, and boundaries, you:

- Prevent hallucinated architectural criticism and out-of-scope suggestions
- Keep feedback aligned with the actual change and the provided code
- Preserve signal by still catching correctness/consistency/maintainability problems that are caused by the PR logic (not by imaginary surrounding systems)
- Reduce noise while avoiding the “too strict” failure mode where important issues get ignored

**Examples:**

**Good Example:**

```
Review this PR.

Context:
- Here is the codebase before the PR.
- Here is the codebase after the PR.

Assumptions / out of scope:
- Assume authentication, request validation, and database persistence layers work correctly.
- Treat auth/validation/persistence implementation details as out of scope unless the PR code misuses them.

Review boundaries (non-goals):
- Do not suggest broader architectural redesigns.
- Do not propose changes to unrelated modules or systems not shown here.

What you MUST still flag:
- Any correctness, consistency, or maintainability issues that arise directly from the PR logic, including interactions visible within the shown functions and their call relationships.

Keep the review strictly within these boundaries.
```

**Bad Example:**

```
Review this PR and suggest improvements.
```

---

### Guideline 9: Create a structured instruction file [9].

**Description:**  

Add a Copilot Code Review instructions file that is concise, structured, and scoped to where it should apply:

* Use repo-wide `.github/copilot-instructions.md` for standards that apply everywhere.

* Use path-specific `.github/instructions/*.instructions.md` with applyTo frontmatter for language/module-specific rules. 

Your instruction file should be concise and structured, consider including sections like: "Naming Conventions", "Code Style", "Error Handling", "Testing", and "Example".

**Reasoning:**  
LLMs struggle with complex tasks that require extensive contextual or repository understanding [5], and due to the inherent undeterministic nature of LLMs, their outputs can drift in unexpected directions without clear constraints. Github Copilot recently added support for repo-wide and path-specific instructions [9] so that you can define a universal and customized guidelines for your Copilot agent to fit into your workflow. By providing structured headings and bullet points, it helps Copilot to access organized and focued instruction. However, long instruction files (over 1000 lines) should be avoided, as this leads to inconsistent behaviours and may cause "Lost in the middle" effect [16]. 

**Good Example:**  

```
---
applyTo: "**/*.ts"
---
# TypeScript Coding Standards
This file defines our TypeScript coding conventions for Copilot code review.

## Naming Conventions

- [Define your naming conventions here.]

## Code Style

- [Define your code style expectations here.]

## Error Handling

- [Define your error handling expectations here.]

## Testing

- [Define your testing expectations here. ]

## Example

```typescript
// Good
[One good example here]

// Bad
[One bad example here]
```

**Bad Example:**

```
Perform a Pull Request review.
```

---

### Guideline 10: Use Automated CI Gates [8]

#### Guideline 10.1: Static Analysis Tool together with LLM [11]

**Description:**

Integrate static analysis tools (e.g., linters, type checkers, security scanners) into your CI pipeline and configure them as mandatory checks before pull request merge. GitHub CI supports assorted static analysis tool integrations like CodeQL (primarily for security), Semgrep (pattern based bug finding with customized rules), and your ecosystem’s usual linters/type checkers (ESLint/tsc, pylint/mypy, etc.). Compare the output given by the Static Analysis Tool along with the output from the LLM and use the tool findings to ground, verify, or challenge the LLM’s review comments rather than treating the LLM as the sole reviewer.

**Reasoning:**

Unlike LLMs, most static analysis tools like Semgrep, CodeQL, etc. are deterministic and rule-based. They enforce predefined constraints across all changes, which can provide a consistent and systematic guarantee to your project. Depending on its proprietary, static analysis tools are generally capable of detecting: Syntax and type errors, Code style violations, Security vulnerabilities, Dead code or unreachable branches, and Complexity thresholds. However, this is not in conflict with LLM-assisted Code Review, as static analysis tools sometimes lack flexibility and may generate false alarms. These tools should be combined together. 

**Good Example:**

An good example of static analysis tool pattern definition file using Semgrep could be found in `.github/semgrep.yml`. 

However, it should be noted that this configuration is illustrative rather than exhaustive. Please use the LLM to generate more suitable patterns, you can check the static analysis result using our example at [PR #11 -> Files Changed](https://github.com/U70-TK/cs846-presentation-winter-26/pull/11/changes).

Customized static analysis patterns should neither be overly broad nor overly strict.

- If it's too broad, it may trigger too many false positives. 
- If it's too strict, it likely will not catch anything. 

A good static analysis pattern definition should find a balance in between, and match project-specific conventions and expectations. 

**Bad Example:**

Static analysis patterns being too broad or too strict. Either:

- Too many false positives are captured, or
- Didn't catch any useful things.

#### Guideline 10.2: Automated Dependency Management Tools together with LLM

**Description:**

Secure your project against vulnerable or outdated third-party packages using two complementary approaches: (1) actively audit dependencies by having the LLM run ecosystem-specific audit tools, and (2) proactively monitor for new vulnerabilities by enabling automated dependency alerting services like Dependabot.

**Reasoning:**

A large portion of modern security risk does not originate from first-party code, but from third-party dependencies [17]. Even if your internal code is perfectly written, a vulnerable library version can introduce critical vulnerabilities into production. Active auditing (on-demand scans) catches issues at review time, while proactive monitoring (continuous alerting) catches newly disclosed vulnerabilities in packages you already depend on. Combining both provides defense in depth against software supply-chain attacks.

**Good Example (Active — LLM-driven audit):**

During code review, instruct the LLM to run the appropriate audit command for your package ecosystem to identify known vulnerabilities:

- **Node.js:** `npm audit` or `yarn audit`
- **Python (pip):** `pip-audit`
- **Rust:** `cargo audit`
- **Ruby:** `bundle-audit`

The LLM can then interpret the audit output, assess severity, and suggest remediation steps (e.g., upgrading a specific package version).

**Good Example (Proactive — Dependabot alerting):**

In GitHub, fork the current repository (to make sure you have admin access), then go to:

Settings -> Security -> Advanced Security -> Dependabot -> Enable Dependabot Alerts -> Enable.

Trigger a push on main branch, then go to:

Security -> Vulnerability Alerts -> Dependabot.

This continuously monitors vulnerability databases and alerts you when a dependency has a known CVE, without requiring manual scans.

**Bad Example:**

```
You are an experienced coding agent, please verify the dependency versions for me: [path-to-file].
```

This is too vague — it does not specify what tool to use, what vulnerabilities to check against, or what action to take on findings.

#### Guideline 10.3 Enforce Test Quality over Coverage

**Description:**

Before approving a pull request, verify that automated tests are executed in CI and that the change is covered by meaningful tests. Ensure that the project’s minimum test coverage threshold is met, and dedicatedly review the tests themselves to confirm they validate real behavior rather than merely increasing coverage numbers.

**Reasoning:**

While static analysis and dependency scanning catch structural and known vulnerability issues, they do not validate runtime behavior. Tests provide behavioral guarantees and protect against regressions.

**Good Example:**

Ensure the PR followed good testing principles introduced in `Week 9 - Testing` on Learn. The test suite should be reviewed as a first-class component of the pull request, not as an afterthought. Enforce a team-wide test coverage as a threshold and integrate it into GitHub Actions. 

**Bad Example:**

Writing meaningless test cases to inflate high test coverage.

---

### Guideline 11: Detect Malicious Pull Requests [13]

**Description:**

When reviewing a pull request, instruct the LLM to actively scan for potentially malicious patterns in the diff — such as obfuscated code, hardcoded credentials, suspicious network calls, unexpected permission escalations, or data exfiltration attempts. **Especially flag binary executables** (e.g., `.exe`, `.dll`, `.jar`, `.so`, `.wasm`), which cannot be diffed, linted, or statically analyzed and represent a blind spot for both human and automated review. For any binary detected, demand provenance, integrity verification (e.g., SHA-256 checksum), reproducibility, and a necessity justification before allowing the merge.

To make this reliable in practice, operationalize it through structured instruction files (Guideline 1). Without explicit instructions, Copilot tends to drift into surface-level review and can underweight supply-chain and security risks.

**Reasoning:**

Malicious pull requests are a real and growing attack vector in software supply chains [12]. These can range from subtle backdoors injected through obfuscated code to committed binaries containing known CVE vulnerabilities [13]. Unlike source code, binary artifacts cannot be meaningfully reviewed using standard development workflows, making them particularly dangerous. Simply stating "be cautious" is insufficient — without a concrete checklist encoded in the instruction file, LLMs tend to skip or underweight these findings entirely. By framing malicious pattern detection as a mandatory escalation with specific evidence requirements, the LLM is forced to surface these risks regardless of how the PR is described.

**Good Example:**

Add a security detection section to `.github/copilot-instructions.md`:

```markdown
## CRITICAL: Malicious Pattern Detection

When reviewing a PR, actively check for:
- Obfuscated or minified code that was not generated by a build tool.
- Hardcoded secrets, tokens, or credentials.
- Unexpected outbound network calls or data exfiltration patterns.
- Permission escalations or changes to authentication/authorization logic.
- Binary executables or non-text files invoked by code.

For any binary file detected, immediately flag it as a BLOCKER-severity finding and demand:
1. Provenance (source origin).
2. Integrity evidence (SHA-256 checksum matching a known-good artifact).
3. Justification for why it must be a committed binary.
4. The merge decision MUST be Reject until all items are provided.
```

**Bad Example:**

Ignore suspicious patterns and merge the PR, or rely solely on the PR description to determine safety.

---

## 2. Counter Guidelines with Partial or Indirect Alignment

### Guideline 1: Diagnose first, patch later (Group 2)

**Description:**

When using an LLM for an iterative debugging or diagnostic task where the root cause is unclear, prompt it to explain the likely issue, the supporting evidence, and what remains uncertain *before* proposing any code changes. Do not use a structured instruction file that forces a complete answer (patch + tests + summary) in one shot, as this causes the LLM to skip genuine diagnosis and jump to speculative fixes.

**Reasoning:**

A repo-wide instruction file that mandates a full structured response (root-cause analysis, proposed patch, test updates, edge cases, and summary) works well for well-defined review tasks, but over-constrains under-specified debugging scenarios. When the root cause is genuinely unclear, forcing the LLM to produce a patch in one shot leads it to fabricate a plausible-looking but potentially incorrect fix.


**Provided Good Example:**

No `instruction.md` is used for this task. 

```
This is an iterative debugging task. Do not propose code changes yet.
First explain the likely issue in the current code, what evidence supports it, and what is still uncertain.
Avoid refactoring or broad fixes until the cause is clear.
```

**Rationale for the Lack of Direct Alignment:**

This guideline targets iterative debugging, but the scope of this week's guidelines is code review. In a typical code review workflow, the reviewer acts as a gatekeeper — evaluating the correctness, style, and safety of changes submitted by the code owner — rather than diagnosing and fixing bugs on the owner's behalf. Debugging is the responsibility of the code author, not the reviewer. While the "diagnose before patching" principle is sound engineering advice, it addresses a fundamentally different activity than reviewing a pull request, which is why it does not directly align with our code review focus.

### Guideline 2: Discuss Merge Conflict with Copilot in Web App instead of through instructions file (Group 6)

**Description:**
Github has a web app that allows copilot conversations with access to the git repo, and this is a much easier method to discuss merge conflicts and what will come of each possible choice.

**Reasoning:**
This is quicker and easier to deal with merge conflicts than setting them up locally and simply using the instructions file does not deal with them automatically.

**Provided Good Example:**

For this solution, the copilot chat in the GitHub web app was used instead of the instructions file for the detailed review.

```
Please review the changes and identify merge conflicts, describing what each option would entail.

Please walk through each conflict section and spell out what ours vs theirs is for each conflicting file.

Please produce the 3-way merged chunks with step-by-step resolution ideas, for the merge into NewGuideline
```

**Rationale for the Lack of Direct Alignment:**

Resolving merge conflicts is not a code review activity. Merge conflicts are the PR author's responsibility — the reviewer acts as a gatekeeper who evaluates the correctness and quality of the proposed changes, not someone who resolves version-control issues on the author's behalf. Platforms like GitHub, GitLab already detect and block conflicting PRs automatically, and Git itself along with IDE merge editors (e.g., VS Code's built-in 3-way merge editor) already provide robust tooling for conflict resolution. I personally don't agree that this is a task needed much assistance from LLMs and this falls outside the PR reviewer's workflow entirely.

---

## 3. References

[1] Alami, Adam, et al. ‘Accountability in Code Review: The Role of Intrinsic Drivers and the Impact of LLMs’. ACM Trans. Softw. Eng. Methodol., vol. 34, no. 8, Association for Computing Machinery, Oct. 2025, https://doi.org/10.1145/3721127.

[2] Haider, Md Asif, et al. "Prompting and fine-tuning large language models for automated code review comment generation." arXiv preprint arXiv:2411.10129 (2024).

[3] Aðalsteinsson, Fannar Steinn, et al. "Rethinking code review workflows with llm assistance: An empirical study." 2025 ACM/IEEE International Symposium on Empirical Software Engineering and Measurement (ESEM). IEEE, 2025.

[4] Collante, Antonio, et al. "The Impact of Large Language Models (LLMs) on Code Review Process." arXiv preprint arXiv:2508.11034 (2025).

[5] Kawalerowicz, Marcin, Marcin Pietranik, and Krzysztof Stępniak. "LLMs as Code Review Agents: A Rapid Review and Experimental Evaluation with Human Expert Judges." International Conference on Computational Collective Intelligence. Cham: Springer Nature Switzerland, 2025.

[6] Cihan, Umut, et al. "Evaluating Large Language Models for Code Review." arXiv preprint arXiv:2505.20206 (2025).

[7] Cihan, Umut, et al. "Automated code review in practice." 2025 IEEE/ACM 47th International Conference on Software Engineering: Software Engineering in Practice (ICSE-SEIP). IEEE, 2025.

[8] Shwer, Elle, et al. “Code Review in the Age of AI: Why Developers Will Always Own the Merge Button.” The GitHub Blog, 14 July 2025, github.blog/ai-and-ml/generative-ai/code-review-in-the-age-of-ai-why-developers-will-always-own-the-merge-button.

[9] Gopu, Ria, et al. “Unlocking the Full Power of Copilot Code Review: Master Your Instructions Files.” The GitHub Blog, 15 Nov. 2025, github.blog/ai-and-ml/unlocking-the-full-power-of-copilot-code-review-master-your-instructions-files.

[10] “Using GitHub Copilot Code Review - GitHub Docs.” GitHub Docs, docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review.

[11] Mahajan, Sonal. “uReview: Scalable, Trustworthy GenAI for Code Review at Uber | Uber Blog.” Uber Blog, 3 Sept. 2025, www.uber.com/en-CA/blog/ureview.

[12] Qian, Callan Lamb Christoph Hamsen, Julien Doutre, Jason Foral, Kassen. “Detecting Malicious Pull Requests at Scale With LLMs | Datadog.” Datadog, 21 Oct. 2025, www.datadoghq.com/blog/engineering/malicious-pull-requests.

[13] Szymanski, M. et al. (2024). Limitations of the LLM-as-a-Judge Approach for Evaluating LLM Outputs in Expert Knowledge Tasks. In Proceedings of the 30th International Conference on Intelligent User Interfaces (IUI 2025). ACM. DOI: 10.1145/3708359.3712091. Available at: https://dl.acm.org/doi/10.1145/3708359.3712091

[14] Wang, R., Guo, J., Gao, C., Fan, G., Chong, C. Y., & Xia, X. (2025). Can LLMs Replace Human Evaluators? An Empirical Study of LLM-as-a-Judge in Software Engineering. arXiv preprint arXiv:2502.06193. Available at: https://arxiv.org/abs/2502.06193


---