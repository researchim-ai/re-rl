# re_rl/tasks/formal/__init__.py
"""
Formal mathematics tasks - генерация теорем и доказательств в Lean 4.

Поддерживаемые категории:
- propositional: пропозициональная логика (∧, ∨, →, ¬)
- predicate: предикатная логика (∀, ∃)
- nat_arithmetic: арифметика натуральных чисел
- list_operations: операции над списками
- equality: свойства равенства

Пример использования:
    from re_rl.tasks.formal import LeanProofTask, generate_lean_proof_task
    
    # Создание задачи по сложности
    task = LeanProofTask.from_difficulty(difficulty=3, language="ru")
    task.solve()
    print(task.get_result())
    
    # Случайная генерация
    task = generate_lean_proof_task(difficulty=5, language="en")
"""

from re_rl.tasks.formal.lean_proof_task import (
    LeanProofTask,
    generate_lean_proof_task,
)
from re_rl.tasks.formal.theorem_templates import (
    THEOREM_TEMPLATES,
    get_theorem_categories,
)

__all__ = [
    "LeanProofTask",
    "generate_lean_proof_task",
    "THEOREM_TEMPLATES",
    "get_theorem_categories",
]
