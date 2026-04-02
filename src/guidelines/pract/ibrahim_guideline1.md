# Guideline 7: Understand the Intent Before You Review — Verify Claims Against Implementation

## Description

Before judging any code, establish what it is supposed to do by reading the docstring, inline comments, function signature, and surrounding context. However, **do not treat these claims as ground truth**. Instead, verify each claim — especially security-related claims — against the actual implementation. If the intended behavior is unclear or if documentation contradicts the code, flag that mismatch as a finding. When using an LLM as part of your review, include both the claimed intent and explicit instructions to verify the claims rather than assume them. This approach ensures reviewers and models catch code that runs but either does the wrong thing or makes false security promises.

---

## Reasoning

- **Docstrings can be aspirational, stale, or wrong**, especially around security properties. Simply accepting docstring claims as ground truth leads reviewers and LLMs to approve code that violates those claims.
- **Code correction ratio improves by up to 23 percentage points** when intent is included in the review prompt, but only if that intent is actively verified rather than passively accepted.
- **False security claims are dangerous**. If code claims to use constant-time comparison but doesn't, or claims to use parameterized queries but concatenates user input, that mismatch is a P1 bug regardless of whether the code "works."
- **GPT-4o assessed code correctness 68.5% of the time when given a problem description**, dropping significantly without it. However, if the problem description itself is incorrect, the model validates against the wrong spec and approves dangerous code.
- **Missing, misleading, or incorrect documentation directly reduces review accuracy** more than generic syntactic or stylistic issues, because it shapes what both human reviewers and LLM models consider "correct."
- **Claims without proof are placeholders for bugs**. A pull request message claiming "this PR fixes a divide-by-zero bug" doesn't mean it actually does. Reviewers must verify that the claimed fix is present in the code and that the fix is sound.

---

## Good Example: Intent Stated and Claims Verified

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

## Bad Example: Intent Accepted Without Verification

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

## Bad Example: Claims Accepted Without Scrutiny

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


