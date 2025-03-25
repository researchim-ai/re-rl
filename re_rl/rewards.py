import re
import math
from typing import Optional, List, Dict, Union

##############################################################################
# 1) Утилиты для извлечения chain-of-thought (reasoning) и финального ответа #
##############################################################################

def extract_reasoning_and_answer(full_text: str) -> (str, str):
    """
    Ищем:
      <reasoning>
         ... некий текст ...
      </reasoning>
      <answer>
         ... финальный ответ ...
      </answer>
    Возвращаем (reasoning_text, answer_text).
    Если не нашли теги, возвращаем ("", full_text) или ("", ""), зависит от стратегии.

    Можем дополнить проверки на хитрые попытки (reward hack), 
    например, если теги дублируются, добавлять штраф.
    """
    # Простейший шаблон:
    reasoning_pat = re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL)
    answer_pat    = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)

    reasoning_match = reasoning_pat.search(full_text)
    answer_match    = answer_pat.search(full_text)

    reasoning_str = reasoning_match.group(1).strip() if reasoning_match else ""
    answer_str    = answer_match.group(1).strip() if answer_match else ""

    return (reasoning_str, answer_str)

def check_format_compliance(full_text: str) -> float:
    """
    Проверяем, что текст содержит ровно ОДИН блок <reasoning>...</reasoning>
    и ровно ОДИН блок <answer>...</answer>, без вложенностей, повторений и т.п.
    Чем сложнее проверки, тем труднее модели «обмануть» логику.

    Если всё ок, вернём +0.2, иначе 0. (Примерный вес.)
    """
    # Можно считать количество вхождений:
    num_reasoning_open  = full_text.count("<reasoning>")
    num_reasoning_close = full_text.count("</reasoning>")
    num_answer_open     = full_text.count("<answer>")
    num_answer_close    = full_text.count("</answer>")

    if (num_reasoning_open == 1 and 
        num_reasoning_close == 1 and
        num_answer_open == 1 and
        num_answer_close == 1):
        return 0.2
    else:
        return 0.0


##############################################################################
# 2) Парсеры финальных ответов (для разных задач)                           #
##############################################################################

def parse_linear_answer(text: str) -> Optional[float]:
    """
    Линейная задача обычно 1 корень. Пример: 'x = 2.0' или просто '2'.
    Более надёжный способ – искать float в строке, но если несколько – 
    берём, скажем, первый.
    """
    # Удаляем лишние слова, типа "x =", "ответ:" и т.д.
    # Затем пытаемся float.
    # Или ищем все числа:
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    if not nums:
        return None
    # Предположим, берём первое как ответ
    try:
        val = float(nums[0])
        return val
    except:
        return None

def parse_list_of_floats(text: str) -> List[float]:
    """
    Универсальная функция: ищет все вещественные числа. 
    Возвращает список float (может быть пустым).
    """
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    return [float(n) for n in nums]

def parse_quadratic_answer(text: str) -> Optional[List[float]]:
    """
    Для квадратного уравнения: хотим 2 корня (возможно 1, если корни совпадают).
    Но LLM может вывести 0,1,2 корней, 
    Возвращаем список float (множество корней). 
    """
    parsed = parse_list_of_floats(text)
    return parsed if parsed else None

def parse_cubic_answer(text: str) -> Optional[List[float]]:
    """
    Аналогично, но 3 (или 1..3) корня. 
    """
    parsed = parse_list_of_floats(text)
    return parsed if parsed else None

def parse_urn_probability_answer(text: str) -> Optional[float]:
    """
    UrnProbabilityTask: вероятность (0..1). 
    Модель может вывести '0.1234' или '0.99'.
    Если число за пределами [0,1], можно решить давать 0 reward 
    (или clamp).
    """
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    if not nums:
        return None
    val = float(nums[0])
    if val < 0 or val > 1.0001:
        # Можно дать штраф, но пока просто None
        return None
    return val

