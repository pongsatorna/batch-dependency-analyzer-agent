# Batch Dependency Analyzer Agent

This plugin provides a deterministic end-to-end suite for analyzing PostgreSQL batch jobs from CSV files, parsing their SQL to extract column-level reads/writes, and building a Directed Acyclic Graph (DAG) to classify data dependencies.

## Architecture

This plugin follows the **Master Orchestrator / Playbook** framework. It consists of one orchestrator skill and three execution sub-skills.

### Master Orchestrator
- **`batch-dependency-orchestrator`**: The entry point for the agent. It manages the entire lifecycle, ensuring strict deterministic execution by gating each phase until required outputs are produced.

### Sub-Skills
1. **`csv-batch-ingester`**: Scans the `./inbox/` directory for `.csv` files, validates them, and sanitizes the data into a clean JSON structure (`jobs.json`).
2. **`sql-column-lineage-parser`**: Parses the SQL AST using `sqlglot` to map column-level reads and writes for each job (`lineage.json`).
3. **`job-dependency-classifier`**: Uses `networkx` to mathematically resolve data lineage into a DAG, detecting circular dependencies and calculating parallel execution tiers.

## Installation

You can install this plugin via the Gemini CLI (`agy cli`):

```bash
agy plugin install https://github.com/pongsatorna/batch-dependency-analyzer-agent.git
```

## Usage

1. Initialize an agent in your workspace.
2. Create an `inbox` directory at the root of your workspace: 
   ```bash
   mkdir inbox
   ```
3. Place your raw batch job `.csv` files into the `inbox` directory.
4. Ask the agent to analyze your batch jobs:
   > "Please analyze the batch dependencies for the jobs in my inbox."
5. The **Master Orchestrator** will automatically take over, invoking the necessary sub-skills in sequence.
