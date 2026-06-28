import sys
import json
import pandas as pd
from pathlib import Path

def ingest_csv_directory(directory_path: str):
    path = Path(directory_path)
    if not path.is_dir():
        print(json.dumps({"error": f"Directory not found: {directory_path}"}))
        sys.exit(1)
        
    csv_files = list(path.glob("*.csv"))
    if not csv_files:
        print(json.dumps({"error": f"No .csv files found in directory: {directory_path}"}))
        sys.exit(1)

    all_records = []
    
    try:
        for file_path in csv_files:
            # We assume comma separated, but handle potential issues gracefully
            df = pd.read_csv(file_path)
            
            # Standardize column names (lowercase, strip whitespace)
            df.columns = [c.strip().lower() for c in df.columns]
            
            required_cols = {"running time", "jobid", "sql statement"}
            missing = required_cols - set(df.columns)
            if missing:
                print(json.dumps({"error": f"Missing required columns in {file_path.name}: {', '.join(missing)}"}))
                sys.exit(1)
                
            # Sanitize data
            df['running time'] = df['running time'].astype(str).str.strip()
            df['jobid'] = df['jobid'].astype(str).str.strip()
            df['sql statement'] = df['sql statement'].astype(str).str.strip()
            
            # Drop rows where jobid or sql statement is empty/nan
            df = df.dropna(subset=['jobid', 'sql statement'])
            df = df[df['jobid'] != 'nan']
            df = df[df['sql statement'] != 'nan']
            
            records = df.to_dict(orient='records')
            all_records.extend(records)

        # Output as clean JSON
        print(json.dumps({"status": "success", "data": all_records}, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    target_dir = "./inbox"
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    
    ingest_csv_directory(target_dir)
