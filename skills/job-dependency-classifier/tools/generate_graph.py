import sys
import json
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import defaultdict


def generate_graph(dag_path="dag_result.json", jobs_path="jobs.json", output="dag_graph.png"):
    with open(dag_path) as f:
        dag = json.load(f)
    with open(jobs_path) as f:
        jobs = {j['jobid']: j for j in json.load(f)['data']}

    G = nx.DiGraph()
    G.add_edges_from(dag['edges'])
    for tier in dag['tiers']:
        for j in tier['jobs']:
            G.add_node(j)

    # Position by tier
    tier_groups = defaultdict(list)
    for tier in dag['tiers']:
        for j in tier['jobs']:
            tier_groups[tier['tier']].append(j)

    pos = {}
    for t, nodes in tier_groups.items():
        for i, node in enumerate(sorted(nodes)):
            pos[node] = (i - len(nodes) / 2, -t)

    # Color by job group
    groups = sorted(set(jobs[j].get('job_name', '').strip() for j in G.nodes() if j in jobs))
    cmap = matplotlib.colormaps['tab20']
    color_map_src = {g: cmap(i / max(len(groups), 1)) for i, g in enumerate(groups)}
    colors = [color_map_src.get(jobs[n].get('job_name', '').strip(), 'gray') if n in jobs else 'gray' for n in G.nodes()]

    fig, ax = plt.subplots(1, 1, figsize=(40, 20))
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=150, font_size=4,
            node_color=colors, edge_color='#cccccc', arrows=True, arrowsize=5, width=0.3)
    ax.set_title(f'Batch Job Dependency DAG ({len(dag["tiers"])} Tiers)', fontsize=16)

    legend_elements = [Patch(facecolor=color_map_src[g], label=g) for g in groups[:20]]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7, ncol=2)

    plt.tight_layout()
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Saved: {output}")


if __name__ == "__main__":
    dag_file = sys.argv[1] if len(sys.argv) > 1 else "dag_result.json"
    jobs_file = sys.argv[2] if len(sys.argv) > 2 else "jobs.json"
    out_file = sys.argv[3] if len(sys.argv) > 3 else "dag_graph.png"
    generate_graph(dag_file, jobs_file, out_file)
