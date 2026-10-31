"""Historical error detection and transactional, provenance-preserving regeneration."""
import hashlib
import json
from pathlib import Path
import random
from unittest.mock import patch
import pytest
from scripts.audit_saved_physics import ROOT,templates,inspect_record,build_report
from scripts.regenerate_saved_physics import regenerate


def row(family,subtype,data,output='old',reasoning=False):
    legacy=json.loads((ROOT/'re_rl/tasks/i18n/orphans.json').read_text())
    return dict(instruction='Solve with <think> and <answer> tags.' if reasoning else 'Solve step by step.',
                input=legacy[family]['problem'][subtype]['en'].format(**data),output=output,
                metadata=dict(task_type=family,difficulty=2,language='en',output_format='text',reasoning_mode=reasoning))


def source_files(tmp_path):
    samples=[
      row('oscillations','harmonic',dict(A=1,omega=2),'Answer: T=3.1416 s, f=0.3183 Hz'),
      row('oscillations','spring',dict(k=8,m=2),'Answer: T=3.1416 s, omega=2 rad/s'),
      row('waves','period',dict(f=100000000),'Answer: 0 s'),
      row('waves','sound_speed',dict(f=100000000,lambda_=1000000),'Answer: 1e14 m/s'),
      row('momentum','elastic_collision',dict(m1=1,m2=2,v1=3),reasoning=True),
      row('heat_transfer','heat_capacity',dict(m=1,substance='ice',T1=20,T2=40,c=2090)),
    ]
    train=tmp_path/'train.jsonl';evaluation=tmp_path/'eval.jsonl'
    train.write_text('\n'.join(json.dumps(r) for r in samples[:3]+[dict(metadata=dict(task_type='linear'))])+'\n')
    evaluation.write_text('\n'.join(json.dumps(r) for r in samples[3:])+'\n')
    return [train,evaluation]


def test_historical_issues_are_not_just_new_format_rejections():
    patterns=templates(ROOT)
    cases=[
      row('oscillations','harmonic',dict(A=1,omega=2),'Answer: T=3.1416 s, f=0.3183 Hz'),
      row('oscillations','spring',dict(k=8,m=2),'Answer: T=3.1416 s, omega=2 rad/s'),
      row('waves','period',dict(f=100000000),'Answer: 0 s'),
      row('waves','sound_speed',dict(f=100000000,lambda_=1000000),'Answer: 1e14 m/s')]
    expected=['missing_requested_maximum_speed','missing_requested_ordinary_frequency','nonzero_period_rounded_to_zero','superluminal_acoustic_speed']
    for record,issue in zip(cases,expected):assert inspect_record(record,patterns)['issues']==[issue]
    good=row('oscillations','harmonic',dict(A=1,omega=2),'Answer: T=3.14159265 s; v_max=2 m/s')
    assert inspect_record(good,patterns)['issues']==[]
    good=row('waves','period',dict(f=100),'Answer: 0.01 s')
    assert inspect_record(good,patterns)['issues']==[]


def test_regeneration_new_problems_preserves_sources_splits_rng_and_full_traces(tmp_path):
    paths=source_files(tmp_path);before={p:p.read_bytes() for p in paths}
    report=build_report(ROOT,paths)
    random.seed(77);state=random.getstate();output=tmp_path/'reviewed'
    manifest=regenerate(report,output)
    assert random.getstate()==state
    assert manifest['records']==manifest['self_verification_passed']==manifest['unique_problem_texts']==manifest['unique_parameter_instances']==6
    all_inputs=set()
    for entry in manifest['files']:
        target=output/entry['path']
        assert hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256']
        for line in target.read_text().splitlines():
            item=json.loads(line);meta=item['metadata']
            assert meta['algorithm_trace'] and meta['computation_inputs'] and meta['self_verification']==1
            assert meta['source']['path'] in {str(p) for p in paths}
            original=json.loads(Path(meta['source']['path']).read_text().splitlines()[meta['source']['line']-1])
            assert item['input']!=original['input']
            assert meta['source']['instruction']==original['instruction']
            assert meta['output_verification']==1
            assert meta['source']['reasoning_mode']==original['metadata']['reasoning_mode']
            assert meta['reasoning_mode'] is True
            if meta['reasoning_mode']:assert '<think>' in item['output'] and '<answer>' in item['output']
            assert item['input'] not in all_inputs;all_inputs.add(item['input'])
    from scripts.validate_physics_slice import validate
    replay=validate(output)
    assert replay['records_replayed']==replay['full_outputs_verified']==replay['exact_trace_matches']==6
    assert replay['unchanged_source_files']==2
    assert all(p.read_bytes()==before[p] for p in paths)
    duplicate=tmp_path/'repeated'
    regenerate(report,duplicate)
    assert [(output/p['path']).read_bytes() for p in manifest['files']]==[(duplicate/p['path']).read_bytes() for p in manifest['files']]
    with pytest.raises(FileExistsError):regenerate(report,output)


