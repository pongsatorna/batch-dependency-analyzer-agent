---
name: sql-column-lineage-parser
description: Parses PostgreSQL statements to extract table and column-level read/write operations.
version: 1.0.0
---

# Execution Playbook: SQL Column Lineage Parser

As the SQL Column Lineage Parser, your goal is to deterministically parse raw SQL strings into explicit, column-level data access mappings (Reads and Writes).

## 1. Environmental Scan & Pre-flight Check
- Verify that the `jobs.json` file (produced by Phase 1) exists in the workspace.
- Verify that the required python package `sqlglot` is installed. If not, notify the Orchestrator or run `pip install -r requirements.txt`.

## 2. Deterministic Extraction (Compute Tools)
- **Action**: Execute the python parsing tool to evaluate the SQL ASTs.
- **Command**: `python scripts/parse_lineage.py jobs.json`
- **Redirection**: Save the standard output of this command to a file named `lineage.json` (e.g., `python scripts/parse_lineage.py jobs.json > lineage.json`).

## 3. Validation & Assessment
- Check the contents of `lineage.json`.
- It must contain a `status: "success"` key and a `lineage` dictionary mapping `jobid` to their `reads` and `writes`.
- If parsing failed for specific jobs, assess if the output is still viable or if it requires user intervention.

## 4. Final Handover
- Confirm that `lineage.json` has been successfully created.
- Summarize any complex queries or parse warnings.
- Hand control back to the **Master Orchestrator** to proceed to Phase 3 (Dependency Graph Classification).
