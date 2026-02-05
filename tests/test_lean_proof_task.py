# tests/test_lean_proof_task.py
"""
Тесты для LeanProofTask — генерации формальных доказательств.
"""

import pytest
from re_rl.tasks.formal import (
    LeanProofTask,
    generate_lean_proof_task,
    THEOREM_TEMPLATES,
    get_theorem_categories,
)
from re_rl.tasks.formal.lean_proof_task import generate_lean_proof_batch
from re_rl.tasks.formal.theorem_templates import (
    TheoremTemplate,
    get_random_template,
    get_templates_by_difficulty,
)


class TestTheoremTemplates:
    """Тесты для шаблонов теорем."""
    
    def test_categories_exist(self):
        """Проверяем, что есть категории теорем."""
        categories = get_theorem_categories()
        assert len(categories) >= 4
        assert "propositional" in categories
        assert "nat_arithmetic" in categories
        assert "predicate" in categories
        assert "equality" in categories
    
    def test_templates_have_required_fields(self):
        """Проверяем, что все шаблоны имеют необходимые поля."""
        for category, templates in THEOREM_TEMPLATES.items():
            for template in templates:
                assert template.name, f"Template in {category} missing name"
                assert template.theorem, f"{template.name} missing theorem"
                assert template.proof, f"{template.name} missing proof"
                assert template.natural_statement, f"{template.name} missing natural_statement"
                assert "ru" in template.natural_statement or "en" in template.natural_statement
                assert 1 <= template.difficulty <= 10
    
    def test_get_random_template(self):
        """Тест получения случайного шаблона."""
        template = get_random_template()
        assert isinstance(template, TheoremTemplate)
        assert template.theorem
        assert template.proof
    
    def test_get_random_template_by_category(self):
        """Тест получения шаблона по категории."""
        template = get_random_template(category="propositional")
        assert template.category == "propositional"
    
    def test_get_templates_by_difficulty(self):
        """Тест фильтрации по сложности."""
        easy_templates = get_templates_by_difficulty(min_diff=1, max_diff=2)
        assert all(t.difficulty <= 2 for t in easy_templates)
        
        hard_templates = get_templates_by_difficulty(min_diff=5, max_diff=10)
        assert all(t.difficulty >= 5 for t in hard_templates)


class TestLeanProofTask:
    """Тесты для LeanProofTask."""
    
    def test_from_difficulty_creates_task(self):
        """Тест создания задачи по сложности."""
        task = LeanProofTask.from_difficulty(difficulty=3, language="ru")
        assert task.theorem_statement
        assert task.category
    
    def test_solve_fills_solution_steps(self):
        """Тест решения задачи."""
        task = LeanProofTask.from_difficulty(difficulty=2, language="ru")
        task.solve()
        
        assert task.solution_steps
        assert task.final_answer
        assert task.proof
    
    def test_get_result_returns_dict(self):
        """Тест получения результата."""
        task = LeanProofTask.from_difficulty(difficulty=3, language="en")
        result = task.get_result()
        
        assert isinstance(result, dict)
        assert result["task_type"] == "lean_proof"
        assert "theorem_statement" in result
        assert "proof" in result
        assert "solution_steps" in result
        assert "final_answer" in result
    
    def test_to_sft_format(self):
        """Тест конвертации в SFT формат."""
        task = LeanProofTask.from_difficulty(difficulty=2, language="ru")
        task.solve()
        sft = task.to_sft_format()
        
        assert "instruction" in sft
        assert "input" in sft
        assert "output" in sft
        assert "metadata" in sft
        assert sft["metadata"]["task_type"] == "lean_proof"
    
    def test_to_chat_format(self):
        """Тест конвертации в Chat формат."""
        task = LeanProofTask.from_difficulty(difficulty=2, language="en")
        task.solve()
        chat = task.to_chat_format()
        
        assert "messages" in chat
        assert len(chat["messages"]) == 3
        assert chat["messages"][0]["role"] == "system"
        assert chat["messages"][1]["role"] == "user"
        assert chat["messages"][2]["role"] == "assistant"
    
    def test_different_difficulties(self):
        """Тест разных уровней сложности."""
        for difficulty in [1, 3, 5, 7, 10]:
            task = LeanProofTask.from_difficulty(difficulty=difficulty, language="ru")
            task.solve()
            assert task.final_answer
    
    def test_different_languages(self):
        """Тест разных языков."""
        for lang in ["ru", "en"]:
            task = LeanProofTask.from_difficulty(difficulty=3, language=lang)
            task.solve()
            assert task.description  # Должно быть на соответствующем языке
    
    def test_specific_category(self):
        """Тест создания задачи из конкретной категории."""
        task = LeanProofTask.from_difficulty(
            difficulty=5, 
            language="ru",
            category="nat_arithmetic"
        )
        assert task.category == "nat_arithmetic"


class TestGenerators:
    """Тесты для функций-генераторов."""
    
    def test_generate_lean_proof_task(self):
        """Тест основной функции генерации."""
        task = generate_lean_proof_task(difficulty=3, language="ru")
        assert isinstance(task, LeanProofTask)
        task.solve()
        assert task.final_answer
    
    def test_generate_lean_proof_batch(self):
        """Тест batch генерации."""
        tasks = generate_lean_proof_batch(
            num_samples=5,
            difficulties=[1, 2, 3],
            language="ru"
        )
        assert len(tasks) == 5
        for task in tasks:
            assert task.final_answer  # Все задачи уже решены


class TestLeanSyntax:
    """Тесты корректности Lean синтаксиса."""
    
    def test_theorem_starts_with_keyword(self):
        """Теоремы должны начинаться с theorem."""
        for category, templates in THEOREM_TEMPLATES.items():
            for template in templates:
                assert template.theorem.strip().startswith("theorem"), \
                    f"{template.name}: theorem должен начинаться с 'theorem'"
    
    def test_theorem_ends_with_by(self):
        """Теоремы должны заканчиваться на := by."""
        for category, templates in THEOREM_TEMPLATES.items():
            for template in templates:
                assert ":= by" in template.theorem, \
                    f"{template.name}: theorem должен содержать ':= by'"
    
    def test_proof_not_empty(self):
        """Доказательства не должны быть пустыми."""
        for category, templates in THEOREM_TEMPLATES.items():
            for template in templates:
                assert template.proof.strip(), \
                    f"{template.name}: proof не должен быть пустым"
    
    def test_no_sorry_in_proofs(self):
        """Доказательства не должны содержать sorry."""
        for category, templates in THEOREM_TEMPLATES.items():
            for template in templates:
                assert "sorry" not in template.proof.lower(), \
                    f"{template.name}: proof не должен содержать 'sorry'"


class TestIntegrationWithGenerators:
    """Тесты интеграции с общими генераторами."""
    
    def test_lean_proof_in_all_generators(self):
        """lean_proof должен быть в ALL_TASK_GENERATORS."""
        from re_rl.tasks.generators import ALL_TASK_GENERATORS
        assert "lean_proof" in ALL_TASK_GENERATORS
    
    def test_generate_random_task_lean_proof(self):
        """Тест генерации через универсальный генератор."""
        from re_rl.tasks.generators import generate_random_task
        task = generate_random_task(task_type="lean_proof", language="ru")
        assert isinstance(task, LeanProofTask)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
