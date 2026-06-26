import sys
import json
import sqlglot
from sqlglot import exp

def parse_sql(sql_str):
    reads = []
    writes = []
    
    try:
        # Parse the SQL using postgres dialect
        parsed = sqlglot.parse_one(sql_str, read='postgres')
    except Exception as e:
        # If parsing fails, return empty lists or log error
        return reads, writes

    # Naive extraction strategy (this can be expanded for complex queries)
    # Extract tables being read
    for table in parsed.find_all(exp.Table):
        # We need to determine if this is a read or write context
        # For simplicity in this demo, let's look at all columns used
        pass

    # Extract all columns
    for column in parsed.find_all(exp.Column):
        col_name = column.name
        table_name = column.table
        
        # Check if this column is part of a SELECT (read) or INSERT/UPDATE (write)
        # This is a basic heuristic. A robust implementation would walk the AST 
        # and check the parent nodes (e.g., isinstance(parent, exp.Select)).
        # For this skeleton, we will just classify them all as reads unless they are in an update/insert.
        reads.append({"table": table_name, "column": col_name})

    # In a real implementation, we would segregate writes by finding exp.Insert and exp.Update nodes
    for insert in parsed.find_all(exp.Insert):
        if insert.this:
            table_name = insert.this.name
            writes.append({"table": table_name, "column": "*"})

    # Deduplicate
    reads = [dict(t) for t in {tuple(d.items()) for d in reads if d.get("column")}]
    writes = [dict(t) for t in {tuple(d.items()) for d in writes if d.get("column")}]

    return reads, writes

def parse_lineage(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    jobs = data.get("data", [])
    result = {}
    
    for job in jobs:
        jobid = job.get("jobid")
        sql = job.get("sql statement", "")
        
        reads, writes = parse_sql(sql)
        result[jobid] = {
            "reads": reads,
            "writes": writes
        }
        
    print(json.dumps({"status": "success", "lineage": result}, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing input JSON file. Usage: python parse_lineage.py <jobs.json>"}))
        sys.exit(1)
        
    parse_lineage(sys.argv[1])
