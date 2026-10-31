"""Independent checks for the remaining graph algorithms and legacy wrappers."""
import itertools
import random
from collections import Counter

import networkx as nx
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import (
    euler_trace, hamilton_trace, matching_trace, tsp_trace, dag_trace, floyd_trace,
)


@pytest.mark.parametrize('name', ['eulerian_path', 'hamiltonian_path', 'bipartite_matching', 'tsp', 'dag_longest_path'])
@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
def test_all_levels_and_languages(name, language, difficulty):
    for seed in range(2):
        random.seed(seed)
        task = ALL_TASK_GENERATORS[name](language=language, difficulty=difficulty)
        assert len(task.solution_steps) == len(task.algorithm_trace) > 2
        assert task.verify(f'<answer>{task.final_answer}</answer>') == 1.0
        before = task.get_result()
        task.solve()
        assert task.get_result() == before
        if language == 'en':
            assert not any('\u0400' <= c <= '\u04ff' for c in '\n'.join(task.solution_steps))
        graph = nx.Graph()
        if name == 'bipartite_matching':
            left = [('L', v) for v in range(task.L)]
            graph.add_nodes_from(left, bipartite=0)
            graph.add_nodes_from([('R', v) for v in range(task.R)], bipartite=1)
            graph.add_edges_from((('L', a), ('R', b)) for a, b in task.pairs)
            assert int(task.final_answer) == len(nx.bipartite.maximum_matching(graph, top_nodes=left)) // 2
            pairs = task.algorithm_trace[-1]['matching']
            assert len({a for a, _ in pairs}) == len({b for _, b in pairs}) == len(pairs)
            assert all(tuple(pair) in task.pairs for pair in pairs)
        elif name == 'tsp':
            expected = min(sum(task.d[a][b] for a, b in zip((0,) + perm, perm + (0,)))
                           for perm in itertools.permutations(range(1, task.n)))
            assert int(task.final_answer) == expected
            event = task.algorithm_trace[-1]
            assert sorted(event['path'][:-1]) == list(range(task.n))
            assert event['path'][0] == event['path'][-1] == 0
            assert sum(event['weights']) == expected
            costs = {(1, 0): 0}
            for event in task.algorithm_trace:
                if event['event'] != 'transition':
                    continue
                assert event['cost'] == costs[event['mask'], event['vertex']]
                key = (event['new_mask'], event['neighbor'])
                assert event['old'] == costs.get(key)
                assert event['candidate'] == event['cost'] + task.d[event['vertex']][event['neighbor']]
                update = event['old'] is None or event['candidate'] < event['old']
                assert event['improved'] == int(update)
                if update:
                    costs[key] = event['candidate']
        elif name == 'dag_longest_path':
            graph = nx.DiGraph()
            graph.add_nodes_from(range(task.n))
            graph.add_weighted_edges_from(task.edges)
            assert int(task.final_answer) == nx.dag_longest_path_length(graph)
            path = task.algorithm_trace[-1]['path']
            assert sum(graph[a][b]['weight'] for a, b in zip(path, path[1:])) == int(task.final_answer)
        elif name == 'eulerian_path':
            graph.add_nodes_from(range(task.n))
            graph.add_edges_from(task.edges)
            assert task._answer == nx.has_eulerian_path(graph)
            if task._answer:
                path = task.algorithm_trace[-1]['path']
                assert Counter(tuple(sorted(edge)) for edge in zip(path, path[1:])) == Counter(tuple(sorted(edge)) for edge in task.edges)
        else:
            event = task.algorithm_trace[-1]
            if task._answer:
                assert sorted(event['path']) == list(range(task.n))
                allowed = {tuple(sorted(edge)) for edge in task.edges}
                assert all(tuple(sorted(edge)) in allowed for edge in zip(event['path'], event['path'][1:]))
            else:
                assert event['event'] == 'impossible'


