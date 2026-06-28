---
name: csv-batch-ingester
description: Ingests and sanitizes batch job data from CSV files. Supports multiple column formats with auto-mapping.
version: 2.0.0
---

# Execution Playbook: CSV Batch Ingester

As the CSV Batch Ingester, your goal is to deterministically read, validate, and sanitize raw CSV files into a clean JSON structure that downstream skills can consume.

## 1. Environmental Scan & Pre-flight Check

- Verify that the `./inbox/` directory exists and contains at least one `.csv` file.
- Verify that the required python package `pandas` is installed. If not, run `pip install -r requirements.txt`.

## 2. Column Format Detection

The tool auto-detects and maps columns:

**Format A (direct):** `running time`, `jobid`, `sql statement`

**Format B (Check-In Batch Job):**
- `start_time` → `running time`
- `task_id` → `jobid` (combined as `{job_id}_{task_id}`)
- `command` → `sql statement`
- `action` → filter: only `EXECUTE_SQL` rows kept
- `is_enable` → filter: only `Y` rows kept
- `step`, `job_name`, `description` → preserved as metadata

## 3. Deterministic Execution

- **Command:** `python3 skills/csv-batch-ingester/tools/ingest_csv.py ./inbox > jobs.json`

## 4. Validation & Assessment

- Output must contain `"status": "success"` and a `data` array.
- Each record has at minimum: `running time`, `jobid`, `sql statement`.
- Report total records ingested and any rows filtered out.

## 5. Final Handover

- Confirm `jobs.json` created successfully.
- Summarize: total jobs, job groups found, any filtering applied.
- Hand control back to the **Master Orchestrator** for Phase 2.
