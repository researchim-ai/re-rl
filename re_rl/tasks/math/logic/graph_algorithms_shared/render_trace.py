"""Render structured graph events using the shared RU/EN catalog."""
from re_rl.tasks.i18n import TaskTexts

texts = TaskTexts(__file__, 'trace_i18n.json')


def render_trace(events, algorithm, language, vertex_offset=0):
    steps = []
    for event in events:
        namespace = event.get('algorithm', algorithm)
        values = {key: ('∞' if value is None else value) for key, value in event.items()}
        offset = event.get('vertex_offset', vertex_offset)
        if offset:
            for key in ('a', 'b', 'via', 'vertex', 'neighbor', 'source', 'target', 'child', 'parent'):
                if key in values and isinstance(values[key], int) and values[key] >= 0:
                    values[key] += offset
            for key in ('queue', 'visited', 'discovered', 'chosen', 'path', 'neighbors', 'order', 'group', 'added', 'nodes', 'points', 'leaves', 'reverse_route'):
                if key in values:
                    values[key] = [v + offset for v in values[key]]
            if 'groups' in values:
                values['groups'] = [[v + offset for v in group] for group in values['groups']]
        if 'matrix' in values:
            values['matrix'] = str([[value if value is not None else '∞' for value in row] for row in event['matrix']])
        if 'distances' in values:
            distance_offset = 1 if namespace == 'counts' else offset
            values['distances'] = ', '.join(f'{i + distance_offset}:{value if value is not None else "∞"}'
                                          for i, value in enumerate(event['distances']))
        if 'path' in values:
            values['path'] = ' → '.join(map(str, values['path']))
        if namespace == 'dijkstra' and event['event'] == 'relax':
            values['decision'] = texts.t('update' if event['improved'] else 'keep', language)
        if namespace == 'dijkstra' and event['event'] == 'path':
            values['weights'] = ' + '.join(map(str, event['weights'])) or '0'
        if namespace == 'kruskal' and event['event'] == 'edge':
            values['decision'] = texts.t('accept' if event['accepted'] else 'reject', language)
        if namespace == 'kahn' and event['event'] == 'done':
            values['decision'] = texts.t('cycle' if event['cycle'] else 'acyclic', language)
        steps.append(texts.t(f"{namespace}.{event['event']}", language, **values))
    return steps