def test_hamilton_and_euler_all_four_vertex_graphs():
    possible = list(itertools.combinations(range(4), 2))
    for mask in range(64):
        edges = [edge for i, edge in enumerate(possible) if mask & (1 << i)]
        allowed = {tuple(sorted(edge)) for edge in edges}
        expected = any(all(tuple(sorted((a, b))) in allowed for a, b in zip(path, path[1:]))
                       for path in itertools.permutations(range(4)))
        actual, trace = hamilton_trace(4, edges)
        assert actual == expected
        reachable = {(1 << v, v) for v in range(4)}
        for event in trace:
            if event['event'] == 'transition':
                assert (event['mask'], event['vertex']) in reachable
                assert not event['mask'] & (1 << event['neighbor'])
                key = event['new_mask'], event['neighbor']
                assert event['fresh'] == int(key not in reachable)
                reachable.add(key)
        actual, trace = euler_trace(4, edges)
        graph = nx.Graph(edges)
        expected = bool(edges) and nx.has_eulerian_path(graph)
        assert actual == expected


def test_matching_all_two_by_three_graphs_and_reassignment():
    possible = list(itertools.product(range(2), range(3)))
    for mask in range(64):
        edges = [edge for i, edge in enumerate(possible) if mask & (1 << i)]
        value, trace = matching_trace(2, 3, edges)
        # Independent enumeration of injective partial assignments.
        expected = max(sum(r != -1 for r in assignment) for assignment in itertools.product(range(-1, 3), repeat=2)
                       if len([r for r in assignment if r != -1]) == len(set(r for r in assignment if r != -1))
                       and all(r == -1 or (l, r) in edges for l, r in enumerate(assignment)))
        assert value == expected
    value, trace = matching_trace(2, 2, [(0, 0), (0, 1), (1, 0)])
    assert value == 2
    assert any(e['event'] == 'augment' and len(e['assignments']) == 2 for e in trace)


@pytest.mark.parametrize('name,subtypes', [
    ('graph_reasoning', ['shortest_path', 'num_components', 'is_bipartite']),
    ('floyd_distance', ['sum', 'diameter']),
    ('graph', ['shortest_path', 'minimum_spanning_tree', 'diameter', 'clustering_coefficient']),
    ('graph_justification', ['shortest_path', 'mst', 'max_flow']),
])
@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
def test_auxiliary_graph_tasks(name, subtypes, language, difficulty):
    for subtype in subtypes:
        random.seed(17)
        kw = {'subtype': subtype} if name == 'graph_reasoning' else {'task_type': subtype}
        task = ALL_TASK_GENERATORS[name](language=language, difficulty=difficulty, **kw)
        result = task.get_result()
        assert len(result['algorithm_trace']) == len(result['solution_steps']) > 2
        task.solve()
        assert task.get_result() == result
        if name == 'floyd_distance':
            graph = nx.DiGraph()
            graph.add_nodes_from(range(task.n))
            for a, b, weight in task.edges:
                if not graph.has_edge(a, b) or weight < graph[a][b]['weight']:
                    graph.add_edge(a, b, weight=weight)
            distances = dict(nx.all_pairs_dijkstra_path_length(graph))
            finite = [distances[a][b] for a in range(task.n) for b in range(task.n) if a != b]
            assert task.total == sum(finite) and task.diameter == max(finite)
        if name == 'graph':
            assert str(task.edges) in task.description
            if subtype == 'diameter':
                assert int(task.final_answer) == nx.diameter(task.graph)
            elif subtype == 'clustering_coefficient':
                assert float(task.final_answer) == pytest.approx(nx.average_clustering(task.graph))
        if language == 'en':
            assert not any('\u0400' <= c <= '\u04ff' for c in '\n'.join(task.solution_steps))


