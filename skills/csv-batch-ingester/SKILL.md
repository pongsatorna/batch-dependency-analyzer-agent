---
name: csv-batch-ingester
description: Ingests and sanitizes batch job data from batch_jobs.csv.
version: 1.0.0
---

# Execution Playbook: CSV Batch Ingester

As the CSV Batch Ingester, your goal is to deterministically read, validate, and sanitize the raw `batch_jobs.csv` file into a clean JSON structure that downstream skills can consume.

## 1. Environmental Scan & Pre-flight Check
- Verify that `batch_jobs.csv` exists in the workspace.
- Verify that the required python package `pandas` is installed. If not, notify the Orchestrator or run `pip install -r requirements.txt`.

## 2. Deterministic Extraction (Compute Tools)
- **Action**: Execute the python extraction tool to parse the CSV.
- **Command**: `python scripts/ingest_csv.py`
  - *Note: If the file is located elsewhere, pass the path: `python scripts/ingest_csv.py <path/to/batch_jobs.csv>`*
- **Redirection**: Save the standard output of this command to a file named `jobs.json` (e.g., `python scripts/ingest_csv.py > jobs.json`).

## 3. Validation & Assessment
- Check the contents of `jobs.json`.
- It must contain a `status: "success"` key and an array of job records under `data`.
- If the script outputs an error (e.g., missing columns), halt the process and report the exact error to the user.

## 4. Final Handover
- Confirm that `jobs.json` has been successfully created.
- Summarize the number of batch jobs successfully ingested.
- Hand control back to the **Master Orchestrator** to proceed to Phase 2 (Lineage Parsing).
