## Problem A:

---

## Problem B: Backend PR Review and Comment Validation

### Problem B.1: Functional Correctness Review
**Model to Use:** GPT-4.1

#### Evaluation Description
The review should:
- First summarize the PR's intended change, affected components, and highest-risk areas before giving findings.
- Stay scoped to functional correctness, endpoint/helper consistency, and regression risk only.
- Ground findings in the actual PR contents rather than generic review boilerplate.
- Provide up to 5 concrete findings and a final merge recommendation.
- Avoid drifting into security, style, or architecture feedback.

#### Bad Example

**Prompt Used**

Please solve this question for me: Review this PR for correctness, consistency, and regression risk. Include a summary, findings, and a merge recommendation.

**Characteristics of Output**
- The response is structurally acceptable, but it stays generic throughout.
- It names broad areas like "summary logic," "ordering," and "test coverage" without tying them to specific functions, files, endpoints, or changed behaviors in the PR.
- Several points appear inferred from a likely pattern of PRs rather than from demonstrated evidence in the diff.
- The findings are mostly cautionary statements about what "might" be wrong, not concrete correctness defects or inconsistencies in the changed code.
- The merge recommendation is driven by generalized test concerns, so it is not especially actionable for the PR author.

**Why This Is Weak**

Without the context-first guideline, the model produced a review that sounds plausible but is not well anchored in the actual change. It nominally follows the requested format, but the content is too abstract to help a reviewer decide whether the implementation is correct. A human reviewer would still need to inspect the diff from scratch to determine whether the concerns are real.

#### Good Example

**Prompt Used**

```
You are an expert code reviewer. Please follow these steps for your review:

**Step 1: Structured Summary**  
First, summarize the pull request by clearly identifying:
- The intended change (what new feature or fix is being introduced)
- The components or files affected by the change
- The areas that appear highest risk (e.g., complex logic, critical data flows, or integration points)

**Step 2: Focused Review**  
Using your summary, conduct a review that is strictly scoped to the following concerns:
- Functional correctness: Does the changed code do what it claims, and are there any logic errors?
- Endpoint/helper consistency: Are endpoints and helper functions used consistently and correctly?
- Regression risk: Could these changes unintentionally break existing functionality?

**Instructions:**  
- Present your answer with clear headings and bullet points.
- Include up to 5 findings, each with a brief explanation.
- End with a final merge recommendation: Approve, Request Changes, or Reject.
- Do not include feedback on security, style, or architecture in this review.

**PR to Review:**  
[Add customer summary feature and seed data with tests #1](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/1/)  
Diff: https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch
```

**Characteristics of Output**
- The response follows the required two-stage structure clearly.
- It better matches the task by separating PR understanding from issue detection.
- It remains scoped to correctness and regression concerns and does not drift into out-of-scope categories.
- The organization is stronger: intended change, affected components, risk areas, findings, and recommendation are all easy to scan.
- However, the actual findings are still fairly generic and not strongly evidenced from the PR itself; the answer improves structure more than substantive review quality.

**Why This Is Stronger**

The guideline improved prompt compliance and review discipline. The model first established context, then stayed within the requested review boundaries. That makes the output easier to trust and easier to read. The main remaining weakness is that it still does not cite concrete implementation details, so the review is more organized than it is deeply validated.

#### Overall Comparison

The guided version is better than the unguided version, but mostly in form rather than depth. Guideline 6 helped the model produce a cleaner, more scoped, context-first review, which is exactly what the task asked for. However, both outputs are still limited by weak grounding in the PR's concrete code.

So the evaluation is:
- `Without guideline`: weak, generic, only partially useful.
- `With guideline`: better structured and better scoped, but only moderately better overall.
- `Conclusion`: Guideline 6 helped, but its impact here was incremental rather than transformative because the resulting review still lacked PR-specific evidence.

### Problem B.2: Test Review and Comment Validation
**Model to Use:** GPT-4.1

