import re
import math
from typing import Optional, List, Dict, Union, Any
from rich import print
##############################################################################
# 1) Утилиты для извлечения chain-of-thought (reasoning) и финального ответа #
##############################################################################

def extract_reasoning_and_answer(full_text: str) -> (str, str):
    """
    Ищем:
      <reasoning>...</reasoning>
      <answer>...</answer>

    Возвращаем (reasoning_text, answer_text).
    Если что-то не нашли — вернём пустые строки.
    """
    reasoning_pat = re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL)
    answer_pat    = re.compile(r"<answer>(.*?)</answer>", re.DOTALL)

    reasoning_match = reasoning_pat.search(full_text)
    answer_match    = answer_pat.search(full_text)

    reasoning_str = reasoning_match.group(1).strip() if reasoning_match else ""
    answer_str    = answer_match.group(1).strip() if answer_match else ""

    return (reasoning_str, answer_str)

def check_format_compliance(full_text: str) -> float:
    """
    Проверяем, что текст содержит ровно ОДИН <reasoning>...</reasoning>
    и ровно ОДИН <answer>...</answer>, без повторов.
    Если всё ок, +0.2, иначе 0.
    """
    num_reason_open  = full_text.count("<reasoning>")
    num_reason_close = full_text.count("</reasoning>")
    num_ans_open     = full_text.count("<answer>")
    num_ans_close    = full_text.count("</answer>")
    if (num_reason_open == 1 and 
        num_reason_close == 1 and
        num_ans_open == 1 and
        num_ans_close == 1):
        return 0.2
    else:
        return 0.0

##############################################################################
# 2) Парсеры финальных ответов (для разных типов задач)
##############################################################################

def parse_linear_answer(text: str) -> Optional[float]:
    """
    Для линейной задачи (a*x+b=c) — обычно 1 корень (float). 
    Ищем первое попавшееся число.
    """
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    if not nums:
        return None
    try:
        return float(nums[0])
    except:
        return None

def parse_list_of_floats(text: str) -> List[float]:
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    return [float(n) for n in nums]

def parse_quadratic_answer(text: str) -> Optional[List[float]]:
    """
    Возвращаем список корней (0..2).
    """
    # Ищем числа в формате x1 = 1, x2 = -1 или просто 1, -1
    pairs = re.findall(r"x\d+\s*=\s*([-+]?\d+(?:\.\d+)?)", text)
    if pairs:
        return [float(p) for p in pairs[:2]]
    
    # Если не нашли в формате x1=..., ищем просто числа
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    if not nums:
        return None
    return [float(n) for n in nums[:2]]

def parse_cubic_answer(text: str) -> Optional[List[float]]:
    """
    Аналогично — список корней (0..3).
    """
    vals = parse_list_of_floats(text)
    return vals if vals else None

def parse_urn_probability_answer(text: str) -> Optional[float]:
    """
    Должно быть число 0..1.
    """
    nums = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
    if not nums:
        return None
    val = float(nums[0])
    if val<0 or val>1.0001:
        return None
    return val

def parse_knights_knaves_answer(answer_text: str) -> Optional[Dict[str, str]]:
    """
    Парсит ответ для задачи рыцарей и лжецов.
    
    Args:
        answer_text: Текст ответа в формате "name1: role1, name2: role2, ..."
        
    Returns:
        Optional[Dict[str, str]]: Словарь с ролями или None в случае ошибки
    """
    if not answer_text:
        return None
        
    try:
        roles = {}
        pairs = answer_text.split(",")
        for pair in pairs:
            name, role = pair.strip().split(":")
            roles[name.strip().lower()] = role.strip().lower()
        return roles
    except:
        return None

def parse_futoshiki_answer(text: str) -> Optional[List[List[int]]]:
    """
    Матрица чисел NxN (1..N).
    """
    lines = text.strip().split("\n")
    matrix = []
    for line in lines:
        row_nums = re.findall(r"\d+", line)
        if row_nums:
            matrix.append([int(x) for x in row_nums])
    return matrix if matrix else None

def parse_graph_answer(text: str) -> str:
    """
    Оставим как сырую строку.
    """
    return text.strip()

def parse_contradiction_answer(text: str) -> str:
    """
    "False statement: <...>"
    """
    m = re.search(r"[Ff]alse statement[:\-]*\s*(.+)$", text)
    if m:
        return m.group(1).strip()
    return text.strip()

