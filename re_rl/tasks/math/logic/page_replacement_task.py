"""PageReplacementTask — число отказов страниц (page faults).

Подтипы:
- ``fifo`` — первым вытесняется самый давно загруженный;
- ``lru``  — вытесняется тот, к кому дольше всего не обращались;
- ``opt``  — вытесняется страница, чьё следующее обращение дальше всех
  (при равенстве — страница с меньшим номером).

Обязательные загрузки в пустые кадры тоже считаются отказами.
"""

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
        ru = language == "ru"
        seq = " ".join(map(str, self.refs))
        rules = {
            "fifo": ("FIFO: вытесняется страница, загруженная раньше всех." if ru else
                     "FIFO: evict the page that was loaded earliest."),
            "lru": ("LRU: вытесняется страница, к которой дольше всего не обращались." if ru else
                    "LRU: evict the page that has gone unused the longest."),
            "opt": ("OPT: вытесняется страница, чьё следующее обращение дальше всех; "
                    "при равенстве — страница с меньшим номером." if ru else
                    "OPT: evict the page whose next reference is farthest; ties go to the "
                    "smaller page number."),
        }[self.task_type]
        return ((f"Кадров памяти: {self.frames_n}. Последовательность обращений: {seq}. {rules} "
                 f"Сколько будет отказов страниц? Загрузка в пустой кадр тоже считается отказом.")
                if ru else
                (f"Memory frames: {self.frames_n}. Reference string: {seq}. {rules} "
                 f"How many page faults occur? Loading into an empty frame counts as a fault."))

    def solve(self):
        ru = self.language == "ru"
        marked = " ".join(self.trace)
        self.solution_steps = [
            (("Звёздочка — отказ. Кадры после каждого обращения:" if ru else
              "A star marks a fault. Frames after each reference:") + " " + marked),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
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
