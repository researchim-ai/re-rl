import pytest
from re_rl.rewards import (
    extract_reasoning_and_answer,
    check_format_compliance,
    parse_linear_answer,
    parse_quadratic_answer,
    parse_cubic_answer,
    parse_urn_probability_answer,
    parse_knights_knaves_answer,
    parse_futoshiki_answer,
    parse_graph_answer,
    parse_contradiction_answer,
    parse_text_stats_answer,
    parse_system_linear_answer,
    reward_linear,
    reward_polynomial_roots,
    reward_float,
    reward_knights_knaves,
    reward_futoshiki,
    reward_contradiction,
    reward_text_stats,
    reward_system_linear,
    reward_default_str,
    parse_ref_answer,
    compare_answers,
    compute_correctness_score
)

# Тесты для extract_reasoning_and_answer
def test_extract_reasoning_and_answer():
    # Корректный случай
    text = "Some text <reasoning>This is reasoning</reasoning> More text <answer>42</answer>"
    reasoning, answer = extract_reasoning_and_answer(text)
    assert reasoning == "This is reasoning"
    assert answer == "42"

    # Отсутствующие теги
    text = "Just some text"
    reasoning, answer = extract_reasoning_and_answer(text)
    assert reasoning == ""
    assert answer == ""

    # Множественные теги (должны взять первые)
    text = "<reasoning>First</reasoning><reasoning>Second</reasoning><answer>1</answer><answer>2</answer>"
    reasoning, answer = extract_reasoning_and_answer(text)
    assert reasoning == "First"
    assert answer == "1"

# Тесты для check_format_compliance
def test_check_format_compliance():
    # Корректный случай
    text = "<reasoning>Test</reasoning><answer>42</answer>"
    assert check_format_compliance(text) == 0.2

    # Отсутствующие теги
    text = "Just some text"
    assert check_format_compliance(text) == 0.0

    # Дублирующиеся теги
    text = "<reasoning>First</reasoning><reasoning>Second</reasoning><answer>1</answer>"
    assert check_format_compliance(text) == 0.0

# Тесты для парсеров ответов
def test_parse_linear_answer():
    assert parse_linear_answer("x = 42") == 42.0
    assert parse_linear_answer("Answer: -3.14") == -3.14
    assert parse_linear_answer("No numbers here") is None

def test_parse_quadratic_answer():
    assert parse_quadratic_answer("x1 = 1, x2 = -1") == [1.0, -1.0]
    assert parse_quadratic_answer("No roots") is None

def test_parse_urn_probability_answer():
    assert parse_urn_probability_answer("P = 0.5") == 0.5
    assert parse_urn_probability_answer("Probability = 1.0") == 1.0
    assert parse_urn_probability_answer("P = 1.5") is None  # > 1
    assert parse_urn_probability_answer("P = -0.1") is None  # < 0

def test_parse_knights_knaves_answer():
    assert parse_knights_knaves_answer("Alice: knight, Bob: liar") == {
        "alice": "knight",
        "bob": "liar"
    }
    assert parse_knights_knaves_answer("Invalid format") is None

def test_parse_futoshiki_answer():
    text = "1 2 3\n4 5 6\n7 8 9"
    expected = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert parse_futoshiki_answer(text) == expected
    assert parse_futoshiki_answer("Invalid") is None

# Тесты для функций начисления наград
def test_reward_linear():
    assert reward_linear(42.0, 42.0) == 1.0
    assert reward_linear(42.0, 42.1) == 0.5
    assert reward_linear(42.0, 43.0) == 0.0
    assert reward_linear(None, 42.0) == 0.0
    assert reward_linear(42.0, None) == 0.0

def test_reward_polynomial_roots():
    assert reward_polynomial_roots([1.0, -1.0], [1.0, -1.0]) == 1.0
    assert reward_polynomial_roots([1.0, -1.0], [1.0, 0.0]) == 0.5
    assert reward_polynomial_roots([1.0, -1.0], [2.0, 3.0]) == 0.0
    assert reward_polynomial_roots(None, [1.0, -1.0]) == 0.0

def test_reward_knights_knaves():
    ref = "<reasoning>Analyzing statements</reasoning><answer>alice: knight, bob: liar</answer>"
    pred = "<reasoning>Analyzing statements</reasoning><answer>alice: knight, bob: liar</answer>"
    assert reward_knights_knaves(ref, pred) == 1.0

def test_reward_futoshiki():
    ref = [[1, 2], [3, 4]]
    pred = [[1, 2], [3, 4]]
    assert reward_futoshiki(ref, pred) == 1.0
    
    pred = [[1, 2], [3, 5]]
    assert reward_futoshiki(ref, pred) == 0.75
    
    pred = [[1, 2], [3]]
    assert reward_futoshiki(ref, pred) == 0.0

def test_reward_contradiction():
    assert reward_contradiction("Statement A", "Statement A") == 1.0
    assert reward_contradiction("Statement A", "Statement B") == 0.0
    assert reward_contradiction("", "") == 0.0

def test_reward_text_stats():
    assert reward_text_stats(42, 42) == 1.0
    assert reward_text_stats(42, 43) == 0.7
    assert reward_text_stats(42, 44) == 0.0
    assert reward_text_stats(None, 42) == 0.0

# Тесты для основных функций
def test_compute_correctness_score():
    # Тест для линейного уравнения
    ref_answer = "x = 42"
    model_output = "<reasoning>Solving step by step</reasoning><answer>42</answer>"
    score = compute_correctness_score("linear", ref_answer, model_output)
    assert 0 <= score <= 1
    
    # Тест для задачи рыцарей и лжецов
    ref_answer = "<reasoning>Analyzing statements</reasoning><answer>alice: knight, bob: liar</answer>"
    model_output = "<reasoning>Analyzing statements</reasoning><answer>alice: knight, bob: liar</answer>"
    score = compute_correctness_score("knights_knaves", ref_answer, model_output)
    assert score == 1.0
    
    # Тест для задачи противоречий
    ref_answer = "Statement 1 is false"
    model_output = "<reasoning>Analyzing contradictions</reasoning><answer>Statement 1 is false</answer>"
    score = compute_correctness_score("contradiction", ref_answer, model_output)
    assert score == 1.0

def test_compare_answers():
    # Тест для разных типов задач
    assert compare_answers("linear", 42.0, 42.0) == 1.0
    ref = "<reasoning>Analyzing statements</reasoning><answer>alice: knight</answer>"
    pred = "<reasoning>Analyzing statements</reasoning><answer>alice: knight</answer>"
    assert compare_answers("knights_knaves", ref, pred) == 1.0 