def test_failure_or_changed_source_cannot_publish_partial_dataset(tmp_path):
    paths=source_files(tmp_path);report=build_report(ROOT,paths)
    state=random.getstate()
    with pytest.raises(RuntimeError,match='unique_generation_exhausted'):
        regenerate(report,tmp_path/'failed',max_attempts=0)
    assert not (tmp_path/'failed').exists() and not list(tmp_path.glob('.physics-regeneration-*'))
    assert random.getstate()==state
    paths[0].write_text(paths[0].read_text()+'\n')
    with pytest.raises(RuntimeError,match='source_changed_since_audit'):
        regenerate(report,tmp_path/'changed')
    assert not (tmp_path/'changed').exists()


def test_published_slice_hash_tampering_is_rejected(tmp_path):
    from scripts.validate_physics_slice import validate
    report=build_report(ROOT,source_files(tmp_path));output=tmp_path/'published'
    manifest=regenerate(report,output)
    target=output/manifest['files'][0]['path']
    target.write_text(target.read_text()+'\n')
    with pytest.raises(ValueError,match='dataset_hash_mismatch'):validate(output)


def test_compatible_code_updates_require_actual_replay_and_keep_version_provenance(tmp_path):
    from scripts.validate_physics_slice import validate
    report=build_report(ROOT,source_files(tmp_path));output=tmp_path/'versioned'
    regenerate(report,output)
    with patch('scripts.validate_physics_slice.code_version',return_value='a_different_code_version'):
        replay=validate(output)
        assert replay['generator_version_matches'] is False
        assert replay['exact_trace_matches']==6
        assert replay['replay_code_sha256']=='a_different_code_version'
        with pytest.raises(ValueError,match='generator_version_mismatch'):
            validate(output,require_version_match=True)


def test_projectile_published_rounding_audit_and_regeneration(tmp_path):
    import math
    legacy=json.loads((ROOT/'re_rl/tasks/physics/mechanics/projectile_motion/i18n.json').read_text())['prompt']
    problem=legacy['instructions']['en']+'\n\n'+legacy['problem']['range']['en'].format(v0=10.1,angle=30)
    hidden_answer=round(10.149**2*math.sin(2*math.radians(30.049))/9.81,2)
    record=dict(instruction='Solve step by step.',input=problem,output=f'Answer: L = {hidden_answer} m',
                metadata=dict(task_type='projectile_motion',difficulty=2,language='en',output_format='text'))
    finding=inspect_record(record,templates(ROOT))
    assert finding['subtype']=='range'
    assert finding['issues']==['reference_inconsistent_with_published_inputs_and_legacy_g']
    assert finding['evidence']['absolute_error']>0.005001
    expected=10.1**2*math.sin(2*math.radians(30))/9.81
    correct=dict(record,output=f'Answer: L = {round(expected,2)} m')
    assert inspect_record(correct,templates(ROOT))['issues']==[]
    source=tmp_path/'projectile.jsonl';source.write_text(json.dumps(record)+'\n')
    report=build_report(ROOT,[source]);target=tmp_path/'reviewed_projectile'
    regenerate(report,target)
    from scripts.validate_physics_slice import validate
    assert validate(target)['records_replayed']==1
    height_problem=legacy['instructions']['en']+'\n\n'+legacy['problem']['velocity_at_height']['en'].format(v0=10,angle=30,h=2)
    unreachable=dict(record,input=height_problem,output=f'Answer: v = {round(math.sqrt(100-2*9.81*2),2)} m/s')
    assert inspect_record(unreachable,templates(ROOT))['issues']==['published_height_unreachable']
