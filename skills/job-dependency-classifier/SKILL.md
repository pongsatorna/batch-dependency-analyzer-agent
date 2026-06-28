---
name: job-dependency-classifier
description: Builds a Directed Acyclic Graph (DAG) of job dependencies based on column-level read/write lineages.
version: 1.0.0
---

# Execution Playbook: Job Dependency Classifier

As the Job Dependency Classifier, your goal is to mathematically resolve data lineage mappings into a Directed Acyclic Graph (DAG), detect circular dependencies, and output safe execution tiers.

## 1. Environmental Scan & Pre-flight Check
- Verify that the `lineage.json` file (produced by Phase 2) exists in the workspace.
- Verify that the required python package `networkx` is installed. If not, notify the Orchestrator or run `pip install -r requirements.txt`.

## 2. Deterministic Execution (Compute Tools)
- **Action**: Execute the python graph-building tool to calculate execution tiers.
- **Command**: `python scripts/classify_dependencies.py lineage.json`
- **Capture**: Read the JSON output produced by the script (you may save it to a file or read it directly into your context).

## 3. Validation & Assessment
- Check the output from the script.
- If the status is `error` and a `Circular dependency detected` message is present, immediately halt and present the cycle to the user.
- If successful, the output will contain an array of `tiers`. Each tier represents jobs that can be executed in parallel during that phase.

## 4. Final Handover
- The orchestration pipeline is now complete.
- Format the execution tiers into a clear, readable Markdown artifact (e.g., tables or Mermaid graph) for the user.
- Hand control back to the **Master Orchestrator** to signal the completion of the lifecycle.
