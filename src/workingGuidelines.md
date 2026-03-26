# Week 10 Guidelines: CodeReview / PR

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


## 1. Original guidelines that worked for all

#### Guideline 2.1: Static Analysis Tool together with LLM [11]

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

----

#### Guideline 2.3 Enforce Test Quality over Coverage [18]

**Description:**

Before approving a pull request, verify that automated tests are executed in CI and that the change is covered by meaningful tests. Ensure that the project’s minimum test coverage threshold is met, and dedicatedly review the tests themselves to confirm they validate real behavior rather than merely increasing coverage numbers.

**Reasoning:**

While static analysis and dependency scanning catch structural and known vulnerability issues, they do not validate runtime behavior. Tests provide behavioral guarantees and protect against regressions.

**Good Example:**

Ensure the PR followed good testing principles introduced in `Week 9 - Testing` on Learn. The test suite should be reviewed as a first-class component of the pull request, not as an afterthought. Enforce a team-wide test coverage as a threshold and integrate it into GitHub Actions. 

**Bad Example:**

Writing meaningless test cases to inflate high test coverage.

----

### Guideline 4: Use a Structured, Context-First Review Prompt [3][7]

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

### Guideline 5: Require Evidence-Grounded Justification Before Accepting LLM Claims [3]
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

### Guideline 8: Write Structured Review Comments [2]

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

----



## 2. References

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