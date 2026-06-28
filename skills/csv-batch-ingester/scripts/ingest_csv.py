import sys
import json
import pandas as pd
from pathlib import Path

def ingest_csv(file_path: str):
    path = Path(file_path)
    if not path.is_file():
        print(json.dumps({"error": f"File not found: {file_path}"}))
        sys.exit(1)

    try:
        # We assume comma separated, but handle potential issues gracefully
        df = pd.read_csv(path)
        
        # Standardize column names (lowercase, strip whitespace)
        df.columns = [c.strip().lower() for c in df.columns]
        
        required_cols = {"running time", "jobid", "sql statement"}
        missing = required_cols - set(df.columns)
        if missing:
            print(json.dumps({"error": f"Missing required columns: {', '.join(missing)}"}))
            sys.exit(1)
            
        # Sanitize data
        df['running time'] = df['running time'].astype(str).str.strip()
        df['jobid'] = df['jobid'].astype(str).str.strip()
        df['sql statement'] = df['sql statement'].astype(str).str.strip()
        
        # Drop rows where jobid or sql statement is empty/nan
        df = df.dropna(subset=['jobid', 'sql statement'])
        df = df[df['jobid'] != 'nan']
        df = df[df['sql statement'] != 'nan']

        # Output as clean JSON
        records = df.to_dict(orient='records')
        print(json.dumps({"status": "success", "data": records}, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    target_file = "batch_jobs.csv"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    ingest_csv(target_file)
