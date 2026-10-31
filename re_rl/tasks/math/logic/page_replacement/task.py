"""PageReplacementTask — число отказов страниц (page faults).

Подтипы:
- ``fifo`` — первым вытесняется самый давно загруженный;
- ``lru``  — вытесняется тот, к кому дольше всего не обращались;
- ``opt``  — вытесняется страница, чьё следующее обращение дальше всех
  (при равенстве — страница с меньшим номером).

Обязательные загрузки в пустые кадры тоже считаются отказами.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class PageReplacementTask(BaseMathTask):
    TASK_TYPE = "page_replacement"
    TASK_TYPES = ["fifo", "lru", "opt"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"frames": 2, "length": 6, "pages": 3},
        2: {"frames": 2, "length": 7, "pages": 3},
        3: {"frames": 3, "length": 8, "pages": 4},
        4: {"frames": 3, "length": 9, "pages": 4},
        5: {"frames": 3, "length": 10, "pages": 4},
        6: {"frames": 3, "length": 12, "pages": 5},
        7: {"frames": 3, "length": 13, "pages": 5},
        8: {"frames": 4, "length": 14, "pages": 5},
        9: {"frames": 4, "length": 15, "pages": 6},
        10: {"frames": 4, "length": 16, "pages": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.frames_n = int(p["frames"])
        self.length = int(p["length"])
        self.n_pages = int(p["pages"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.refs = [random.randint(1, self.n_pages) for _ in range(self.length)]
        self.answer, self.trace = self.simulate(self.refs, self.frames_n, self.task_type)

    @staticmethod
    def simulate(refs: List[int], cap: int, policy: str) -> Tuple[int, List[str]]:
        frames: List[int] = []
        faults = 0
        trace = []
        for i, page in enumerate(refs):
            if page in frames:
                if policy == "lru":
                    frames.remove(page)
                    frames.append(page)
                trace.append(f"{page}->[{','.join(map(str, frames))}]")
                continue
            faults += 1
            if len(frames) < cap:
                frames.append(page)
            elif policy in ("fifo", "lru"):
                frames.pop(0)
                frames.append(page)
            else:  # opt: дальше следующее обращение, при равенстве меньший номер
                def nxt(pg: int) -> int:
                    for j in range(i + 1, len(refs)):
                        if refs[j] == pg:
                            return j
                    return len(refs) + 1

                victim = max(frames, key=lambda pg: (nxt(pg), -pg))
                frames[frames.index(victim)] = page
            trace.append(f"{page}*->[{','.join(map(str, frames))}]")
        return faults, trace

    def _descr(self, language):
        seq = " ".join(map(str, self.refs))
        rules = {
            "fifo": ((texts.t('s1', language))),
            "lru": ((texts.t('s2', language))),
            "opt": ((texts.t('s3', language))),
        }[self.task_type]
        return ((texts.t('s0', language, frames_n=self.frames_n, seq=seq, rules=rules)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        marked = " ".join(self.trace)
        self.solution_steps = [
            (((texts.t('s4', self.language))) + " " + marked),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
