import random

from re_rl.tasks.math.logic.propositional_logic_task import PropositionalLogicTask


def test_generation_and_registration():
    from re_rl.tasks.registry import registry
    from re_rl.tasks.generators import ALL_TASK_GENERATORS

    assert "propositional_logic" in registry
    assert "propositional_logic" in ALL_TASK_GENERATORS

    task = PropositionalLogicTask.generate_random_task(language="ru", difficulty=5)
    assert task.description
    assert task.final_answer in ("YES", "NO")


def test_verify_synonyms():
    random.seed(1)
    task = PropositionalLogicTask.generate_random_task(difficulty=4)
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0

    if task.final_answer == "YES":
        assert task.verify("<answer>да</answer>") == 1.0
        assert task.verify("<answer>true</answer>") == 1.0
        assert task.verify("<answer>нет</answer>") == 0.0
    else:
        assert task.verify("<answer>нет</answer>") == 1.0
        assert task.verify("<answer>false</answer>") == 1.0
        assert task.verify("<answer>да</answer>") == 0.0


def test_both_classes_appear():
    random.seed(0)
    labels = {PropositionalLogicTask.generate_random_task(difficulty=5).final_answer for _ in range(40)}
    assert labels == {"YES", "NO"}


def test_tautology_verdict_present():
    # Среди сгенерированных формул должны встречаться тавтологии (YES).
    verdicts = {
        PropositionalLogicTask.generate_random_task(difficulty=2).final_answer
        for _ in range(30)
    }
    assert "YES" in verdicts
