"""Replay every published physics record from its exact inputs and verify file provenance."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.atomic_files import write_text
from scripts.regenerate_saved_physics import code_version


def validate(directory,source_root=ROOT,require_version_match=False):
    from re_rl.tasks.registry import registry
    import re_rl.tasks.physics.generators
    from re_rl.rewards import check_format_compliance
    manifest=json.loads((directory/'manifest.json').read_text())
    current_version=code_version();same_version=manifest['generator_code_sha256']==current_version
    if require_version_match and not same_version:raise ValueError('generator_version_mismatch')
    state=random.getstate();conditions=set();instances=set();count=0;source_hashes={}
    try:
        for file in manifest['files']:
            path=directory/file['path']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=file['sha256']:raise ValueError('dataset_hash_mismatch')
            source=source_root/file['source']
            source_hashes[file['source']]=hashlib.sha256(source.read_bytes()).hexdigest()
            if source_hashes[file['source']]!=file['source_sha256']:raise ValueError('source_hash_mismatch')
            rows=0
            for line in path.read_text().splitlines():
                record=json.loads(line);meta=record['metadata'];family=meta['task_type']
                inputs=meta['computation_inputs']
                params={k:(v if k=='substance' else Fraction(v)) for k,v in inputs.items() if k not in ('model','dimension_axes')}
                task=registry[family](task_type=meta['subtype'],language=meta['language'],
                                      difficulty=meta['difficulty'],reasoning_mode=True,**params)
                task.solve()
                if task.algorithm_trace!=meta['algorithm_trace'] or task.computation_inputs!=inputs:
                    raise ValueError('trace_replay_mismatch')
                if task.final_answer!=meta['final_answer']:raise ValueError('reference_replay_mismatch')
                if task.verify(record['output'])!=1 or check_format_compliance(record['output'])!=0.2:
                    raise ValueError('saved_output_verification_failed')
                key=json.dumps(dict(family=family,subtype=meta['subtype'],inputs=inputs),sort_keys=True)
                if record['input'] in conditions or key in instances:raise ValueError('cross_file_duplicate')
                conditions.add(record['input']);instances.add(key);rows+=1;count+=1
            if rows!=file['records']:raise ValueError('record_count_mismatch')
        if count!=manifest['records']:raise ValueError('total_count_mismatch')
        return dict(records_replayed=count,full_outputs_verified=count,exact_trace_matches=count,
                    unique_conditions=len(conditions),unique_parameter_instances=len(instances),
                    unchanged_source_files=len(source_hashes),generator_code_sha256=manifest['generator_code_sha256'],
                    replay_code_sha256=current_version,generator_version_matches=same_version)
    finally:random.setstate(state)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--require-version-match',action='store_true')
    args=parser.parse_args();report=validate(args.directory,require_version_match=args.require_version_match)
    write_text(args.directory/'validation.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
