# Guideline 1: Create Structured Instructions + Iterative Diagnosis + Conversational Tools

## Description

Combine three complementary approaches for effective Copilot-assisted code review:

1. **Structured Instruction Files** (foundation): Maintain repo-wide `.github/copilot-instructions.md` and path-specific `.github/instructions/*.instructions.md` files with clear, organized sections (Naming Conventions, Code Style, Error Handling, Testing, Examples).

2. **Iterative Diagnosis First** (process): Before proposing code fixes or solutions, always ask Copilot to diagnose the problem first—explain the likely issue, what evidence supports it, and what remains uncertain. Avoid refactoring or broad fixes until the root cause is clear.

3. **Conversational Web Tools for Complex Scenarios** (escalation): For complex tasks like merge conflict resolution or real-time collaboration that require interactive back-and-forth, use GitHub Copilot's web app chat interface instead of static instruction files. These tools provide faster, more intuitive resolution paths than local setup.

## Reasoning

- **Instruction files alone are necessary but insufficient.** LLMs benefit from structured, organized guidance to reduce drift [5], but long instruction files (>1000 lines) can trigger the "Lost in the middle" effect [16], making them ineffective for complex, non-linear tasks.

- **Diagnosis-first prevents false fixes.** By requiring Copilot to state its assumptions and identify evidence before proposing changes, you prevent surface-level pattern matching and ensure fixes address root causes, not symptoms.

- **Web app conversations excel at complex, interactive tasks.** Merge conflicts and real-time collaboration issues have contexts that evolve as the conversation progresses. The web UI's chat interface handles this flow naturally, whereas static instruction files cannot adapt to new information revealed during the session.

- **Each tool has the right scope.** Instruction files enforce consistency and baseline standards across many small decisions. Iterative diagnosis ensures correctness on a single issue. Web chat handles multi-faceted, interactive scenarios that span many decisions and require human judgment.

## Good Example

**Scenario:** Reviewing a Pull Request with potential security issues and merge conflicts.

**Step 1 — Static Instructions (foundation)**
```
File: .github/copilot-instructions.md

# Copilot Code Review Instructions

## Naming Conventions
- Use camelCase for variables and functions.
- Use PascalCase for classes and types.

## Error Handling
- Always handle promise rejections with try/catch.
- Never use bare catch (error) without typing.

## Testing
- Require unit tests for all exported functions.
- Use Jest for all testing.
- Name test files as <filename>.test.ts.

## Security
- Validate and sanitize all inputs passed to child_process functions.
- Flag any use of unsanitized user input as CRITICAL.
```

**Step 2 — Iterative Diagnosis (process)**
```
Prompt to Copilot:
"Before suggesting fixes, diagnose the issue in auth.py:
1. What is the likely security issue in the authenticate_user() function?
2. What evidence in the code supports this?
3. What assumptions are you making, and what is still uncertain?
Do NOT propose code changes yet — only diagnosis."
```

**Step 3 — Web Chat for Merge Conflicts (escalation)**
```
Use GitHub Copilot's web app chat:
"I have a merge conflict in middleware.ts between main and feature/security.
- main deletes the password-hashing function
- feature/security adds input validation before hashing
Please walk through each conflicting section and explain what 'ours' vs 'theirs' means.
What is the best way to resolve this without losing security improvements?"
```

## Bad Example

**Approach 1: Instruction File as Sole Source of Truth**
```
File: .github/copilot-instructions.md
[1000+ lines of verbose prose about every possible scenario]
[No clear sections or hierarchy]
[Conflicting or redundant statements]

Result: Copilot ignores large portions, becomes inconsistent,
and loses focus (Lost in the middle effect).
```

**Approach 2: Diagnosis Skipped; Direct Patching**
```
Prompt: "Fix all bugs in order_parser.py"

Result: Copilot proposes fixes without understanding root causes.
Surface-level pattern matching creates new bugs or overlooks subtle issues.
```

**Approach 3: Trying to Resolve Merge Conflicts via Instruction File Alone**
```
File: .github/copilot-instructions.md
[Attempts to configure merge conflict resolution strategies in YAML]

Result: Merge conflicts require interactive back-and-forth to understand
which branch's intent should win. Static files cannot model this.
Use web chat instead for 10x faster resolution.
```

---
