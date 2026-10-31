"""Create a new, physics-only SFT dataset version with provenance and executable traces.

Original JSONL files are read only. A new directory must be chosen for each run.
Affected records are regenerated as new problems of the same family/subtype and
split, not relabeled as repairs of their original numerical instance.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys
import shutil
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.audit_saved_physics import build_report
from scripts.atomic_files import write_text


CODE_PATHS=[
 're_rl/tasks/physics/spectrum_models.py','re_rl/tasks/physics/conservation_models.py',
 're_rl/tasks/physics/trajectory_models.py','re_rl/tasks/physics/mechanical_models.py','re_rl/tasks/i18n/orphans.json',
 're_rl/tasks/physics/conservation_models_i18n.json','re_rl/tasks/physics/generators.py',
 're_rl/tasks/physics/constants.py','re_rl/tasks/physics/constants_i18n.json',
 're_rl/tasks/execution_trace.py','re_rl/tasks/execution_trace_i18n.json',
 're_rl/tasks/i18n/loader.py','re_rl/tasks/i18n/common.json','re_rl/tasks/base_task.py','scripts/audit_saved_physics.py','scripts/regenerate_saved_physics.py']
for folder in ('oscillations/oscillations','waves/waves','mechanics/momentum','thermodynamics/heat_transfer','mechanics/kinematics','mechanics/projectile_motion'):
    CODE_PATHS += [f're_rl/tasks/physics/{folder}/{name}' for name in ('task.py','i18n.json')]


def code_version():
    digest=hashlib.sha256()
    for relative in CODE_PATHS:digest.update(relative.encode()+b'\0'+(ROOT/relative).read_bytes()+b'\0')
    return digest.hexdigest()


def regenerate(report,output_dir,source_root=ROOT,max_attempts=100):
    from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS
    from re_rl.tasks.base_task import format_reasoning_output
    from re_rl.tasks.i18n import common_text
    from re_rl.rewards import check_format_compliance
    import sympy
    output_dir=Path(output_dir)
    if output_dir.exists():raise FileExistsError('output_directory_already_exists')
    version=code_version();state=random.getstate();seen=set();parameter_instances=set();files=[];counts=Counter();duplicates=0
    output_dir.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix=".physics-regeneration-",dir=output_dir.parent))
    try:
        for source in report['files']:
            path=source_root/source['path'];findings={r['line']:r for r in source['rows']}
            lines=[];source_bytes=path.read_bytes();source_digest=hashlib.sha256(source_bytes).hexdigest()
            if source.get('source_sha256')!=source_digest:raise RuntimeError('source_changed_since_audit')
            for line_number,line in enumerate(source_bytes.decode('utf-8').splitlines(keepends=True),1):
                if line_number not in findings:continue
                previous=json.loads(line);finding=findings[line_number];family=finding['family']
                metadata=dict(previous.get('metadata',{}));language=metadata.get('language','ru')
                difficulty=metadata.get('difficulty',5);source_reasoning=metadata.get('reasoning_mode',False)
                for attempt in range(max_attempts):
                    seed_text=f'{version}:{source["path"]}:{line_number}:{attempt}'
                    seed=int.from_bytes(hashlib.sha256(seed_text.encode()).digest(),'big')
                    random.seed(seed)
                    kwargs=dict(language=language,difficulty=difficulty,reasoning_mode=True,output_format="text")
                    if finding['subtype'] is not None:kwargs['task_type']=finding['subtype']
                    task=ALL_PHYSICS_TASK_GENERATORS[family](**kwargs)
                    result=task.get_result();key=result['problem'].strip()
                    instance=json.dumps(dict(family=family,subtype=task.task_type,inputs=result['computation_inputs']),sort_keys=True)
                    if key in seen or instance in parameter_instances:duplicates+=1;continue
                    if task.verify('<answer>'+str(result['final_answer'])+'</answer>')!=1:
                        raise RuntimeError('self_verification_failed')
                    if not result.get('algorithm_trace') or not result.get('computation_inputs'):
                        raise RuntimeError('missing_training_trace')
                    seen.add(key);parameter_instances.add(instance);break
                else:raise RuntimeError(f'unique_generation_exhausted: {family}/{finding["subtype"]}, difficulty={difficulty}, {source["path"]}:{line_number}')
                formatted=format_reasoning_output(result['solution_steps'],str(result['final_answer']),True,language)
                if task.verify(formatted)!=1 or check_format_compliance(formatted)!=0.2:raise RuntimeError('formatted_output_verification_failed')
                original_format=metadata.get('output_format','text')
                metadata.update(subtype=task.task_type,generator_code_sha256=version,reasoning_mode=True,output_format='text',
                                algorithm_trace=result['algorithm_trace'],computation_inputs=result['computation_inputs'],
                                final_answer=result['final_answer'],self_verification=1.0,output_verification=1.0,
                                source=dict(path=source['path'],line=line_number,sha256=source_digest,
                                            row_sha256=hashlib.sha256(line.encode()).hexdigest(),instruction=previous['instruction'],
                                            reasoning_mode=source_reasoning,output_format=original_format),
                                regeneration='new_problem_and_solution_same_family_and_subtype')
                row=dict(instruction=common_text('multiturn.common.system_reasoning',language,augment=False),input=result['problem'],
                         output=formatted,
                         metadata=metadata)
                lines.append(json.dumps(row,ensure_ascii=False));counts[family]+=1
            target=staging/path.name
            if target.exists():raise FileExistsError('duplicate_source_basename')
            write_text(target,'\n'.join(lines)+'\n')
            files.append(dict(path=target.name,records=len(lines),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                              source=source['path'],source_sha256=source_digest))
        manifest=dict(generator_code_sha256=version,sympy_version=sympy.__version__,families=dict(counts),
                      records=sum(counts.values()),self_verification_passed=sum(counts.values()),unique_problem_texts=len(seen),
                      unique_parameter_instances=len(parameter_instances),duplicate_attempts_rejected=duplicates,
                      scope='Regenerated physics-only slices; other task families are excluded.',
                      provenance='New problem/solution pairs preserve family, inferred subtype, original split/file and row provenance. Output uses think/answer tags; previous settings are recorded in source metadata.',
                      limitations='No duplicate condition text or exact parameter instance across these output files; this does not prove semantic disjointness or certify other datasets.',
                      files=files)
        write_text(staging/'manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        if output_dir.exists():raise FileExistsError('output_directory_already_exists')
        staging.rename(output_dir)
        return manifest
    finally:
        random.setstate(state)
        if staging.exists():shutil.rmtree(staging)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--datasets',type=Path,default=ROOT/'datasets')
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    report=build_report(ROOT,sorted(args.datasets.glob('*.jsonl')))
    destination=args.output_dir or ROOT/'datasets'/('physics_reviewed_'+code_version()[:12])
    manifest=regenerate(report,destination)
    print(json.dumps(dict(output=str(destination),records=manifest['records'],families=manifest['families'],
                          duplicate_attempts_rejected=manifest['duplicate_attempts_rejected']),ensure_ascii=False))


if __name__=='__main__':main()
