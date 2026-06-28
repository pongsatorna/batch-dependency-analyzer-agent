import sys
import json
import networkx as nx
from collections import defaultdict


def build_dag_and_classify(lineage_path: str, jobs_path: str = "jobs.json"):
    with open(lineage_path, 'r') as f:
        data = json.load(f)
    lineage = data.get("lineage", {})

    # Load job metadata for step ordering
    with open(jobs_path, 'r') as f:
        jobs_data = json.load(f)

    # Build job_id_group and step lookup: "37_659" -> (job_group=37, step=1, start_time)
    job_order = {}
    for job in jobs_data.get("data", []):
        jobid = job.get("jobid")
        parts = jobid.split("_", 1)
        job_group = parts[0]
        step = job.get("step", 0)
        start_time = job.get("running time", "99:99:99")
        job_order[jobid] = (job_group, int(step) if step else 0, start_time)

    # 1. Map writers
    writers_map = defaultdict(list)
    for jobid, mapping in lineage.items():
        for w in mapping.get("writes", []):
            writers_map[(w["table"], w.get("column", "*"))].append(jobid)

    # 2. Build graph with step-ordering constraint
    G = nx.DiGraph()
    for jobid in lineage:
        G.add_node(jobid)

    for jobid, mapping in lineage.items():
        for r in mapping.get("reads", []):
            table = r.get("table")
            column = r.get("column", "*")
            potential_writers = set(writers_map.get((table, column), []))
            potential_writers.update(writers_map.get((table, "*"), []))

            for writer in potential_writers:
                if writer == jobid:
                    continue

                # Option 1: Use step ordering to break ties
                writer_order = job_order.get(writer, ("", 0, "99:99:99"))
                reader_order = job_order.get(jobid, ("", 0, "99:99:99"))

                if writer_order[0] == reader_order[0]:
                    # Same job group: respect step order
                    if writer_order[1] < reader_order[1]:
                        G.add_edge(writer, jobid)
                else:
                    # Different job groups: respect start_time order
                    if writer_order[2] < reader_order[2]:
                        G.add_edge(writer, jobid)
                    elif writer_order[2] == reader_order[2]:
                        # Same start_time, use group id as tiebreaker
                        if writer_order[0] < reader_order[0]:
                            G.add_edge(writer, jobid)

    # 3. Detect remaining cycles
    try:
        cycle = nx.find_cycle(G)
        print(json.dumps({
            "status": "error",
            "message": "Circular dependency detected",
            "cycle": list(cycle)
        }))
        sys.exit(1)
    except nx.NetworkXNoCycle:
        pass

    # 4. Compute execution tiers
    longest_paths = {}
    for node in nx.topological_sort(G):
        max_dist = 0
        for predecessor in G.predecessors(node):
            max_dist = max(max_dist, longest_paths[predecessor] + 1)
        longest_paths[node] = max_dist

    tier_map = defaultdict(list)
    for node, dist in longest_paths.items():
        tier_map[dist].append(node)

    tiers = []
    for dist in sorted(tier_map.keys()):
        tiers.append({"tier": dist + 1, "jobs": tier_map[dist]})

    print(json.dumps({
        "status": "success",
        "tiers": tiers,
        "edges": list(G.edges()),
        "summary": {
            "total_jobs": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "total_tiers": len(tiers)
        }
    }, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python classify_dependencies.py <lineage.json> [jobs.json]"}))
        sys.exit(1)
    jobs_file = sys.argv[2] if len(sys.argv) > 2 else "jobs.json"
    build_dag_and_classify(sys.argv[1], jobs_file)
