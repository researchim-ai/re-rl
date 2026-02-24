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
            # Exact DP by capacity: O(n * capacity) instead of brute-force 2^n
            n = len(items)
            dp = [[0] * (capacity + 1) for _ in range(n + 1)]
            take = [[False] * (capacity + 1) for _ in range(n + 1)]
            for i in range(1, n + 1):
                w, v = items[i - 1]
                for cap in range(capacity + 1):
                    dp[i][cap] = dp[i - 1][cap]
                    if w <= cap and dp[i - 1][cap - w] + v > dp[i][cap]:
                        dp[i][cap] = dp[i - 1][cap - w] + v
                        take[i][cap] = True
            best_val = dp[n][capacity]
            cap = capacity
            for i in range(n, 0, -1):
                if take[i][cap]:
                    best_subset.append(i - 1)
                    cap -= items[i - 1][0]
            best_subset.reverse()
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
            # Exact shortest-cover on bitmasks: O(m * 2^n)
            ordered_universe = sorted(universe)
            pos = {val: i for i, val in enumerate(ordered_universe)}
            full_mask = (1 << len(ordered_universe)) - 1
            set_masks: List[int] = []
            for s in sets:
                mask = 0
                for val in s:
                    mask |= 1 << pos[val]
                set_masks.append(mask)

            inf = 10**9
            best = [inf] * (full_mask + 1)
            prev_state = [-1] * (full_mask + 1)
            prev_set = [-1] * (full_mask + 1)
            best[0] = 0
            for mask in range(full_mask + 1):
                if best[mask] == inf:
                    continue
                for i, s_mask in enumerate(set_masks):
                    nxt = mask | s_mask
                    if best[mask] + 1 < best[nxt]:
                        best[nxt] = best[mask] + 1
                        prev_state[nxt] = mask
                        prev_set[nxt] = i

            cur = full_mask
            if best[cur] < inf:
                while cur != 0:
                    i = prev_set[cur]
                    if i < 0:
                        break
                    chosen.append(i)
                    cur = prev_state[cur]
                chosen.reverse()
        return len(chosen), chosen, sets, universe

    def _held_karp_tsp(self, d: List[List[int]]) -> Tuple[int, List[int]]:
        """Exact TSP with DP: O(n^2 * 2^n), much faster than permutations."""
        n = len(d)
        if n <= 2:
            return d[0][1] + d[1][0], [0, 1, 0] if n == 2 else [0, 0]

        dp: Dict[Tuple[int, int], int] = {}
        parent: Dict[Tuple[int, int], int] = {}

        for j in range(1, n):
            mask = 1 << (j - 1)
            dp[(mask, j)] = d[0][j]

        for subset_size in range(2, n):
            next_dp: Dict[Tuple[int, int], int] = {}
            for mask in range(1, 1 << (n - 1)):
                if mask.bit_count() != subset_size:
                    continue
                for j in range(1, n):
                    if not (mask & (1 << (j - 1))):
                        continue
                    prev_mask = mask ^ (1 << (j - 1))
                    best_cost = math.inf
                    best_k = -1
                    for k in range(1, n):
                        if not (prev_mask & (1 << (k - 1))):
                            continue
                        cost = dp.get((prev_mask, k), math.inf) + d[k][j]
                        if cost < best_cost:
                            best_cost = cost
                            best_k = k
                    if best_k != -1:
                        next_dp[(mask, j)] = int(best_cost)
                        parent[(mask, j)] = best_k
            dp = next_dp

        full_mask = (1 << (n - 1)) - 1
        best_len = math.inf
        end_node = -1
        for j in range(1, n):
            cost = dp.get((full_mask, j), math.inf) + d[j][0]
            if cost < best_len:
                best_len = cost
                end_node = j

        path_nodes = [end_node]
        mask = full_mask
        cur = end_node
        while mask != (1 << (cur - 1)):
            prev = parent.get((mask, cur), -1)
            if prev == -1:
                break
            path_nodes.append(prev)
            mask ^= 1 << (cur - 1)
            cur = prev
        route = [0] + list(reversed(path_nodes)) + [0]
        return int(best_len), route

    def _two_opt(self, route: List[int], d: List[List[int]]) -> List[int]:
        """Small 2-opt local optimization for approximation route."""
        improved = True
        best = route[:]
        n = len(best)
        while improved:
            improved = False
            for i in range(1, n - 3):
                for j in range(i + 1, n - 2):
                    a, b = best[i - 1], best[i]
                    c, e = best[j], best[j + 1]
                    delta = (d[a][c] + d[b][e]) - (d[a][b] + d[c][e])
                    if delta < 0:
                        best[i : j + 1] = reversed(best[i : j + 1])
                        improved = True
            # one pass is usually enough for fast generation
            break
        return best

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
            best_route = self._two_opt(route, d)
            best_len = sum(d[best_route[i]][best_route[i + 1]] for i in range(len(best_route) - 1))
        else:
            # For exact mode, use DP Held-Karp up to practical limit.
            if n <= 12:
                best_len, best_route = self._held_karp_tsp(d)
            else:
                route = [0]
                unvisited = set(nodes)
                cur = 0
                while unvisited:
                    nxt = min(unvisited, key=lambda x: d[cur][x])
                    route.append(nxt)
                    unvisited.remove(nxt)
                    cur = nxt
                route.append(0)
                best_route = self._two_opt(route, d)
                best_len = sum(d[best_route[i]][best_route[i + 1]] for i in range(len(best_route) - 1))
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
