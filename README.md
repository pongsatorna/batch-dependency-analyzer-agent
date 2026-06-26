# Batch Dependency Analyzer Plugin

This plugin provides a set of composable agent skills to analyze PostgreSQL batch jobs from CSV files and classify their data dependencies at the column level.

## Installation

You can install this plugin via the Gemini CLI (`agy cli`):

```bash
agy plugin install <this-github-repo-url>
```

## Skills

### 1. `csv-batch-ingester`
Reads, validates, and sanitizes batch job data from `Check-In-Batch-Job.csv`.

**Usage:**
The agent will automatically trigger this skill when asked to process the batch job CSV file.

*More skills (like SQL lineage parsing and dependency classification) are planned for future phases.*
