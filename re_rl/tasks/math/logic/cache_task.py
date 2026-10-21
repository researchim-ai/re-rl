"""DirectMappedCacheTask — кэш прямого отображения.

Адрес разбирается целочисленно:
index = (addr // block_size) mod n_lines,
tag = (addr // block_size) // n_lines.
Кэш изначально пуст. Попадание — в строке index уже записан тот же tag.

Подтипы: ``hits``, ``misses``, ``tag`` (tag одного из адресов трассы).
"""

import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def locate(addr: int, block_size: int, n_lines: int) -> Tuple[int, int]:
    block = addr // block_size
    return block // n_lines, block % n_lines


def simulate(addrs: List[int], block_size: int, n_lines: int) -> Tuple[int, int, List[str]]:
    """Возвращает (hits, misses, трасса)."""
    cache: Dict[int, int] = {}
    hits = 0
    trace = []
    for addr in addrs:
        tag, index = locate(addr, block_size, n_lines)
        hit = cache.get(index) == tag
        if hit:
            hits += 1
        else:
            cache[index] = tag
        mark = "hit" if hit else "miss"
        trace.append(f"{addr}:{mark}(tag={tag},idx={index})")
    return hits, len(addrs) - hits, trace


class DirectMappedCacheTask(BaseMathTask):
    TASK_TYPE = "direct_mapped_cache"
    TASK_TYPES = ["hits", "misses", "tag"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"lines": 2, "block": 4, "length": 5},
        2: {"lines": 2, "block": 4, "length": 6},
        3: {"lines": 4, "block": 4, "length": 7},
        4: {"lines": 4, "block": 8, "length": 8},
        5: {"lines": 4, "block": 8, "length": 9},
        6: {"lines": 8, "block": 8, "length": 10},
        7: {"lines": 8, "block": 16, "length": 12},
        8: {"lines": 8, "block": 16, "length": 13},
        9: {"lines": 16, "block": 16, "length": 14},
        10: {"lines": 16, "block": 32, "length": 16},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n_lines = int(p["lines"])
        self.block_size = int(p["block"])
        self.length = int(p["length"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        n_blocks = self.n_lines * random.randint(2, 4)
        blocks = [random.randrange(n_blocks) for _ in range(self.length)]
        for i in range(1, self.length):
            if random.random() < 0.45:
                blocks[i] = blocks[random.randrange(i)]
        offsets = [random.randrange(self.block_size) for _ in range(self.length)]
        self.addrs = [b * self.block_size + o for b, o in zip(blocks, offsets)]
        self.hits, self.misses, self.trace = simulate(self.addrs, self.block_size, self.n_lines)
        if self.task_type == "hits":
            self.answer = self.hits
        elif self.task_type == "misses":
            self.answer = self.misses
        else:
            self.which = random.randrange(self.length)
            self.answer, _ = locate(self.addrs[self.which], self.block_size, self.n_lines)

    def _descr(self, language):
        ru = language == "ru"
        seq = " ".join(map(str, self.addrs))
        rule = ((f"Кэш прямого отображения: {self.n_lines} строк, размер блока {self.block_size} байт, "
                 f"изначально пуст. Для адреса addr: block = addr // {self.block_size}, "
                 f"index = block mod {self.n_lines}, tag = block // {self.n_lines}. "
                 f"Попадание, если в строке index уже лежит тот же tag; иначе это промах и tag записывается.")
                if ru else
                (f"Direct-mapped cache: {self.n_lines} lines, block size {self.block_size} bytes, "
                 f"initially empty. For an address addr: block = addr // {self.block_size}, "
                 f"index = block mod {self.n_lines}, tag = block // {self.n_lines}. "
                 f"It is a hit when line index already holds the same tag; otherwise it is a miss "
                 f"and the tag is stored."))
        seq_line = (f"Трасса адресов: {seq}." if ru else f"Address trace: {seq}.")
        if self.task_type == "hits":
            ask = ("Сколько попаданий?" if ru else "How many hits?")
        elif self.task_type == "misses":
            ask = ("Сколько промахов?" if ru else "How many misses?")
        else:
            addr = self.addrs[self.which]
            ask = (f"Какой tag у адреса {addr}?" if ru else f"What is the tag of address {addr}?")
        return f"{rule} {seq_line} {ask}"

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "tag":
            addr = self.addrs[self.which]
            tag, index = locate(addr, self.block_size, self.n_lines)
            step = ((f"Адрес {addr}: block = {addr // self.block_size}, tag = {tag}, index = {index}.")
                    if ru else
                    (f"Address {addr}: block = {addr // self.block_size}, tag = {tag}, index = {index}."))
        else:
            step = (("Трасса: " if ru else "Trace: ") + " ".join(self.trace) + ".")
        self.solution_steps = [step, (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}.")]
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
