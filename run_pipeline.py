#!/usr/bin/env python3
"""
Batch Dependency Analyzer - Full Pipeline Runner

Usage:
    python run_pipeline.py [inbox_dir]

Runs all 3 phases sequentially:
  Phase 1: Ingest CSV from inbox/ -> jobs.json
  Phase 2: Parse SQL lineage -> lineage.json
  Phase 3: Build DAG + execution tiers -> dag_result.json
  + Generate graph (dag_graph.png) and report (ANALYSIS_REPORT.md)
"""
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(SCRIPT_DIR, "skills")


def run(cmd, output_file=None):
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stdout}{result.stderr}")
        sys.exit(1)
    if output_file:
        with open(output_file, 'w') as f:
            f.write(result.stdout)
    return result.stdout


def main():
    inbox = sys.argv[1] if len(sys.argv) > 1 else "./inbox"
    os.chdir(SCRIPT_DIR)

    print("=" * 60)
    print("BATCH DEPENDENCY ANALYZER - FULL PIPELINE")
    print("=" * 60)

    # Phase 1
    print("\n[Phase 1] Ingesting CSV...")
    run(["python3", f"{SKILLS_DIR}/csv-batch-ingester/tools/ingest_csv.py", inbox], "jobs.json")
    print("  ✓ jobs.json created")

    # Phase 2
    print("\n[Phase 2] Parsing SQL lineage...")
    run(["python3", f"{SKILLS_DIR}/sql-column-lineage-parser/tools/parse_lineage.py", "jobs.json"], "lineage.json")
    print("  ✓ lineage.json created")

    # Phase 3
    print("\n[Phase 3] Building dependency DAG...")
    run(["python3", f"{SKILLS_DIR}/job-dependency-classifier/tools/classify_dependencies.py", "lineage.json", "jobs.json"], "dag_result.json")
    print("  ✓ dag_result.json created")

    # Generate graph
    print("\n[Graph] Generating visualization...")
    run(["python3", f"{SKILLS_DIR}/job-dependency-classifier/tools/generate_graph.py", "dag_result.json", "jobs.json", "dag_graph.png"])
    print("  ✓ dag_graph.png created")

    # Generate report
    print("\n[Report] Generating analysis report...")
    run(["python3", f"{SKILLS_DIR}/job-dependency-classifier/tools/generate_report.py", "jobs.json", "lineage.json", "dag_result.json", "ANALYSIS_REPORT.md"])
    print("  ✓ ANALYSIS_REPORT.md created")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print("\nOutputs:")
    print("  jobs.json           - Ingested job data")
    print("  lineage.json        - SQL read/write lineage")
    print("  dag_result.json     - DAG with tiers and edges")
    print("  dag_graph.png       - Visual graph")
    print("  ANALYSIS_REPORT.md  - Full analysis report")


if __name__ == "__main__":
    main()
