# Laboratory results

## Diagnosis

Read README.md, AGENTS.md, both workflow files, pyproject.toml and the checkout
specification before implementing changes. Part 1 was already fixed in commit
`a4b7246`: mutable default reservation state, missing type annotations, unused
imports, incorrect low-stock boundary, exhausted stock entries and report types
were corrected; deprecated `datetime.utcnow()` was replaced with UTC-aware time.

The checkout initially validated nothing and calculated only subtotal plus VAT.
Each new invalid-input test failed because validation returned None. Discount,
delivery and invalid-total tests failed against the incomplete calculation.

Tests were completed independently of implementation commits. Existing assertions
were preserved. Tests for behavior already implemented were recorded as passing,
rather than claiming they demonstrated a new RED phase. The implementation kept
its ellipsis until enough tests had been committed, then removed it in a separate
refactoring commit. No checks or configuration were weakened.

## Commands and results

```bash
uv run pytest tests/test_checkout.py::test_non_numeric_quantity_is_rejected -v
# Before implementation: FAILED (validation returned None).

uv run pytest tests/test_checkout.py -v
# Final: 21 passed.

./scripts/check.sh
# 45 passed; format, lint, types and TDD history all pass.

./scripts/check-part2.sh
# 21 passed; checkout coverage 100%; TDD history passes.
```

Full per-step RED/GREEN command output from the automated continuation is saved
locally at `/tmp/lab-tdd-evidence.txt`. Tests cover all ten validation rules,
discount tiers, promo selection and cap, delivery thresholds after discounts,
VAT rounding and invalid orders returning None. Money remains integer kopecks.

The first full local run after implementation exposed formatting, function
complexity (13 > 9) and the remaining ellipsis. Refactoring extracted line
validation, formatting was applied, and the final committed history passed the
TDD checker (`e742d4ff` tests before `b8cb5afb` completed implementation).

Local verification used Python 3.12.15 and Python 3.13.16: 45 tests passed on
each version, using dependencies exported from the frozen lockfile. Python 3.13
was checked in a separate temporary environment without changing project files.
GitHub Actions for PR #10 returned `action_required`: the upstream owner must
approve the fork workflow runs before remote CI can execute.
Historical failed GitHub runs could be listed but their logs returned
`log not found`; they were not used as evidence of a specific code failure.

The user authorized completion of the remaining test cases by the agent because
of limited time. Earlier tests were written and committed by the user. This is
recorded explicitly so the division of work can be explained accurately.