#### Evaluation Description
The review should:
- Validate only the peer review comment about the tests added in the PR.
- Classify the comment as `Accurate`, `Partially Accurate`, or `Inaccurate`.
- Ground the reasoning in specific test code, assertions, helper calls, line references, or test case names.
- State the minimum additional tests needed before merge based on concrete evidence from the changed tests.
- Avoid unsupported claims about missing coverage if the response cannot point to exact code evidence.

#### Bad Example

**Prompt Used**

Please solve this question for me: Review the tests added in this PR and say whether this review comment is accurate. Then explain why and suggest what tests should be added.

**Characteristics of Output**
- The response reaches the right top-level classification, but the explanation is broad and unsupported.
- It says the tests mainly verify helper invocation and top-level keys, but does not identify the exact test names, assertions, or code locations that prove this.
- It claims missing checks around totals, ordering, and edge cases without tying those claims to specific omissions in the test code.
- The “minimum additional tests” section expands into general suggestions rather than the smallest evidence-based gap required by the task.
- A reviewer reading the answer would still need to inspect the tests manually to verify whether the classification is justified.

**Why This Is Weak**

Without the evidence-grounding guideline, the model gives a plausible validation answer but does not show its work. That makes the output harder to trust, especially because this task is specifically about validating whether a review comment is supported by the test code. The answer is directionally correct, but not auditable.

#### Good Example

**Prompt Used**

```
You are reviewing a pull request that adds new tests to a Python project. Your task is to validate the following peer review comment:

> "The new tests mostly prove that helper functions were called and that a response has the right top-level keys, but they do not verify the actual summary semantics carefully enough. These tests could still pass if the report total or invoice ordering were wrong."

**Instructions (Guideline 7: Require Evidence-Grounded Justification):**

- Review only the tests added in this PR.
- For each claim you make, you must:
  1. Quote the specific line(s) of code (test case names, assertions, or helper calls) that support your claim.
  2. Explain your reasoning using only those lines.
  3. If you cannot point to a specific line, do not include the finding.
- Classify the peer review comment as:
  - `Accurate`
  - `Partially Accurate`
  - `Inaccurate`
- Provide:
  - Brief reasoning, citing specific code evidence.
  - The minimum additional tests needed before merge, again citing concrete test gaps with evidence.

**Resources:**
- PR description and patch: https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch

**Example Output:**

- Classification: Accurate / Partially Accurate / Inaccurate
- Reasoning: (with quoted lines and explanations)
- Minimum additional tests needed: (with evidence of missing checks)
```

**Characteristics of Output**
- The response is much closer to the task's intended standard because it explicitly tries to justify the classification from named tests and assertions.
- It ties the classification to concrete artifacts such as helper-call assertions and response-key checks instead of relying only on summary statements.
- It keeps the scope on validating the peer review comment rather than drifting into a general test review.
- The recommended follow-up tests are more directly connected to the claimed gaps in semantic validation.
- However, the answer still falls short of the full guideline standard because it references test names and example assertions loosely rather than consistently citing exact line numbers from the diff.

**Why This Is Stronger**

Guideline 7 materially improved the response because it pushed the model to justify its classification with concrete code evidence rather than intuition. That makes the answer more reviewable and more defensible. Even though the grounding is still imperfect, the guided version is clearly closer to the intended evaluation behavior than the unguided one.

#### Overall Comparison

The improvement in B2 is more meaningful than in B1. In this task, the purpose of the guideline is very specific: force the model to support its claims with evidence from the tests. The unguided answer largely skips that requirement, while the guided answer moves in the right direction by naming the types of assertions and test behaviors that support the classification.

So the evaluation is:
- `Without guideline`: correct conclusion, but weak evidence and low auditability.
- `With guideline`: stronger justification, better scoped reasoning, and closer to the required evidence-based standard.
- `Conclusion`: Guideline 7 clearly helped here. The guided response is more trustworthy because it attempts to anchor its claims in the actual tests, even if it still could be improved with stricter line-level citations.

### Problem B.3: Maintainability and PR-fit Review
**Model to Use:** GPT-4.1