def test_legacy_graph_keeps_isolates_and_handles_zero_edge_probability():
    from re_rl.tasks.math.discrete.graph.task import GraphTask
    task = GraphTask(task_type='shortest_path', num_nodes=4, edge_prob=0)
    task.solve()
    assert task.graph.number_of_nodes() == 4
    assert nx.is_connected(task.graph)


@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
@pytest.mark.parametrize('name,subtypes', [
    ('graph_connectivity', ['scc', 'articulation_points', 'bridges', 'negative_cycle']),
    ('tree_queries', ['diameter', 'height', 'leaves', 'lca']),
    ('tree_mis', ['size']), ('tree_times', ['enter', 'size']),
    ('tree_radius', ['radius', 'eccentricity']), ('spanning_trees', ['count']),
    ('havel_hakimi', ['graphic']), ('minimax_tree', ['value', 'action']),
])
def test_structural_algorithms(name, subtypes, language, difficulty):
    for subtype in subtypes:
        random.seed(3)
        task = ALL_TASK_GENERATORS[name](task_type=subtype, language=language, difficulty=difficulty)
        assert len(task.solution_steps) >= len(task.algorithm_trace) > 2
        assert task.verify(f'<answer>{task.final_answer}</answer>') == 1
        assert task.get_result()['graph']
        if language == 'en':
            assert not any('\u0400' <= c <= '\u04ff' for c in '\n'.join(task.solution_steps))
        if name == 'graph_connectivity':
            graph = nx.DiGraph() if task.directed else nx.Graph()
            graph.add_nodes_from(range(task.n))
            if subtype == 'negative_cycle':
                graph.add_weighted_edges_from(task.wedges)
                assert task.answer == nx.negative_edge_cycle(graph)
                if task.answer:
                    path = task.algorithm_trace[-1]['path']
                    assert path[0] == path[-1]
                    assert sum(graph[a][b]['weight'] for a, b in zip(path, path[1:])) < 0
            else:
                graph.add_edges_from(task.edges)
                if subtype == 'scc': expected = nx.number_strongly_connected_components(graph)
                elif subtype == 'bridges': expected = len(list(nx.bridges(graph)))
                else: expected = len(list(nx.articulation_points(graph)))
                assert task.answer == expected
        elif name == 'tree_queries':
            graph = nx.Graph(task.edges)
            if subtype == 'diameter': expected = nx.diameter(graph)
            elif subtype == 'height': expected = max(nx.single_source_shortest_path_length(graph, 1).values())
            elif subtype == 'leaves': expected = sum(d == 1 for _, d in graph.degree())
            else:
                rooted = nx.bfs_tree(graph, 1)
                expected = nx.lowest_common_ancestor(rooted, task.a, task.b)
            assert task.answer == expected
        elif name == 'tree_radius':
            graph = nx.Graph(task.edges)
            assert task.radius == nx.radius(graph)
            assert task.ecc[task.vertex] == nx.eccentricity(graph, task.vertex)
        elif name == 'tree_mis':
            chosen = task.algorithm_trace[-1]['chosen']
            assert len(chosen) == task.answer
            assert all(not (a in chosen and b in chosen) for a, b in task.edges)
            graph = nx.Graph(task.edges)
            left = {v for v, c in nx.bipartite.color(graph).items() if c == 0}
            matching = nx.bipartite.maximum_matching(graph, left)
            assert task.answer == task.n - len(matching) // 2
        elif name == 'havel_hakimi':
            assert task.graphic == nx.is_graphical(task.seq)
        elif name == 'minimax_tree':
            minima = [min(branch) for branch in task.branches]
            assert task.value == max(minima)
            assert task.choice == minima.index(max(minima)) + 1
        elif name == 'spanning_trees':
            import sympy
            graph = nx.Graph()
            graph.add_nodes_from(range(task.n)); graph.add_edges_from(task.edges)
            lap = nx.laplacian_matrix(graph).toarray().tolist()
            assert task.answer == sympy.Matrix([r[:-1] for r in lap[:-1]]).det()
        else:
            # Entry times form a permutation; subtree sizes equal descendants + 1.
            rooted = nx.DiGraph((task.parents[v], v) for v in range(2, task.n + 1))
            assert sorted(task.enter[1:]) == list(range(1, task.n + 1))
            for v in range(1, task.n + 1):
                assert task.sizes[v] == len(nx.descendants(rooted, v)) + 1


