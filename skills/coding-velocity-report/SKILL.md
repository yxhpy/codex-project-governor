---
name: coding-velocity-report
description: Produce a velocity report for a task, measuring context time, first patch time, repair rounds, quality gate pass rate, patch size, reuse ratio, drift findings, and manual approvals.
---

# Coding Velocity Report

Use after implementation or during retrospectives.

## Purpose

Measure acceleration without rewarding large patches, drift, skipped gates, or low-quality repairs.

## Output

Create `VELOCITY_REPORT.md` and return velocity score, quality score, bottlenecks, and recommendations.