def parse_knights_knaves_answer(text: str) -> Optional[Dict[str, str]]:
    """
    'Аня: лжец, Борис: правдивый, Ваня: лжец'
    Пытаемся собрать словарь: { 'Аня': 'лжец', 'Борис': 'правдивый', ... }.
    Или 'Alice: liar, Bob: knight, Charlie: liar'.
    """
    # грубо:
    pairs = re.findall(r"([\wА-яЁё]+)\s*:\s*([\wА-яЁё]+)", text)
    if not pairs:
        return None
    role_map = {}
    for name, role in pairs:
        role_map[name] = role.lower()
    return role_map

def parse_futoshiki_answer(text: str) -> Optional[List[List[int]]]:
    """
    Ищем решение (N x N). 
    Пример: 
      1 3 2 4
      2 4 1 3
      ...
    """
    lines = text.strip().split("\n")
    matrix = []
    for line in lines:
        row_nums = re.findall(r"\d+", line)
        if row_nums:
            row = [int(x) for x in row_nums]
            matrix.append(row)
    if matrix:
        return matrix
    else:
        return None

def parse_graph_answer(text: str) -> str:
    """
    Графовую задачу парсить детально сложно, т.к. решения разные:
    - Кратчайший путь: "Final path: [1,2,3]"
    - MST: "Edges: (1,2), (2,3), ..."
    - ...
    Здесь можно вернуть сырую строку и потом что-то сравнивать, 
    либо делать хитрую логику.
    """
    return text.strip()

def parse_contradiction_answer(text: str) -> str:
    """
    ContradictionTask: "False statement: Солнце вращается вокруг Земли"
    """
    # Грубый поиск:
    m = re.search(r"[Ff]alse statement[:\-]*\s*(.+)$", text)
    if m:
        return m.group(1).strip()
    # Или если ничего не нашли, вернём сам текст, 
    return text.strip()

def parse_text_stats_answer(text: str) -> Optional[int]:
    """
    TextStatsTask: итог — целое число вхождений. 
    """
    nums = re.findall(r"\d+", text)
    if not nums:
        return None
    return int(nums[0])

def parse_system_linear_answer(text: str) -> Optional[List[float]]:
    """
    Для SystemLinearTask: "x1=2.00, x2=1.00"
    Сформируем список [2.0, 1.0] и сравним с эталоном.
    """
    # Ищем шаблон x\d\s*=\s*число
    pairs = re.findall(r"x(\d+)\s*=\s*([-+]?\d+(?:\.\d+)?)", text)
    # Вернём [значения] в порядке x1, x2, ...
    if not pairs:
        # Может, модель просто вывела (2,1)
        floats = parse_list_of_floats(text)
        return floats if floats else None

    # pairs = [('1','2.00'), ('2','1.00')]
    # Сортируем по индексу var, потом берем float
    pairs_sorted = sorted(pairs, key=lambda x: int(x[0]))
    return [float(p[1]) for p in pairs_sorted]


##############################################################################
# 3) Сравнение корректности (final_answer) с «правильным»                    #
##############################################################################

def reward_linear(ref_val: Optional[float], pred_val: Optional[float]) -> float:
    if ref_val is None or pred_val is None:
        return 0.0
    # Примем за «правильное», если ошибка < 1e-4
    diff = abs(ref_val - pred_val)
    if diff < 1e-4:
        return 1.0
    elif diff < 0.1:
        return 0.5  # «почти»
    else:
        return 0.0

