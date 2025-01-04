import random

def build_semantic_matrix(nodes):
    """
    Build a symmetric similarity matrix (dictionary) for the given 'nodes'.
    We'll do a naive approach using categories deduced from node names.
    similarity[node1][node2] in [0,1].
    """
    similarity = {node: {} for node in nodes}

    def get_category(n):
        query_metrics = ["QueryTemplate"]
        result_metrics = ["ReturnedRows", "ReturnedBytes", "ResultCacheHit"]
        time_metrics = ["ExecTime", "CompileTime", "PlanTime", "LockWaitTime", "ElapsedTime"]
        structure_metrics = ["NumJoins", "NumTables", "NumColumns"]

        if n in query_metrics:
            return "query_metrics"
        elif n in result_metrics:
            return "result_metrics"
        elif n in time_metrics:
            return "time_metrics"
        elif n in structure_metrics:
            return "structure_metrics"
        else:
            return "other"


    # We'll pick random values in [0.8,1.0] if same category, else [0.0,0.6]
    node_list = list(nodes)
    for i in range(len(node_list)):
        for j in range(i, len(node_list)):
            ni = node_list[i]
            nj = node_list[j]
            if ni == nj:
                sim_val = 1.0
            else:
                if get_category(ni) == get_category(nj):
                    sim_val = random.uniform(0.8, 1.0)
                else:
                    sim_val = random.uniform(0.0, 0.6)
            similarity[ni][nj] = sim_val
            similarity[nj][ni] = sim_val
    return similarity

def cluster_by_similarity(similarity, threshold=0.7):
    """
    Very naive clustering: for each node, if it's above 'threshold' sim to an
    existing cluster's representative, it joins that cluster. Otherwise, start new.
    """
    clusters = []
    reps = []  # cluster representatives

    all_nodes = list(similarity.keys())
    for node in all_nodes:
        placed = False
        for idx, rep_node in enumerate(reps):
            if similarity[node][rep_node] >= threshold:
                clusters[idx].append(node)
                placed = True
                break
        if not placed:
            # create new cluster
            clusters.append([node])
            reps.append(node)
    return clusters

def assign_colors_to_clusters(clusters):
    """
    Assign each cluster a distinct base color, and if the cluster is large,
    vary the shade among them. Return dict: node -> color.
    """
    base_colors = [
        (0, 128, 0),   # green
        (255, 69, 0),  # orangeRed
        (30, 144, 255),# dodgerblue
        (128, 0, 128), # purple
        (220, 20, 60), # crimson
        (255, 215, 0), # gold
    ]
    color_map = {}
    for i, cluster_nodes in enumerate(clusters):
        base = base_colors[i % len(base_colors)]
        step = 30
        for idx2, node in enumerate(cluster_nodes):
            r = min(max(base[0] - step * idx2, 0), 255)
            g = min(max(base[1] - step * idx2, 0), 255)
            b = min(max(base[2] - step * idx2, 0), 255)
            color_map[node] = f"rgb({r},{g},{b})"
    return color_map

def colorize_nodes_by_similarity(nodes):
    """
    1) Build similarity
    2) Cluster by threshold
    3) Assign colors
    Returns: (similarity, clusters, color_map)
    """
    similarity = build_semantic_matrix(nodes)
    clusters = cluster_by_similarity(similarity, 0.7)
    color_map = assign_colors_to_clusters(clusters)
    return similarity, clusters, color_map
