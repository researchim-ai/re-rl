"""Масштабируемые задачи: число звеньев и длина решения растут вместе с уровнем."""

import math
import random
import re

import pytest

from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.math.discrete.greedy_coins.task import greedy_picks, optimal_count
from re_rl.tasks.math.logic.line_infection.task import spread_once
from re_rl.tasks.math.logic.next_greater.task import next_greater
from re_rl.tasks.math.probability.polya_urn.task import sequence_probability
from re_rl.tasks.ml.kmeans_rounds.task import cluster_rounds
from re_rl.tasks.math.analysis.difference_table.task import extend_table, polynomial_value
from re_rl.tasks.math.discrete.cf_expand.task import convergents
from re_rl.tasks.physics.networks.network_reduce.task import equivalent, leaf_sum
from re_rl.tasks.physics.quantum.decay_generations.task import decay_tick
from re_rl.tasks.registry import registry

CYRILLIC = re.compile(r"[А-Яа-яЁё]")

POOL = [
    "gear_train",
    "relay_time",
    "voltage_divider",
    "crew_work",
    "mix_chain",
    "mod_chain",
    "spring_series",
    "lens_stack",
    "block_stack",
    "sticking_chain",
    "gcd_chain",
    "recurrence_walk",
    "turtle_walk",
    "horner_eval",
    "ledger_guard",
    "door_toggles",
    "truck_trips",
    "portal_walk",
    "cascade_tanks",
    "greedy_coins",
    "walk_range",
    "line_infection",
    "corridor_keys",
    "carry_add",
    "next_greater",
    "window_max",
    "two_pointer_merge",
    "cooldown_schedule",
    "pancake_trace",
    "bracket_scan",
    "kmeans_rounds",
    "bayes_updates",
    "polya_urn",
    "policy_rollout",
    "extended_euclid",
    "crt_chain",
    "cf_expand",
    "nim_sum",
    "difference_table",
    "network_reduce",
    "decay_generations",
    "bounce_heights",
]


def _one(task_type, language, difficulty, subtype=None, seed=0):
    random.seed(seed)
    kwargs = {"language": language, "difficulty": difficulty}
    if subtype is not None:
        kwargs["task_type"] = subtype
    return ALL_TASK_GENERATORS[task_type](**kwargs)


@pytest.mark.parametrize("task_type", POOL)
def test_registered(task_type):
    assert task_type in registry
    assert task_type in ALL_TASK_GENERATORS


@pytest.mark.parametrize("task_type", POOL)
@pytest.mark.parametrize("language", ["ru", "en"])
@pytest.mark.parametrize("difficulty", [1, 5, 10])
def test_self_consistent(task_type, language, difficulty):
    for subtype in registry[task_type].TASK_TYPES:
        for seed in range(3):
            task = _one(task_type, language, difficulty, subtype, seed + difficulty)
            blob = task.description + "\n" + "\n".join(task.solution_steps)
            assert task.final_answer is not None
            assert "{" not in blob
            assert len(task.solution_steps) >= task.n
            assert task.verify(f"<answer>{task.final_answer}</answer>") == pytest.approx(1.0)
            if language == "en":
                assert not CYRILLIC.search(blob)
            else:
                assert CYRILLIC.search(task.description)


@pytest.mark.parametrize("task_type", POOL)
def test_size_grows_with_difficulty(task_type):
    low = _one(task_type, "ru", 1, seed=1)
    high = _one(task_type, "ru", 10, seed=1)
    assert high.n > low.n
    assert len(high.solution_steps) > len(low.solution_steps)


