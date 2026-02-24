import itertools
import math
import random
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class CombinatorialOptimizationTask(BaseMathTask):
    """Small NP optimization tasks: knapsack, set cover, tsp."""

    TASK_TYPE = "combinatorial_optimization"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"task_type": "knapsack", "n": 5, "solve_mode": "exact"},
        2: {"task_type": "knapsack", "n": 6, "solve_mode": "exact"},
        3: {"task_type": "set_cover", "n": 5, "solve_mode": "exact"},
        4: {"task_type": "set_cover", "n": 6, "solve_mode": "exact"},
        5: {"task_type": "tsp_small", "n": 5, "solve_mode": "exact"},
        6: {"task_type": "tsp_small", "n": 6, "solve_mode": "exact"},
        7: {"task_type": "knapsack", "n": 9, "solve_mode": "approx"},
        8: {"task_type": "set_cover", "n": 9, "solve_mode": "approx"},
        9: {"task_type": "tsp_small", "n": 8, "solve_mode": "approx"},
        10: {"task_type": "mixed", "n": 10, "solve_mode": "approx"},
    }

    def __init__(
        self,
        task_type: Optional[str] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        solve_mode: Optional[str] = None,
        n: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.task_type = task_type or str(preset.get("task_type", "mixed"))
        if self.task_type == "mixed":
            self.task_type = random.choice(["knapsack", "set_cover", "tsp_small"])
        self.solve_mode = solve_mode or str(preset.get("solve_mode", "exact"))
        self.n = n if n is not None else int(preset.get("n", 6))
        self.augment = augment
        super().__init__("", language=language, detail_level=detail_level, output_format=output_format, reasoning_mode=reasoning_mode)

    def _solve_knapsack(self) -> Tuple[int, List[int], List[Tuple[int, int]]]:
        items = [(random.randint(1, 10), random.randint(2, 30)) for _ in range(self.n)]
        capacity = max(8, int(sum(w for w, _ in items) * 0.4))
        self.description = get_template(
            PROMPT_TEMPLATES["combinatorial_optimization"],
            "problem_knapsack",
            self.language,
            augment=self.augment,
            items=items,
            capacity=capacity,
            mode=self.solve_mode,
        )
        best_val = -1
        best_subset: List[int] = []
        if self.solve_mode == "approx":
            order = sorted(range(len(items)), key=lambda i: items[i][1] / items[i][0], reverse=True)
            total_w = 0
            for i in order:
                w, _ = items[i]
                if total_w + w <= capacity:
                    total_w += w
                    best_subset.append(i)
            best_val = sum(items[i][1] for i in best_subset)
        else:
            for mask in range(1 << len(items)):
                idxs = [i for i in range(len(items)) if (mask >> i) & 1]
                total_w = sum(items[i][0] for i in idxs)
                if total_w <= capacity:
                    total_v = sum(items[i][1] for i in idxs)
                    if total_v > best_val:
                        best_val = total_v
                        best_subset = idxs
        return best_val, best_subset, items

    def _solve_set_cover(self) -> Tuple[int, List[int], List[Set[int]], Set[int]]:
        universe = set(range(1, self.n + 1))
        sets: List[Set[int]] = []
        for _ in range(self.n):
            size = random.randint(2, max(2, self.n // 2 + 1))
            sets.append(set(random.sample(list(universe), k=size)))
        sets[0] = sets[0] | set(random.sample(list(universe), k=min(2, self.n)))
        self.description = get_template(
            PROMPT_TEMPLATES["combinatorial_optimization"],
            "problem_set_cover",
            self.language,
            augment=self.augment,
            universe=sorted(universe),
            sets=[sorted(s) for s in sets],
            mode=self.solve_mode,
        )
        chosen: List[int] = []
        if self.solve_mode == "approx":
            uncovered = set(universe)
            while uncovered:
                idx = max(range(len(sets)), key=lambda i: len(sets[i] & uncovered))
                if len(sets[idx] & uncovered) == 0:
                    break
                chosen.append(idx)
                uncovered -= sets[idx]
        else:
            for k in range(1, len(sets) + 1):
                found = None
                for comb in itertools.combinations(range(len(sets)), k):
                    covered = set().union(*[sets[i] for i in comb])
                    if covered == universe:
                        found = list(comb)
                        break
                if found is not None:
                    chosen = found
                    break
        return len(chosen), chosen, sets, universe

    def _solve_tsp(self) -> Tuple[int, List[int], List[List[int]]]:
        n = min(self.n, 9 if self.solve_mode == "exact" else 12)
        d = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                w = random.randint(2, 25)
                d[i][j] = w
                d[j][i] = w
        self.description = get_template(
            PROMPT_TEMPLATES["combinatorial_optimization"],
            "problem_tsp",
            self.language,
            augment=self.augment,
            matrix=d,
            mode=self.solve_mode,
        )
        best_len = math.inf
        best_route: List[int] = []
        nodes = list(range(1, n))
        if self.solve_mode == "approx":
            route = [0]
            unvisited = set(nodes)
            cur = 0
            while unvisited:
                nxt = min(unvisited, key=lambda x: d[cur][x])
                route.append(nxt)
                unvisited.remove(nxt)
                cur = nxt
            route.append(0)
            best_route = route
            best_len = sum(d[route[i]][route[i + 1]] for i in range(len(route) - 1))
        else:
            for perm in itertools.permutations(nodes):
                route = [0] + list(perm) + [0]
                dist = sum(d[route[i]][route[i + 1]] for i in range(len(route) - 1))
                if dist < best_len:
                    best_len = dist
                    best_route = route
        return int(best_len), best_route, d

    def solve(self):
        section = PROMPT_TEMPLATES["combinatorial_optimization"]
        if self.task_type == "knapsack":
            value, subset, _ = self._solve_knapsack()
            self.solution_steps.append(get_template(section, "step_tradeoff", self.language, augment=False))
            self.final_answer = f"value={value};items={subset}"
            return
        if self.task_type == "set_cover":
            size, chosen, _, _ = self._solve_set_cover()
            self.solution_steps.append(get_template(section, "step_tradeoff", self.language, augment=False))
            self.final_answer = f"size={size};sets={chosen}"
            return
        dist, route, _ = self._solve_tsp()
        self.solution_steps.append(get_template(section, "step_tradeoff", self.language, augment=False))
        self.final_answer = f"distance={dist};route={route}"

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "CombinatorialOptimizationTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
