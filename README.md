# Batch Dependency Analyzer Plugin

This plugin provides a set of composable agent skills to analyze PostgreSQL batch jobs from CSV files and classify their data dependencies at the column level.

## Installation

You can install this plugin via the Gemini CLI (`agy cli`):

```bash
agy plugin install <this-github-repo-url>
```

## Skills

### 1. `csv-batch-ingester`
Reads, validates, and sanitizes batch job data from CSV files placed in the `./inbox/` directory.

**Usage:**
1. Create an `inbox` directory in your workspace: `mkdir inbox`.
2. Place your raw batch job `.csv` files into the `inbox` directory.
3. The agent will automatically trigger this skill when asked to process the batch jobs.

*More skills (like SQL lineage parsing and dependency classification) are planned for future phases.*
