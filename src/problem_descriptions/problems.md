# Week 10 Example Summarized Problems: CodeReview / PR

**Authors:** [Neel Sanjaybhai Faganiya, Ibrahim Mohammed Sayem, Felix Wang]

**GitHub Repository:** https://github.com/U70-TK/cs846-presentation-feedback-summary

## 1. Example Problems

### Problem A: 
**Model to Use:** 
### Problem Description



### Problem A_1: 

**Task Description:**  

**Starter Code:**  

---

### Problem A_2: 

**Task Description:**  


**Starter Code:**  

---

### Problem A_3: 

**Task Description:**  

**Starter Code:**  

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

## Problem B1: Context-First Correctness Review [4 mins]

**Guideline Target:** Guideline 4: Use a Structured, Context-First Review Prompt

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

## Problem B2: Evidence-Grounded Test Review and Comment Validation [5 mins]

**Guideline Target:** Guideline 5: Require Evidence-Grounded Justification Before Accepting LLM Claims

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

## Problem B3: Boundary-Controlled Review [3 mins]

**Guideline Target:** Guideline 6: Explicitly State Assumptions, Non-Goals, and Review Boundaries

**Task Description:**  
Review this PR for maintainability and PR-fit concerns only. Your review should stay within the scope implied by the PR description and the changed files. Focus on issues introduced by the new helper and endpoint logic, brittle coupling between changed functions, and any mismatch between the stated intent of the PR and the implemented behavior. Do not include findings about unrelated modules or broader redesign ideas. List findings with severity, and end with a merge decision.


**PR To Review:**

[Add customer summary feature and seed data with tests #1](https://github.com/U70-TK/cs846-presentation-feedback-summary/pull/1/) on branch [feat-customer-summary](https://github.com/U70-TK/cs846-presentation-feedback-summary/tree/feat-customer-summary)

**Diff and Commit Details:**

https://patch-diff.githubusercontent.com/raw/U70-TK/cs846-presentation-feedback-summary/pull/1.patch

---

### Problem C: 

**Model to use:** 

**Task Description:**  

---

### Problem D: 

**Model to use:** 

#### Problem D.1: 

**Task Description:**  

**Starter Code:**  

---
#### Problem D.2: 

**Task Description:**

**Starter Code:**


## 2. References

---
