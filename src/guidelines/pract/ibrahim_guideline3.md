# Guideline 3: Categorize Every Issue, Then Triage Interactions and Escalate Design Decisions

## Description

Before suggesting fixes, require the LLM to label every review finding with a **Type** and **Priority** so critical issues don't get buried under minor improvements. Extend the taxonomy to cover common "review gaps" (requirements/contracts and testing/validation), add an explicit **Design Decision** label for ambiguous source-of-truth conflicts, and finish with a **Compound Risk Assessment** step that looks for issue combinations (or change interactions) that create higher-severity risks than any single finding.

**Taxonomy:**
- **Types:** Bug Fix | Requirement/Contract | Testing/Validation | Enhancement | Documentation | Design Decision
- **Priorities:** P1 (block merge) | P2 (fix soon) | P3 (nice-to-have)

---

## Reasoning

1. **Unstructured reviews conflate severity and urgency:** Without explicit categorization, critical defects can be lost among stylistic notes. A type+priority taxonomy forces deliberate triage and makes the review actionable for both author and reviewer.

2. **Extended taxonomy addresses common failure modes:**
   - Missing or unclear expected behavior is not just "documentation" — it's a **Requirement/Contract** risk that may require design decisions before code can be written or fixed.
   - Lack of tests for edge cases is often the main merge risk — so **Testing/Validation** deserves its own bucket. A bug with full test coverage is lower risk than a bug with no tests.
   - Some findings cannot be correctly fixed until the team decides whether code or contract/docs is the source of truth. Labeling these as **Design Decision** prevents "confident but wrong" fixes that solve the wrong problem.

3. **Compound Risk Assessment catches interaction effects:** Individual issues may look minor alone—a missing edge-case test here, a silent error handler there—but when chained together in a single PR, they create higher-severity risks (e.g., a latent bug that is never tested + a security-sensitive code path that now touches that latent bug = P1). Without this step, the LLM never surfaces the compound risk.

4. **Reduces false negatives and alert fatigue:** By forcing explicit categorization, the LLM cannot hide critical issues under generic summaries, and reviewers learn to trust the labels because they are deterministic and evidence-grounded.

---

## Good Example: Categorize Then Triage

**Prompt:**

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
If the "right" fix depends on what the intended behavior is (e.g., mismatch between requirements/docs/tests vs code),
DO NOT force a single label. Use:
[P?] [Design Decision] - <issue>
Competing interpretations: (A) ... (B) ...
Decision needed: ...
Then suggest next steps (e.g., clarify contract, add tests) rather than a single definitive code change.

Step 2 — Compound Risk Assessment:
Now consider ALL findings and ALL changes together.
Do any combinations of changes/issues interact to create a higher-severity security or correctness risk 
than any single item alone?
Describe any vulnerability/correctness chains and assign a combined severity (P1/P2/P3).
Example: "Bug A (missing validation) + Bug B (silent exception handler in auth) = P1 security risk chain."

Here is the diff:
[paste full diff BEFORE -> AFTER]
```

## Bad Example: Generic or Non-Categorized Review

**Prompt:**

```
Review this PR and suggest improvements.
```