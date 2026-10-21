"""HuffmanCodingTask — оптимальное префиксное кодирование (жадный алгоритм).

Даны частоты символов; нужно найти минимальную суммарную длину закодированного
сообщения (в битах) = Σ частота·глубина при оптимальном коде Хаффмана.
"""

import heapq
import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class HuffmanCodingTask(BaseMathTask):
    TASK_TYPE = "huffman_coding"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 3, "fmax": 9}, 2: {"k": 3, "fmax": 15}, 3: {"k": 4, "fmax": 20},
        4: {"k": 5, "fmax": 25}, 5: {"k": 5, "fmax": 30}, 6: {"k": 6, "fmax": 40},
        7: {"k": 7, "fmax": 50}, 8: {"k": 8, "fmax": 60}, 9: {"k": 9, "fmax": 80},
        10: {"k": 10, "fmax": 99},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.k = int(p["k"])
        self.fmax = int(p["fmax"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        alphabet = "ABCDEFGHIJKLMNOP"
        self.symbols = list(alphabet[:self.k])
        self.freqs = [random.randint(1, self.fmax) for _ in range(self.k)]
        self.answer = self._huffman_cost(self.freqs)

    @staticmethod
    def _huffman_cost(freqs: List[int]) -> int:
        if len(freqs) == 1:
            return freqs[0]  # один символ — код длины 1
        heap = list(freqs)
        heapq.heapify(heap)
        total = 0
        while len(heap) > 1:
            a = heapq.heappop(heap)
            b = heapq.heappop(heap)
            total += a + b
            heapq.heappush(heap, a + b)
        return total

    def _descr(self, language):
        ru = language == "ru"
        pairs = ", ".join(f"{s}:{f}" for s, f in zip(self.symbols, self.freqs))
        return ((f"Частоты символов: {pairs}. Построив оптимальный код Хаффмана, найдите минимальную "
                 f"суммарную длину закодированного сообщения (в битах) — сумму по всем символам "
                 f"частота×длина кода.") if ru else
                (f"Symbol frequencies: {pairs}. Using an optimal Huffman code, find the minimum total "
                 f"length of the encoded message (in bits) — the sum over symbols of "
                 f"frequency×code length."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Жадно объединяем две наименьшие частоты; сумма всех промежуточных объединений равна "
             "стоимости кода." if ru else
             "Greedily merge the two smallest frequencies; the sum of all merge values equals the "
             "code cost."),
            (f"Минимальная длина: {self.answer} бит." if ru else
             f"Minimum length: {self.answer} bits.")]
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
