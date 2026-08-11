"""Дедуктивные задачи: логическая сетка соответствий, круговая рассадка,
турнирные подсчёты (круговой и на выбывание)."""

import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_NAMES = ["Анна", "Борис", "Вера", "Глеб", "Дина", "Егор"]
_NAMES_EN = ["Anna", "Boris", "Vera", "Gleb", "Dina", "Egor"]
_TEAMS = ["Альфа", "Браво", "Виктор", "Дельта", "Эхо", "Фокстрот", "Гольф", "Отель"]
_TEAMS_EN = ["Alpha", "Bravo", "Victor", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]


class _DedBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class LogicGridTask(_DedBase):
    TASK_TYPE = "logic_grid"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 3}, 4: {"n": 4}, 5: {"n": 4},
        6: {"n": 4}, 7: {"n": 4}, 8: {"n": 5}, 9: {"n": 5}, 10: {"n": 5},
    }
    _DRINKS = {"ru": ["чай", "кофе", "сок", "молоко", "какао"],
               "en": ["tea", "coffee", "juice", "milk", "cocoa"]}
    _SPORTS = {"ru": ["теннис", "шахматы", "футбол", "плавание", "бег"],
               "en": ["tennis", "chess", "football", "swimming", "running"]}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.lang = language
        self.augment = augment
        self.people = (_NAMES if language == "ru" else _NAMES_EN)[:self.n]
        self.drinks = self._DRINKS["ru" if language == "ru" else "en"][:self.n]
        self.sports = self._SPORTS["ru" if language == "ru" else "en"][:self.n]
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.drink_of = dict(zip(self.people, random.sample(self.drinks, self.n)))
        self.sport_of = dict(zip(self.people, random.sample(self.sports, self.n)))

        pool = []  # (тип, текст-функция, предикат(assignment)->bool)
        for pr in self.people:
            pool.append(("d+", pr, self.drink_of[pr]))
            pool.append(("s+", pr, self.sport_of[pr]))
            pool.append(("link", self.drink_of[pr], self.sport_of[pr]))  # у кого напиток -> тот спорт
        for pr in self.people:  # отрицания
            other = random.choice([d for d in self.drinks if d != self.drink_of[pr]])
            pool.append(("d-", pr, other))
        random.shuffle(pool)

        clues = []
        for cl in pool:
            clues.append(cl)
            if self._count_solutions(clues) == 1:
                break
        if self._count_solutions(clues) != 1:
            clues = [("d+", pr, self.drink_of[pr]) for pr in self.people] + \
                    [("s+", pr, self.sport_of[pr]) for pr in self.people]
        pruned = clues[:]
        for cl in clues:
            trial = [x for x in pruned if x is not cl]
            if self._count_solutions(trial) == 1:
                pruned = trial
        random.shuffle(pruned)
        self.clues = pruned
        self.query_person = random.choice(self.people)
        self.query_attr = random.choice(["drink", "sport"])
        self.answer = self.drink_of[self.query_person] if self.query_attr == "drink" \
            else self.sport_of[self.query_person]

    def _clue_holds(self, cl, dmap, smap):
        kind, a, b = cl
        if kind == "d+":
            return dmap[a] == b
        if kind == "d-":
            return dmap[a] != b
        if kind == "s+":
            return smap[a] == b
        # link: человек с напитком a занимается спортом b
        person = next(pr for pr in self.people if dmap[pr] == a)
        return smap[person] == b

    def _count_solutions(self, clues):
        cnt = 0
        people = self.people
        for dperm in permutations(self.drinks):
            dmap = dict(zip(people, dperm))
            if not all(self._clue_holds(c, dmap, None) for c in clues if c[0] in ("d+", "d-")):
                continue
            for sperm in permutations(self.sports):
                smap = dict(zip(people, sperm))
                if all(self._clue_holds(c, dmap, smap) for c in clues):
                    cnt += 1
                    if cnt > 1:
                        return cnt
        return cnt

    def _clue_text(self, cl, ru):
        kind, a, b = cl
        if kind == "d+":
            return (f"{a} пьёт {b}." if ru else f"{a} drinks {b}.")
        if kind == "d-":
            return (f"{a} не пьёт {b}." if ru else f"{a} does not drink {b}.")
        if kind == "s+":
            return (f"{a} занимается: {b}." if ru else f"{a} plays {b}.")
        return (f"Тот, кто пьёт {a}, занимается: {b}." if ru else
                f"The one who drinks {a} plays {b}.")

    def _descr(self, language):
        ru = language == "ru"
        head = (f"{self.n} человек ({', '.join(self.people)}), у каждого свой напиток "
                f"({', '.join(self.drinks)}) и свой вид спорта ({', '.join(self.sports)}).\nПодсказки:\n" if ru else
                f"{self.n} people ({', '.join(self.people)}), each with a unique drink "
                f"({', '.join(self.drinks)}) and a unique sport ({', '.join(self.sports)}).\nClues:\n")
        body = "\n".join(f"- {self._clue_text(c, ru)}" for c in self.clues)
        if self.query_attr == "drink":
            q = (f"\nЧто пьёт {self.query_person}?" if ru else f"\nWhat does {self.query_person} drink?")
        else:
            q = (f"\nКаким спортом занимается {self.query_person}?" if ru else
                 f"\nWhich sport does {self.query_person} play?")
        return head + body + q

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Комбинируем подсказки, сужая соответствие людей, напитков и спорта." if ru else
             "Combine clues to pin down the person–drink–sport correspondence."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = self.answer

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self.answer])