def parse_text_stats_answer(text: str) -> Optional[int]:
    """
    Целое число вхождений.
    """
    nums = re.findall(r"\d+", text)
    if not nums:
        return None
    return int(nums[0])

def parse_system_linear_answer(text: str) -> Optional[List[float]]:
    """
    "x1=2.00, x2=1.00" => [2.0,1.0]
    Или в тексте 2,1
    """
    pairs = re.findall(r"x(\d+)\s*=\s*([-+]?\d+(?:\.\d+)?)", text)
    if not pairs:
        # fallback: ищем float'ы
        floats = parse_list_of_floats(text)
        return floats if floats else None
    # сортируем
    pairs_sorted = sorted(pairs, key=lambda x: int(x[0]))
    return [float(p[1]) for p in pairs_sorted]

##############################################################################
# 3) Функции сравнения "корректности" финального ответа
##############################################################################

def reward_linear(ref_val: Optional[float], pred_val: Optional[float]) -> float:
    if ref_val is None or pred_val is None:
        return 0.0
    diff = abs(ref_val - pred_val)
    if diff < 1e-4:
        return 1.0
    elif diff < 0.5:  # Увеличиваем порог для частичного совпадения
        return 0.5
    else:
        return 0.0

def reward_polynomial_roots(ref_roots: Optional[List[float]], pred_roots: Optional[List[float]], tol=1e-3) -> float:
    """
    partial credit, если часть корней совпала.
    """
    if not ref_roots or not pred_roots:
        return 0.0
    ref_sorted = sorted(ref_roots)
    pred_sorted = sorted(pred_roots)

    matched = 0
    used_pred = [False]*len(pred_sorted)
    for r in ref_sorted:
        best_idx = None
        best_dist = 999999
        for i, pp in enumerate(pred_sorted):
            if not used_pred[i]:
                dist = abs(r - pp)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
        if best_idx is not None and best_dist < tol:
            matched += 1
            used_pred[best_idx] = True
    fraction = matched / max(len(ref_sorted), len(pred_sorted))
    return fraction

def reward_float(ref_val: Optional[float], pred_val: Optional[float], tol=1e-3) -> float:
    if ref_val is None or pred_val is None:
        return 0.0
    diff = abs(ref_val - pred_val)
    if diff < tol:
        return 1.0
    elif diff < 0.05:
        return 0.5
    return 0.0

def reward_knights_knaves(ref_answer: str, pred_answer: str) -> float:
    """
    Вычисляет награду для задачи рыцарей и лжецов.
    
    Args:
        ref_answer: Строка с эталонным ответом в формате <reasoning>...</reasoning><answer>...</answer>
        pred_answer: Строка с предсказанным ответом в формате <reasoning>...</reasoning><answer>...</answer>
    
    Returns:
        float: Награда от 0 до 1
    """
    # Извлекаем рассуждения и ответы
    ref_reasoning, ref_answer = extract_reasoning_and_answer(ref_answer)
    pred_reasoning, pred_answer = extract_reasoning_and_answer(pred_answer)
    
    if not ref_answer or not pred_answer:
        return 0.0
        
    # Парсим роли из ответов
    ref_roles = parse_knights_knaves_answer(ref_answer)
    pred_roles = parse_knights_knaves_answer(pred_answer)
    
    if not ref_roles or not pred_roles:
        return 0.0
        
    # Проверяем точное совпадение ролей
    if ref_roles == pred_roles:
        return 1.0
    
    # Проверяем частичное совпадение ролей
    correct_roles = sum(1 for name, role in ref_roles.items() 
                       if name in pred_roles and pred_roles[name] == role)
    role_score = correct_roles / len(ref_roles)
    
    return role_score

def reward_futoshiki(ref_matrix: Optional[List[List[int]]], pred_matrix: Optional[List[List[int]]]) -> float:
    if not ref_matrix or not pred_matrix:
        return 0.0
    R = len(ref_matrix)
    if len(pred_matrix)!=R:
        return 0.0
    C = len(ref_matrix[0])
    correct_cells = 0
    total = R*C
    for r in range(R):
        if len(pred_matrix[r])!=C:
            return 0.0
        for c in range(C):
            if ref_matrix[r][c]==pred_matrix[r][c]:
                correct_cells+=1
    return correct_cells/total

