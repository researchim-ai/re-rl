"""Rebuild the static website snapshot from the real project registry.
Run from the repository root: MPLCONFIGDIR=/tmp/re-rl-mpl python web/scripts/build_data.py
"""
import hashlib
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('MPLCONFIGDIR', '/tmp/re-rl-mpl')
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.visual.generators import ALL_VISUAL_TASK_GENERATORS
from re_rl.tasks.registry import registry
from scripts.atomic_files import save_task_image, write_text

WEB = ROOT / 'web'
html = (ROOT / 'examples/catalog.html').read_text()
catalog = json.loads(html.split('const DATA = ', 1)[1].split('\nconst tasks', 1)[0].strip().removesuffix(';'))
assert {t['id'] for t in catalog['tasks']} == set(ALL_TASK_GENERATORS) | set(ALL_VISUAL_TASK_GENERATORS), 'Rebuild examples/catalog.html first: registry differs.'

def family(task):
    if task['kind'] == 'visual': return 'visual'
    module = registry[task['id']].__module__
    for key in ('physics', 'ml', 'rl', 'formal'):
        if f'.{key}.' in module: return key
    return 'math'

tasks = []
for original in catalog['tasks']:
    task = dict(original)
    task['family'] = family(task)
    tasks.append(task)

# Curated examples span domains, languages, levels and subtypes.
guides = {
    'horn_fire': ('Правила Хорна', 'Делать выводы из известных фактов', 'Удерживать набор известных атомов и применять правило только при выполнении обеих посылок.'),
    'gate_fold': ('Логические вентили', 'Прослеживать изменение состояния', 'Последовательно обновлять бит, различая AND, OR и XOR.'),
    'union_find': ('Объединение множеств', 'Отслеживать связи', 'Обновлять компоненты связности после объединений и отвечать на запросы.'),
    'euler_method': ('Метод Эйлера', 'Вычислять траекторию по шагам', 'Подставлять текущее состояние в производную и переходить к следующему узлу.'),
    'q_learning': ('Обновление Q-learning', 'Связывать награду и оценку будущего', 'Вычислять TD-ошибку и обновлять ценность действия.'),
    'discounted_return': ('Дисконтированная отдача', 'Учитывать отложенные награды', 'Суммировать награды с учетом их положения в траектории и дисконта.'),
    'stable_matching': ('Устойчивые пары', 'Рассуждать о предпочтениях', 'Следить за предложениями и отличать устойчивое паросочетание от блокирующей пары.'),
    'hamming_code': ('Код Хэмминга', 'Обнаруживать ошибки по ограничениям', 'Вычислять контрольные биты и синдром, опираясь на проверки четности.'),
    'page_replacement': ('Замещение страниц', 'Моделировать работу памяти', 'Обновлять содержимое кэша по FIFO, LRU или OPT и считать промахи.'),
    'min_coins': ('Минимум монет', 'Находить оптимум', 'Сравнивать способы набрать сумму; крупнейший номинал не всегда дает оптимальный результат.'),
    'binary_search': ('Двоичный поиск', 'Сужать пространство поиска', 'Сравнивать средний элемент и корректно обновлять границы интервала.'),
    'matrix_chain': ('Цепочка матриц', 'Разбивать задачу на подзадачи', 'Выбирать порядок скобок с минимальным количеством скалярных умножений.'),
    'perceptron_update': ('Обучение перцептрона', 'Прослеживать обновление весов', 'Сопоставлять предсказание с меткой и применять правило обучения.'),
    'gini_split': ('Критерий Джини', 'Сравнивать решения по метрике', 'Считать взвешенную нечистоту ветвей и сравнивать разбиения.'),
    'shannon_entropy': ('Энтропия Шеннона', 'Оценивать неопределенность', 'Связывать распределение вероятностей с информационной энтропией.'),
    'sarsa': ('Обновление SARSA', 'Учитывать выбранное действие', 'Использовать ценность следующего действия в целевом значении обновления.'),
    'bellman_backup': ('Шаг Беллмана', 'Сравнивать будущие исходы', 'Взвешивать переходы по вероятностям и выбирать действие по ожидаемой ценности.'),
    'gae_advantage': ('Преимущество GAE', 'Объединять ошибки во времени', 'Вычислять временные разности и накапливать их с весами γ и λ.'),
    'ballistic_pendulum': ('Баллистический маятник', 'Выбирать физический закон для этапа', 'Различать неупругий удар и последующий подъем маятника.'),
    'resistor_pair': ('Соединение резисторов', 'Соотносить схему и формулу', 'Различать последовательное и параллельное соединения.'),
    'half_life_steps': ('Период полураспада', 'Рассуждать о повторном изменении', 'Последовательно применять уменьшение вдвое и восстанавливать число периодов.'),
    'wave_relation': ('Параметры волны', 'Связывать физические величины', 'Находить неизвестный параметр из скорости, частоты и длины волны.'),
    'boolean_circuit_image': ('Логическая схема', 'Читать схему вычислений', 'Извлекать связи с рисунка и вычислять выходы логических вентилей.'),
    'shortest_path_image': ('Путь на графе', 'Планировать по изображению', 'Читать веса ребер и сравнивать маршруты на нарисованном графе.'),
    'bar_chart_read': ('Столбчатая диаграмма', 'Извлекать данные из изображения', 'Сопоставлять категории и высоты столбцов для вычисления ответа.'),
    'arrow_turn': ('Повороты стрелок', 'Рассуждать о направлении', 'Сравнивать соседние стрелки и различать повороты на четверть оборота.'),
}
featured = list(guides)
samples = []
sample_dir = WEB / 'assets' / 'samples'
sample_dir.mkdir(parents=True, exist_ok=True)
for name in featured:
    item = next(t for t in tasks if t['id'] == name)
    item.update(title=guides[name][0], skill=guides[name][1], explanation=guides[name][2])
    generator = (ALL_VISUAL_TASK_GENERATORS if item['kind'] == 'visual' else ALL_TASK_GENERATORS)[name]
    for language in ('ru', 'en'):
        for difficulty in range(1, 11):
            for variant in range(3):
                seed = int(hashlib.sha256(f'{name}/{language}/{difficulty}/{variant}'.encode()).hexdigest()[:8], 16)
                random.seed(seed)
                kwargs = {'task_type': item['subtypes'][variant % len(item['subtypes'])]} if item['subtypes'] else {}
                task = generator(language=language, difficulty=difficulty, augment=False, **kwargs)
                assert task.description and task.solution_steps and str(task.final_answer)
                score = task.verify(f'<answer>{task.final_answer}</answer>')
                assert score == 1.0, (name, language, difficulty, variant, score)
                sample = dict(id=name, language=language, difficulty=difficulty, variant=variant, seed=seed,
                              subtype=getattr(task, 'task_type', ''), prompt=task.description,
                              steps=task.solution_steps, answer=str(task.final_answer), self_score=score)
                if hasattr(task, 'algorithm_trace'):
                    result = task.get_result()
                    sample.update({key: result[key] for key in ('algorithm_trace', 'graph', 'computation_inputs') if key in result})
                if item['kind'] == 'visual':
                    image = f'assets/samples/{name}-{language}-{difficulty}-{variant}.png'
                    save_task_image(task,WEB / image)
                    sample['image'] = image
                samples.append(sample)
    print(f'{name}: 60 samples', flush=True)

