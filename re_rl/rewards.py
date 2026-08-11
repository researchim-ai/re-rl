import os
import re
import math
from fractions import Fraction
from typing import Optional, List, Dict, Union, Any, Tuple

try:
    from loguru import logger
except Exception:  # pragma: no cover - loguru всегда есть в зависимостях
    import logging

    logger = logging.getLogger("re_rl.rewards")

# Число с поддержкой знака, десятичной части и научной нотации (1.2e-3).
NUMBER_RE = r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"

# Если выставлено RE_RL_REWARD_DEBUG=1 — reward_correctness будет логировать
# запрос/ответ модели. По умолчанию выключено, чтобы не спамить stdout в RL.
_REWARD_DEBUG = os.getenv("RE_RL_REWARD_DEBUG", "0") == "1"


def _to_float(token: str) -> Optional[float]:
    """Преобразует токен в float, поддерживая дроби вида ``a/b`` и науч. нотацию."""
    token = token.strip()
    if not token:
        return None
    # Дробь a/b (но не деление в составе выражения — только «чистая» дробь)
    frac_match = re.fullmatch(r"([-+]?\d+)\s*/\s*(\d+)", token)
    if frac_match:
        try:
            return float(Fraction(int(frac_match.group(1)), int(frac_match.group(2))))
        except (ZeroDivisionError, ValueError):
            return None
    try:
        return float(token)
    except ValueError:
        return None


