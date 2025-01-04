import networkx as nx
from networkx.drawing.nx_agraph import read_dot
import streamlit as st
import logging
import tempfile
import os
import numpy as np
import networkx as nx

logger = logging.getLogger(__name__)

def is_valid_dag(G: nx.DiGraph):
    """
    Check if the provided graph is a valid Directed Acyclic Graph (DAG).
    """
    is_dag = nx.is_directed_acyclic_graph(G)
    logger.debug(f"Graph validation result: {is_dag}")
    return is_dag

def load_dag_from_file(file):
    """
    Loads a DAG from a DOT file by saving it to a temporary file and passing 
    the file path to read_dot().
    """
    try:
        content = file.getvalue().decode("utf-8")
        logger.debug("Received DOT file content for parsing.")

        with tempfile.NamedTemporaryFile(delete=False, suffix='.dot') as tmp_file:
            tmp_file.write(content.encode('utf-8'))
            temp_filepath = tmp_file.name
            logger.debug(f"Temporary DOT file created at: {temp_filepath}")

        G = read_dot(temp_filepath)
        DG = nx.DiGraph(G)

        if not is_valid_dag(DG):
            st.warning("The uploaded graph is not a valid Directed Acyclic Graph (DAG). Visualization may not be accurate.")
            logger.warning("Uploaded graph is not a valid DAG.")
        else:
            logger.info("Uploaded graph is a valid DAG.")

        return DG

    except Exception as e:
        st.error(f"An error occurred while loading the DOT file: {e}")
        logger.exception("Exception occurred while loading DOT file: %s", e)
        return None

    finally:
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            logger.debug(f"Temporary DOT file {temp_filepath} deleted.")

def generate_dag_algorithm():
    """
    Generates a simple DAG as a placeholder.
    """
    logger.debug("Generating a placeholder DAG (no dataset).")
    G = nx.DiGraph()
    G.add_nodes_from(["A", "B", "C"])
    G.add_edges_from([("A", "B"), ("B", "C")])
    logger.info(f"Placeholder DAG generated with nodes: {list(G.nodes)} and edges: {list(G.edges)}")
    return G

def generate_dag_from_dataset(dataset_bytes):
    """
    Generate a DAG from the provided dataset (Not implemented yet).
    """
    logger.debug("Generating DAG from dataset (placeholder).")
    G = nx.DiGraph()
    G.add_nodes_from(["DatasetNode1", "DatasetNode2"])
    G.add_edge("DatasetNode1", "DatasetNode2")
    logger.info(f"DAG from dataset generated with nodes: {list(G.nodes)} and edges: {list(G.edges)}")
    return G

def to_pyvis_compatible(G: nx.DiGraph) -> nx.DiGraph:
    """
    Returns a new DiGraph that is guaranteed to have:
      1) String node IDs only
      2) No or minimal node/edge attributes with only string keys
    Thus PyVis can safely render it.
    """
    newG = nx.DiGraph()

    # 1) For each node in the old graph:
    for old_node, node_data in G.nodes(data=True):
        # Force the node ID to a string
        if isinstance(old_node, str):
            new_node_id = old_node
        else:
            new_node_id = ",\n".join(str(x) for x in old_node)  # or any logic you want

        # Optionally, keep a minimal set of node attributes
        # or omit them entirely if not needed
        new_node_data = {}
        for k, v in node_data.items():
            # only keep it if k is a str
            if isinstance(k, str):
                new_node_data[k] = v

        # Add the node to the new graph
        newG.add_node(new_node_id, **new_node_data)

    # 2) For each edge in the old graph:
    for u, v, edge_data in G.edges(data=True):
        # Convert u,v to the new node IDs
        if isinstance(u, str):
            new_u = u
        else:
            new_u = ",\n".join(str(x) for x in u)

        if isinstance(v, str):
            new_v = v
        else:
            new_v = ",\n".join(str(x) for x in v)

        # Optionally keep a minimal set of edge attributes
        new_edge_data = {}
        for k, val in edge_data.items():
            if isinstance(k, str):
                new_edge_data[k] = val

        # Add the edge to the new graph
        newG.add_edge(new_u, new_v, **new_edge_data)

    return newG

def fix_nested_keys_in_edge_attrs(G: nx.DiGraph) -> None:
    """
    Modifies G in-place by finding any nested dictionary
    inside edge attributes that has a non-string key,
    converting that key into a string.

    Example:
      edge_data["contraction"] = {('NodeX','NodeY'): {...}}  -->  edge_data["contraction"]["NodeX,NodeY"] = {...}
    """
    for (u, v, attr_dict) in G.edges(data=True):
        # We might have multiple layers of nested dicts.
        # We'll do a small recursion or repeated scanning to fix them.
        _fix_dict_recursively(attr_dict)

def _fix_dict_recursively(d: dict) -> None:
    """
    Recursively replace any non-string keys in dictionary d
    with a string. Modifies d in-place.
    """
    # We'll build up a list of replacements after iterating,
    # so we don't change dict size while iterating
    replacements = []

    for key, value in list(d.items()):
        if not isinstance(key, str):
            # Convert the key to a string
            if isinstance(key, tuple):
                new_key = ",\n".join(str(x) for x in key)
            else:
                new_key = str(key)

            replacements.append((key, new_key, value))

    # Actually perform the replacements
    for (old_key, new_key, old_value) in replacements:
        del d[old_key]
        d[new_key] = old_value

    # Now check if any values are themselves dictionaries and recurse
    for k, v in d.items():
        if isinstance(v, dict):
            _fix_dict_recursively(v)


def dict_of_dicts_to_numpy(similarity):
    # Get a stable, consistent ordering of the "outer" keys
    nodes = sorted(similarity.keys())
    n = len(nodes)
    
    # Initialize a 2D NumPy array
    array = np.zeros((n, n), dtype=float)
    
    # Fill the array
    for i, ni in enumerate(nodes):
        for j, nj in enumerate(nodes):
            array[i, j] = similarity[ni][nj]
    
    return array
