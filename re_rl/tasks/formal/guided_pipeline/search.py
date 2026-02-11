"""
Guided proof search engines for deeper Lean trajectories.

This module provides two search modes:
1) Best-first guided search (lightweight baseline)
2) MCTS (UCT-style) guided search
"""

from __future__ import annotations

import heapq
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from re_rl.tasks.formal.lean_navigator.core import (
    MAX_TACTIC_FROM_TEMPLATE,
    ProofFinished,
    ProofState,
    TrainingPair,
    classify_lean_elements,
    generate_tactics_from_template,
    get_inverse_tactic,
)


@dataclass
class GuidedSearchConfig:
    max_steps: int = 12000
    max_time: int = 180
    max_states: int = 6000
    max_depth: int = 12
    candidate_top_k: int = 96
    max_total_tactics_per_state: int = 192
    max_tactics_per_template: int = MAX_TACTIC_FROM_TEMPLATE
    auto_tactics_after_depth: int = 3
    negatives_per_state: int = 2
    banned_tactics: Optional[Set[str]] = None


@dataclass
class MCTSConfig(GuidedSearchConfig):
    mcts_iters: int = 2000
    mcts_c_puct: float = 1.4
    mcts_gamma: float = 0.97


@dataclass
class GuidedSearchResult:
    theorem_name: str
    theorem_proven: bool
    proof_tactics: List[str]
    n_steps: int
    n_states: int
    elapsed: float
    pairs: List[TrainingPair]
    max_depth_reached: int
    search_stats: Optional[dict] = None