def reward_contradiction(ref_answer: str, pred_answer: str) -> float:
    """
    Вычисляет награду для задачи противоречий.
    
    Args:
        ref_answer: Эталонное утверждение
        pred_answer: Предсказанное утверждение
    
    Returns:
        float: Награда от 0 до 1
    """
    if not ref_answer or not pred_answer:
        return 0.0
        
    # Нормализуем строки
    ref_answer = ref_answer.strip().lower()
    pred_answer = pred_answer.strip().lower()
    
    return 1.0 if ref_answer == pred_answer else 0.0

def reward_text_stats(ref_count: Optional[int], pred_count: Optional[int]) -> float:
    if ref_count is None or pred_count is None:
        return 0.0
    diff = abs(ref_count - pred_count)
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.7
    else:
        return 0.0  # Возвращаем 0 для больших различий

def reward_system_linear(ref_vec: Optional[List[float]], pred_vec: Optional[List[float]]) -> float:
    if not ref_vec or not pred_vec:
        return 0.0
    matched=0
    n = max(len(ref_vec), len(pred_vec))
    for i in range(min(len(ref_vec), len(pred_vec))):
        if abs(ref_vec[i]-pred_vec[i])<1e-3:
            matched+=1
    return matched/n

def reward_default_str(ref_str: str, pred_str: str) -> float:
    """
    Точное равенство строк (при желании можно fuzzy).
    """
    if ref_str.strip().lower()==pred_str.strip().lower():
        return 1.0
    return 0.0


##############################################################################
# 4) parse / compare для "Только проверка конечного результата"
##############################################################################

def parse_ref_answer(task_type: str, text: str):
    """
    Возвращаем Python-структуру (число, список, матрицу...).
    Без chain-of-thought. 
    """
    tt = task_type.lower()
    if tt=="linear":
        return parse_linear_answer(text)
    elif tt=="quadratic":
        return parse_quadratic_answer(text)
    elif tt=="cubic":
        return parse_cubic_answer(text)
    elif tt=="urn_probability":
        return parse_urn_probability_answer(text)
    elif tt=="knights_knaves":
        return parse_knights_knaves_answer(text)
    elif tt=="futoshiki":
        return parse_futoshiki_answer(text)
    elif tt=="graph":
        return parse_graph_answer(text)
    elif tt=="contradiction":
        return parse_contradiction_answer(text)
    elif tt=="text_stats":
        return parse_text_stats_answer(text)
    elif tt=="system_linear":
        return parse_system_linear_answer(text)
    return text.strip()

def compare_answers(task_type: str, ref_val: Any, pred_val: Any) -> float:
    """
    Сравнивает ответы в зависимости от типа задачи.
    
    Args:
        task_type: Тип задачи
        ref_val: Эталонное значение
        pred_val: Предсказанное значение
        
    Returns:
        float: Оценка корректности от 0 до 1
    """
    if ref_val is None or pred_val is None:
        return 0.0
        
    if task_type == "linear":
        # Для линейного уравнения сравниваем числа
        try:
            ref_num = float(ref_val)
            pred_num = float(pred_val)
            return 1.0 if abs(ref_num - pred_num) < 1e-6 else 0.0
        except:
            return 0.0
    elif task_type == "knights_knaves":
        # Для задачи рыцарей и лжецов сравниваем роли
        ref_roles = parse_knights_knaves_answer(ref_val)
        pred_roles = parse_knights_knaves_answer(pred_val)
        if not ref_roles or not pred_roles:
            return 0.0
        return 1.0 if ref_roles == pred_roles else 0.0
    elif task_type == "contradiction":
        # Для задачи противоречий сравниваем утверждения
        return 1.0 if ref_val.strip().lower() == pred_val.strip().lower() else 0.0
    else:
        return 1.0 if ref_val == pred_val else 0.0