def reward_polynomial_roots(ref_roots: Optional[List[float]], pred_roots: Optional[List[float]], tol=1e-3) -> float:
    """
    Для квадратных/кубических. Пример: ref_roots=[2,3], pred_roots=[1.9999,3.01].
    Сортируем, сравниваем размер, затем покомпонентно. 
    Можно дать partial credit за совпадение некоторых корней.
    """
    if not ref_roots or not pred_roots:
        return 0.0
    ref_sorted = sorted(ref_roots)
    pred_sorted = sorted(pred_roots)

    matched = 0
    used_pred = [False]*len(pred_sorted)

    for r in ref_sorted:
        # ищем pred, близкий к r
        best_idx = None
        best_dist = float('inf')
        for i, pp in enumerate(pred_sorted):
            if not used_pred[i]:
                dist = abs(r - pp)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
        if best_idx is not None and best_dist < tol:
            matched += 1
            used_pred[best_idx] = True

    # matched = сколько корней совпало 
    # max(len(ref_sorted), len(pred_sorted)) — общее число 
    fraction = matched / max(len(ref_sorted), len(pred_sorted))
    # например, полностью совпали => fraction=1 => reward=1
    return fraction

def reward_float(ref_val: Optional[float], pred_val: Optional[float], tol=1e-3) -> float:
    """
    Напр., UrnProbabilityTask, если |pred - ref|<tol => 1. 
    Если чуть больше, можно 0.5. 
    """
    if ref_val is None or pred_val is None:
        return 0.0
    diff = abs(ref_val - pred_val)
    if diff < tol:
        return 1.0
    elif diff < 0.05:
        return 0.5
    else:
        return 0.0

def reward_knights_knaves(ref_map: Optional[Dict[str,str]], pred_map: Optional[Dict[str,str]]) -> float:
    """
    Считаем, сколько персонажей совпало. 
    fraction = (# fully correct) / (# in ref)
    """
    if not ref_map or not pred_map:
        return 0.0
    correct = 0
    total = len(ref_map)
    for name, role in ref_map.items():
        pred_role = pred_map.get(name, "")
        if pred_role == role:
            correct += 1
    return correct / total

def reward_futoshiki(ref_matrix: Optional[List[List[int]]], pred_matrix: Optional[List[List[int]]]) -> float:
    """
    Сравниваем полностью. Optionally, можно проверить частичное совпадение.
    """
    if not ref_matrix or not pred_matrix:
        return 0.0
    R = len(ref_matrix)
    if len(pred_matrix) != R:
        return 0.0
    C = len(ref_matrix[0])

    correct_cells = 0
    total_cells = R*C
    for r in range(R):
        if len(pred_matrix[r]) != C:
            return 0.0
        for c in range(C):
            if ref_matrix[r][c] == pred_matrix[r][c]:
                correct_cells += 1

    fraction = correct_cells / total_cells
    # Можно возвращать fraction: полностью совпало =>1, частично =>0.3..., 
    return fraction

def reward_contradiction(ref_str: str, pred_str: str) -> float:
    """
    Если финальная строка (ложное утверждение) совпадает точно => 1
    Иначе 0. 
    Можно fuzzy match, 
    но риск reward hacking (модель вставит substring).
    """
    if not ref_str.strip() or not pred_str.strip():
        return 0.0
    if ref_str.strip().lower() == pred_str.strip().lower():
        return 1.0
    return 0.0

def reward_text_stats(ref_count: Optional[int], pred_count: Optional[int]) -> float:
    """
    Для TextStatsTask: целое число вхождений. 
    Если точно совпало =>1, ±1 => 0.5, и т.д.
    """
    if ref_count is None or pred_count is None:
        return 0.0
    diff = abs(ref_count - pred_count)
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.7
    elif diff == 2:
        return 0.3
    else:
        return 0.0

def reward_system_linear(ref_vec: Optional[List[float]], pred_vec: Optional[List[float]]) -> float:
    """
    Система: x1..xn. 
    Проверяем pokomponentno. 
    """
    if not ref_vec or not pred_vec:
        return 0.0
    matched = 0
    n = max(len(ref_vec), len(pred_vec))
    for i in range(min(len(ref_vec), len(pred_vec))):
        if abs(ref_vec[i] - pred_vec[i]) < 1e-3:
            matched += 1
    return matched / n

