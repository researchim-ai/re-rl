"""Базовые задачи машинного обучения с точными ответами."""

from re_rl.tasks.ml.entropy_task import ShannonEntropyTask
from re_rl.tasks.ml.gini_task import GiniSplitTask
from re_rl.tasks.ml.knn_task import KNNClassifyTask
from re_rl.tasks.ml.perceptron_task import PerceptronUpdateTask
from re_rl.tasks.ml.kmeans_task import KMeansStepTask
from re_rl.tasks.ml.naive_bayes_task import NaiveBayesTask
from re_rl.tasks.ml.confusion_task import ConfusionMetricsTask
from re_rl.tasks.ml.gradient_step_task import GradientStepTask
from re_rl.tasks.ml.ranking_auc_task import RankingAUCTask
from re_rl.tasks.ml.hinge_task import HingeLossTask
from re_rl.tasks.ml.cosine_task import CosineRankTask
from re_rl.tasks.ml.univariate_regression_task import UnivariateRegressionTask
from re_rl.tasks.ml.decision_stump_task import DecisionStumpTask
from re_rl.tasks.ml.brier_task import BrierScoreTask
from re_rl.tasks.ml.mse_task import MseTask
from re_rl.tasks.ml.precision_at_k_task import PrecisionAtKTask
from re_rl.tasks.ml.kappa_task import CohenKappaTask
from re_rl.tasks.ml.r2_task import R2Task
from re_rl.tasks.ml.average_precision_task import AveragePrecisionTask
from re_rl.tasks.ml.mae_task import MaeTask
from re_rl.tasks.ml.jaccard_task import JaccardTask
from re_rl.tasks.ml.reciprocal_rank_task import ReciprocalRankTask
from re_rl.tasks.ml.kalman_task import KalmanUpdateTask
from re_rl.tasks.ml.hmm_task import HmmDecodeTask
from re_rl.tasks.ml.elimination_task import EliminationQueryTask
from re_rl.tasks.ml.pagerank_task import PageRankTask

__all__ = [
    "ShannonEntropyTask",
    "GiniSplitTask",
    "KNNClassifyTask",
    "PerceptronUpdateTask",
    "KMeansStepTask",
    "NaiveBayesTask",
    "ConfusionMetricsTask",
    "GradientStepTask",
    "RankingAUCTask",
    "HingeLossTask",
    "CosineRankTask",
    "UnivariateRegressionTask",
    "DecisionStumpTask",
    "BrierScoreTask",
    "MseTask",
    "PrecisionAtKTask",
    "CohenKappaTask",
    "R2Task",
    "AveragePrecisionTask",
    "MaeTask",
    "JaccardTask",
    "ReciprocalRankTask",
    "KalmanUpdateTask",
    "HmmDecodeTask",
    "EliminationQueryTask",
    "PageRankTask",
]