def compute_correctness_score(task_type: str, ref_answer: str, pred_answer: str) -> float:
    """
    Вычисляет оценку корректности ответа.
    
    Args:
        task_type: Тип задачи
        ref_answer: Эталонный ответ
        pred_answer: Предсказанный ответ
        
    Returns:
        float: Оценка корректности от 0 до 1
    """
    if task_type == "knights_knaves":
        return reward_knights_knaves(ref_answer, pred_answer)
        
    # Извлекаем ответ из предсказания, если он в формате с reasoning
    _, pred_final = extract_reasoning_and_answer(pred_answer)
    if not pred_final:  # Если не нашли в формате reasoning, используем как есть
        pred_final = pred_answer
        
    # Для противоречий используем весь текст ответа
    if task_type == "contradiction":
        ref_final = ref_answer
    else:
        # Для остальных задач пытаемся извлечь ответ из формата с reasoning
        _, ref_final = extract_reasoning_and_answer(ref_answer)
        if not ref_final:  # Если не нашли, используем как есть
            ref_final = ref_answer
            
    return compare_answers(task_type, ref_final, pred_final)

def extract_answer_value(task_type: str, answer: str) -> Any:
    """
    Извлекает значение из ответа в зависимости от типа задачи.
    
    Args:
        task_type: Тип задачи
        answer: Ответ
        
    Returns:
        Any: Извлеченное значение
    """
    if task_type == "linear":
        # Для линейного уравнения извлекаем число
        match = re.search(r"<answer>(\d+(?:\.\d+)?)</answer>", answer)
        if match:
            return float(match.group(1))
        return None
    elif task_type == "knights_knaves":
        # Для задачи рыцарей и лжецов извлекаем роли
        match = re.search(r"<answer>(.*?)</answer>", answer)
        if match:
            return match.group(1)
        return None
    elif task_type == "contradiction":
        # Для задачи противоречий извлекаем утверждение
        match = re.search(r"<answer>(.*?)</answer>", answer)
        if match:
            return match.group(1)
        return None
    else:
        return answer

##############################################################################
# 5) ОТДЕЛЬНЫЕ ФУНКЦИИ-РЕВАРДЫ
##############################################################################

def reward_format_check(prompts, completions, answer, **kwargs) -> List[float]:
    """
    Смотрим, есть ли ОДИН <reasoning>...</reasoning> и ОДИН <answer>...</answer>.
    => +0.2 или 0.
    """
    rewards = []
    batch_size = len(prompts)
    for b in range(batch_size):
        gen_list = completions[b]
        for c in gen_list:
            text = c["content"]
            sc = check_format_compliance(text)
            rewards.append(sc)
    return rewards


def reward_cot_quality(prompts, completions, answer, **kwargs) -> List[float]:
    """
    Мини-бонус, если chain-of-thought > 5 слов, etc.
    """
    rewards = []
    batch_size = len(prompts)
    for b in range(batch_size):
        user_msg = prompts[b][-1]
        # problem_text = user_msg.get("metadata", {}).get("problem","") # если нужно
        gen_list = completions[b]
        for c in gen_list:
            text = c["content"]
            reasoning_str, _ = extract_reasoning_and_answer(text)
            words = reasoning_str.strip().split()
            sc = 0.0
            if len(words)>=5:
                sc += 0.1
            rewards.append(sc)
    return rewards


def reward_correctness(prompts, completions, answer, **kwargs) -> List[float]:
    """
    ONLY проверяем итоговый ответ на правильность.
    Не учитываем формат, не учитываем CoT.
    """
    rewards = []
    batch_size = len(prompts)
    for b in range(batch_size):
        system_msg = prompts[b][0]
        user_msg = prompts[b][-1]
        meta = user_msg.get("metadata", {})
        task_type = meta.get("task_type", "unknown")
        ref_answer = meta.get("ref_final_answer", "")

        question = prompts[b][-1]["content"]
        # answer[b] – список одинаковых эталонов (длиной num_generations)
        # (либо возьмём meta["ref_final_answer"])
        ref_ans = answer[b] # предполагаем, что answer[b] одинаков
        # -> "ref_ans" — строка
        gen_list = completions[b]
        # answer[b] (эталон) обычно совпадает, но 
        # берём всё равно meta["ref_final_answer"].
        for c in gen_list:
            model_text = c["content"]
            print("-"*20)
            print(f"System:\n{system_msg}")
            print(f"Question:\n{question}")
            print(f"\nRef answer:\n{ref_ans}")
            print(f"\nModel response :\n{model_text}")
            # if extracted_ans:
            #     print(f"\nExtracted answer:\n{extracted_ans}")
            print("-"*20)
            model_output = c["content"]
            sc = compute_correctness_score(
                task_type,
                ref_answer,
                model_output
            )
            rewards.append(sc)
    return rewards
