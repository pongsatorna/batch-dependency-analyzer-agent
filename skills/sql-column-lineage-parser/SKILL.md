---
name: sql-column-lineage-parser
description: Parses PostgreSQL statements to extract table-level read/write operations using AST analysis.
version: 2.0.0
---

# Execution Playbook: SQL Column Lineage Parser

As the SQL Column Lineage Parser, your goal is to deterministically parse raw SQL strings into explicit table-level data access mappings (Reads and Writes).

## 1. Environmental Scan & Pre-flight Check

- Verify that `jobs.json` (produced by Phase 1) exists in the workspace.
- Verify that the required python package `sqlglot` is installed. If not, run `pip install -r requirements.txt`.

## 2. SQL Statement Handling

The parser handles these DML statement types:
- **DELETE FROM table** → write to `table`, reads from subquery tables
- **UPDATE table SET ...** → write to `table`, reads from subquery/join tables
- **INSERT INTO table** → write to `table`, reads from source tables
- **SELECT** → reads only (no writes)

Self-referencing detection: If the write target also appears in a subquery, it is correctly classified as a read dependency.

## 3. Deterministic Execution

- **Command:** `python3 skills/sql-column-lineage-parser/tools/parse_lineage.py jobs.json > lineage.json`

## 4. Validation & Assessment

- Output must contain `"status": "success"` and a `lineage` dict mapping jobid → `{reads: [...], writes: [...]}`.
- Each read/write entry has `{"table": "name", "column": "*"}` (table-level granularity).
- Report: jobs with reads, jobs with writes, jobs with both, jobs with no lineage.

## 5. Final Handover

- Confirm `lineage.json` created successfully.
- Summarize any parse warnings or jobs with no detectable lineage.
- Hand control back to the **Master Orchestrator** for Phase 3.
