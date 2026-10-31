"""Inventory trace quality indicators across both registries.

Indicators are review candidates, not proofs of incorrect reasoning. Optional
runtime checks are bounded in isolated forked workers, with explicit failures.
"""
import argparse
import ast
from collections import Counter
import inspect
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('MPLCONFIGDIR', '/tmp/re-rl-mpl')


def static_indicators(cls):
    delegated = hasattr(cls, '_solve_before_trace')
    method = cls._solve_before_trace if delegated else cls.solve
    source = Path(inspect.getfile(method))
    tree = ast.parse(source.read_text())
    line = method.__code__.co_firstlineno
    node = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.lineno == line)
    loops = any(isinstance(n, (ast.For, ast.While, ast.comprehension)) for n in ast.walk(node))
    precomputed = sorted({n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)
                          and isinstance(n.ctx, ast.Load) and isinstance(n.value,ast.Name)
                          and n.value.id == 'self' and n.attr in {
                              'answer','_answer','value','total','result','grad',
                              'hidden','klass','test_out','grid','row','pi','count',
                              'answer_int','answer_bool','_answer_maze','end_x','end_y','end_dir','target_is_mine','false_statement_index','role','valid','_valid','_entails','secret','_error_index','_always_nonneg'}})
    grid_fields = {n.attr for n in ast.walk(node) if isinstance(n,ast.Attribute)
                   and isinstance(n.ctx,ast.Load) and isinstance(n.value,ast.Name)
                   and n.value.id == 'self' and n.attr in {'sol','solution','solution_grid','_solution','shaded','stars','target_value'}}
    called = {n.func.id if isinstance(n.func,ast.Name) else n.func.attr
              if isinstance(n.func,ast.Attribute) else '?' for n in ast.walk(node) if isinstance(n,ast.Call)}
    formatting_calls = {'str','range','join','t','common','format','map','enumerate',
                        'len','_grid_str','_format_grid','_format_solution','get_template','append','sorted'}
    rendered_cached_grid = bool(grid_fields and called <= formatting_calls)
    cached_final_grid = any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
                            and n.func.attr == '_format_grid' and any(
                                isinstance(arg,ast.Attribute) and isinstance(arg.value,ast.Name)
                                and arg.value.id == 'self' and arg.attr == 'solution'
                                for arg in n.args) for n in ast.walk(node))
    writes_solution = any(isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name)
                          and n.value.id == 'self' and n.attr == 'solution'
                          and isinstance(n.ctx,ast.Store) for n in ast.walk(node))
    cached_final_grid = cached_final_grid and not writes_solution
    random_solver_calls = sorted({n.func.attr for n in ast.walk(node)
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
        and isinstance(n.func.value,ast.Name) and n.func.value.id == 'random'})
    plan_fields = {'moves','_plan','solution_path'}
    reads_plan = any(isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name)
                     and n.value.id == 'self' and n.attr in plan_fields
                     and isinstance(n.ctx,ast.Load) for n in ast.walk(node))
    writes_plan = any(isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name)
                      and n.value.id == 'self' and n.attr in plan_fields
                      and isinstance(n.ctx,ast.Store) for n in ast.walk(node))
    rendered_cached_plan = reads_plan and not writes_plan and called <= formatting_calls | {
        'gcd','index','_format_action','_format_state','_get_item_name','_format_move','_person_name'}
    return dict(source=str(source.relative_to(ROOT)), line=line,
                delegated_execution=delegated,
                source_lines=node.end_lineno - node.lineno + 1,
                has_iteration=loops, precomputed_reads=precomputed,
                rendered_cached_grid=rendered_cached_grid,
                cached_final_grid=cached_final_grid,
                rendered_cached_plan=rendered_cached_plan,
                random_solver_calls=random_solver_calls,
                candidate=bool(precomputed and not loops) or rendered_cached_grid or cached_final_grid or rendered_cached_plan or bool(random_solver_calls))