def coerce_float(value: Any) -> Optional[float]:
    """Пытается привести произвольное значение/строку к float.

    Поддерживает дроби (``3/4``), научную нотацию и извлекает первое число
    из более длинной строки. Возвращает ``None``, если число не найдено.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    # Сначала пробуем распарсить строку целиком (учитывает дроби).
    direct = _to_float(text)
    if direct is not None:
        return direct
    # Иначе ищем дробь внутри текста, затем первое число.
    frac_match = re.search(r"([-+]?\d+)\s*/\s*(\d+)", text)
    if frac_match:
        val = _to_float(frac_match.group(0))
        if val is not None:
            return val
    nums = re.findall(NUMBER_RE, text)
    if not nums:
        return None
    try:
        return float(nums[0])
    except ValueError:
        return None


def numbers_close(ref: Optional[float], pred: Optional[float], rel_tol: float = 1e-3, abs_tol: float = 1e-6) -> bool:
    """Сравнивает два числа с относительным и абсолютным допуском."""
    if ref is None or pred is None:
        return False
    return math.isclose(ref, pred, rel_tol=rel_tol, abs_tol=abs_tol)


def reward_numeric(ref_val: Any, pred_val: Any, rel_tol: float = 1e-3, abs_tol: float = 1e-6) -> float:
    """Универсальная числовая награда с допуском и частичным кредитом.

    Возвращает 1.0 при совпадении в пределах допуска, 0.5 при близком
    (в пределах 5% относительной ошибки) и 0.0 иначе.
    """
    ref = coerce_float(ref_val)
    pred = coerce_float(pred_val)
    if ref is None or pred is None:
        return 0.0
    if numbers_close(ref, pred, rel_tol=rel_tol, abs_tol=abs_tol):
        return 1.0
    denom = max(abs(ref), 1e-9)
    if abs(ref - pred) / denom < 0.05:
        return 0.5
    return 0.0


##############################################################################
# 1) Утилиты для извлечения chain-of-thought (reasoning) и финального ответа #
##############################################################################

def extract_reasoning_and_answer(full_text: str) -> Tuple[str, str]:
    """
    Ищем reasoning в двух совместимых форматах:
      <reasoning>...</reasoning> (legacy)
      <think>...</think>         (current)
    и:
      <answer>...</answer>

    Возвращаем (reasoning_text, answer_text).
    Если что-то не нашли — вернём пустые строки.
    """
    reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", full_text, re.DOTALL)
    if not reasoning_match:
        reasoning_match = re.search(r"<think>(.*?)</think>", full_text, re.DOTALL)
    answer_match = re.search(r"<answer>(.*?)</answer>", full_text, re.DOTALL)

    reasoning_str = reasoning_match.group(1).strip() if reasoning_match else ""
    answer_str = answer_match.group(1).strip() if answer_match else ""

    return (reasoning_str, answer_str)

def check_format_compliance(full_text: str) -> float:
    """
    Проверяем, что текст содержит ровно ОДИН reasoning-блок
    (<reasoning>...</reasoning> ИЛИ <think>...</think>)
    и ровно ОДИН <answer>...</answer>, без повторов.
    Если всё ок, +0.2, иначе 0.
    """
    reasoning_pairs = len(re.findall(r"<reasoning>.*?</reasoning>", full_text, re.DOTALL))
    think_pairs = len(re.findall(r"<think>.*?</think>", full_text, re.DOTALL))
    answer_pairs = len(re.findall(r"<answer>.*?</answer>", full_text, re.DOTALL))

    # Дополнительно контролируем "сырые" теги, чтобы отлавливать сломанный XML-подобный формат
    num_reason_open = full_text.count("<reasoning>")
    num_reason_close = full_text.count("</reasoning>")
    num_think_open = full_text.count("<think>")
    num_think_close = full_text.count("</think>")
    num_ans_open = full_text.count("<answer>")
    num_ans_close = full_text.count("</answer>")

    if (
        reasoning_pairs + think_pairs == 1
        and answer_pairs == 1
        and num_reason_open == num_reason_close
        and num_think_open == num_think_close
        and num_ans_open == num_ans_close
    ):
        return 0.2
    else:
        return 0.0

##############################################################################
# 2) Парсеры финальных ответов (для разных типов задач)
##############################################################################

def parse_linear_answer(text: str) -> Optional[float]:
    """
    Для линейной задачи (a*x+b=c) — обычно 1 корень (float).
    Поддерживает дроби, научную нотацию и извлекает первое число из текста.
    """
    return coerce_float(text)

def parse_list_of_floats(text: str) -> List[float]:
    nums = re.findall(NUMBER_RE, text)
    return [float(n) for n in nums]

def parse_quadratic_answer(text: str) -> Optional[List[float]]:
    """
    Возвращаем список корней (0..2).
    """
    # Ищем числа в формате x1 = 1, x2 = -1 или просто 1, -1
    pairs = re.findall(rf"x\d+\s*=\s*({NUMBER_RE})", text)
    if pairs:
        return [float(p) for p in pairs[:2]]
    
    # Если не нашли в формате x1=..., ищем просто числа
    nums = re.findall(NUMBER_RE, text)
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
    val = coerce_float(text)
    if val is None:
        return None
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

    # Роли на двух языках; используем для устойчивого извлечения пар из текста.
    role_words = ["рыцарь", "лжец", "knight", "liar", "knave"]
    role_alt = "|".join(role_words)
    pattern = re.compile(rf"([A-Za-zА-Яа-яЁё]+)\s*[:\-]\s*({role_alt})", re.IGNORECASE)
    found = pattern.findall(answer_text)
    if found:
        return {name.strip().lower(): role.strip().lower() for name, role in found}

    # Fallback: старый формат "name: role, name: role".
    try:
        roles = {}
        for pair in answer_text.split(","):
            name, role = pair.strip().split(":")
            roles[name.strip().lower()] = role.strip().lower()
        return roles
    except (ValueError, AttributeError):
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
    pairs = re.findall(rf"x(\d+)\s*=\s*({NUMBER_RE})", text)
    if not pairs:
        # fallback: ищем float'ы
        floats = parse_list_of_floats(text)
        return floats if floats else None
    # сортируем
    pairs_sorted = sorted(pairs, key=lambda x: int(x[0]))
    return [float(p[1]) for p in pairs_sorted]


def parse_probability_value(text: str) -> Optional[float]:
    """Parse first probability-like float from answer."""
    return coerce_float(text)


def parse_status_answer(text: str) -> str:
    """Normalize SAT/UNSAT/TRUE/FALSE style answers."""
    return text.strip().upper()


def sympy_equivalent(ref_str: str, pred_str: str) -> bool:
    """Проверяет символическую эквивалентность двух выражений через sympy.

    Поддерживает ``^`` как степень. Возвращает False при ошибке парсинга.
    """
    try:
        import sympy as sp
    except Exception:
        return False

    def _parse(s: str):
        s = str(s).strip().split(":")[-1].strip().rstrip(".").replace("^", "**")
        if not s:
            return None
        try:
            return sp.sympify(s, locals={"x": sp.Symbol("x"), "y": sp.Symbol("y")})
        except (sp.SympifyError, SyntaxError, TypeError, ValueError):
            return None

    a = _parse(ref_str)
    b = _parse(pred_str)
    if a is None or b is None:
        return False
    try:
        return sp.simplify(a - b) == 0
    except Exception:
        return False

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
    # Извлекаем рассуждения и ответы; если тегов нет — используем сырой текст.
    _, ref_extracted = extract_reasoning_and_answer(ref_answer)
    _, pred_extracted = extract_reasoning_and_answer(pred_answer)
    ref_answer = ref_extracted or ref_answer
    pred_answer = pred_extracted or pred_answer

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
    elif tt in {"bayesian_reasoning"}:
        return parse_probability_value(text)
    elif tt in {"sat_smt_mini", "proof_cases_counterexample", "propositional_logic", "regex_dfa", "inequality_proof"}:
        return parse_status_answer(text)
    elif tt in {"csp_reasoning", "graph_justification", "combinatorial_optimization",
                "symbolic_simplification", "symbolic_regression", "polynomial_factorization",
                "taylor_series", "partial_fractions", "partial_derivatives", "recurrence"}:
        return text.strip()
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
    elif task_type == "bayesian_reasoning":
        try:
            r = float(ref_val)
            p = float(pred_val)
            return 1.0 if abs(r - p) < 1e-3 else (0.5 if abs(r - p) < 5e-2 else 0.0)
        except Exception:
            return 0.0
    elif task_type in {"sat_smt_mini", "proof_cases_counterexample", "propositional_logic", "regex_dfa", "inequality_proof"}:
        return 1.0 if str(ref_val).strip().upper() == str(pred_val).strip().upper() else 0.0
    elif task_type in {"symbolic_simplification", "symbolic_regression", "polynomial_factorization",
                       "taylor_series", "partial_fractions", "partial_derivatives", "recurrence"}:
        # Любая математически эквивалентная форма ответа засчитывается.
        return 1.0 if sympy_equivalent(str(ref_val), str(pred_val)) else 0.0
    elif task_type in {"csp_reasoning", "graph_justification", "combinatorial_optimization"}:
        return 1.0 if str(ref_val).strip() == str(pred_val).strip() else 0.0
    else:
        # Точное совпадение (в т.ч. для строковых ответов).
        if ref_val == pred_val:
            return 1.0
        # Числовой fallback: покрывает физику, геометрию, calculus и прочие
        # типы с числовым ответом, для которых нет специального компаратора.
        ref_num = coerce_float(ref_val)
        pred_num = coerce_float(pred_val)
        if ref_num is not None and pred_num is not None:
            return reward_numeric(ref_num, pred_num)
        # Иначе — нормализованное сравнение строк.
        return 1.0 if str(ref_val).strip().lower() == str(pred_val).strip().lower() else 0.0


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
            
    # Общее правило: если текст ответа точно совпадает с эталоном — это верно.
    # Покрывает вырожденные случаи (например, ответ «Нет решения») и любые
    # типы, где эталон не парсится в число/структуру.
    if ref_final is not None and pred_final is not None:
        if str(ref_final).strip().lower() == str(pred_final).strip().lower():
            return 1.0

    ref_val = parse_ref_answer(task_type, ref_final)
    pred_val = parse_ref_answer(task_type, pred_final)
    return compare_answers(task_type, ref_val, pred_val)

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
        user_msg = prompts[b][-1]
        meta = user_msg.get("metadata", {})
        task_type = meta.get("task_type", "unknown")
        ref_answer = meta.get("ref_final_answer", "")

        ref_ans = answer[b]  # предполагаем, что answer[b] одинаков
        gen_list = completions[b]
        for c in gen_list:
            model_output = c["content"]
            if _REWARD_DEBUG:
                logger.debug(
                    "reward_correctness | task_type={} | ref={!r} | model={!r}",
                    task_type,
                    ref_ans,
                    model_output,
                )
            sc = compute_correctness_score(
                task_type,
                ref_answer,
                model_output
            )
            rewards.append(sc)
    return rewards
