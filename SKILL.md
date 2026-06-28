---
name: batch-dependency-orchestrator
description: The Master Orchestrator for analyzing batch job dependencies. Coordinates Ingestion, Lineage Parsing, DAG Classification, and Visualization.
version: 2.0.0
---

# Execution Playbook: Batch Dependency Orchestrator (The Master)

You are the Master Orchestrator. Your role is to manage the end-to-end batch dependency analysis lifecycle by delegating to specialized sub-skills.

## Quick Path (One Command)

If the user just wants results fast:
```bash
python3 run_pipeline.py
```
This executes all phases and generates all outputs.

## The Orchestration Workflow

### Phase 1: Ingestion and Sanitization

- **Condition:** The user requests to analyze batch jobs, or `.csv` files are provided in `./inbox/`.
- **Action:** Invoke **`csv-batch-ingester`**.
- **Command:** `python3 skills/csv-batch-ingester/tools/ingest_csv.py ./inbox > jobs.json`
- **Goal:** Obtain a sanitized JSON output file `jobs.json` containing the batch jobs.
- **Supported CSV Formats:**
  - Format A: columns `running time`, `jobid`, `sql statement`
  - Format B: columns `start_time`, `task_id`, `job_id`, `job_name`, `command`, `action`, `is_enable`, `step`, `description`
- **🛑 Phase 1 Gate Verification Rules**:
  1. The `jobs.json` file must exist and contain `"status": "success"` with a `data` array.
  2. Report total jobs ingested and any filtering applied (e.g., non-SQL rows skipped).

### Phase 2: SQL Table Lineage Parsing

- **Condition:** Outputs from Phase 1 (`jobs.json`) are ready.
- **Action:** Invoke **`sql-column-lineage-parser`**.
- **Command:** `python3 skills/sql-column-lineage-parser/tools/parse_lineage.py jobs.json > lineage.json`
- **Goal:** Obtain a `lineage.json` file mapping job IDs to their table-level reads and writes.
- **Handles:** `DELETE FROM`, `UPDATE ... SET`, `INSERT INTO`, `SELECT` with subqueries and JOINs.
- **🛑 Phase 2 Gate Verification Rules**:
  1. The `lineage.json` file must exist with `"status": "success"` and a `lineage` dict.
  2. Report count of jobs with reads, writes, both, and no lineage detected.

### Phase 3: Dependency Graph Classification

- **Condition:** Outputs from Phase 2 (`lineage.json`) and Phase 1 (`jobs.json`) are ready.
- **Action:** Invoke **`job-dependency-classifier`**.
- **Command:** `python3 skills/job-dependency-classifier/tools/classify_dependencies.py lineage.json jobs.json > dag_result.json`
- **Goal:** Obtain execution tiers and DAG edges.
- **Circular Dependency Resolution:**
  - Same job group: step order (lower step runs first)
  - Different job groups: start_time order (earlier time runs first)
- **🛑 Phase 3 Gate Verification Rules**:
  1. The `dag_result.json` must contain `"status": "success"` with `tiers` and `edges`.
  2. If `"status": "error"` with circular dependency, report the cycle to the user.

### Phase 4: Visualization (Optional)

- **Condition:** Phase 3 completed successfully.
- **Graph:** `python3 skills/job-dependency-classifier/tools/generate_graph.py dag_result.json jobs.json dag_graph.png`
- **Report:** `python3 skills/job-dependency-classifier/tools/generate_report.py jobs.json lineage.json dag_result.json ANALYSIS_REPORT.md`

## Governance Rules

1. **Never Skip Phases:** Do not attempt to build a dependency graph without first ingesting the CSV and parsing the lineage.
2. **Deterministic Handoffs:** Ensure the output files of one skill are present before starting the next.
3. **Phase 3 requires both files:** `lineage.json` AND `jobs.json` (for step/time ordering).
4. **Project Management:** After the entire workflow is complete, summarize the final execution tiers for the user.

## Output Files

| File | Description |
|------|-------------|
| `jobs.json` | Sanitized job records from CSV |
| `lineage.json` | Table-level read/write lineage per job |
| `dag_result.json` | DAG with execution tiers, edges, and summary |
| `dag_graph.png` | Visual dependency graph (color-coded by job group) |
| `ANALYSIS_REPORT.md` | Full Markdown analysis report |
