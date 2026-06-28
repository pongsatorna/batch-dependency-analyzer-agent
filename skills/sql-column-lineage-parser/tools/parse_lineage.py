import sys
import json
import sqlglot
from sqlglot import exp


def parse_sql(sql_str):
    reads = []
    writes = []
    try:
        parsed = sqlglot.parse_one(sql_str, read='postgres', error_level=sqlglot.ErrorLevel.IGNORE)
    except Exception:
        return reads, writes

    # Determine statement type and extract write target
    if isinstance(parsed, exp.Delete):
        table_node = parsed.this
        if table_node and isinstance(table_node, exp.Table):
            writes.append({"table": table_node.name.lower(), "column": "*"})
    elif isinstance(parsed, exp.Update):
        table_node = parsed.this
        if table_node and isinstance(table_node, exp.Table):
            writes.append({"table": table_node.name.lower(), "column": "*"})
    elif isinstance(parsed, exp.Insert):
        table_node = parsed.this
        if table_node and isinstance(table_node, exp.Table):
            writes.append({"table": table_node.name.lower(), "column": "*"})

    # Extract all tables that are read (from subqueries, joins, where clauses)
    write_table_names = {w["table"] for w in writes}

    for table in parsed.find_all(exp.Table):
        tname = table.name.lower()
        if not tname or tname in ('dual', 'excluded'):
            continue
        # Skip the write target itself unless it appears in a subquery context
        if tname in write_table_names:
            # Check if this table ref is inside a subquery (then it's a read)
            parent = table.parent
            in_subquery = False
            while parent:
                if isinstance(parent, (exp.Subquery, exp.Exists)):
                    in_subquery = True
                    break
                parent = parent.parent
            if not in_subquery:
                continue
        reads.append({"table": tname, "column": "*"})

    # Deduplicate
    reads = [dict(t) for t in {tuple(d.items()) for d in reads}]
    writes = [dict(t) for t in {tuple(d.items()) for d in writes}]
    return reads, writes


def parse_lineage(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)

    jobs = data.get("data", [])
    result = {}

    for job in jobs:
        jobid = job.get("jobid")
        sql = job.get("sql statement", "")
        # Clean up \r\n
        sql = sql.replace('\r\n', '\n').replace('\r', '\n')
        reads, writes = parse_sql(sql)
        result[jobid] = {"reads": reads, "writes": writes}

    print(json.dumps({"status": "success", "lineage": result}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing input JSON file. Usage: python parse_lineage.py <file>"}))
        sys.exit(1)
    parse_lineage(sys.argv[1])
