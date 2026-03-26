# Guideline 1 Counterexample

Authors: Anudeep Das, Henry Guo, Mariia Ponomarenko

# Counterexample for Guideline 1

Guideline 7 is “Understand the Intent Before you Review”

“Before judging any code, first establish what it is supposed to do. Read the docstring, inline  
comments, and any surrounding context. If the intended behavior is unclear, that absence is  
itself a finding worth flagging. When using an LLM model as part of your review, carry that same understanding into your prompt; otherwise, neither you nor the model has a basis to determine whether the code is correct or just internally consistent.”

This guideline does not work well for enforcing security best practices.

## Problem

Consider the following password authentication code for code review, with several problems.

python\`\`\`  
import hashlib  
import time  
import os  
   
SALT \= "demo\_salt"  
stored\_password \= os.getenv("password")

\# Stored salted hash (pretend this is from a database)  
STORED\_HASH \= hashlib.sha256((SALT \+ stored\_password).encode()).hexdigest()  
   
   
def compare(a, b):  
    """  
    Compares strings character-by-character.  
    """  
    if len(a) \!= len(b):  
        return False  
   
    for i in range(len(a)):  
        if a\[i\] \!= b\[i\]:  
            return False  
    return True  
   
   
def check\_password(password):  
    """  
    Hashes the provided password with a salt and compares it to the stored hash.  
    """  
    if password \== 'abc':  
        return 1  
    candidate\_hash \= hashlib.sha256((SALT \+ password).encode()).hexdigest()  
    return compare(candidate\_hash, STORED\_HASH)  
   
   
if \_\_name\_\_ \== "\_\_main\_\_":  
    attempt \= input("Enter password: ")  
   
    if check\_password(attempt):  
        print("Access granted")  
\`\`\`

# Prompting GPT-4.1

Following the guideline, we prompt with the following text:

\`\`\`  
Please review the week10\_counter file. 

This library is for authenticating a user who enters their password. 

The checkpassword function will salt the input, calculate its hash, and pass to the compare function that will check if the calculated hash matches the stored hash for the password.

The function must be able to accept password inputs greater than length 0, of arbitrary length, consisting of arbitrary ascii characters. 

Please check if the code matches the intended behaviour and not just if it runs. 

Make a concrete verdict (Approve / Request Changes / Reject) at the end to force a  
judgment rather than a list of observations  
\`\`\`

## GPT-4.1 Response

\`\`\`  
Here is a review of the week10\_counter.py file based on your requirements:

Intended Behavior:

Authenticate a user by checking if their input password, after salting and hashing, matches the stored hash.  
Accept passwords of arbitrary length and ASCII characters (length \> 0).  
Code Review:

Salting and Hashing:

The code salts the input password (SALT \+ password) and hashes it using SHA-256, which is correct.  
Stored Hash:

The stored hash is generated at runtime from the environment variable password. This is fine for demo, but in production, the hash should be stored securely and not recalculated every run.  
Password Input:

The check\_password function accepts any string input, including arbitrary ASCII and length \> 0\.  
Comparison:

The compare function does a character-by-character comparison. This is correct, but it is not constant-time and is vulnerable to timing attacks. For security, use hmac.compare\_digest().  
Special Case:

The function returns 1 if the password is 'abc', bypassing the hash check. This is a security flaw and should be removed.  
Edge Cases:

No explicit check for empty passwords, but the hash will still be calculated. Accepts arbitrary length and ASCII.  
Verdict:

The code matches the intended behavior for salting, hashing, and comparison, but the special case for 'abc' is a security flaw, and the comparison method is not secure.  
Concrete Verdict: Request Changes

Remove the special case for 'abc'.  
Replace the compare function with hmac.compare\_digest() for secure comparison.  
Optionally, add a check to reject empty passwords if desired.  
Let me know if you want me to make these changes.  
\`\`\`

## Judgement

The code review is decent and catches a lot of the problems with the code, but crucially, it reads the password from an environment variable, which is a poor practice. The LLM should have flagged this as a concern in its review. It is also assuming that the code review is for a demo, which is why it did not raise this as a requested change. However, it was not indicated in the prompt that this is demo code, hence being a problem

# Alternative Guideline

## Explicitly tell the model “This code is going to be pushed to production. Please ensure that best practices are followed”, and if the company has a .md file with best practices that the model can use, then this guideline is further strengthened. 

## By priming the model to assume that the code is going to be pushed to production, and to follow best practices, the model is going to be more strict in its code review because production-grade code should have zero tolerance for poor practices. 

# Prompting GPT-4o again

We append the text pertaining to our new guideline to the original guideline.

Please review the week10\_counter file. 

This library is for authenticating a user who enters their password. 

The checkpassword function will salt the input, calculate its hash, and pass to the compare function that will check if the calculated hash matches the stored hash for the password.

The function must be able to accept password inputs greater than length 0, of arbitrary length, consisting of arbitrary ascii characters. 

Please check if the code matches the intended behaviour and not just if it runs. 

Make a concrete verdict (Approve / Request Changes / Reject) at the end to force a  
judgment rather than a list of observations.

**This code is going to be pushed to production. Please ensure that best practices are followed.**

## Results

## 

## \`\`\`\`

## Read week10\_counter.py

## Here is a detailed review of the code in week10\_counter.py:

## Intended Behavior

## The library authenticates a user by checking their password.

## The check\_password function salts the input, hashes it, and compares it to a stored hash using the compare function.

## Passwords should be accepted if they are greater than length 0, of arbitrary length, and consist of arbitrary ASCII characters.

## Code Review

## 1\. Password Handling

## The code uses os.getenv("password") to retrieve the stored password, which is then salted and hashed to create STORED\_HASH.

## The check\_password function salts and hashes the input password and compares it to STORED\_HASH.

## 2\. Salting and Hashing

## The salt is hardcoded as "demo\_salt". This is not ideal for production; salts should be unique per user and stored securely.

## The hashing uses SHA-256, which is acceptable, but for production, a password hashing function like bcrypt, scrypt, or Argon2 is strongly recommended.

## 3\. Comparison Function

## The compare function compares strings character-by-character. This is vulnerable to timing attacks. Use hmac.compare\_digest() for constant-time comparison.

## 4\. Input Validation

## The code does not explicitly check for password length or character set, but the hashing function will accept any string input.

## The special case if password \== 'abc': return 1 is a backdoor and must be removed for production.

## 5\. Error Handling

## If os.getenv("password") is not set, stored\_password will be None, leading to a TypeError when concatenating with the salt.

## There is no error handling for missing environment variables.

## 6\. Security Best Practices

## **Hardcoded salt and environment variable for password are not secure.**

## No rate limiting or logging for failed attempts.

## No password complexity checks.

## Verdict

## Request Changes

## Required Changes for Production:

## Remove the backdoor (if password \== 'abc': return 1).

## Use a secure password hashing library (bcrypt, scrypt, Argon2).

## Use hmac.compare\_digest() for hash comparison.

## Handle missing environment variables gracefully.

## Use a unique salt per user, stored securely.

## Remove hardcoded salt.

## Add error handling and logging.

\`\`\`

## Why Better

The model now points out the criticism of having the password stored in an environment variable, and provides a better overall review of the code. Notably, the recommended actions does not instruct the programmer to remove the password from the environment variable, but at least it is mentioned in the review body itself.

# Guideline 10.2 Counterexample

Authors: Anudeep Das, Henry Guo, Mariia Ponomarenko

# Counterexample for Guideline 10.2

**Guideline 10.2:** Use Automated Dependency Management Tools

**Description**:  
Enable automated dependency monitoring and update mechanisms in your CI/CD workflow to continuously detect and remediate vulnerable or outdated third-party packages before merge.

**Reasoning**:  
A large portion of modern security risk does not originate from first-party code, but from third-party dependencies \[17\]. Even if your internal code is perfectly written, a vulnerable library version can introduce critical vulnerabilities into production. Automated dependency management tools like Dependabot are continuously monitoring vulnerability databases and ensuring the packages used are free of known vulnerabilities, so as to mitigate software supply-chain attacks.

**Good Example**:  
In GitHub, fork the current repository (to make sure you have admin access), then go to:  
Settings \-\> Security \-\> Advanced Security \-\> Dependabot \-\> Enable Dependabot Alerts \-\> Enable.  
Trigger a push on main branch, then go to:  
Security \-\> Vulnerability Alerts \-\> Dependabot.

**Bad Example**:  
You are an experienced coding agent, please verify the dependency versions for me: \[path-to-file\].

**Problem**  
We reuse problem C from the Week 10 problem set as seen in [https://github.com/U70-TK/cs846-presentation-winter-26](https://github.com/U70-TK/cs846-presentation-winter-26).

**Task Description**:  
Navigate to problem\_c/ . The problem\_c/before/ folder contains the dependency files  
package.json and package-lock.json before the pull request, and the problem\_c/after  
folder contains the dependency files package.json and package-lock.json after the pull request. Please review from a software supply-chain perspective and verify that the update does not introduce supply-chain risk.  
Write your response in the form of a list of findings in bullet points. End with a merge decision ( Approve , Request Changes , or Reject ) based on all prior considerations

Use GPT-4.1 to solve the problem.

**Response with Old Guideline**  
According to the old guideline we do not use an LLM to perform dependency evaluations. Instead, we use Github’s built-in deterministic dependency checker.

This is a problem because dependency checkers may not be available in the platform where the repository is hosted. The code could be in a personal git server, not available remotely, or the remote repository hosting site could simply not have access to good dependency checkers.

**New Guideline**  
**Description:**   
Ask the LLM to use available dependency checking tools to evaluate the change.

**Reasoning:**   
Most recent (2026) LLMs have tool-use capabilities built-in. The LLM will be able to call upon these deterministic package dependency auditing tools and then collect and analyze the results.

**Good Example:**  
“use an automated package dependency management tool to audit this change”

Bad Example:  
“Look at this change and tell me if there are any security problems with the package dependency updates”

**Response with New Guideline**  
Prompt:  
Navigate to problem\_c/ . The problem\_c/before/ folder contains the dependency files  
package.json and package-lock.json before the pull request, and the problem\_c/after  
folder contains the dependency files package.json and package-lock.json after the pull request. Please review from a software supply-chain perspective and verify that the update does not introduce supply-chain risk.  
Write your response in the form of a list of findings in bullet points. End with a merge decision ( Approve , Request Changes , or Reject ) based on all prior considerations. write to answer.txt  
use an automated package dependency management tool to do this

Response:  
The LLM created 2 audit files using npm audit and a final answer text file.

Audit-before.json  
{  
  "auditReportVersion": 2,  
  "vulnerabilities": {  
    "@nestjs/core": {  
      "name": "@nestjs/core",  
      "severity": "high",  
      "isDirect": true,  
      "via": \[  
        "@nestjs/platform-express"  
      \],  
      "effects": \[  
        "@nestjs/platform-express"  
      \],  
      "range": "7.6.0-next.1 \- 11.0.0-next.4",  
      "nodes": \[  
        "node\_modules/@nestjs/core"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/core",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    },  
    "@nestjs/platform-express": {  
      "name": "@nestjs/platform-express",  
      "severity": "high",  
      "isDirect": true,  
      "via": \[  
        "@nestjs/core",  
        "multer"  
      \],  
      "effects": \[  
        "@nestjs/core"  
      \],  
      "range": "\<=11.1.15 || \>=12.0.0-alpha.0",  
      "nodes": \[  
        "node\_modules/@nestjs/platform-express"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/platform-express",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    },  
    "multer": {  
      "name": "multer",  
      "severity": "high",  
      "isDirect": false,  
      "via": \[  
        {  
          "source": 1113996,  
          "name": "multer",  
          "dependency": "multer",  
          "title": "Multer Vulnerable to Denial of Service via Uncontrolled Recursion",  
          "url": "https://github.com/advisories/GHSA-5528-5vmv-3xc2",  
          "severity": "high",  
          "cwe": \[  
            "CWE-674"  
          \],  
          "cvss": {  
            "score": 0,  
            "vectorString": null  
          },  
          "range": "\<2.1.1"  
        }  
      \],  
      "effects": \[  
        "@nestjs/platform-express"  
      \],  
      "range": "\<2.1.1",  
      "nodes": \[  
        "node\_modules/multer"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/platform-express",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    }  
  },  
  "metadata": {  
    "vulnerabilities": {  
      "info": 0,  
      "low": 0,  
      "moderate": 0,  
      "high": 3,  
      "critical": 0,  
      "total": 3  
    },  
    "dependencies": {  
      "prod": 156,  
      "dev": 21,  
      "optional": 0,  
      "peer": 0,  
      "peerOptional": 0,  
      "total": 176  
    }  
  }  
}

Audit-after.json  
{  
  "auditReportVersion": 2,  
  "vulnerabilities": {  
    "@nestjs/core": {  
      "name": "@nestjs/core",  
      "severity": "high",  
      "isDirect": true,  
      "via": \[  
        "@nestjs/platform-express"  
      \],  
      "effects": \[  
        "@nestjs/platform-express",  
        "@nestjs/testing"  
      \],  
      "range": "7.6.0-next.1 \- 11.0.0-next.4",  
      "nodes": \[  
        "node\_modules/@nestjs/core"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/core",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    },  
    "@nestjs/platform-express": {  
      "name": "@nestjs/platform-express",  
      "severity": "high",  
      "isDirect": true,  
      "via": \[  
        "@nestjs/core",  
        "multer"  
      \],  
      "effects": \[  
        "@nestjs/core",  
        "@nestjs/testing"  
      \],  
      "range": "\<=11.1.14 || \>=12.0.0-alpha.0",  
      "nodes": \[  
        "node\_modules/@nestjs/platform-express"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/platform-express",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    },  
    "@nestjs/testing": {  
      "name": "@nestjs/testing",  
      "severity": "high",  
      "isDirect": true,  
      "via": \[  
        "@nestjs/core",  
        "@nestjs/platform-express"  
      \],  
      "effects": \[\],  
      "range": "7.6.0-next.1 \- 11.0.0-next.4",  
      "nodes": \[  
        "node\_modules/@nestjs/testing"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/testing",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    },  
    "multer": {  
      "name": "multer",  
      "severity": "high",  
      "isDirect": false,  
      "via": \[  
        {  
          "source": 1113635,  
          "name": "multer",  
          "dependency": "multer",  
          "title": "Multer vulnerable to Denial of Service via incomplete cleanup",  
          "url": "https://github.com/advisories/GHSA-xf7r-hgr6-v32p",  
          "severity": "high",  
          "cwe": \[  
            "CWE-459"  
          \],  
          "cvss": {  
            "score": 0,  
            "vectorString": null  
          },  
          "range": "\<2.1.0"  
        },  
        {  
          "source": 1113636,  
          "name": "multer",  
          "dependency": "multer",  
          "title": "Multer vulnerable to Denial of Service via resource exhaustion",  
          "url": "https://github.com/advisories/GHSA-v52c-386h-88mc",  
          "severity": "high",  
          "cwe": \[  
            "CWE-772"  
          \],  
          "cvss": {  
            "score": 0,  
            "vectorString": null  
          },  
          "range": "\<2.1.0"  
        },  
        {  
          "source": 1113996,  
          "name": "multer",  
          "dependency": "multer",  
          "title": "Multer Vulnerable to Denial of Service via Uncontrolled Recursion",  
          "url": "https://github.com/advisories/GHSA-5528-5vmv-3xc2",  
          "severity": "high",  
          "cwe": \[  
            "CWE-674"  
          \],  
          "cvss": {  
            "score": 0,  
            "vectorString": null  
          },  
          "range": "\<2.1.1"  
        }  
      \],  
      "effects": \[  
        "@nestjs/platform-express"  
      \],  
      "range": "\<=2.1.0",  
      "nodes": \[  
        "node\_modules/multer"  
      \],  
      "fixAvailable": {  
        "name": "@nestjs/platform-express",  
        "version": "11.1.16",  
        "isSemVerMajor": true  
      }  
    }  
  },  
  "metadata": {  
    "vulnerabilities": {  
      "info": 0,  
      "low": 0,  
      "moderate": 0,  
      "high": 4,  
      "critical": 0,  
      "total": 4  
    },  
    "dependencies": {  
      "prod": 156,  
      "dev": 279,  
      "optional": 2,  
      "peer": 0,  
      "peerOptional": 0,  
      "total": 434  
    }  
  }  
}

Answer.txt  
Automated Supply-Chain Risk Review (npm audit)

\*\*Before the update:\*\*  
\- 3 high-severity vulnerabilities detected:  
	\- \`@nestjs/core\` (high, direct): fix available in 11.1.16  
	\- \`@nestjs/platform-express\` (high, direct): fix available in 11.1.16  
	\- \`multer\` (high, indirect): Denial of Service vulnerabilities, fix available via updating \`@nestjs/platform-express\`  
\- No critical, moderate, or low vulnerabilities found.

\*\*After the update:\*\*  
\- 4 high-severity vulnerabilities detected:  
	\- \`@nestjs/core\` (high, direct): fix available in 11.1.16  
	\- \`@nestjs/platform-express\` (high, direct): fix available in 11.1.16  
	\- \`@nestjs/testing\` (high, direct, new): fix available in 11.1.16  
	\- \`multer\` (high, indirect): Denial of Service vulnerabilities, fix available via updating \`@nestjs/platform-express\`  
\- No critical, moderate, or low vulnerabilities found.  
\- The new vulnerability is due to the addition of \`@nestjs/testing\` as a devDependency, which inherits the same issues as the other NestJS packages.

\*\*Automated Tool Findings:\*\*  
\- All vulnerabilities are known and originate from the NestJS ecosystem and its dependency on \`multer\`.  
\- Fixes are available but require a major version upgrade of NestJS packages.  
\- No new or unknown supply-chain risks were introduced by the update; the risk profile is unchanged except for the addition of a test-only package with the same known issues.  
\- No evidence of malicious or suspicious packages.

\*\*Merge Decision: Approve\*\*  
Rationale: The update does not introduce new production supply-chain risks. All vulnerabilities are known, have available fixes, and are present in both before and after states. The only new issue is in a devDependency used for testing. Recommend addressing by upgrading NestJS to the latest major version in a future update.

The answer is satisfactory as it identified all the necessary packages with potential security risks, especially multer. Though the LLM’s decision was to accept the change, the user can use this dependency change security vulnerabilities summary to make their own decision.

# Guideline 2 Counterexample

# Guideline 2: Write Structured Review Comments

**Description** 

Every issue you find should be reported in a consistent format that includes the location of the problem, its description, the reason it matters, and the steps to resolve it. A vague comment like this looks unsafe is not actionable. A reviewer reading your report, or a developer receiving your feedback, needs all four pieces to understand and act on the finding. Use this template for every finding: \[Location\] → \[What\] → \[Why\_it\_matters\] → \[Suggested\_fix\] 

**Reasoning**

 • Practitioners rate review comments on three dimensions: Relevance, Information completeness, and Explanation clarity \[2\].   
• Comments missing any one of these three dimensions are considered low quality by real developers.  
• Structured comments reduce back-and-forth between reviewer and author; the fix is self-contained.   
• When asking Copilot to review code, requesting this format in your prompt directly improves the quality of its output. 

**Example** 

storage.py:   
search\_by\_error\_type(), line 79   
\-\> SQL string interpolated with f-string   
\-\> Attacker-controlled input reaches the database query unchanged (SQL Injection) \-\> Replace with parameterized query: conn.execute("SELECT \* FROM crashes WHERE error\_type \=?", (error\_type,)) 

**Good Example: Structured Review**   
\- Ask Copilot to report every issue using a consistent format: location, what, why, and fix   
\- Specify the exact output format so every finding is self-contained and actionable   
\- Group findings under clear headings so critical issues are not buried alongside minor ones   
\- Ask for a severity (Critical / High / Medium / Low) label on each finding so issues can be triaged by importance   
\- Request a concrete verdict at the end to force an overall judgment on the code 

**Bad Example:**   
Not Structured Can you check the crash\_dedup code and tell me if there are any problems?

## Issue

While the original guideline provides the format of structured feedback for the code, it also makes LLM concentrate on specific precise issues and pay less attention to general architecture. However the problem sometimes can be conceptual, span across several files and represent bad design choices. 

## Example Problem

**database.py**

import sqlite3

def get\_connection():  
    conn \= sqlite3.connect("crashes.db")  
    conn.row\_factory \= sqlite3.Row  
    return conn

from flask import Flask, request, jsonify  
import database

app \= Flask(\_\_name\_\_)

@app.route("/crashes")  
def get\_crashes():  
    error\_type \= request.args.get("error\_type")

    conn \= database.get\_connection()  
    cursor \= conn.cursor()

    query \= "SELECT \* FROM crashes WHERE error\_type \= ?"  
    cursor.execute(query, (error\_type,))

    rows \= cursor.fetchall()

    result \= \[\]  
    for row in rows:  
        result.append({  
            "id": row\["id"\],  
            "message": row\["message"\],  
            "error\_type": row\["error\_type"\]  
        })

    conn.close()  
    return jsonify(result)

**api.py**

@app.route("/crashes", methods=\["POST"\])  
def create\_crash():  
    data \= request.json

    conn \= database.get\_connection()  
    cursor \= conn.cursor()

    cursor.execute(  
        "INSERT INTO crashes (message, error\_type) VALUES (?, ?)",  
        (data\["message"\], data\["error\_type"\])  
    )

    conn.commit()  
    conn.close()

    return {"status": "ok"}

**analytics.py**

import database

def count\_crashes(error\_type):  
    conn \= database.get\_connection()  
    cursor \= conn.cursor()

    cursor.execute(  
        "SELECT COUNT(\*) FROM crashes WHERE error\_type \= ?",  
        (error\_type,)  
    )

    count \= cursor.fetchone()\[0\]

    conn.close()  
    return count

**Note: Code was generated by ChatGPT**

## Input Prompt using Original Guideline

**Note: the prompt was constructed with the help of the guideline and ChatGPT.**

Review the following code for potential issues related to security, correctness, performance, and maintainability.

Report every issue using the following structured format:

Severity: (Critical | High | Medium | Low)  
Location: file name, function/method, and line number  
What: short description of the issue  
Why it matters: explain the impact or risk  
Suggested fix: concrete recommendation or code change

Requirements:

Every issue must follow this exact structure.  
Each finding must be self-contained and actionable.  
Group findings under the following headings:  
Critical Issues  
High Severity Issues  
Medium Severity Issues  
Low Severity Issues  
Do not mix severity levels within the same section.  
If multiple issues occur in the same file, report them separately.  
After listing all findings, provide a final verdict summarizing the overall quality of the code. The verdict should include:

A short summary of the main risks  
Whether the code is safe to deploy or requires fixes before release.

## Output when using Original Guideline 

High Severity Issues

Severity: High  
Location: api.py, create\_crash, line 32  
What: No input validation or sanitization for POST data  
Why it matters: Accepting and inserting user-provided data directly into the database without validation exposes the application to security risks such as SQL injection (if the database driver is misconfigured), and allows malformed or malicious data to be stored.  
Suggested fix: Validate and sanitize all incoming data fields (message, error\_type) before using them. Check for required fields, types, and length constraints.

Medium Severity Issues

Severity: Medium  
Location: api.py, get\_crashes, line 8  
What: No error handling for database operations  
Why it matters: If the database connection fails or a query error occurs, the application will raise an unhandled exception, potentially exposing stack traces or causing the server to crash.  
Suggested fix: Wrap database operations in try-except blocks and return appropriate error responses.

Severity: Medium  
Location: api.py, create\_crash, line 32  
What: No error handling for database insert  
Why it matters: If the insert fails (e.g., due to constraint violation), the server will return a 500 error and may expose sensitive information.  
Suggested fix: Add try-except around the insert and return a user-friendly error message.

Low Severity Issues

Severity: Low  
Location: api.py, get\_crashes, line 8  
What: No check for missing or empty error\_type parameter  
Why it matters: If error\_type is not provided, the query will search for rows with a NULL error\_type, which may not be intended.  
Suggested fix: Return a 400 error if error\_type is missing or empty.

Severity: Low  
Location: api.py, get\_crashes, line 18  
What: Inefficient row-to-dict conversion  
Why it matters: Manually building the result list is error-prone and less efficient than using a helper or ORM.  
Suggested fix: Use a helper function or a library like sqlite3.Row to convert rows to dictionaries automatically.

Severity: Low  
Location: api.py, general  
What: No logging of errors or important events  
Why it matters: Lack of logging makes debugging and monitoring difficult.  
Suggested fix: Add logging for errors and key actions.

## Analysis

The issue with this output is that while the LLM found certain imperfections in the code, it missed the major design issue which is API directly accessing the database without any service layer in between. 

## New Guideline

**Description** 

Every issue you find should be reported in a consistent format that includes the location of the problem, its description, the reason it matters, and the steps to resolve it. A vague comment like this looks unsafe is not actionable. A reviewer reading your report, or a developer receiving your feedback, needs all four pieces to understand and act on the finding. Use this template for every finding: \[Location\] → \[What\] → \[Why\_it\_matters\] → \[Suggested\_fix\]. **However if the design issue is found, it should be reported but does not have to precisely follow the aforementioned format (for example exact lines of code do not have to be reported).** 

**Reasoning**

• Structured comments reduce back-and-forth between reviewer and author; the fix is self-contained.   
• In case of major design issues the format can be partly ignored, as suggested fix might be too big or unfeasible, and location can span across the whole project. 

**Example** 

**Good Example: Structured Review**   
\- Ask Copilot to report every issue using a consistent format: location, what, why, and fix   
\- Note that it should pay attention to overall design and provide insight on general/conceptual issues with the code 

**Bad Example:** 

Asking to always stick to a specific format.

## Input Prompt using New Guideline

**Note: Prompt was constructed with the help of new guideline and ChatGPT**

Review the following code for issues related to security, correctness, performance, maintainability, and software architecture.  
Report every issue using the following structured format:  
Severity: (Critical | High | Medium | Low)  
Location: file name, function/method, and line number(s). If the issue spans multiple files or is architectural, list all relevant files.  
What: short description of the issue  
Why it matters: explain the impact or risk  
Suggested fix: concrete recommendation or design improvement  
Requirements:  
• Every issue must follow this exact structure.  
• Each finding must be self-contained and actionable.  
• If a problem spans multiple files or layers, describe it as a cross-file or architectural issue.  
• Group findings under the following headings:  
Critical Issues  
High Severity Issues  
Medium Severity Issues  
Low Severity Issues  
**In addition to code-level problems, analyze design and architectural concerns and report them. Those can include:**  
• tight coupling between modules  
• missing abstraction layers  
• violations of separation of concerns  
• duplicated logic across files  
• patterns that make testing difficult  
After listing all findings, provide a Final Verdict that includes:  
• a short summary of the most important risks  
• whether the code is safe to deploy  
• the most important fix that should be addressed first.

## Output when using New Guideline 

Critical Issues  
Severity: Critical  
Location: api.py → create\_crash() (lines 30-45)  
What: No validation of request body / missing fields  
Why it matters: If the request body is missing, not JSON, or lacks "message" / "error\_type", the code raises a TypeError/KeyError, causing a 500 response and potentially crashing the request handler. This is a denial-of-service vector and makes the API unreliable.  
Suggested fix: Validate request.json and required keys before use. Return a clear 400 response when input is invalid. Example: check if not data or "message" not in data or "error\_type" not in data: return jsonify(error="..."), 400\.  
---

Severity: Critical  
Location: api.py → get\_crashes() (lines 6-27)  
What: Unbounded input from query parameter used in query without validation/normalization  
Why it matters: While parameterized SQL protects from injection, allowing arbitrary error\_type values (including very large payloads) can lead to inefficient queries and may expose sensitive data if the DB schema changes. It also means the endpoint behavior is undefined when error\_type is missing (None).  
Suggested fix: Explicitly validate and normalize error\_type (e.g., whitelist allowed values, enforce length/format). If missing, either return 400 or treat it as “return all crashes” with deliberate logic.  
---

High Severity Issues  
Severity: High  
Location: api.py \+ database.py (architectural)  
What: Database connection logic is tightly coupled and uses a hard-coded relative DB path ("crashes.db")  
Why it matters: The DB file location depends on the working directory, which can change between deployments/tests, making behavior unpredictable and hard to configure. This also makes unit testing difficult because tests may write to the same production file.  
Suggested fix: Parameterize DB path via config/environment variable; allow injecting a connection factory for tests. Example: get\_connection(db\_path=os.getenv("DB\_PATH", "crashes.db")).  
---

Severity: High  
Location: api.py (both handlers)  
What: No error handling around database operations (connection, query, commit)  
Why it matters: Any DB error (lock, disk full, missing table) will raise and propagate as a 500 error, and may leak stack traces or crash the app.  
Suggested fix: Wrap DB calls in try/except and return a controlled 500 response; ensure conn.close() runs in a finally block or via context manager.  
---

Severity: High  
Location: api.py (both handlers)  
What: No authentication/authorization or rate limiting  
Why it matters: Anyone can read or insert crash records, opening the system to spam, data pollution, or privacy exposure.  
Suggested fix: Add an auth layer (API keys, token auth) and/or rate limiting middleware appropriate for the use case.  
---

Medium Severity Issues  
Severity: Medium  
Location: api.py → get\_crashes() (lines 14-26)  
What: Manual JSON serialization is repetitive and brittle  
Why it matters: If new columns are added to crashes or schema changes, this code must be updated; missing fields cause KeyError.  
Suggested fix: Use a helper serializer (e.g., dict(row) with filtering) or a model/schema layer (e.g., Marshmallow, Pydantic).  
---

Severity: Medium  
Location: api.py (both handlers)  
What: No content-type enforcement for JSON requests/responses  
Why it matters: If a client sends wrong Content-Type, request.json may be None, and the endpoint breaks instead of returning a helpful error.  
Suggested fix: Enforce Content-Type: application/json and return 415/400 when missing.  
---

Severity: Medium  
Location: database.py  
What: No connection pooling or threaded-safety considerations  
Why it matters: If Flask is run with multiple threads/processes, SQLite can lock and fail under concurrent requests.  
Suggested fix: Use a connection per request (Flask g object) and/or use a more suitable DB for concurrency (PostgreSQL) if concurrency is expected.  
---

Low Severity Issues  
Severity: Low  
Location: api.py (both handlers)  
What: No explicit HTTP status codes in responses  
Why it matters: Implicit defaults (200 OK) are fine, but explicit status codes improve clarity and allow more precise API contracts.  
Suggested fix: Return jsonify(...), 200 or jsonify(...), 201 for create, and use explicit status codes for errors.  
---

Severity: Low  
Location: api.py  
What: No logging of requests or errors  
Why it matters: Debugging production issues is harder without logs; auditing API calls is impossible.  
Suggested fix: Add structured logging (e.g., app.logger.info(...)) and error logging in exception handlers.  
---

Severity: Low  
Location: api.py  
What: No documentation / docstrings on endpoints  
Why it matters: Future maintainers can’t quickly understand expected request/response format.  
Suggested fix: Add minimal docstrings above each route explaining parameters and response format.  
---

Final Verdict  
🔍 Most Important Risks

* The API crashes on invalid/malformed input (missing JSON or required keys), causing 500 errors.  
* Database access isn’t protected or configured, making the system fragile and hard to test.  
* No auth means anyone can read/insert crash data.

✅ Safe to deploy?  
Not yet. The service is not safe for a public or production environment due to input validation failures and lack of error handling/auth.  
🚨 Most important fix (first priority)  
Add strong input validation and safe error handling around request.json and DB operations (especially in create\_crash()), ensuring malformed requests return controlled 4xx responses rather than crashing the endpoint.

