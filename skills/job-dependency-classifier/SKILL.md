---
name: job-dependency-classifier
description: Builds a DAG of job dependencies based on table-level read/write lineages. Resolves cycles using step/time ordering.
version: 2.0.0
---

# Execution Playbook: Job Dependency Classifier

As the Job Dependency Classifier, your goal is to resolve data lineage mappings into a Directed Acyclic Graph (DAG), break circular dependencies using execution order, and output parallel execution tiers.

## 1. Environmental Scan & Pre-flight Check

- Verify that `lineage.json` (Phase 2) AND `jobs.json` (Phase 1) exist in the workspace.
- Verify that `networkx` and `matplotlib` are installed. If not, run `pip install -r requirements.txt`.

## 2. Dependency Logic

A dependency edge `A → B` is created when:
- Job A **writes** to a table that Job B **reads** from.

### Circular Dependency Resolution

When cycles occur (multiple jobs read+write the same table):
- **Same job group** (same `job_id`): Only edge from lower `step` → higher `step`
- **Different job groups**: Only edge from earlier `start_time` → later `start_time`

## 3. Tools

### Build DAG
```bash
python3 skills/job-dependency-classifier/tools/classify_dependencies.py lineage.json jobs.json > dag_result.json
```

### Generate Graph (PNG)
```bash
python3 skills/job-dependency-classifier/tools/generate_graph.py dag_result.json jobs.json dag_graph.png
```

### Generate Report (Markdown)
```bash
python3 skills/job-dependency-classifier/tools/generate_report.py jobs.json lineage.json dag_result.json ANALYSIS_REPORT.md
```

## 4. Validation & Assessment

- `dag_result.json` must contain `"status": "success"` with `tiers`, `edges`, and `summary`.
- If `"status": "error"` with circular dependency message, report the cycle to the user.
- Summary includes: `total_jobs`, `total_edges`, `total_tiers`.

## 5. Final Handover

- Present execution tiers to the user (Tier 1 jobs can run in parallel, etc.).
- Highlight the key insight: percentage of jobs in Tier 1 and critical path depth.
- Optionally generate `dag_graph.png` and `ANALYSIS_REPORT.md`.