class _SearchCommon:
    _ALWAYS_TACTICS = [
        "intro", "intros", "rintro nvar0", "cases nvar0", "constructor",
        "apply", "exact", "refine", "rw", "erw", "simp", "simp_all",
        "aesop", "assumption", "exfalso", "by_contra", "contrapose",
        "linarith", "norm_num", "norm_cast", "tauto", "trivial",
    ]

    _AUTO_ROOTS = {
        "simp", "simp_all", "aesop", "tauto", "decide",
        "omega", "linarith", "ring", "norm_num", "trivial",
    }

    _ROOT_PRIOR = {
        "intro": 0.45,
        "intros": 0.45,
        "rintro": 0.4,
        "cases": 0.25,
        "rcases": 0.25,
        "constructor": 0.35,
        "apply": 0.5,
        "exact": 0.48,
        "refine": 0.46,
        "rw": 0.42,
        "erw": 0.38,
        "simp": 0.18,
        "simp_all": 0.12,
        "assumption": 0.22,
        "exfalso": 0.15,
        "by_contra": 0.14,
        "contrapose": 0.14,
    }

    def __init__(self, dojo, rag, config: GuidedSearchConfig, verbose: bool = False):
        self.dojo = dojo
        self.rag = rag
        self.config = config
        self.verbose = verbose

    @staticmethod
    def _tactic_root(tactic: str) -> str:
        s = (tactic or "").strip()
        if s.startswith("·"):
            s = s[1:].strip()
        for i, ch in enumerate(s):
            if ch in " \t[({⟨":
                return s[:i]
        return s

    @staticmethod
    def _state_features(pp: str) -> Tuple[int, int]:
        return pp.count("⊢"), len(pp)

    def _value_score(self, pp: str, depth: int) -> float:
        n_goals, n_chars = self._state_features(pp)
        return -0.60 * n_goals - 0.0009 * n_chars - 0.08 * depth

    def _heuristic_reward(self, pp: str, depth: int) -> float:
        # Convert textual state quality into [0, 1] reward proxy.
        v = self._value_score(pp, depth)
        # Shift+scale sigmoid to avoid near-zero gradients.
        return 1.0 / (1.0 + math.exp(-0.35 * (v + 6.0)))

    def _policy_score(self, tactic: str, template_rank: int, depth: int) -> float:
        root = self._tactic_root(tactic)
        score = 1.8 / (1.0 + template_rank)
        score += self._ROOT_PRIOR.get(root, 0.0)
        if root in self._AUTO_ROOTS and depth < self.config.auto_tactics_after_depth:
            score -= 0.35
        if "nvar" in tactic:
            score -= 0.05
        return score

    def _collect_candidates_with_scores(
        self,
        curr_state: ProofState,
        theorem_name: str,
        theorem_code: str,
        depth: int,
    ) -> List[Tuple[str, float]]:
        cfg = self.config
        type_of_item, def_of_item = classify_lean_elements(curr_state.pp)
        for var in list(def_of_item.keys()):
            if var not in type_of_item:
                def_of_item.pop(var, None)

        query_text = theorem_code if theorem_code else theorem_name
        suggestions = self.rag.get_similar_templates(
            curr_state.pp, theorem_code=query_text, num_returned=200
        )
        tac_templates = [s[0] for s in suggestions]

        for tac_template in list(tac_templates):
            inv = get_inverse_tactic(tac_template)
            if inv and inv not in tac_templates:
                tac_templates.append(inv)

        scored: Dict[str, float] = {}
        for rank, template in enumerate(tac_templates):
            try:
                generated = generate_tactics_from_template(
                    template, type_of_item, max_tactics=cfg.max_tactics_per_template
                )
            except Exception:
                continue
            for tactic in generated:
                if not tactic:
                    continue
                root = self._tactic_root(tactic)
                if cfg.banned_tactics and root in cfg.banned_tactics:
                    continue
                s = self._policy_score(tactic, rank, depth)
                prev = scored.get(tactic)
                if prev is None or s > prev:
                    scored[tactic] = s

        for tactic in self._ALWAYS_TACTICS:
            root = self._tactic_root(tactic)
            if cfg.banned_tactics and root in cfg.banned_tactics:
                continue
            s = self._policy_score(tactic, template_rank=999, depth=depth)
            prev = scored.get(tactic)
            if prev is None or s > prev:
                scored[tactic] = s

        ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
        if cfg.max_total_tactics_per_state > 0:
            ranked = ranked[: cfg.max_total_tactics_per_state]
        if cfg.candidate_top_k > 0:
            ranked = ranked[: cfg.candidate_top_k]
        return ranked

    def _build_pairs_from_proof(
        self,
        theorem_name: str,
        theorem_goal_expr: str,
        init_state: ProofState,
        proof_tactics: List[str],
    ) -> List[TrainingPair]:
        pairs: List[TrainingPair] = []
        if not proof_tactics:
            return pairs

        cur_state = init_state
        transition_states = [cur_state.pp]
        for tac in proof_tactics:
            nxt = self.dojo.run_tac(cur_state, tac)
            if isinstance(nxt, ProofState):
                transition_states.append(nxt.pp)
                cur_state = nxt
            else:
                transition_states.append("")
                break

        for i, tac in enumerate(proof_tactics):
            st = transition_states[i]
            ns = transition_states[i + 1] if i + 1 < len(transition_states) else ""
            dist = len(proof_tactics) - i
            pairs.append(
                TrainingPair(
                    state=st,
                    tactic=tac,
                    next_state=ns,
                    distance_to_proof=dist,
                    theorem_name=theorem_name,
                    theorem_statement=theorem_goal_expr,
                )
            )
        return pairs

    def _append_negative_pairs(
        self,
        theorem_name: str,
        theorem_goal_expr: str,
        failed_by_state: Dict[str, Set[str]],
        pairs: List[TrainingPair],
    ) -> None:
        if self.config.negatives_per_state <= 0:
            return
        for st, failed_set in failed_by_state.items():
            sampled = list(failed_set)
            random.shuffle(sampled)
            sampled = sampled[: self.config.negatives_per_state]
            for _ in sampled:
                pairs.append(
                    TrainingPair(
                        state=st,
                        tactic="",
                        next_state="",
                        distance_to_proof=-1,
                        theorem_name=theorem_name,
                        theorem_statement=theorem_goal_expr,
                    )
                )


