"""EpisodeCutTask — обрыв эпизода в момент цели.

Награда шага, где состояние впервые равно цели, ещё входит. Дальше награды не берутся.
Если цель не встретилась, входит вся сумма.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def cut_trace(states: Sequence[int], rewards: Sequence[int], goal: int) -> List[Tuple[int, int, int]]:
    kept = 0
    full = 0
    stopped = 0
    done = False
    trace = []
    for index, (state, reward) in enumerate(zip(states, rewards), 1):
        full += reward
        if not done:
            kept += reward
            if state == goal:
                done = True
                stopped = index
        trace.append((kept, full, stopped))
    return trace


class EpisodeCutTask(BaseMathTask):
    TASK_TYPE = "episode_cut"
    TASK_TYPES = ["kept", "stop"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.states = [random.randint(0, 4) for _ in range(self.n)]
        self.rewards = [random.randint(-2, 3) for _ in range(self.n)]
        self.goal = random.randint(0, 4)
        self.trace = cut_trace(self.states, self.rewards, self.goal)
        self.kept = self.trace[-1][0]
        self.stop = self.trace[-1][2]
        self.answer = self.kept if self.task_type == "kept" else self.stop
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        states = ", ".join(str(state) for state in self.states)
        rewards = ", ".join(str(reward) for reward in self.rewards)
        key = "s0" if self.task_type == "kept" else "s1"
        return texts.t(key, language, n=self.n, states=states, rewards=rewards, goal=self.goal)

    def solve(self):
        steps = []
        for index, (state, reward, (kept, full, stopped)) in enumerate(
            zip(self.states, self.rewards, self.trace), 1
        ):
            steps.append(texts.t(
                "s2", self.language, i=index, state=state, reward=reward,
                kept=kept, full=full, stop=stopped,
            ))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
