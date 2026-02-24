import unittest

from re_rl.tasks import (
    BayesianReasoningTask,
    CombinatorialOptimizationTask,
    CSPReasoningTask,
    GraphJustificationTask,
    ProofCasesCounterexampleTask,
    SATSMTMiniTask,
)


class TestNewReasoningFamilies(unittest.TestCase):
    def test_csp_reasoning(self):
        task = CSPReasoningTask.generate_random_task(language="ru", difficulty=5)
        result = task.get_result()
        self.assertIn("problem", result)
        self.assertTrue(str(result["final_answer"]).strip())

    def test_sat_smt_mini(self):
        task = SATSMTMiniTask.generate_random_task(language="ru", difficulty=7)
        result = task.get_result()
        self.assertIn("problem", result)
        self.assertTrue("SAT" in str(result["final_answer"]) or "UNSAT" in str(result["final_answer"]))

    def test_proof_cases_counterexample(self):
        task = ProofCasesCounterexampleTask.generate_random_task(language="ru", difficulty=6)
        result = task.get_result()
        self.assertIn("problem", result)
        self.assertTrue(
            str(result["final_answer"]).startswith("TRUE") or str(result["final_answer"]).startswith("FALSE")
        )

    def test_graph_justification(self):
        task = GraphJustificationTask.generate_random_task(language="ru", difficulty=8)
        result = task.get_result()
        self.assertIn("problem", result)
        self.assertTrue(str(result["final_answer"]).strip())

    def test_bayesian_reasoning(self):
        task = BayesianReasoningTask.generate_random_task(language="ru", difficulty=8)
        result = task.get_result()
        self.assertIn("P(", str(result["final_answer"]))

    def test_combinatorial_optimization(self):
        task = CombinatorialOptimizationTask.generate_random_task(language="ru", difficulty=9)
        result = task.get_result()
        self.assertIn("problem", result)
        self.assertTrue(str(result["final_answer"]).strip())


if __name__ == "__main__":
    unittest.main()
