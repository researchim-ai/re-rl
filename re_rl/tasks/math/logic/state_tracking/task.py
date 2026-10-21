"""StateTrackingTask — отслеживание состояния мира после серии действий.

Люди перемещаются между комнатами, берут и кладут предметы. Нужно определить,
в какой комнате окажется указанный предмет в конце. Симулятор детерминирован.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ROOMS_RU = [texts.literal('literals.s11'), texts.literal('literals.s12'), texts.literal('literals.s13'), texts.literal('literals.s14'), texts.literal('literals.s15'), texts.literal('literals.s16')]
_ROOMS_EN = ["kitchen", "bedroom", "living room", "study", "hallway", "garden"]
_PEOPLE_RU = [texts.literal('literals.s17'), texts.literal('literals.s18'), texts.literal('literals.s19'), texts.literal('literals.s20')]
_PEOPLE_EN = ["Ann", "Bob", "Vicky", "Dan"]
_ITEMS_RU = [texts.literal('literals.s21'), texts.literal('literals.s22'), texts.literal('literals.s23'), texts.literal('literals.s24'), texts.literal('literals.s25')]
_ITEMS_EN = ["key", "book", "apple", "lamp", "ball"]


class StateTrackingTask(BaseMathTask):
    TASK_TYPE = "state_tracking"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"rooms": 2, "people": 1, "items": 2, "steps": 3},
        2: {"rooms": 2, "people": 2, "items": 2, "steps": 4},
        3: {"rooms": 3, "people": 2, "items": 2, "steps": 5},
        4: {"rooms": 3, "people": 2, "items": 3, "steps": 6},
        5: {"rooms": 3, "people": 3, "items": 3, "steps": 8},
        6: {"rooms": 4, "people": 3, "items": 3, "steps": 10},
        7: {"rooms": 4, "people": 3, "items": 4, "steps": 12},
        8: {"rooms": 5, "people": 4, "items": 4, "steps": 14},
        9: {"rooms": 5, "people": 4, "items": 5, "steps": 16},
        10: {"rooms": 6, "people": 4, "items": 5, "steps": 20},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.language = language
        self.rooms = (({"ru": (_ROOMS_RU), "en": (_ROOMS_EN)}.get(language, (_ROOMS_EN))))[:preset["rooms"]]
        self.people = (({"ru": (_PEOPLE_RU), "en": (_PEOPLE_EN)}.get(language, (_PEOPLE_EN))))[:preset["people"]]
        self.items = (({"ru": (_ITEMS_RU), "en": (_ITEMS_EN)}.get(language, (_ITEMS_EN))))[:preset["items"]]
        self.num_steps = preset["steps"]
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        # Начальное состояние.
        self.person_room = {p: random.choice(self.rooms) for p in self.people}
        # Предмет либо лежит в комнате (room, name), либо у человека (person, name).
        item_loc = {it: ("room", random.choice(self.rooms)) for it in self.items}

        self.actions: List[str] = []
        init_lines = []
        for p in self.people:
            init_lines.append(((texts.t('s5', self.language, p=p, v1=self.person_room[p]))))
        for it in self.items:
            init_lines.append(((texts.t('s6', self.language, it=it, v1=item_loc[it][1]))))
        self.init_lines = init_lines

        for _ in range(self.num_steps):
            p = random.choice(self.people)
            choice = random.random()
            carried = [it for it, loc in item_loc.items() if loc == ("person", p)]
            here = [it for it, loc in item_loc.items() if loc == ("room", self.person_room[p])]
            if choice < 0.45 or (not carried and not here):
                new_room = random.choice([r for r in self.rooms if r != self.person_room[p]] or self.rooms)
                self.person_room[p] = new_room
                self.actions.append(((texts.t('s7', self.language, p=p, new_room=new_room))))
            elif here and choice < 0.75:
                it = random.choice(here)
                item_loc[it] = ("person", p)
                self.actions.append(((texts.t('s8', self.language, p=p, it=it))))
            elif carried:
                it = random.choice(carried)
                item_loc[it] = ("room", self.person_room[p])
                self.actions.append(((texts.t('s9', self.language, p=p, it=it))))
            else:
                it = random.choice(here)
                item_loc[it] = ("person", p)
                self.actions.append(((texts.t('s10', self.language, p=p, it=it))))

        self.target_item = random.choice(self.items)
        loc = item_loc[self.target_item]
        self.answer_room = loc[1] if loc[0] == "room" else self.person_room[loc[1]]
        self._final_item_loc = item_loc

    def _make_description(self, language: str) -> str:
        head = ((texts.t('s0', language)))
        head += "\n".join(f"- {l}" for l in self.init_lines)
        acts = ((texts.t('s1', language)))
        acts += "\n".join(f"{i + 1}. {a}" for i, a in enumerate(self.actions))
        q = ((texts.t('s2', language, target_item=self.target_item)))
        return head + acts + q

    def solve(self):
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language, target_item=self.target_item, answer_room=self.answer_room))),
        ]
        self.final_answer = self.answer_room

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self.answer_room])

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