def reward_default_str(ref_str: str, pred_str: str) -> float:
    """
    Если хочется точное совпадение.
    Или, при желании, partial match, 
    или ключевые слова. 
    """
    r = ref_str.strip().lower()
    p = pred_str.strip().lower()
    if r == p:
        return 1.0
    else:
        return 0.0


##############################################################################
# 4) Обобщённая функция: parse + compare + (дополнительно) chain-of-thought  #
##############################################################################

def parse_ref_answer(task_type: str, text: str):
    """
    Парсим "правильный" ответ (из датасета) — можно без chain-of-thought.
    """
    tt = task_type.lower()
    if tt == "linear":
        return parse_linear_answer(text)
    elif tt == "quadratic":
        return parse_quadratic_answer(text)
    elif tt == "cubic":
        return parse_cubic_answer(text)
    elif tt == "urn_probability":
        return parse_urn_probability_answer(text)
    elif tt == "knights_knaves":
        return parse_knights_knaves_answer(text)
    elif tt == "futoshiki":
        return parse_futoshiki_answer(text)
    elif tt == "graph":
        return parse_graph_answer(text)  # строка
    elif tt == "contradiction":
        return parse_contradiction_answer(text)
    elif tt == "text_stats":
        return parse_text_stats_answer(text)
    elif tt == "system_linear":
        return parse_system_linear_answer(text)
    else:
        return text.strip()  # default

def parse_pred_answer(task_type: str, text: str):
    """
    Парсим модельный ответ. 
    (Сюда же можем «жёстче» относится: если LLM заспамила 100 чисел, 
    обрезать. Или искать сигнатуры обмана.)
    """
    return parse_ref_answer(task_type, text)

def compare_answers(task_type: str, ref_parsed, pred_parsed) -> float:
    """
    Считаем итоговую «корректность» для финального ответа.
    """
    tt = task_type.lower()
    if tt == "linear":
        return reward_linear(ref_parsed, pred_parsed)
    elif tt in ["quadratic", "cubic"]:
        return reward_polynomial_roots(ref_parsed, pred_parsed)
    elif tt == "urn_probability":
        return reward_float(ref_parsed, pred_parsed, 1e-4)
    elif tt == "knights_knaves":
        return reward_knights_knaves(ref_parsed, pred_parsed)
    elif tt == "futoshiki":
        return reward_futoshiki(ref_parsed, pred_parsed)
    elif tt == "graph":
        # Можно как-то сравнить? Если dataloader хранит реальный ответ => default
        return reward_default_str(ref_parsed, pred_parsed)
    elif tt == "contradiction":
        return reward_contradiction(ref_parsed, pred_parsed)
    elif tt == "text_stats":
        return reward_text_stats(ref_parsed, pred_parsed)
    elif tt == "system_linear":
        return reward_system_linear(ref_parsed, pred_parsed)
    else:
        return reward_default_str(str(ref_parsed), str(pred_parsed))


def chain_of_thought_reward(task_type: str, reasoning_str: str, problem_str: str) -> float:
    """
    Дополнительный reward за вменяемый chain-of-thought:
     - упоминает ли ключевые слова из problem_str
     - имеет ли длину > X
     - и т.д.

    Чтобы избежать reward hacking, можно проверять осмысленные паттерны:
     - Наличие чисел, если задача numeric
     - N >= 3 предложений
     - ...

    Здесь — лишь пример.
    """
    r = reasoning_str.strip().lower()
    if len(r.split()) < 5:
        return 0.0  # очень короткая цепочка
    # Пример: Если task_type = 'linear', проверим наличие 'x' 'a' 'b' 'c'...
    # ...
    return 0.1  # за "наличие цепочки"


###########################################
# 5) Финальная «главная» reward-функция   #
###########################################