# Render all images and use the matching prompt/answer in the catalog.
preview_dir = WEB / 'assets' / 'previews'
preview_dir.mkdir(parents=True, exist_ok=True)
for item in tasks:
    if item['kind'] != 'visual': continue
    random.seed(3)
    task = ALL_VISUAL_TASK_GENERATORS[item['id']](language='ru', difficulty=3)
    save_task_image(task,preview_dir / f"{item['id']}.png")
    item.update(example=task.description, answer=str(task.final_answer), steps=task.solution_steps,
                image=f"assets/previews/{item['id']}.png")

payload = dict(tasks=tasks, samples=samples, counts=dict(Counter(t['family'] for t in tasks)),
               provenance=dict(text=len(ALL_TASK_GENERATORS), visual=len(ALL_VISUAL_TASK_GENERATORS),
                               samples=len(samples), featured=featured, variants=3, catalog='examples/catalog.html', registry='re_rl/tasks/generators.py'))
write_text(WEB / 'data.js','window.RE_RL_DATA = ' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(json.dumps({'counts': payload['counts'], 'samples_generated': len(samples), 'self_verification_passed': sum(s['self_score'] == 1.0 for s in samples), 'previews_rendered': len(ALL_VISUAL_TASK_GENERATORS)}, ensure_ascii=False))