class SeatingCircularTask(_DedBase):
    TASK_TYPE = "seating_circular"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 6}, 10: {"n": 6},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self.people = (_NAMES if language == "ru" else _NAMES_EN)[:self.n]
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _adjacent(self, order, x, y):
        i = order.index(x)
        n = len(order)
        return order[(i + 1) % n] == y or order[(i - 1) % n] == y

    def _neighbors(self, order, x):
        i = order.index(x)
        n = len(order)
        return {order[(i + 1) % n], order[(i - 1) % n]}

    def _build(self):
        order = self.people[:]
        random.shuffle(order)
        self.true_order = order
        n = self.n
        pos_pairs = [(order[i], order[(i + 1) % n]) for i in range(n)]
        pool = [("next", a, b) for a, b in pos_pairs]
        # несколько отрицаний
        for _ in range(n):
            a, b = random.sample(self.people, 2)
            if not self._adjacent(order, a, b):
                pool.append(("notnext", a, b))
        random.shuffle(pool)

        self.query = random.choice(self.people)
        self.answer_neighbors = self._neighbors(order, self.query)

        clues = []
        for cl in pool:
            clues.append(cl)
            if self._neighbors_unique(clues):
                break
        if not self._neighbors_unique(clues):
            clues = pool
        pruned = clues[:]
        for cl in clues:
            trial = [x for x in pruned if x is not cl]
            if self._neighbors_unique(trial):
                pruned = trial
        random.shuffle(pruned)
        self.clues = pruned

    def _clue_ok(self, cl, order):
        kind, a, b = cl
        if kind == "next":
            return self._adjacent(order, a, b)
        return not self._adjacent(order, a, b)

    def _neighbors_unique(self, clues):
        found = set()
        base = self.people
        for perm in permutations(base[1:]):  # фиксируем первого — убираем вращения
            order = [base[0]] + list(perm)
            if all(self._clue_ok(c, order) for c in clues):
                found.add(frozenset(self._neighbors(order, self.query)))
                if len(found) > 1:
                    return False
        return len(found) == 1

    def _clue_text(self, cl, ru):
        kind, a, b = cl
        if kind == "next":
            return (f"{a} сидит рядом с {b}." if ru else f"{a} sits next to {b}.")
        return (f"{a} не сидит рядом с {b}." if ru else f"{a} does not sit next to {b}.")

    def _descr(self, language):
        ru = language == "ru"
        head = (f"{self.n} человек сидят за круглым столом: {', '.join(self.people)}.\nПодсказки:\n" if ru else
                f"{self.n} people sit at a round table: {', '.join(self.people)}.\nClues:\n")
        body = "\n".join(f"- {self._clue_text(c, ru)}" for c in self.clues)
        q = (f"\nКто сидит рядом с {self.query}? Назовите обоих соседей." if ru else
             f"\nWho sits next to {self.query}? Name both neighbors.")
        return head + body + q

    def solve(self):
        ru = self.language == "ru"
        nb = ", ".join(sorted(self.answer_neighbors))
        self.solution_steps = [
            ("Расставляем людей по кругу согласно подсказкам о соседстве." if ru else
             "Seat people around the circle according to the adjacency clues."),
            (f"Соседи {self.query}: {nb}." if ru else f"Neighbors of {self.query}: {nb}."),
        ]
        self.final_answer = nb

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        found = set(U.extract_name_sequence(prediction, self.people))
        return 1.0 if self.answer_neighbors.issubset(found) and self.query not in found else 0.0