class GuidedSearchExplorer(_SearchCommon):
    """Best-first guided search baseline."""

    def __init__(self, dojo, rag, config: Optional[GuidedSearchConfig] = None, verbose: bool = False):
        super().__init__(dojo=dojo, rag=rag, config=config or GuidedSearchConfig(), verbose=verbose)

    def search(self, theorem_name: str, theorem_goal_expr: str, theorem_code: str = "") -> GuidedSearchResult:
        cfg = self.config
        t0 = time.time()

        init_state = self.dojo.goal_start_expr(theorem_name)
        if init_state is None or isinstance(init_state, ProofFinished):
            return GuidedSearchResult(theorem_name, False, [], 0, 0, time.time() - t0, [], 0, None)

        state_map: Dict[str, ProofState] = {init_state.pp: init_state}
        parent: Dict[str, Tuple[Optional[str], str]] = {init_state.pp: (None, "")}
        depth_of: Dict[str, int] = {init_state.pp: 0}
        explored: Set[str] = set()
        failed_by_state: Dict[str, Set[str]] = {}

        frontier = []
        ctr = 0
        heapq.heappush(frontier, (-self._value_score(init_state.pp, 0), ctr, init_state.pp))

        n_steps = 0
        theorem_proven = False
        proof_terminal_parent: Optional[str] = None
        proof_terminal_tactic = ""
        max_depth_reached = 0

        while frontier:
            if cfg.max_time > 0 and (time.time() - t0) >= cfg.max_time:
                break
            if cfg.max_steps > 0 and n_steps >= cfg.max_steps:
                break

            _, _, curr_key = heapq.heappop(frontier)
            if curr_key in explored:
                continue
            explored.add(curr_key)

            curr_state = state_map[curr_key]
            curr_depth = depth_of[curr_key]
            max_depth_reached = max(max_depth_reached, curr_depth)
            if curr_depth >= cfg.max_depth:
                continue
            if cfg.max_states > 0 and len(state_map) >= cfg.max_states:
                break

            tactics = [t for t, _ in self._collect_candidates_with_scores(curr_state, theorem_name, theorem_code, curr_depth)]
            random.shuffle(tactics)

            for tactic in tactics:
                n_steps += 1
                if cfg.max_steps > 0 and n_steps > cfg.max_steps:
                    break
                result = self.dojo.run_tac(curr_state, tactic)
                if result is None:
                    if cfg.negatives_per_state > 0:
                        failed_by_state.setdefault(curr_key, set()).add(tactic)
                    continue
                if isinstance(result, ProofFinished):
                    theorem_proven = True
                    proof_terminal_parent = curr_key
                    proof_terminal_tactic = tactic
                    break
                if not isinstance(result, ProofState):
                    continue

                next_key = result.pp
                if next_key not in state_map:
                    state_map[next_key] = result
                    parent[next_key] = (curr_key, tactic)
                    depth_of[next_key] = curr_depth + 1
                    ctr += 1
                    heapq.heappush(frontier, (-self._value_score(next_key, curr_depth + 1), ctr, next_key))

            if theorem_proven:
                break

        pairs: List[TrainingPair] = []
        proof_tactics: List[str] = []
        if theorem_proven and proof_terminal_parent is not None:
            chain_tactics: List[str] = []
            cur = proof_terminal_parent
            while cur is not None:
                p, tac = parent[cur]
                if p is not None:
                    chain_tactics.append(tac)
                cur = p
            chain_tactics.reverse()
            proof_tactics = [t for t in chain_tactics if t] + [proof_terminal_tactic]
            pairs.extend(self._build_pairs_from_proof(theorem_name, theorem_goal_expr, init_state, proof_tactics))

        self._append_negative_pairs(theorem_name, theorem_goal_expr, failed_by_state, pairs)
        return GuidedSearchResult(
            theorem_name=theorem_name,
            theorem_proven=theorem_proven,
            proof_tactics=proof_tactics,
            n_steps=n_steps,
            n_states=len(state_map),
            elapsed=time.time() - t0,
            pairs=pairs,
            max_depth_reached=max_depth_reached,
            search_stats=None,
        )