#### Evaluation Description
The review should:
- Stay tightly scoped to maintainability and PR-fit concerns only.
- Respect the PR description and changed files as the boundary for what is in scope.
- Focus on issues introduced by the new helper and endpoint logic, brittle coupling between changed functions, and any mismatch between stated intent and implemented behavior.
- Avoid findings about unrelated modules, authentication/validation/persistence details handled elsewhere, or broader redesign ideas.
- List findings with severity and end with a merge decision.

#### Bad Example

**Prompt Used**

Please solve this question for me: Review this PR and suggest maintainability issues, scope concerns, and anything that seems brittle. End with a merge decision.

**Characteristics of Output**
- The response stays relatively concise, but it remains generic and loosely grounded.
- It raises broad maintainability points like adding inline comments, clearer naming, and documenting the endpoint/helper contract without tying those concerns to specific changed code.
- The “brittle coupling” finding is plausible, but it is framed at a high level and not supported with concrete evidence from the PR logic.
- It does correctly note that the PR seems aligned with its stated scope, but that conclusion is again fairly abstract.
- Overall, the answer reads more like a generic maintainability checklist than a boundary-controlled review of the actual diff.

**Why This Is Weak**

Without explicit assumptions and review boundaries, the model stayed somewhat on-topic but did not become meaningfully more precise. The findings are not clearly derived from the changed helper and endpoint behavior, so the review has limited value to the PR author. It avoids major scope violations, but mostly by staying shallow rather than by carefully reasoning within the allowed boundaries.

#### Good Example

**Prompt Used**

```
Review this PR for maintainability and PR-fit concerns only.

Context:
- Here is the codebase before the PR: https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/main/src/artifacts/problem_b.
- Here is the codebase after the PR: https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/feat-customer-summary/src/artifacts/problem_b.
- Focus on the new helper and endpoint logic introduced by the PR.

Assumptions / out of scope:
- Assume authentication, request validation, and database persistence layers work correctly.
- Treat auth/validation/persistence implementation details as out of scope unless the PR code misuses them.

Review boundaries (non-goals):
- Do not suggest broader architectural redesigns.
- Do not propose changes to unrelated modules or systems not shown here.
- Do not include findings about unrelated modules or broader redesign ideas.

What you MUST still flag:
- Any maintainability, correctness, consistency, or brittle coupling issues that arise directly from the PR logic, including interactions visible within the changed functions and their call relationships.
- Any mismatch between the stated intent of the PR and the implemented behavior.

Keep the review strictly within these boundaries. List findings with severity, and end
```

**Characteristics of Output**
- The response in is better aligned with the requested review shape: it uses severities, stays focused on helper/endpoint interaction, and ends with a merge recommendation.
- It does a better job of framing the review around maintainability and PR-fit rather than drifting into unrelated systems.
- The prompt boundary-setting clearly helped the model avoid broad architectural redesign advice.
- However, some findings are still hypothetical rather than grounded in the visible PR code, especially the claim about malformed input and incomplete error handling.
- The coupling concern is directionally relevant, but it is still expressed generically instead of being tied to a concrete mismatch or brittle dependency shown in the diff.

**Why This Is Stronger**

Guideline 8 improved scoping more than substance. The guided answer is better because it follows the intended review boundaries and avoids obvious overreach into unrelated areas. But it still does not fully satisfy the guideline's goal of flagging only issues that arise directly from the PR code, since some concerns are speculative rather than evidenced by the changed functions themselves.

#### Overall Comparison

The guided version is better for B3, but only modestly. Its main improvement is that it stays closer to the requested boundary-controlled review style: scoped topic, severity labels, and less architectural drift. The unguided version is also fairly restrained, so the delta is smaller than the prompt design would ideally produce.

The key weakness in both responses is the same: neither one is strongly anchored in concrete PR details. The guided version still invents some hypothetical maintainability risk instead of identifying a clearly demonstrated one from the changed helper and endpoint logic.

So the evaluation is:
- `Without guideline`: reasonably scoped, but generic and not well evidenced.
- `With guideline`: better boundary discipline and presentation, but still only moderately grounded in the actual PR code.
- `Conclusion`: Guideline 8 helped keep the review within scope, but it did not fully solve the deeper issue of generic, weakly evidenced findings.

---

## Problem C:
