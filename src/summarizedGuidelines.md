##Add new summarized guideline here



### Guideline 1: Create a structured instruction file (DO NOT FORGET TO UPDATE THE NAME OF THE GUIDELINE AS WELL)

---

### Guideline 3: Be Extra Cautious about Binary Executables (DO NOT FORGET TO UPDATE THE NAME OF THE GUIDELINE AS WELL)

---

### Guideline 4: Assess Regression Risk as Part of Every Review Decision (DO NOT FORGET TO UPDATE THE NAME OF THE GUIDELINE AS WELL)

---

### Guideline 6: Explicitly State Assumptions, Non-Goals, and Review Boundaries

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

### Guideline 7: Understand the Intent Before You Review (DO NOT FORGET TO UPDATE THE NAME OF THE GUIDELINE AS WELL)

---

### Guideline 9: Categorize Every Issue, Then Triage Interactions and Escalate Design Decisions

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

Step 0 — Scope:
Focus only on issues supported by the diff and the shown code. Prefer high-signal findings.

Step 1 — Categorize EACH finding before suggesting fixes:
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

Step 2 — Compound Risk Assessment:
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

### Guideline 11: Issues That Require Human Judgment (DO NOT FORGET TO UPDATE THE NAME OF THE GUIDELINE AS WELL)

---