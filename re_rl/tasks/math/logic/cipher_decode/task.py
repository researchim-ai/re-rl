"""Разные логические задачи: расшифровка шифра (Цезарь / подстановка), принцип
Дирихле, парадокс Монти Холла и отношения Аллена между интервалами."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
import string
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Optional
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.misc_logic_shared.base import _MiscBase, _letters_only

class CipherDecodeTask(_MiscBase):
    TASK_TYPE = "cipher_decode"
    TASK_TYPES = ["caesar", "substitution"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 4, "alpha": 5}, 2: {"L": 5, "alpha": 6}, 3: {"L": 6, "alpha": 6},
        4: {"L": 7, "alpha": 7}, 5: {"L": 8, "alpha": 8}, 6: {"L": 9, "alpha": 8},
        7: {"L": 10, "alpha": 9}, 8: {"L": 11, "alpha": 10}, 9: {"L": 12, "alpha": 10},
        10: {"L": 14, "alpha": 12},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L = int(p["L"])
        self.alpha_size = int(p["alpha"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype == "caesar":
            self.shift = random.randint(1, 25)
            self.plain = "".join(random.choice(string.ascii_lowercase) for _ in range(self.L))
            self.cipher = "".join(chr((ord(ch) - 97 + self.shift) % 26 + 97) for ch in self.plain)
        else:
            self.alphabet = string.ascii_lowercase[:self.alpha_size]
            perm = list(self.alphabet)
            random.shuffle(perm)
            self.key = dict(zip(self.alphabet, perm))       # plain -> cipher
            self.inv = {c: p for p, c in self.key.items()}  # cipher -> plain
            self.plain = "".join(random.choice(self.alphabet) for _ in range(self.L))
            self.cipher = "".join(self.key[ch] for ch in self.plain)

    def _descr(self, language):
        if self.subtype == "caesar":
            return ((texts.t('s1', language, shift=self.shift, shift_2=self.shift, cipher=self.cipher)))
        table = ", ".join(f"{p}→{self.key[p]}" for p in self.alphabet)
        return ((texts.t('s0', language, table=table, cipher=self.cipher)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s2', self.language))),
            ((texts.t('s3', self.language, plain=self.plain))),
        ]
        self.final_answer = self.plain

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return 1.0 if self.plain in _letters_only(prediction) else 0.0
