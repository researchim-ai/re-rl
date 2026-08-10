from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.multiple_choice import (
    to_multiple_choice,
    format_choice_prompt,
    verify_choice,
)


def _make(task_type="arithmetic", difficulty=3):
    task = ALL_TASK_GENERATORS[task_type](language="ru", difficulty=difficulty)
    task.get_result()
    return task


def test_structure_and_uniqueness():
    task = _make()
    mc = to_multiple_choice(task, num_options=4, seed=7)
    assert len(mc["options"]) == 4
    assert len(mc["labels"]) == 4
    # Правильный ответ присутствует ровно на своей позиции.
    assert mc["options"][mc["correct_index"]] == mc["answer"]
    assert mc["correct_label"] == mc["labels"][mc["correct_index"]]
    # Все варианты уникальны.
    assert len(set(mc["options"])) == len(mc["options"])


def test_reproducible_with_seed():
    task = _make()
    a = to_multiple_choice(task, num_options=4, seed=42)
    b = to_multiple_choice(task, num_options=4, seed=42)
    assert a["options"] == b["options"]
    assert a["correct_label"] == b["correct_label"]


def test_verify_choice_letter_and_value():
    task = _make()
    mc = to_multiple_choice(task, num_options=4, seed=3)
    assert verify_choice(f"<answer>{mc['correct_label']}</answer>", mc) == 1.0
    assert verify_choice(f"<answer>{mc['answer']}</answer>", mc) == 1.0
    wrong_label = next(l for l in mc["labels"] if l != mc["correct_label"])
    assert verify_choice(f"<answer>{wrong_label}</answer>", mc) == 0.0


def test_format_prompt_contains_options():
    task = _make()
    mc = to_multiple_choice(task, num_options=4, seed=1)
    text = format_choice_prompt(mc)
    for label, opt in zip(mc["labels"], mc["options"]):
        assert f"{label}) {opt}" in text
