import random

from re_rl.tasks.math.logic.find_the_error_task import FindTheErrorTask


def test_generation_and_registration():
    from re_rl.tasks.registry import registry
    from re_rl.tasks.generators import ALL_TASK_GENERATORS

    assert "find_the_error" in registry
    assert "find_the_error" in ALL_TASK_GENERATORS

    task = FindTheErrorTask.generate_random_task(language="ru", difficulty=4)
    assert task.description
    assert task.final_answer
    assert 1 <= int(task.final_answer) <= task.num_steps


def test_exactly_one_error_step():
    random.seed(1)
    task = FindTheErrorTask.generate_random_task(difficulty=5)
    wrong = [i for i, (a, op, b, shown, correct) in enumerate(task._steps, start=1) if shown != correct]
    assert wrong == [int(task.final_answer)]


def test_verify():
    random.seed(2)
    task = FindTheErrorTask.generate_random_task(difficulty=3)
    assert task.verify(f"<answer>{task.final_answer}</answer>") == 1.0
    # Ответ «Шаг N» тоже засчитывается (извлекается число).
    assert task.verify(f"<answer>Шаг {task.final_answer}</answer>") == 1.0
    wrong = str((int(task.final_answer) % task.num_steps) + 1)
    if wrong != task.final_answer:
        assert task.verify(f"<answer>{wrong}</answer>") == 0.0


def test_bilingual():
    for lang in ("ru", "en"):
        task = FindTheErrorTask.generate_random_task(language=lang, difficulty=2)
        assert task.description
        assert task.verify(str(task.final_answer)) == 1.0
