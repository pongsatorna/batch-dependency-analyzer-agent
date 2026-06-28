import sys
import json
from collections import Counter
from datetime import datetime


def generate_report(jobs_path="jobs.json", lineage_path="lineage.json", dag_path="dag_result.json", output="ANALYSIS_REPORT.md"):
    with open(jobs_path) as f:
        jobs_data = json.load(f)
    jobs = {j['jobid']: j for j in jobs_data['data']}

    with open(lineage_path) as f:
        lineage = json.load(f)['lineage']

    with open(dag_path) as f:
        dag = json.load(f)

    # Collect tables
    read_tables, write_tables = set(), set()
    for v in lineage.values():
        for r in v.get('reads', []):
            if r.get('table'): read_tables.add(r['table'])
        for w in v.get('writes', []):
            if w.get('table'): write_tables.add(w['table'])

    now = datetime.now().strftime("%Y-%m-%dT%H:%M")

    report = f"""# Batch Dependency Analysis Report

**Generated:** {now}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total jobs analyzed | {len(lineage)} |
| Dependency edges | {dag['summary']['total_edges']} |
| Execution tiers | {dag['summary']['total_tiers']} |
| Unique tables read | {len(read_tables)} |
| Unique tables written | {len(write_tables)} |

**Key Insight:** {len(dag['tiers'][0]['jobs'])}/{len(lineage)} jobs ({100*len(dag['tiers'][0]['jobs'])//len(lineage)}%) have zero dependencies (Tier 1). Longest critical path: {dag['summary']['total_tiers']} tiers.

---

## Jobs by Group

"""
    names = Counter(jobs[jid].get('job_name', 'unknown').strip() for jid in lineage)
    group_times = {}
    for j in jobs_data['data']:
        name = j.get('job_name', '').strip()
        if name not in group_times:
            group_times[name] = j['running time']

    report += "| Job Group | Tasks | Start Time |\n|-----------|-------|------------|\n"
    for name, count in sorted(names.items(), key=lambda x: group_times.get(x[0], '99:99')):
        report += f"| {name} | {count} | {group_times.get(name, '')} |\n"

    report += f"""
---

## SQL Lineage Summary

| Metric | Value |
|--------|-------|
| Jobs with reads | {sum(1 for v in lineage.values() if v.get('reads'))} |
| Jobs with writes | {sum(1 for v in lineage.values() if v.get('writes'))} |
| Jobs with both (dependency-forming) | {sum(1 for v in lineage.values() if v.get('reads') and v.get('writes'))} |

### Tables Written To

"""
    for t in sorted(write_tables):
        report += f"- `{t}`\n"

    report += "\n---\n\n## Execution Tiers\n\n"
    report += "| Tier | Jobs | Can Run In Parallel |\n|------|------|--------------------|\n"
    for tier in dag['tiers']:
        report += f"| Tier {tier['tier']} | {len(tier['jobs'])} | Yes |\n"

    report += "\n### Detailed Breakdown\n\n"
    for tier in dag['tiers']:
        report += f"#### Tier {tier['tier']} ({len(tier['jobs'])} jobs)\n\n"
        report += "| Job ID | Start Time | Job Group | Step | Description |\n"
        report += "|--------|-----------|-----------|------|-------------|\n"
        for jid in sorted(tier['jobs'], key=lambda x: (jobs[x]['running time'], jobs[x].get('job_name', ''), jobs[x].get('step', 0))):
            j = jobs[jid]
            report += f"| {jid} | {j['running time']} | {j.get('job_name', '').strip()} | {j.get('step', '')} | {j.get('description', '')} |\n"
        report += "\n"

    with open(output, 'w') as f:
        f.write(report)
    print(f"Saved: {output}")


if __name__ == "__main__":
    jobs_file = sys.argv[1] if len(sys.argv) > 1 else "jobs.json"
    lineage_file = sys.argv[2] if len(sys.argv) > 2 else "lineage.json"
    dag_file = sys.argv[3] if len(sys.argv) > 3 else "dag_result.json"
    out_file = sys.argv[4] if len(sys.argv) > 4 else "ANALYSIS_REPORT.md"
    generate_report(jobs_file, lineage_file, dag_file, out_file)