@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
@pytest.mark.parametrize('name', ['triangle_girth', 'wiener_index', 'dag_paths', 'shortest_path_count', 'prufer_code', 'expectimax', 'deadlock'])
def test_additional_graph_families(name, language, difficulty):
    from re_rl.tasks.registry import registry
    for subtype in registry[name].TASK_TYPES:
        random.seed(4)
        task = ALL_TASK_GENERATORS[name](task_type=subtype, language=language, difficulty=difficulty)
        task.solve()
        assert len(task.solution_steps) >= len(task.algorithm_trace) > 2
        assert task.verify(f'<answer>{task.final_answer}</answer>') == 1
        graph = nx.DiGraph() if name in ('dag_paths', 'deadlock') else nx.Graph()
        if hasattr(task, 'n'):
            graph.add_nodes_from(range(task.n) if name == 'deadlock' else range(1, task.n + 1))
            graph.add_edges_from(task.edges)
        if name == 'triangle_girth':
            assert task.triangles == sum(nx.triangles(graph).values()) // 3
            cycles = list(nx.simple_cycles(graph))
            assert task.girth == min(map(len, cycles), default=0)
        elif name == 'wiener_index':
            assert task.answer == nx.wiener_index(graph)
        elif name == 'dag_paths':
            assert task.answer == len(list(nx.all_simple_paths(graph, 1, task.n)))
        elif name == 'shortest_path_count':
            assert task.path_count == len(list(nx.all_shortest_paths(graph, task.source, task.target)))
            assert task.level == sum(d == task.k for d in nx.single_source_shortest_path_length(graph, 1).values())
        elif name == 'prufer_code':
            zero = nx.relabel_nodes(graph, {v: v - 1 for v in graph})
            assert task.code == [v + 1 for v in nx.to_prufer_sequence(zero)]
        elif name == 'expectimax':
            expectations = [sum(prob * value for prob, value in outcomes) for outcomes in task.actions]
            assert task.value == max(expectations)
            assert task.choice == expectations.index(max(expectations)) + 1
        else:
            expected = set()
            for group in nx.strongly_connected_components(graph):
                if len(group) > 1 or any(graph.has_edge(v, v) for v in group): expected.update(group)
            assert task.on_cycle == expected
        if language == 'en':
            assert not any('\u0400' <= c <= '\u04ff' for c in '\n'.join(task.solution_steps))


def test_trace_coverage_contract_and_json_safe_inputs():
    import json
    from re_rl.tasks.math.logic.graph_algorithms_shared.coverage import TRACED_GRAPH_TASKS
    for name in TRACED_GRAPH_TASKS:
        random.seed(9)
        task = ALL_TASK_GENERATORS[name](language='en', difficulty=3)
        result = task.get_result()
        assert result['algorithm_trace'] and result['graph']
        assert result['task_type'] == name
        json.dumps(result)
        task.solve()
        assert task.get_result() == result


def test_distance_labels_and_nested_vertex_offsets():
    from re_rl.tasks.math.logic.graph_algorithms_shared.render_trace import render_trace
    event = dict(event='done', distances=[0, 1, 2], ways=[1, 1, 1])
    rendered = render_trace([event], 'counts', 'en')[0]
    assert '1:0, 2:1, 3:2' in rendered
    event = dict(event='distance', source=0, target=2, path=[0, 1, 2], answer=2,
                 algorithm='walk', vertex_offset=1)
    assert '1 → 2 → 3' in render_trace([event], 'query', 'en')[0]
    assert event['path'] == [0, 1, 2]