def run_one(generator, language, connection):
    try:
        random.seed(31)
        parameters = inspect.signature(generator).parameters
        kwargs = dict(language=language, difficulty=5, augment=False)
        if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in parameters.values()):
            kwargs = {k: v for k, v in kwargs.items() if k in parameters}
        task = generator(**kwargs)
        result = task.get_result()
        connection.send(dict(language=language, status='ok', steps=len(result['solution_steps']),
                             events=len(result.get('algorithm_trace', [])),
                             has_trace_inputs=bool(result.get('computation_inputs') or result.get('graph'))))
    except Exception as exc:
        connection.send(dict(language=language, status='error', error=f'{type(exc).__name__}: {exc}'))
    finally:
        connection.close()


def build_report(runtime=False, timeout=3):
    from re_rl.tasks.generators import ALL_TASK_GENERATORS
    from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
    from re_rl.tasks.registry import registry
    from re_rl.tasks.ml.detailed_solvers import TRACED_ML_TASKS
    from re_rl.tasks.rl.detailed_solvers import TRACED_RL_TASKS
    from re_rl.tasks.math.algorithm_traces.solvers import TRACED_DP_TASKS
    from re_rl.tasks.physics.detailed_solvers import TRACED_PHYSICS_TASKS
    from re_rl.tasks.math.algorithm_traces.automata import TRACED_AUTOMATA_TASKS
    from re_rl.tasks.reviewed_coverage import REVIEWED_TASKS
    from re_rl.tasks.math.logic.graph_algorithms_shared.coverage import TRACED_GRAPH_TASKS, TRACED_VISUAL_GRAPH_TASKS
    covered = set(TRACED_ML_TASKS + TRACED_RL_TASKS + TRACED_DP_TASKS + TRACED_PHYSICS_TASKS + TRACED_AUTOMATA_TASKS + TRACED_GRAPH_TASKS + TRACED_VISUAL_GRAPH_TASKS)
    covered.update(REVIEWED_TASKS)
    rows = []
    generators = {**ALL_TASK_GENERATORS, **ALL_VISUAL_TASK_GENERATORS}
    context = mp.get_context('fork') if runtime else None
    for name, generator in sorted(generators.items()):
        cls = registry.get(name)
        row = dict(id=name, kind='visual' if name in ALL_VISUAL_TASK_GENERATORS else 'text',
                   reviewed_with_regression_tests=name in covered)
        if cls is None:
            row.update(candidate=True, error='missing_registry_class')
        else:
            row.update(static_indicators(cls))
            row['domain'] = cls.__module__.split('.')[2]
        if runtime:
            row['runtime'] = []
            for language in ('ru', 'en'):
                parent, child = context.Pipe(duplex=False)
                process = context.Process(target=run_one, args=(generator, language, child))
                process.start(); child.close()
                if parent.poll(timeout):
                    try: sample = parent.recv()
                    except EOFError: sample = dict(language=language, status='worker_exit')
                else:
                    sample = dict(language=language, status='timeout')
                process.join(timeout=0.1)
                if process.is_alive(): process.terminate(); process.join()
                parent.close()
                row['runtime'].append(sample)
        row['needs_review'] = bool(row.get('candidate') and not row['reviewed_with_regression_tests'])
        rows.append(row)
    summary = dict(total=len(rows), static_candidates=sum(bool(r.get('candidate')) for r in rows),
                   reviewed=sum(r['reviewed_with_regression_tests'] for r in rows),
                   remaining_static_review=sum(r['needs_review'] for r in rows),
                   remaining_by_domain=dict(Counter(r.get('domain', 'unknown') for r in rows if r['needs_review'])))
    if runtime:
        summary['runtime_statuses'] = dict(Counter(s['status'] for r in rows for s in r['runtime']))
        summary['short_samples'] = sum(s.get('steps', 999) <= 2 for r in rows for s in r['runtime'])
    return dict(method='Static indicators plus optional RU/EN generation at difficulty 5, seed 31; human review required.',
                summary=summary, tasks=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', action='store_true')
    parser.add_argument('--timeout', type=float, default=3)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/trace_audit.json')
    args = parser.parse_args()
    if args.timeout <= 0: parser.error('timeout must be positive')
    report = build_report(args.runtime, args.timeout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report['summary'], ensure_ascii=False))


if __name__ == '__main__':
    main()