@dataclass
class _MCTSNode:
    node_id: int
    state: Optional[ProofState]
    state_key: str
    parent_id: Optional[int]
    action_from_parent: str
    depth: int
    prior: float = 0.0
    is_terminal: bool = False
    is_solved: bool = False
    visits: int = 0
    value_sum: float = 0.0
    untried_actions: List[Tuple[str, float]] = field(default_factory=list)
    children: Dict[str, int] = field(default_factory=dict)

    def q_value(self) -> float:
        return (self.value_sum / self.visits) if self.visits > 0 else 0.0


class MCTSSearchExplorer(_SearchCommon):
    """UCT-style MCTS with policy priors from RAG candidate scoring."""

    def __init__(self, dojo, rag, config: Optional[MCTSConfig] = None, verbose: bool = False):
        super().__init__(dojo=dojo, rag=rag, config=config or MCTSConfig(), verbose=verbose)
        self.config: MCTSConfig

    def _uct_score(self, parent: _MCTSNode, child: _MCTSNode) -> float:
        c = self.config.mcts_c_puct
        q = child.q_value()
        u = c * child.prior * math.sqrt(max(1, parent.visits)) / (1 + child.visits)
        return q + u

    def _new_node(
        self,
        node_id: int,
        state: Optional[ProofState],
        state_key: str,
        parent_id: Optional[int],
        action_from_parent: str,
        depth: int,
        prior: float,
        is_terminal: bool,
        is_solved: bool,
    ) -> _MCTSNode:
        return _MCTSNode(
            node_id=node_id,
            state=state,
            state_key=state_key,
            parent_id=parent_id,
            action_from_parent=action_from_parent,
            depth=depth,
            prior=prior,
            is_terminal=is_terminal,
            is_solved=is_solved,
        )

    def _backprop(self, nodes: Dict[int, _MCTSNode], path: List[int], leaf_value: float) -> None:
        g = leaf_value
        for nid in reversed(path):
            n = nodes[nid]
            n.visits += 1
            n.value_sum += g
            g *= self.config.mcts_gamma

    def _extract_proof_from_terminal(self, nodes: Dict[int, _MCTSNode], terminal_id: int) -> List[str]:
        actions = []
        cur = terminal_id
        while cur is not None:
            n = nodes[cur]
            if n.action_from_parent:
                actions.append(n.action_from_parent)
            cur = n.parent_id
        actions.reverse()
        return actions

    def search(self, theorem_name: str, theorem_goal_expr: str, theorem_code: str = "") -> GuidedSearchResult:
        cfg = self.config
        t0 = time.time()

        init_state = self.dojo.goal_start_expr(theorem_name)
        if init_state is None or isinstance(init_state, ProofFinished):
            return GuidedSearchResult(theorem_name, False, [], 0, 0, time.time() - t0, [], 0, None)

        nodes: Dict[int, _MCTSNode] = {}
        next_node_id = 1
        root = self._new_node(
            node_id=0,
            state=init_state,
            state_key=init_state.pp,
            parent_id=None,
            action_from_parent="",
            depth=0,
            prior=1.0,
            is_terminal=False,
            is_solved=False,
        )
        root.untried_actions = self._collect_candidates_with_scores(init_state, theorem_name, theorem_code, depth=0)
        nodes[0] = root

        failed_by_state: Dict[str, Set[str]] = {}
        n_steps = 0
        max_depth_reached = 0
        solved_terminal_id: Optional[int] = None

        iters_done = 0
        for _ in range(cfg.mcts_iters):
            iters_done += 1
            if cfg.max_time > 0 and (time.time() - t0) >= cfg.max_time:
                break
            if cfg.max_steps > 0 and n_steps >= cfg.max_steps:
                break

            path = [0]
            current_id = 0

            # Selection
            while True:
                cur = nodes[current_id]
                if cur.is_terminal or cur.depth >= cfg.max_depth:
                    break
                if cur.untried_actions:
                    break
                if not cur.children:
                    break
                current_id = max(
                    cur.children.values(),
                    key=lambda cid: self._uct_score(cur, nodes[cid]),
                )
                path.append(current_id)

            cur = nodes[current_id]
            max_depth_reached = max(max_depth_reached, cur.depth)

            # Expansion / Evaluation
            if cur.is_terminal:
                leaf_value = 1.0 if cur.is_solved else 0.0
                self._backprop(nodes, path, leaf_value)
                if cur.is_solved:
                    solved_terminal_id = current_id
                    break
                continue

            if cur.depth >= cfg.max_depth:
                leaf_value = self._heuristic_reward(cur.state_key, cur.depth)
                self._backprop(nodes, path, leaf_value)
                continue

            if cur.untried_actions:
                action, prior_score = cur.untried_actions.pop(0)
                n_steps += 1
                res = self.dojo.run_tac(cur.state, action) if cur.state is not None else None
                if res is None:
                    if cfg.negatives_per_state > 0:
                        failed_by_state.setdefault(cur.state_key, set()).add(action)
                    self._backprop(nodes, path, 0.0)
                    continue

                if isinstance(res, ProofFinished):
                    term_id = next_node_id
                    next_node_id += 1
                    term_key = f"{cur.state_key}##FIN##{term_id}"
                    term = self._new_node(
                        node_id=term_id,
                        state=None,
                        state_key=term_key,
                        parent_id=current_id,
                        action_from_parent=action,
                        depth=cur.depth + 1,
                        prior=max(0.01, prior_score),
                        is_terminal=True,
                        is_solved=True,
                    )
                    nodes[term_id] = term
                    cur.children[action] = term_id
                    self._backprop(nodes, path + [term_id], 1.0)
                    solved_terminal_id = term_id
                    break

                if not isinstance(res, ProofState):
                    self._backprop(nodes, path, 0.0)
                    continue

                child_id = next_node_id
                next_node_id += 1
                child = self._new_node(
                    node_id=child_id,
                    state=res,
                    state_key=res.pp,
                    parent_id=current_id,
                    action_from_parent=action,
                    depth=cur.depth + 1,
                    prior=max(0.01, prior_score),
                    is_terminal=False,
                    is_solved=False,
                )
                if cfg.max_states > 0 and len(nodes) >= cfg.max_states:
                    child.untried_actions = []
                else:
                    child.untried_actions = self._collect_candidates_with_scores(
                        res, theorem_name, theorem_code, depth=child.depth
                    )
                nodes[child_id] = child
                cur.children[action] = child_id

                leaf_value = self._heuristic_reward(child.state_key, child.depth)
                self._backprop(nodes, path + [child_id], leaf_value)
            else:
                leaf_value = self._heuristic_reward(cur.state_key, cur.depth)
                self._backprop(nodes, path, leaf_value)

            if solved_terminal_id is not None:
                break

        theorem_proven = solved_terminal_id is not None
        proof_tactics: List[str] = []
        pairs: List[TrainingPair] = []
        if theorem_proven:
            proof_tactics = self._extract_proof_from_terminal(nodes, solved_terminal_id)
            pairs.extend(self._build_pairs_from_proof(theorem_name, theorem_goal_expr, init_state, proof_tactics))

        self._append_negative_pairs(theorem_name, theorem_goal_expr, failed_by_state, pairs)
        root = nodes[0]
        root_actions = []
        for action, cid in root.children.items():
            child = nodes[cid]
            root_actions.append(
                {
                    "tactic": action,
                    "visits": child.visits,
                    "q": round(child.q_value(), 4),
                    "prior": round(child.prior, 4),
                }
            )
        root_actions.sort(key=lambda x: x["visits"], reverse=True)
        search_stats = {
            "engine": "mcts",
            "iterations": iters_done,
            "root_visits": root.visits,
            "root_children": len(root.children),
            "root_top_actions": root_actions[:10],
        }
        return GuidedSearchResult(
            theorem_name=theorem_name,
            theorem_proven=theorem_proven,
            proof_tactics=proof_tactics,
            n_steps=n_steps,
            n_states=len(nodes),
            elapsed=time.time() - t0,
            pairs=pairs,
            max_depth_reached=max_depth_reached,
            search_stats=search_stats,
        )
