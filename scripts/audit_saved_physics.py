"""Read-only audit of saved JSONL examples against legacy physics contracts.

No source dataset is rewritten. Reports affected records and demonstrable output
omissions/zero periods/superluminal acoustic speeds; other historical records are
marked for contract/model review, not automatically declared numerically wrong.
"""
import argparse
import hashlib
from collections import Counter
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import string

ROOT=Path(__file__).resolve().parents[1]
NUMBER=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'


def templates(root):
    raw=json.loads((root/'re_rl/tasks/i18n/orphans.json').read_text())
    patterns={}
    projectile=json.loads((root/'re_rl/tasks/physics/mechanics/projectile_motion/i18n.json').read_text())['prompt']
    for family in ('oscillations','waves','momentum','heat_transfer','kinematics','projectile_motion'):
        patterns[family]=[]
        section=projectile if family=='projectile_motion' else raw[family]
        for kind,languages in section['problem'].items():
            for language,variants in languages.items():
                for text in variants if isinstance(variants,list) else [variants]:
                    if family=='projectile_motion':text=section['instructions'][language]+'\n\n'+text
                    pieces=[]
                    for literal,name,spec,conversion in string.Formatter().parse(text):
                        pieces.append(re.escape(literal))
                        if name is not None:pieces.append('(?P<'+name+'>'+('.+?' if name=='substance' else NUMBER)+')')
                    patterns[family].append((kind,re.compile(''.join(pieces))))
    return patterns


def answer(text):
    matches=re.findall(r'<answer>(.*?)</answer>',text,re.DOTALL|re.IGNORECASE)
    if matches:return matches[-1].strip()
    # Labels come from the repository's localized common catalog, not inference.
    return re.split(r'(?:Ответ|Answer)\s*:',text)[-1].strip()


def inspect_record(record,patterns):
    metadata=record.get('metadata',{});family=metadata.get('task_type')
    if family not in patterns:return None
    text=record.get('input','');response=answer(record.get('output',''))
    if not isinstance(text,str):text=''
    kind=None;data={}
    for candidate,pattern in patterns.get(family,[]):
        match=pattern.fullmatch(text)
        if match:
            kind=candidate;data={key:(value if key=='substance' else Fraction(value)) for key,value in match.groupdict().items()};break
    issues=[]
    if kind=='harmonic' and not re.search(r'v_?max\s*=',response):issues.append('missing_requested_maximum_speed')
    if kind=='spring' and not re.search(r'\bf\s*=',response):issues.append('missing_requested_ordinary_frequency')
    if kind=='period':
        match=re.search(NUMBER,response)
        if match and Fraction(match.group())==0 and data['f']>0:issues.append('nonzero_period_rounded_to_zero')
    if kind=='sound_speed' and data['f']*data['lambda_']>299792458:
        issues.append('superluminal_acoustic_speed')
    evidence=None
    if family=='projectile_motion' and kind is not None:
        speed=float(data['v0']);theta=math.radians(float(data['angle']));gravity=9.81
        expected=None
        if kind=='range':expected=speed*speed*math.sin(2*theta)/gravity
        elif kind=='max_height':expected=(speed*math.sin(theta))**2/(2*gravity)
        elif kind=='flight_time':expected=2*speed*math.sin(theta)/gravity
        else:
            height=float(data['h']);apex=(speed*math.sin(theta))**2/(2*gravity)
            if height>apex+1e-12:issues.append('published_height_unreachable')
            if speed*speed>=2*gravity*height:expected=math.sqrt(speed*speed-2*gravity*height)
        numeric=response.partition('=')[2] if '=' in response else response
        match=re.search(NUMBER,numeric)
        if expected is not None and match:
            stored=float(Fraction(match.group()));error=abs(stored-expected)
            if error>0.005001:
                issues.append('reference_inconsistent_with_published_inputs_and_legacy_g')
                evidence=dict(gravity=gravity,tolerance=0.005001,expected_from_published_inputs=expected,
                              stored_answer=stored,absolute_error=error)
    result=dict(family=family,subtype=kind,issues=issues,legacy_template_matched=kind is not None)
    if evidence is not None:result['evidence']=evidence
    return result


def build_report(root,paths):
    patterns=templates(root);files=[];total=Counter();issue_totals=Counter()
    for path in paths:
        rows=[];families=Counter();issues=Counter();parsed=0
        source_bytes=path.read_bytes()
        for line_number,line in enumerate(source_bytes.decode('utf-8').splitlines(),1):
            if not line.strip():continue
            record=json.loads(line);parsed+=1
            finding=inspect_record(record,patterns)
            if finding is None:continue
            families[finding['family']]+=1;total[finding['family']]+=1
            issues.update(finding['issues']);issue_totals.update(finding['issues'])
            rows.append(dict(line=line_number,**finding))
        if rows:
            label=str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
            files.append(dict(path=label,source_sha256=hashlib.sha256(source_bytes).hexdigest(),records=parsed,affected=len(rows),
                              affected_by_family=dict(families),confirmed_issue_counts=dict(issues),rows=rows))
    return dict(scope='Saved metadata-tagged examples from six changed physics families; historical templates only. Projectile replay assumes the legacy generator g=9.81 and two-decimal output.',
                action='Regenerate affected families using current generators into a separate dataset version. Original files are unchanged.',
                limitations='A contract-review record without an issue is not proven wrong. Unmatched templates and other task families are not semantically certified.',
                affected_by_family=dict(total),confirmed_issue_counts=dict(issue_totals),files=files)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--datasets',type=Path,default=ROOT/'datasets')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/saved_physics_audit.json')
    args=parser.parse_args()
    report=build_report(ROOT,sorted(args.datasets.glob('*.jsonl')))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('affected_by_family','confirmed_issue_counts')},ensure_ascii=False))


if __name__=='__main__':main()
