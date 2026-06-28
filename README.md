# Batch Dependency Analyzer Agent

This plugin provides a deterministic end-to-end suite for analyzing PostgreSQL batch jobs from CSV files, parsing their SQL to extract table-level reads/writes, and building a Directed Acyclic Graph (DAG) to classify data dependencies and compute parallel execution tiers.

## Architecture

This plugin follows the **Master Orchestrator / Playbook** framework. It consists of one orchestrator skill and three execution sub-skills, plus visualization tools.

### Master Orchestrator
- **`batch-dependency-orchestrator`**: The entry point for the agent. It manages the entire lifecycle, ensuring strict deterministic execution by gating each phase until required outputs are produced.

### Sub-Skills
1. **`csv-batch-ingester`**: Scans the `./inbox/` directory for `.csv` files, validates them, maps columns, filters to SQL-only jobs, and sanitizes the data into a clean JSON structure (`jobs.json`).
2. **`sql-column-lineage-parser`**: Parses the SQL AST using `sqlglot` to extract table-level reads and writes for each job (`lineage.json`). Handles `DELETE`, `UPDATE`, `INSERT`, and `SELECT` statements.
3. **`job-dependency-classifier`**: Uses `networkx` to resolve data lineage into a DAG, using step/time ordering to break circular dependencies, and calculates parallel execution tiers.

### Visualization Tools
- **`generate_graph.py`**: Renders the DAG as a PNG image with tier-based layout and color-coded job groups.
- **`generate_report.py`**: Produces a full Markdown analysis report with summaries and detailed tier breakdowns.

## Requirements

```bash
pip install -r requirements.txt
```

Dependencies: `sqlglot`, `pandas`, `networkx`, `matplotlib`

## CSV Input Format

Place your CSV file(s) in the `./inbox/` directory. The ingester supports two column formats:

### Format A (Original)
| Column | Description |
|--------|-------------|
| `running time` | Scheduled execution time |
| `jobid` | Unique job identifier |
| `sql statement` | The SQL query |

### Format B (Check-In Batch Job)
| Column | Maps To | Description |
|--------|---------|-------------|
| `start_time` | `running time` | Scheduled start time |
| `task_id` | `jobid` (combined as `{job_id}_{task_id}`) | Task identifier |
| `job_id` | job group | Job group identifier |
| `job_name` | metadata | Job group name |
| `command` | `sql statement` | The SQL query |
| `action` | filter | Only `EXECUTE_SQL` rows are kept |
| `is_enable` | filter | Only `Y` rows are kept |
| `step` | ordering | Execution order within a job group |
| `description` | metadata | Human-readable task description |

## Usage

### One-Command Pipeline

```bash
mkdir -p inbox
# Place your .csv file(s) in ./inbox/
python3 run_pipeline.py
```

This runs all phases and produces:
- `jobs.json` — Sanitized job records
- `lineage.json` — Table-level read/write lineage per job
- `dag_result.json` — DAG with execution tiers and edges
- `dag_graph.png` — Visual dependency graph
- `ANALYSIS_REPORT.md` — Full analysis report

### Individual Tools

```bash
# Phase 1: Ingest CSV
python3 skills/csv-batch-ingester/tools/ingest_csv.py ./inbox > jobs.json

# Phase 2: Parse SQL lineage
python3 skills/sql-column-lineage-parser/tools/parse_lineage.py jobs.json > lineage.json

# Phase 3: Build DAG
python3 skills/job-dependency-classifier/tools/classify_dependencies.py lineage.json jobs.json > dag_result.json

# Generate graph
python3 skills/job-dependency-classifier/tools/generate_graph.py dag_result.json jobs.json dag_graph.png

# Generate report
python3 skills/job-dependency-classifier/tools/generate_report.py jobs.json lineage.json dag_result.json ANALYSIS_REPORT.md
```

### Agent Usage

Ask the agent:
> "Please analyze the batch dependencies for the jobs in my inbox."

The **Master Orchestrator** will automatically invoke sub-skills in sequence.

## Circular Dependency Resolution

When multiple jobs read from and write to the same table, the classifier uses **step/time ordering** to break cycles:

- **Same job group:** Only create a dependency edge from lower-step → higher-step (respects sequential execution within a group)
- **Different job groups:** Only create a dependency edge from earlier `start_time` → later `start_time` (respects the batch scheduler order)

This reflects actual batch system behavior without losing real data dependencies.
