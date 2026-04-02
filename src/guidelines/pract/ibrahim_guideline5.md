# Guideline 5: Issues That Require Human Judgment — Mitigated by Explicit Dependency Verification

## Description

LLMs have well-documented limitations in code correctness assessment. Research shows LLMs fail to correctly assess code correctness in roughly 1 in 3 cases [Cihan et al.], and achieve only 60-68% agreement with subject-matter experts on domain-specific tasks [Szymanski et al.]. Rather than treating all unmapped issues as inherently unmappable, this guideline identifies a concrete, highly-prevalent failure mode: **hidden dependencies in cached computations** — where LLMs systematically miss state variables, configuration parameters, or external factors that should influence cache keys but do not.

The updated approach shifts from a reactive stance (wait for the LLM to fail, then manually debug) to a proactive stance (explicitly train the LLM to surface and verify hidden dependencies before it signs off on caching logic).

---

## Reasoning

1. **LLMs miss invisible dependencies:** Caching bugs arise when a computation depends on state (e.g., a global variable, configuration flag, or external service) that is never included in the cache key. LLMs often fail to trace these dependencies because they do not appear in the immediate function scope or call chain.

2. **Concrete, operationalizable criteria work better than generic guidelines:** Rather than saying "human judgment required," we provide a specific, checkable procedure for LLMs to follow when they encounter caching logic. This reduces false negatives.

3. **Staleness is often invisible in unit tests:** A cache that always returns stale data may never trigger a test failure if the test runs only once or if the external state is mocked. LLMs cannot infer staleness from code structure alone; they must be explicitly prompted to reason about it.

4. **Low cost, high confidence:** Asking the LLM to enumerate variables, cross-check the cache key, and justify staleness risk adds roughly 10% overhead to review time but catches a class of bugs that slip through otherwise.

---

## Good Example: Explicit Dependency Verification in Caching Review

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

## Bad Example: Generic "Human Judgment Required" Flag Without Specificity

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

## Integration with Code Review Workflow

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

## References

- Cihan et al. [7]: LLM failure rate on code correctness assessment (~33%)
- Szymanski et al. [13]: LLM-expert agreement on domain-specific tasks (60-68%)
- Wang et al. [14]: LLM limitations on security, architecture, regulatory decisions
