"""Refresh catalog graph examples from the actual traced task implementations."""
import json
import os
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('MPLCONFIGDIR', '/tmp/re-rl-mpl')

from scripts.atomic_files import save_task_image, write_text
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.math.logic.graph_algorithms_shared.coverage import TRACED_GRAPH_TASKS, TRACED_VISUAL_GRAPH_TASKS


def main(include_computations=False):
    path = ROOT / 'examples/catalog.html'
    html = path.read_text()
    start = html.index('const DATA = ') + len('const DATA = ')
    end = html.index('\nconst tasks', start)
    data = json.loads(html[start:end].strip().removesuffix(';'))
    supported = set(TRACED_GRAPH_TASKS) | set(TRACED_VISUAL_GRAPH_TASKS)
    if include_computations:
        from re_rl.tasks.ml.detailed_solvers import TRACED_ML_TASKS
        from re_rl.tasks.rl.detailed_solvers import TRACED_RL_TASKS
        from re_rl.tasks.math.algorithm_traces.solvers import TRACED_DP_TASKS
        from re_rl.tasks.physics.detailed_solvers import TRACED_PHYSICS_TASKS
        from re_rl.tasks.math.algorithm_traces.automata import TRACED_AUTOMATA_TASKS
        from re_rl.tasks.reviewed_coverage import REVIEWED_TASKS
        supported.update(TRACED_ML_TASKS + TRACED_RL_TASKS + TRACED_DP_TASKS + TRACED_PHYSICS_TASKS + TRACED_AUTOMATA_TASKS)
        supported.update(REVIEWED_TASKS)
    updated = 0
    for item in data['tasks']:
        if item['id'] not in supported:
            continue
        random.seed(3)
        generators = ALL_VISUAL_TASK_GENERATORS if item['kind'] == 'visual' else ALL_TASK_GENERATORS
        kwargs = {'task_type': item['subtypes'][0]} if item['subtypes'] else {}
        task = generators[item['id']](language='ru', difficulty=3, **kwargs)
        result = task.get_result()
        item.update(example=result['problem'], answer=str(result['final_answer']),
                    steps=result['solution_steps'], error='')
        if item['kind'] == 'visual':
            save_task_image(task,ROOT / 'examples/previews' / f"{item['id']}.png")
        updated += 1
    assert updated == len(supported)
    blob = json.dumps(data, ensure_ascii=False, separators=(', ', ': '))
    write_text(path,html[:start] + blob + ';' + html[end:])
    print(f'Refreshed {updated} traced catalog examples.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-computations', action='store_true')
    main(parser.parse_args().include_computations)
