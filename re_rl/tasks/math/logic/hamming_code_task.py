"""HammingCodeTask — код Хэмминга (7,4) и расстояние Хэмминга.

Подтипы:
- ``encode``    — по 4 битам данных построить 7-битное кодовое слово (чётная чётность);
- ``syndrome``  — номер ошибочной позиции (1..7) или 0, если слово корректно;
- ``distance``  — расстояние Хэмминга между двумя битовыми строками.

Позиции нумеруются слева направо с 1. Биты чётности — в позициях 1, 2, 4
и покрывают позиции, в двоичной записи которых установлен соответствующий бит.
Биты данных d1 d2 d3 d4 стоят в позициях 3, 5, 6, 7.
"""

import random
import re
from typing import Any, ClassVar, Dict

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class HammingCodeTask(BaseMathTask):
    TASK_TYPE = "hamming_code"
    TASK_TYPES = ["encode", "syndrome", "distance"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"length": 6}, 2: {"length": 8}, 3: {"length": 8}, 4: {"length": 12},
        5: {"length": 12}, 6: {"length": 16}, 7: {"length": 20}, 8: {"length": 24},
        9: {"length": 28}, 10: {"length": 32},
    }

    _DATA_POS = (3, 5, 6, 7)
    _PARITY = (1, 2, 4)

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.length = int(p["length"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    @classmethod
    def encode_data(cls, data: str) -> str:
        bits = [0] * 8
        for bit, pos in zip(data, cls._DATA_POS):
            bits[pos] = int(bit)
        for p in cls._PARITY:
            bits[p] = sum(bits[i] for i in range(1, 8) if i & p) % 2
        return "".join(str(bits[i]) for i in range(1, 8))

    @classmethod
    def syndrome(cls, word: str) -> int:
        b = [0] + [int(c) for c in word]
        pos = 0
        for p in cls._PARITY:
            if sum(b[i] for i in range(1, 8) if i & p) % 2:
                pos += p
        return pos

    @staticmethod
    def hamming_distance(a: str, b: str) -> int:
        return sum(x != y for x, y in zip(a, b))

    def _build(self):
        if self.task_type == "distance":
            self.a = "".join(random.choice("01") for _ in range(self.length))
            self.b = "".join(random.choice("01") for _ in range(self.length))
            self.answer = self.hamming_distance(self.a, self.b)
            return
        self.data = "".join(random.choice("01") for _ in range(4))
        code = list(self.encode_data(self.data))
        if self.task_type == "encode":
            self.word = "".join(code)
            self.answer = self.word
            return
        if random.random() < 0.8:
            pos = random.randint(1, 7)
            code[pos - 1] = "0" if code[pos - 1] == "1" else "1"
        self.word = "".join(code)
        self.answer = self.syndrome(self.word)

    def _convention(self, ru: bool) -> str:
        return (("Код Хэмминга (7,4), чётная чётность. Позиции слева направо с 1; биты чётности "
                 "в позициях 1, 2, 4 покрывают те позиции, в номере которых этот бит установлен. "
                 "Данные d1 d2 d3 d4 стоят в позициях 3, 5, 6, 7.") if ru else
                ("Hamming (7,4) code, even parity. Positions run left to right from 1; parity bits "
                 "at 1, 2 and 4 cover positions whose index has that bit set. Data bits d1 d2 d3 d4 "
                 "sit at positions 3, 5, 6, 7."))

    def _descr(self, language):
        ru = language == "ru"
        if self.task_type == "distance":
            return ((f"Найдите расстояние Хэмминга между строками {self.a} и {self.b} "
                     f"(число позиций, в которых биты различаются).") if ru else
                    (f"Find the Hamming distance between {self.a} and {self.b} "
                     f"(the number of positions where the bits differ)."))
        head = self._convention(ru)
        if self.task_type == "encode":
            ask = ((f"Постройте кодовое слово для данных {self.data}. Ответ — 7 бит.") if ru else
                   (f"Build the codeword for data {self.data}. Answer with 7 bits."))
        else:
            ask = ((f"В слове {self.word} не больше одной ошибки. Укажите номер ошибочной позиции "
                    f"(1..7) или 0, если слово корректно.") if ru else
                   (f"The word {self.word} has at most one error. Give the index of the flipped "
                    f"bit (1..7), or 0 if the word is valid."))
        return f"{head} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "distance":
            diff = [str(i + 1) for i, (x, y) in enumerate(zip(self.a, self.b)) if x != y]
            where = (", ".join(diff) if diff else ("нет" if ru else "none"))
            step = ((f"Биты различаются в позициях: {where}.") if ru else
                    (f"Bits differ at positions: {where}."))
            self.final_answer = str(self.answer)
        elif self.task_type == "encode":
            step = ((f"Данные в позициях 3, 5, 6, 7, биты чётности дополняют покрытие до чётности. "
                     f"Слово: {self.answer}.") if ru else
                    (f"Data goes to positions 3, 5, 6, 7; parity bits make each check even. "
                     f"Codeword: {self.answer}."))
            self.final_answer = self.answer
        else:
            checks = []
            b = [0] + [int(c) for c in self.word]
            for p in self._PARITY:
                covered = [i for i in range(1, 8) if i & p]
                bit = sum(b[i] for i in covered) % 2
                checks.append(f"p{p}={bit}")
            step = ((f"Проверки чётности: {', '.join(checks)}. Синдром = {self.answer}.") if ru else
                    (f"Parity checks: {', '.join(checks)}. Syndrome = {self.answer}."))
            self.final_answer = str(self.answer)
        self.solution_steps = [step, (f"Ответ: {self.final_answer}." if ru else
                                      f"Answer: {self.final_answer}.")]

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "encode":
            txt = U.clean(prediction).replace(" ", "").replace("_", "")
            runs = re.findall(r"[01]+", txt)
            if not runs:
                return 0.0
            cand = max(runs, key=len)
            return 1.0 if cand == self.answer else 0.0
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
