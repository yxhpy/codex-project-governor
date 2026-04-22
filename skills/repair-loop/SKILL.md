---
name: repair-loop
description: Repair failed quality checks through a bounded loop without deleting tests, weakening assertions, skipping gates, or expanding implementation scope.
---

# Repair Loop

Use only after `quality-gate` reports failures.

## Rules

- Maximum default rounds: 3.
- Identify failure cause before modifying code.
- Do not delete tests, weaken assertions, skip gates, add escape dependencies, or expand scope.

## Output

Return repair rounds, failures fixed, failures remaining, and final gate status.
