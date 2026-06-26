import sys
import json
import networkx as nx
from collections import defaultdict

def build_dag_and_classify(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    lineage = data.get("lineage", {})
    
    # 1. Map what each job writes
    # writers_map[(table, column)] = [job_id1, job_id2]
    writers_map = defaultdict(list)
    for jobid, mapping in lineage.items():
        writes = mapping.get("writes", [])
        for w in writes:
            table = w.get("table")
            column = w.get("column", "*")
            writers_map[(table, column)].append(jobid)
            
    # 2. Build the graph
    G = nx.DiGraph()
    for jobid in lineage.keys():
        G.add_node(jobid)
        
    for jobid, mapping in lineage.items():
        reads = mapping.get("reads", [])
        for r in reads:
            table = r.get("table")
            column = r.get("column", "*")
            
            # Find jobs that write to this table/column combination
            # Note: in a real implementation, a write to "*" covers all columns,
            # and a read from "*" depends on writes to any column.
            # We will handle exact match and "*" wildcard match here.
            potential_writers = writers_map.get((table, column), [])
            potential_writers += writers_map.get((table, "*"), [])
            
            for writer in set(potential_writers):
                if writer != jobid:
                    # Job A (writer) -> Job B (reader). Job B depends on Job A.
                    G.add_edge(writer, jobid)
                    
    # 3. Detect cycles
    try:
        cycles = list(nx.find_cycle(G))
        if cycles:
            print(json.dumps({"status": "error", "message": "Circular dependency detected", "cycle": cycles}))
            sys.exit(1)
    except nx.NetworkXNoCycle:
        pass
        
    # 4. Group by tiers (Generations)
    # Tier 1 = no incoming edges (in-degree == 0)
    # Tier N = depends on max(Tier N-1)
    tiers = []
    
    # We will compute the longest path to each node from a virtual root
    longest_paths = {}
    for node in nx.topological_sort(G):
        max_dist = 0
        for predecessor in G.predecessors(node):
            max_dist = max(max_dist, longest_paths[predecessor] + 1)
        longest_paths[node] = max_dist
        
    # Group nodes by their max_dist
    tier_map = defaultdict(list)
    for node, dist in longest_paths.items():
        tier_map[dist].append(node)
        
    for dist in sorted(tier_map.keys()):
        tiers.append({
            "tier": dist + 1,
            "jobs": tier_map[dist]
        })
        
    print(json.dumps({
        "status": "success", 
        "tiers": tiers,
        "edges": list(G.edges())
    }, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing input JSON file. Usage: python classify_dependencies.py <lineage.json>"}))
        sys.exit(1)
        
    build_dag_and_classify(sys.argv[1])
