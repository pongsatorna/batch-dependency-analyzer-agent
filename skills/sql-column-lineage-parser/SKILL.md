---
name: sql-column-lineage-parser
description: Parses PostgreSQL statements to extract table and column-level read/write operations.
---

# `sql-column-lineage-parser` Skill

## Description (Layer 1)
This skill analyzes PostgreSQL statements and extracts the exact table and column-level data lineage (reads and writes). It is the second step in the batch dependency analysis pipeline. Trigger this skill when you have a set of SQL statements (e.g., from `csv-batch-ingester`) and you need to determine their read/write data dependencies.

## Instructions (Layer 2)
When invoked:
1. Ensure the input data (a JSON list of jobs, containing `jobid` and `sql statement`) is available. You can write it to a temporary file like `jobs.json`.
2. Execute the `scripts/parse_lineage.py` tool, passing the path to the JSON file.
3. The script will parse the PostgreSQL statements using `sqlglot` and identify which columns and tables are being read (e.g., via `SELECT`) and written to (e.g., via `INSERT`/`UPDATE`).
4. The script will output a JSON mapping: `jobid -> { "reads": [{"table": "...", "column": "..."}], "writes": [{"table": "...", "column": "..."}] }`.
5. Capture this output to build the dependency graph in the next phase.

## Tools (Layer 3)
- Execute `python skills/sql-column-lineage-parser/scripts/parse_lineage.py <path/to/jobs.json>`.
- Make sure `sqlglot` is installed via `pip install -r requirements.txt`.
