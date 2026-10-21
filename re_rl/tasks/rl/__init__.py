"""Задачи обучения с подкреплением с точными дробными ответами."""

from re_rl.tasks.rl.discounted_return_task import DiscountedReturnTask
from re_rl.tasks.rl.q_learning_task import QLearningTask
from re_rl.tasks.rl.bellman_task import BellmanBackupTask
from re_rl.tasks.rl.sarsa_task import SarsaTask
from re_rl.tasks.rl.epsilon_greedy_task import EpsilonGreedyTask
from re_rl.tasks.rl.policy_expectation_task import PolicyExpectationTask
from re_rl.tasks.rl.reward_to_go_task import RewardToGoTask
from re_rl.tasks.rl.double_q_task import DoubleQTask
from re_rl.tasks.rl.polyak_task import PolyakTask
from re_rl.tasks.rl.eligibility_task import EligibilityTraceTask
from re_rl.tasks.rl.expected_sarsa_task import ExpectedSarsaTask
from re_rl.tasks.rl.gae_task import GaeTask
from re_rl.tasks.rl.ppo_task import PpoClipTask
from re_rl.tasks.rl.importance_task import ImportanceRatioTask
from re_rl.tasks.rl.average_reward_task import AverageRewardTask
from re_rl.tasks.rl.vtrace_task import VTraceTask
from re_rl.tasks.rl.priority_replay_task import PriorityReplayTask
from re_rl.tasks.rl.reward_clip_task import RewardClipTask
from re_rl.tasks.rl.finite_horizon_task import FiniteHorizonTask
from re_rl.tasks.rl.q_trajectory_task import QTrajectoryTask
from re_rl.tasks.rl.sarsa_trajectory_task import SarsaTrajectoryTask
from re_rl.tasks.rl.double_q_trajectory_task import DoubleQTrajectoryTask

__all__ = [
    "DiscountedReturnTask",
    "QLearningTask",
    "BellmanBackupTask",
    "SarsaTask",
    "EpsilonGreedyTask",
    "PolicyExpectationTask",
    "RewardToGoTask",
    "DoubleQTask",
    "PolyakTask",
    "EligibilityTraceTask",
    "ExpectedSarsaTask",
    "GaeTask",
    "PpoClipTask",
    "ImportanceRatioTask",
    "AverageRewardTask",
    "VTraceTask",
    "PriorityReplayTask",
    "RewardClipTask",
    "FiniteHorizonTask",
    "QTrajectoryTask",
    "SarsaTrajectoryTask",
    "DoubleQTrajectoryTask",
]