def test_chain_values():
    random.seed(4)
    gear = _one("gear_train", "en", 6, seed=4)
    product = gear.teeth[0] * gear.speeds[0]
    assert all(teeth * speed == product for teeth, speed in zip(gear.teeth, gear.speeds))
    assert gear.answer == gear.speeds[-1]

    relay = _one("relay_time", "en", 7, seed=4)
    assert relay.total == sum(leg["distance"] // leg["speed"] for leg in relay.legs)

    divider = _one("voltage_divider", "en", 8, "part", seed=4)
    assert divider.total_v == divider.current * sum(divider.resistors)
    assert divider.part == divider.current * divider.resistors[divider.k - 1]

    crew = _one("crew_work", "en", 5, seed=4)
    assert crew.job == crew.days * sum(crew.rates)

    mix = _one("mix_chain", "en", 9, seed=4)
    current = mix.start
    for step in mix.steps:
        solute = (mix.volume - step["out"]) * step["before"] + step["out"] * step["added"]
        assert solute % mix.volume == 0
        assert step["after"] == solute // mix.volume
        current = step["after"]
    assert mix.answer == current

    chain = _one("mod_chain", "en", 10, seed=4)
    value = chain.start
    for factor, shift, stored in chain.ops:
        value = (value * factor + shift) % chain.mod
        assert stored == value
    assert chain.answer == value

    springs = _one("spring_series", "en", 6, seed=4)
    assert springs.total == sum(springs.force // item for item in springs.stiffness)
    assert all(springs.force % item == 0 for item in springs.stiffness)

    lenses = _one("lens_stack", "en", 5, seed=4)
    assert lenses.total == sum(lenses.powers)
    assert all(item != 0 for item in lenses.powers)

    blocks = _one("block_stack", "en", 7, "moment", seed=4)
    assert blocks.moment == sum(mass * center for mass, center in zip(blocks.masses, blocks.centers))
    assert all(item % 2 == 0 for item in blocks.thickness)

    carts = _one("sticking_chain", "en", 8, "speed", seed=4)
    assert sum(carts.velocities) == carts.n * carts.speed
    assert carts.momentum == carts.mass * sum(carts.velocities)

    gcd_task = _one("gcd_chain", "en", 9, seed=4)
    assert gcd_task.answer == math.gcd(*gcd_task.numbers)

    walk = _one("recurrence_walk", "en", 10, seed=4)
    for index in range(2, len(walk.terms)):
        assert walk.terms[index] == walk.terms[index - 1] + walk.terms[index - 2]
    assert walk.answer == walk.terms[-1]
    assert len(walk.solution_steps) >= walk.n

    turtle = _one("turtle_walk", "en", 6, "manhattan", seed=4)
    assert turtle.manhattan == abs(turtle.x) + abs(turtle.y)
    assert turtle.trace[-1] == (turtle.x, turtle.y)

    horner = _one("horner_eval", "en", 8, seed=4)
    acc = 0
    for coeff in horner.coeffs:
        acc = acc * horner.x + coeff
    assert horner.answer == acc

    ledger = _one("ledger_guard", "en", 7, "rejected", seed=4)
    balance = ledger.start
    rejected = 0
    for op in ledger.ops:
        if op["sign"] > 0:
            balance += op["amount"]
        elif op["amount"] > balance:
            rejected += 1
        else:
            balance -= op["amount"]
        assert op["balance"] == balance
    assert (ledger.balance, ledger.rejected) == (balance, rejected)

    doors = _one("door_toggles", "en", 10, "count", seed=4)
    assert doors.count == math.isqrt(doors.n)
    assert doors.largest == math.isqrt(doors.n) ** 2

    truck = _one("truck_trips", "en", 9, "trips", seed=4)
    trips = 1
    load = 0
    for size in truck.sizes:
        if load + size > truck.capacity:
            trips += 1
            load = 0
        load += size
    assert (truck.trips, truck.leftover) == (trips, load)
    assert load <= truck.capacity

    portal = _one("portal_walk", "en", 10, seed=4)
    room = 0
    for _ in range(portal.n):
        room = portal.nxt[room]
    assert portal.answer == room

    tanks = _one("cascade_tanks", "en", 8, "tank", seed=4)
    left = tanks.pour
    held = []
    for cap in tanks.caps:
        take = min(cap, left)
        held.append(take)
        left -= take
    assert tanks.held == held
    assert tanks.spilled == left
    assert sum(held) + left == tanks.pour

    coins = _one("greedy_coins", "en", 10, "extra", seed=4)
    assert coins.picks == greedy_picks(coins.amount)
    assert coins.optimal == optimal_count(coins.amount)
    assert coins.extra == len(coins.picks) - coins.optimal
    assert coins.extra > 0
    assert coins.n > _one("greedy_coins", "en", 1, seed=4).n

    walk = _one("walk_range", "en", 9, "lowest", seed=4)
    assert walk.final == sum(walk.deltas)
    assert walk.lowest == min([0] + walk.heights)

    infected = _one("line_infection", "en", 7, seed=4)
    state = infected.infected[:]
    for _ in range(infected.n):
        state = spread_once(state)
    assert infected.answer == sum(state)

    keys = _one("corridor_keys", "en", 8, "farthest", seed=4)
    held = set()
    farthest = 0
    for room in range(keys.n):
        if room and keys.need[room] is not None and keys.need[room] not in held:
            break
        held.update(keys.keys_here[room])
        farthest = room
    assert keys.farthest == farthest
    assert keys.keys == len(held)

    addition = _one("carry_add", "en", 10, "carries", seed=4)
    assert addition.sum == addition.a + addition.b
    assert addition.carries == sum(1 for column in addition.columns if column["carry_out"])

    greater = _one("next_greater", "en", 8, "distance_sum", seed=4)
    assert greater.nxt == next_greater(greater.values)
    assert greater.missing == sum(1 for index in greater.nxt if index < 0)

    window = _one("window_max", "en", 10, "total", seed=4)
    maxima = [
        max(window.values[start:start + window.k])
        for start in range(window.length - window.k + 1)
    ]
    assert window.maxima == maxima
    assert window.n == window.length - window.k + 1
    assert window.n > _one("window_max", "en", 1, seed=4).n

    merged = _one("two_pointer_merge", "en", 9, "wins", seed=4)
    assert merged.merged == sorted(merged.left + merged.right)
    assert len(merged.merged) == merged.n

    schedule = _one("cooldown_schedule", "en", 7, "idles", seed=4)
    assert schedule.time == schedule.n + schedule.idles

    pancakes = _one("pancake_trace", "en", 6, "place", seed=4)
    perm = pancakes.start[:]
    for width in pancakes.flips:
        perm[:width] = list(reversed(perm[:width]))
    assert perm == pancakes.perm
    assert pancakes.place == perm.index(1) + 1

    brackets = _one("bracket_scan", "en", 8, "error", seed=4)
    assert len(brackets.expr) == brackets.n
    assert brackets.max_depth >= 0
    assert brackets.error == 0 or 1 <= brackets.error <= brackets.n + 1

    rounds = _one("kmeans_rounds", "en", 6, "center", seed=4)
    assert rounds.rounds == cluster_rounds(rounds.points, rounds.n)
    assert rounds.center == rounds.rounds[-1][0]

    bayes = _one("bayes_updates", "en", 7, "percent", seed=4)
    favor, against = bayes.start, 100 - bayes.start
    for item in bayes.updates:
        num = favor * item["yes"]
        den = against * item["no"]
        assert item["new"] == (100 * num) // (num + den)
        divisor = math.gcd(num, den)
        favor, against = num // divisor, den // divisor
    assert bayes.percent == (100 * favor) // (favor + against)

    urn = _one("polya_urn", "en", 8, "denom", seed=4)
    probability = sequence_probability(urn.red, urn.blue, urn.sequence)
    assert (urn.numer, urn.denom) == (probability.numerator, probability.denominator)

    rollout = _one("policy_rollout", "en", 9, "reward", seed=4)
    position = rollout.start
    total = 0
    for action_state in rollout.trace:
        pos, action, nxt, running = action_state
        assert pos == position
        landed = min(rollout.length - 1, max(0, position + rollout.policy[position]))
        assert nxt == landed
        total += rollout.rewards[nxt]
        assert running == total
        position = nxt
    assert rollout.total == total
    assert rollout.end == position

    bezout = _one("extended_euclid", "en", 8, "x", seed=4)
    assert len(bezout.trace) == bezout.n
    assert bezout.a * bezout.x + bezout.b * bezout.y == bezout.gcd

    system = _one("crt_chain", "en", 7, "value", seed=4)
    assert all(system.value % mod == rem for mod, rem in zip(system.moduli, system.remainders))
    assert 0 <= system.value < system.modulus

    fraction = _one("cf_expand", "en", 6, "numer", seed=4)
    assert fraction.pairs == convergents(fraction.quotients)
    assert math.gcd(fraction.numer, fraction.denom) == 1

    nim = _one("nim_sum", "en", 9, "winning", seed=4)
    total_xor = 0
    for size in nim.heaps:
        total_xor ^= size
    assert nim.nim == total_xor
    assert nim.winning == (1 if total_xor else 0)

    table = _one("difference_table", "en", 10, "next", seed=4)
    assert table.nxt == polynomial_value(table.coeffs, table.n)
    assert table.nxt == extend_table(table.values)
    assert table.delta == table.coeffs[-1]

    network = _one("network_reduce", "en", 8, "equivalent", seed=4)
    assert network.equivalent == equivalent(network.tree)
    assert network.total_leaves == leaf_sum(network.tree)
    assert network.equivalent <= network.total_leaves

    decay = _one("decay_generations", "en", 6, "stable", seed=4)
    counts = [decay.seed_count * 2 ** decay.n] + [0] * (decay.species - 1)
    for _ in range(decay.n):
        counts = decay_tick(counts)
    assert decay.counts == counts
    assert sum(counts) == decay.seed_count * 2 ** decay.n
    assert counts[0] == decay.seed_count

    bounce = _one("bounce_heights", "en", 10, "at_k", seed=4)
    assert bounce.heights[0] == bounce.start // 2
    assert bounce.final == bounce.unit
    assert bounce.at_k == bounce.start // 2 ** bounce.k
