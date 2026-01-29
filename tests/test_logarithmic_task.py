import pytest
import math
from re_rl.tasks.logarithmic_task import LogarithmicTask

def test_logarithmic_task_ru():
    """Тест логарифмического уравнения на русском языке"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=1)
    result = task.get_result()
    
    assert "2*log(3*x) + 1 = 5" in result["problem"]
    assert len(result["solution_steps"]) == 1
    assert len(result["explanations"]) == 1
    assert len(result["validations"]) == 1
    
def test_logarithmic_task_en():
    """Тест логарифмического уравнения на английском языке"""
    task = LogarithmicTask(2, 3, 1, 5, language="en", detail_level=1)
    result = task.get_result()
    
    assert "2*log(3*x) + 1 = 5" in result["problem"]
    assert len(result["solution_steps"]) == 1
    assert len(result["explanations"]) == 1
    assert len(result["validations"]) == 1
    
def test_logarithmic_task_detail_level_2():
    """Тест логарифмического уравнения с уровнем детализации 2"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=2)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 2
    assert len(result["explanations"]) == 2
    assert len(result["validations"]) == 2
    assert "Анализируем уравнение" in result["solution_steps"][1]
    
def test_logarithmic_task_detail_level_3():
    """Тест логарифмического уравнения с уровнем детализации 3"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=3)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 3
    assert len(result["explanations"]) == 3
    assert len(result["validations"]) == 3
    assert "Переносим свободный член" in result["solution_steps"][2]
    
def test_logarithmic_task_detail_level_4():
    """Тест логарифмического уравнения с уровнем детализации 4"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=4)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 4
    assert len(result["explanations"]) == 4
    assert len(result["validations"]) == 4
    assert "Делим обе части на" in result["solution_steps"][3]
    
def test_logarithmic_task_detail_level_5():
    """Тест логарифмического уравнения с уровнем детализации 5"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=5)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 5
    assert len(result["explanations"]) == 5
    assert len(result["validations"]) == 5
    assert "Применяем экспоненту" in result["solution_steps"][4]
    
def test_logarithmic_task_detail_level_6():
    """Тест логарифмического уравнения с уровнем детализации 6"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=6)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 6
    assert len(result["explanations"]) == 6
    assert len(result["validations"]) == 6
    assert "Решаем относительно x" in result["solution_steps"][5]
    
def test_logarithmic_task_detail_level_7():
    """Тест логарифмического уравнения с уровнем детализации 7"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=7)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 7
    assert len(result["explanations"]) == 7
    assert len(result["validations"]) == 7
    assert "Проверяем решение" in result["solution_steps"][6]
    
def test_logarithmic_task_detail_level_8():
    """Тест логарифмического уравнения с уровнем детализации 8"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=8)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 8
    assert len(result["explanations"]) == 8
    assert len(result["validations"]) == 8
    assert "Геометрическая интерпретация" in result["solution_steps"][7]
    
def test_logarithmic_task_detail_level_9():
    """Тест логарифмического уравнения с уровнем детализации 9"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=9)
    result = task.get_result()
    
    assert len(result["solution_steps"]) == 9
    assert len(result["explanations"]) == 9
    assert len(result["validations"]) == 9
    assert "Проверяем область определения" in result["solution_steps"][8]
    
def test_logarithmic_task_solution():
    """Тест корректности решения логарифмического уравнения"""
    task = LogarithmicTask(2, 3, 1, 5, language="ru", detail_level=6)
    result = task.get_result()
    
    # Проверяем, что решение найдено
    assert result["final_answer"] is not None, "Решение не должно быть None"
    
    # Проверяем, что решение удовлетворяет уравнению
    x = float(result["final_answer"])
    # Подставляем решение в исходное уравнение: 2*log(3*x) + 1 = 5
    assert abs(2 * math.log(3 * x) + 1 - 5) < 1e-10, "Решение не удовлетворяет уравнению"