class TournamentTask(_DedBase):
    TASK_TYPE = "tournament"
    TASK_TYPES = ["round_robin", "knockout"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"rr": 3, "ko": 2}, 2: {"rr": 3, "ko": 2}, 3: {"rr": 4, "ko": 3},
        4: {"rr": 4, "ko": 3}, 5: {"rr": 5, "ko": 3}, 6: {"rr": 5, "ko": 4},
        7: {"rr": 6, "ko": 4}, 8: {"rr": 6, "ko": 4}, 9: {"rr": 7, "ko": 4}, 10: {"rr": 8, "ko": 4},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.rr = int(p["rr"])
        self.ko = int(p["ko"])
        self.augment = augment
        self.teams_pool = _TEAMS if language == "ru" else _TEAMS_EN
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype == "round_robin":
            self.teams = self.teams_pool[:self.rr]
            self.results = []  # (a, b, outcome) outcome in {A,B,D}
            self.points = {t: 0 for t in self.teams}
            for i in range(len(self.teams)):
                for j in range(i + 1, len(self.teams)):
                    a, b = self.teams[i], self.teams[j]
                    o = random.choice(["A", "B", "D"])
                    self.results.append((a, b, o))
                    if o == "A":
                        self.points[a] += 3
                    elif o == "B":
                        self.points[b] += 3
                    else:
                        self.points[a] += 1; self.points[b] += 1
            self.query = random.choice(self.teams)
            self.answer = self.points[self.query]
        else:
            size = 2 ** self.ko
            self.bracket_teams = self.teams_pool[:0] + [f"T{i+1}" for i in range(size)]
            # исходы задаём случайно, детерминированно определяем чемпиона
            self.rounds = []
            cur = self.bracket_teams[:]
            while len(cur) > 1:
                rnd = []
                nxt = []
                for k in range(0, len(cur), 2):
                    win = random.choice([cur[k], cur[k + 1]])
                    rnd.append((cur[k], cur[k + 1], win))
                    nxt.append(win)
                self.rounds.append(rnd)
                cur = nxt
            self.champion = cur[0]

    def _descr(self, language):
        ru = language == "ru"
        if self.subtype == "round_robin":
            lines = []
            for a, b, o in self.results:
                if o == "A":
                    res = (f"{a} победил {b}" if ru else f"{a} beat {b}")
                elif o == "B":
                    res = (f"{b} победил {a}" if ru else f"{b} beat {a}")
                else:
                    res = (f"{a} и {b} сыграли вничью" if ru else f"{a} drew {b}")
                lines.append("- " + res)
            body = "\n".join(lines)
            return ((f"Круговой турнир (победа — 3 очка, ничья — 1, поражение — 0). Результаты:\n{body}\n"
                     f"Сколько очков набрала команда {self.query}?") if ru else
                    (f"Round-robin (win 3 points, draw 1, loss 0). Results:\n{body}\n"
                     f"How many points did team {self.query} score?"))
        lines = []
        for ri, rnd in enumerate(self.rounds):
            for a, b, w in rnd:
                lines.append((f"- Раунд {ri+1}: {a} vs {b} — победил {w}" if ru else
                              f"- Round {ri+1}: {a} vs {b} — {w} won"))
        body = "\n".join(lines)
        return ((f"Турнир на выбывание. Результаты матчей:\n{body}\nКто стал чемпионом?") if ru else
                (f"Single-elimination tournament. Match results:\n{body}\nWho is the champion?"))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "round_robin":
            self.solution_steps = [
                ("Начисляем очки по всем матчам команды и суммируем." if ru else
                 "Award points from each of the team's matches and sum them."),
                (f"Очки {self.query} = {self.answer}." if ru else f"{self.query} points = {self.answer}."),
            ]
            self.final_answer = str(self.answer)
        else:
            self.solution_steps = [
                ("Прослеживаем победителей по раундам до финала." if ru else
                 "Follow the winners round by round up to the final."),
                (f"Чемпион: {self.champion}." if ru else f"Champion: {self.champion}."),
            ]
            self.final_answer = self.champion

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "round_robin":
            return U.verify_int(prediction, int(self.answer))
        return U.verify_label(prediction, [self.champion])
