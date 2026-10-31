"""Explicit scope of graph algorithm traces, exercised by regression tests."""
TRACED_GRAPH_TASKS = (
    'weighted_shortest_path', 'mst_weight', 'topological_sort', 'graph_coloring',
    'max_flow', 'eulerian_path', 'hamiltonian_path', 'bipartite_matching', 'tsp',
    'dag_longest_path', 'graph_reasoning', 'floyd_distance', 'graph', 'graph_justification',
    'graph_connectivity', 'tree_queries', 'tree_mis', 'tree_radius', 'tree_times',
    'spanning_trees', 'havel_hakimi', 'minimax_tree', 'triangle_girth', 'wiener_index',
    'dag_paths', 'shortest_path_count', 'prufer_code', 'expectimax', 'deadlock',
)
TRACED_VISUAL_GRAPH_TASKS = (
    'shortest_path_image', 'mst_image', 'topological_sort_image',
    'graph_coloring_image', 'max_flow_image',
)
