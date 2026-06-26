---
name: job-dependency-classifier
description: Builds a Directed Acyclic Graph (DAG) of job dependencies based on column-level read/write lineages.
---

# `job-dependency-classifier` Skill

## Description (Layer 1)
This skill constructs a dependency graph (DAG) to determine the exact execution order of batch jobs. It is the final step in the batch dependency analysis pipeline. Trigger this skill when you have extracted the data lineages (reads and writes) from the `sql-column-lineage-parser` and need to resolve which jobs depend on which.

## Instructions (Layer 2)
When invoked:
1. Ensure you have the lineage JSON output from the parser (e.g., in a file `lineage.json`).
2. Execute the `scripts/classify_dependencies.py` tool.
3. The script will use `networkx` to build a DAG:
   - For every Job A that writes to `Table X` / `Column Y`.
   - If Job B reads from `Table X` / `Column Y`.
   - Job B depends on Job A (Edge: A -> B).
4. The script will output execution tiers (e.g., Tier 1 can run immediately, Tier 2 depends on Tier 1).
5. Present this final execution graph and tier list to the user as a Markdown artifact or standard output.

## Tools (Layer 3)
- Execute `python skills/job-dependency-classifier/scripts/classify_dependencies.py <path/to/lineage.json>`.
- Make sure `networkx` is installed via `pip install -r requirements.txt`.
