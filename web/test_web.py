"""Integrity checks for the committed static site snapshot (no browser dependency)."""
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'data.js').read_text().removeprefix('window.RE_RL_DATA = ').strip().removesuffix(';'))


def test_catalog_matches_project_catalog():
    html = (ROOT.parent / 'examples/catalog.html').read_text()
    original = json.loads(html.split('const DATA = ', 1)[1].split('\nconst tasks', 1)[0].strip().removesuffix(';'))
    assert {t['id'] for t in DATA['tasks']} == {t['id'] for t in original['tasks']}
    assert len(DATA['tasks']) == len({t['id'] for t in DATA['tasks']})
    assert DATA['counts'] == Counter(t['family'] for t in DATA['tasks'])
    assert sum(DATA['counts'].values()) == DATA['provenance']['text'] + DATA['provenance']['visual']


def test_all_lab_combinations_have_complete_samples():
    samples = DATA['samples']
    ids = {s['id'] for s in samples}
    assert len(ids) == 26
    assert len(samples) == 1560
    assert len({(s['id'], s['language'], s['difficulty'], s['variant']) for s in samples}) == 1560
    for name in ids:
        assert {(s['language'], s['difficulty'], s['variant']) for s in samples if s['id'] == name} == {
            (lang, level, variant) for lang in ('ru', 'en') for level in range(1, 11) for variant in range(3)
        }
    for sample in samples:
        assert sample['prompt'] and sample['answer'] and sample['steps']
        assert sample['self_score'] == 1.0
        if sample.get('image'):
            with Image.open(ROOT / sample['image']) as image:
                image.verify()
        assert all(isinstance(step, str) and step for step in sample['steps'])


def test_every_visual_has_a_valid_matching_image():
    visual = [t for t in DATA['tasks'] if t['kind'] == 'visual']
    assert len(visual) == DATA['provenance']['visual']
    for task in visual:
        assert task['example'] and task['answer'] and task['steps']
        path = ROOT / task['image']
        assert path.stem == task['id']
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            assert image.width > 0 and image.height > 0


def test_page_assets_and_anchor_targets_exist():
    html = (ROOT / 'index.html').read_text()
    ids = re.findall(r'\bid="([^"]+)"', html)
    assert len(ids) == len(set(ids))
    for target in re.findall(r'href="#([^"]+)"', html):
        assert target in ids
    for asset in re.findall(r'(?:src|href)="([^"#]+\.(?:css|js|svg))"', html):
        assert (ROOT / asset).is_file()
    assert '<html lang="ru">' in html
    assert 'prefers-reduced-motion' in (ROOT / 'styles.css').read_text()


def test_curated_tasks_have_explanations_and_all_domains():
    featured = set(DATA['provenance']['featured'])
    tasks = [t for t in DATA['tasks'] if t['id'] in featured]
    assert len(tasks) == 26
    assert {t['family'] for t in tasks} == {'math', 'physics', 'ml', 'rl', 'visual'}
    for task in tasks:
        assert task['title'] and task['skill'] and task['explanation']
        assert len([s for s in DATA['samples'] if s['id'] == task['id']]) == 60
