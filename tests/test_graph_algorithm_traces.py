"""Check graph traces against independent oracles and replay their state changes."""
import itertools
import json
import random

import networkx as nx
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.math.logic.graph_algorithms_shared.traces import (
    coloring_trace, dijkstra_trace, flow_trace, kahn_trace, kruskal_trace,
)

PAIRS = [
    ('weighted_shortest_path', 'shortest_path_image'),
    ('mst_weight', 'mst_image'),
    ('topological_sort', 'topological_sort_image'),
    ('graph_coloring', 'graph_coloring_image'),
    ('max_flow', 'max_flow_image'),
]


@pytest.mark.parametrize('pair', PAIRS)
@pytest.mark.parametrize('language', ['ru', 'en'])
@pytest.mark.parametrize('difficulty', range(1, 11))
def test_generated_graph_traces(pair, language, difficulty):
    for seed in range(3):
        for name in pair:
            random.seed(seed)
            generators = ALL_VISUAL_TASK_GENERATORS if name.endswith('_image') else ALL_TASK_GENERATORS
            task = generators[name](language=language, difficulty=difficulty)
            trace = task.algorithm_trace
            assert len(trace) == len(task.solution_steps) > 2
            assert task.verify(f'<answer>{task.final_answer}</answer>') == 1.0
            assert task.get_result()['algorithm_trace'] == trace
            json.dumps(trace)
            if language == 'en':
                assert not any('\u0400' <= char <= '\u04ff' for char in '\n'.join(task.solution_steps))
            graph = (nx.DiGraph if pair[0] in ('max_flow', 'topological_sort') else nx.Graph)()
            graph.add_nodes_from(range(task.n))
            if pair[0] == 'weighted_shortest_path':
                graph.add_weighted_edges_from(task.edges)
                assert len(task.edges) == graph.number_of_edges()
                assert int(task.final_answer) == nx.shortest_path_length(graph, task.src, task.dst, weight='weight')
                path = trace[-1]['path']
                assert path[0] == task.src and path[-1] == task.dst
                assert sum(graph[a][b]['weight'] for a, b in zip(path, path[1:])) == int(task.final_answer)
                assert sum(trace[-1]['weights']) == int(task.final_answer)
                replay = trace[0]['distances'].copy()
                settled = set()
                for event in trace:
                    if event['event'] == 'settle':
                        available = [(distance, vertex) for vertex, distance in enumerate(replay) if distance is not None and vertex not in settled]
                        assert (event['distance'], event['vertex']) == min(available)
                        settled.add(event['vertex'])
                    if event['event'] == 'relax':
                        assert event['old'] == replay[event['neighbor']]
                        if event['improved']:
                            replay[event['neighbor']] = event['candidate']
                        assert event['distances'] == replay
                        assert event['candidate'] == event['distance'] + event['weight']
                        assert event['improved'] == (event['old'] is None or event['candidate'] < event['old'])
            elif pair[0] == 'mst_weight':
                graph.add_weighted_edges_from(task.edges)
                assert int(task.final_answer) == nx.minimum_spanning_tree(graph).size(weight='weight')
                tree = nx.Graph()
                tree.add_weighted_edges_from(trace[-1]['edges'])
                assert nx.is_tree(tree) and len(tree) == task.n
                total = count = 0
                for event in trace:
                    if event['event'] == 'edge':
                        if event['accepted']:
                            total += event['weight']; count += 1
                        assert (event['total'], event['count']) == (total, count)
            elif pair[0] == 'max_flow':
                graph.add_edges_from((a, b, {'capacity': c}) for a, b, c in task.cap_edges)
                assert int(task.final_answer) == nx.maximum_flow_value(graph, task.s, task.t)
                assert trace[-1]['capacity'] == trace[-1]['total'] == int(task.final_answer)
                assert sum(e['bottleneck'] for e in trace if e['event'] == 'augment') == int(task.final_answer)
                residual = [[0] * task.n for _ in range(task.n)]
                for a, b, capacity in task.cap_edges:
                    residual[a][b] += capacity
                for event in trace:
                    if event['event'] == 'augment':
                        assert min(residual[a][b] for a, b in zip(event['path'], event['path'][1:])) == event['bottleneck']
                    if event['event'] == 'residual':
                        a, b = event['a'], event['b']
                        assert (residual[a][b], residual[b][a]) == (event['old_forward'], event['old_reverse'])
                        residual[a][b], residual[b][a] = event['forward'], event['reverse']
                        assert event['old_forward'] - event['bottleneck'] == event['forward'] >= 0
                        assert event['old_reverse'] + event['bottleneck'] == event['reverse']
            elif pair[0] == 'topological_sort':
                graph.add_edges_from(task.edges)
                assert trace[-1]['cycle'] == (not nx.is_directed_acyclic_graph(graph))
                if not trace[-1]['cycle']:
                    assert trace[-1]['order'] == list(nx.lexicographical_topological_sort(graph))
            else:
                graph.add_edges_from(task.edges)
                successes = [e for e in trace if e['event'] == 'success']
                for event in successes:
                    colors = event['colors']
                    assert all(1 <= c <= event['k'] for c in colors)
                    assert all(colors[a] != colors[b] for a, b in task.edges)