def compute_reward_for_task(
    task_type: str,
    problem_text: str,
    ref_final_answer: str,
    model_output_text: str
) -> float:
    """
    1) Проверяем формат (reasoning/answer) => format_score
    2) Извлекаем reasoning, answer
    3) Считаем chain-of-thought score
    4) Парсим ref_answer и pred_answer
    5) Сравниваем => correctness
    6) Суммируем в итог.

    Все коэффициенты можно тюнить.
    """

    # (1) format check
    fmt_score = check_format_compliance(model_output_text)

    # (2) extract reasoning + final ans
    reasoning_str, final_answer_str = extract_reasoning_and_answer(model_output_text)

    # (3) chain-of-thought reward
    cot_score = chain_of_thought_reward(task_type, reasoning_str, problem_text)

    # (4) parse
    ref_parsed  = parse_ref_answer(task_type, ref_final_answer)
    pred_parsed = parse_pred_answer(task_type, final_answer_str)

    # (5) correctness
    correctness_score = compare_answers(task_type, ref_parsed, pred_parsed)

    # (6) Итого (пример):
    #   correctness ~ базис, format + cot ~ небольшие бонусы
    total = correctness_score + fmt_score + cot_score
    # например, clamp [0..1.5], чтобы не росло бесконечно, 
    # но это уже опционально
    return total

def reward_format_check(prompts, completions, answer, **kwargs) -> List[float]:
    """
    Проверяем, что в ответе есть ОДИН блок <reasoning>...</reasoning> и ОДИН <answer>...</answer>.
    Если всё ок, +0.2. Иначе 0. 
    """
    rewards = []
    batch_size = len(prompts)

    for b in range(batch_size):
        gen_list = completions[b]  # список dict'ов (num_generations)
        for c in gen_list:
            text = c["content"]
            count_reason_open  = text.count("<reasoning>")
            count_reason_close = text.count("</reasoning>")
            count_ans_open     = text.count("<answer>")
            count_ans_close    = text.count("</answer>")
            if (count_reason_open == 1 and 
                count_reason_close == 1 and
                count_ans_open == 1 and
                count_ans_close == 1):
                rewards.append(0.2)
            else:
                rewards.append(0.0)
    return rewards


def reward_cot_quality(prompts, completions, answer, **kwargs) -> List[float]:
    """
    Пример: даём небольшой бонус, если chain-of-thought содержит хотя бы 5 слов,
    упоминает что-то из условия задачи, и т.д.

    (Логика просто демонстрационная.)
    """
    rewards = []
    batch_size = len(prompts)

    for b in range(batch_size):
        user_msg = prompts[b][-1]
        problem_text = user_msg.get("metadata", {}).get("problem", "")
        gen_list = completions[b]
        for c in gen_list:
            text = c["content"]
            # Вырежем reasoning:
            reasoning_str, final_ans_str = extract_reasoning_and_answer(text)
            words_count = len(reasoning_str.split())

            sc = 0.0
            if words_count >= 5:
                sc += 0.1
            # Можно ещё проверить, что reasoning содержит хотя бы одно слово из problem_text
            # if any(word in reasoning_str for word in problem_text.split()):
            #    sc += 0.05

            rewards.append(sc)
    return rewards


def reward_correctness(prompts, completions, answer, **kwargs) -> List[float]:
    """
    Вызываем compute_reward_for_task(...) для каждого ответа.
    """
    rewards = []
    batch_size = len(prompts)

    for b in range(batch_size):
        user_msg = prompts[b][-1]
        meta = user_msg.get("metadata", {})
        task_type = meta.get("task_type", "unknown")
        problem_text = meta.get("problem", "")
        ref_final_answer = meta.get("ref_final_answer", "")

        gen_list = completions[b]
        # answer[b] обычно список из num_generations одинаковых эталонов
        for c in gen_list:
            model_output = c["content"]
            score = compute_reward_for_task(
                task_type = task_type,
                problem_text = problem_text,
                ref_final_answer = ref_final_answer,
                model_output_text = model_output
            )
            rewards.append(score)
    return rewards