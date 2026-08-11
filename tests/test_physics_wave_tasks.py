"""Тесты для новой волны физических задач (16 типов).

Проверяем регистрацию, самосогласованность (эталон засчитывается), устойчивость
проверки к подписям вида «R1 =», а также отклонение неверных ответов и
корректную работу на всех уровнях сложности и обоих языках.
"""

import random

import numpy as np
import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


def _seed(s=0):
    random.seed(s)
    np.random.seed(s)


NEW_PHYSICS_TYPES = [
    "statics_equilibrium", "circular_dynamics", "rolling_motion",
    "kinetic_theory", "thermal_expansion", "blackbody_radiation",
    "standing_waves", "sound_intensity", "beats",
    "kirchhoff_laws", "rl_circuits", "gauss_law", "transformer",
    "relativistic_energy", "velocity_addition", "radiation_pressure",
]


@pytest.mark.parametrize("task_type", NEW_PHYSICS_TYPES)
def test_registered_globally(task_type):
    assert task_type in ALL_TASK_GENERATORS
    assert task_type in ALL_PHYSICS_TASK_GENERATORS


@pytest.mark.parametrize("task_type", NEW_PHYSICS_TYPES)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    _seed(difficulty)
    for _ in range(6):
        task = ALL_PHYSICS_TASK_GENERATORS[task_type](language=language, difficulty=difficulty)
        task.solve()
        assert task.final_answer is not None
        assert len(task.solution_steps) >= 1
        # Описание не должно содержать неподставленных плейсхолдеров.
        assert "{" not in task.description
        assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)


@pytest.mark.parametrize("task_type", NEW_PHYSICS_TYPES)
def test_wrong_answer_rejected(task_type):
    _seed(2)
    task = ALL_PHYSICS_TASK_GENERATORS[task_type](language="ru", difficulty=5)
    assert task.verify("<answer>-987654.321</answer>") < 1.0


def test_label_digits_do_not_break_verification():
    """Подписи вида «R1»/«R2» не должны портить извлечение чисел ответа."""
    _seed(7)
    task = ALL_PHYSICS_TASK_GENERATORS["statics_equilibrium"](
        task_type="beam_supports", language="ru", difficulty=5)
    task.solve()
    r1, r2 = task._answer_numbers
    # Ответ модели с иными подписями, но верными значениями.
    ans = f"реакции опор: слева {r1:.4f} Н, справа {r2:.4f} Н"
    assert task.verify(f"<answer>{ans}</answer>") == pytest.approx(1.0)


def test_beats_symmetric():
    _seed(11)
    task = ALL_PHYSICS_TASK_GENERATORS["beats"](language="en", difficulty=3)
    task.solve()
    beat = abs(task.f1 - task.f2)
    assert task.verify(f"<answer>{beat} Hz</answer>") == pytest.approx(1.0)