def test_dijkstra_replays_improvement_stale_entries_and_unreachable():
    edges = [(0, 1, 9), (0, 2, 1), (2, 1, 1), (1, 3, 20)]
    value, trace = dijkstra_trace(4, edges, 0, 3)
    assert value == 22 and trace[-1]['path'] == [0, 2, 1, 3]
    assert any(e['event'] == 'stale' for e in trace)
    value, trace = dijkstra_trace(3, [(0, 1, 2)], 0, 2)
    assert value == -1 and trace[-1]['event'] == 'unreachable'


def test_flow_trace_replays_reverse_arc_cancellation():
    # The second augmenting path must cancel flow along 1 -> 3.
    edges = [(0, 1, 1), (0, 2, 1), (1, 3, 1), (1, 4, 1),
             (2, 3, 1), (3, 5, 1), (4, 5, 1)]
    value, trace = flow_trace(6, edges, 0, 5)
    assert value == 2
    assert any(e['event'] == 'residual' and (e['a'], e['b']) == (3, 1) for e in trace)


def test_kahn_cycle_and_kruskal_rejected_edge():
    order, cycle, trace = kahn_trace(4, [(0, 1), (1, 2), (2, 1)])
    assert cycle and order == [0, 3] and trace[-1]['blocked'] == [1, 2]
    value, trace = kruskal_trace(4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4)])
    assert value == 7
    assert any(e['event'] == 'edge' and not e['accepted'] for e in trace)


def test_coloring_matches_exhaustive_oracle_for_every_four_vertex_graph():
    all_edges = list(itertools.combinations(range(4), 2))
    for mask in range(1 << len(all_edges)):
        edges = [edge for i, edge in enumerate(all_edges) if mask & (1 << i)]
        expected = next(k for k in range(1, 5) if any(
            all(colors[a] != colors[b] for a, b in edges)
            for colors in itertools.product(range(k), repeat=4)))
        actual, trace = coloring_trace(4, edges)
        assert actual == expected
        assert [e['k'] for e in trace if e['event'] == 'impossible'] == list(range(1, expected))
        for k in range(1, 5):
            result, _ = coloring_trace(4, edges, k)
            assert (result is not None) == (k >= expected)


def test_single_task_export_keeps_structured_trace(tmp_path):
    from re_rl.dataset_generator import DatasetGenerator
    task = DatasetGenerator(output_dir=str(tmp_path)).generate_single_task('weighted_shortest_path')
    assert task['algorithm_trace'][-1]['answer'] == int(task['final_answer'])
    assert task['graph']['n'] >= 4
    assert task['graph']['edges']
