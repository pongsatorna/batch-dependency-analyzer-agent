---
name: csv-batch-ingester
description: Reads, validates, and sanitizes batch job data from Check-In-Batch-Job.csv.
---

# `csv-batch-ingester` Skill

## Description (Layer 1)
This skill handles the ingestion of batch job data from a CSV file. It is the first step in the batch dependency analysis pipeline. Trigger this skill when the user asks to process `Check-In-Batch-Job.csv` or when you need to ingest the raw batch job data for downstream analysis.

## Instructions (Layer 2)
When invoked:
1. Validate that `Check-In-Batch-Job.csv` exists in the workspace.
2. Execute the `scripts/ingest_csv.py` tool.
3. The script will read the file, validate that `running time`, `jobid`, and `sql statement` columns exist, and sanitize the data.
4. The script will output a clean JSON array representing the batch jobs.
5. Capture this JSON output and hold it in your context (or pass it to the next agent skill like `sql-column-lineage-parser`).

## Tools (Layer 3)
- Execute `python skills/csv-batch-ingester/scripts/ingest_csv.py` (assuming the current working directory is the workspace root).
- If the file is named differently, pass the file path as an argument: `python skills/csv-batch-ingester/scripts/ingest_csv.py <path/to/csv>`.
