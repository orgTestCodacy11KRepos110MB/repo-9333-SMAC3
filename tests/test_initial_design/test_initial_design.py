import unittest
import unittest.mock

import numpy as np
from ConfigSpace import Configuration, UniformFloatHyperparameter

from smac.cli.scenario import Scenario
from smac.cli.traj_logging import TrajLogger
from smac.configspace import ConfigurationSpace
from smac.initial_design import InitialDesign
from smac.initial_design.default_design import DefaultInitialDesign
from smac.runhistory.runhistory import RunHistory
from smac.runner.target_algorithm_runner import TargetAlgorithmRunner
from smac.utils.stats import Stats

__copyright__ = "Copyright 2021, AutoML.org Freiburg-Hannover"
__license__ = "3-clause BSD"


class TestSingleInitialDesign(unittest.TestCase):
    def setUp(self):
        self.cs = ConfigurationSpace()
        self.cs.add_hyperparameter(UniformFloatHyperparameter(name="x1", lower=1, upper=10, default_value=1))
        self.scenario = Scenario(
            {
                "cs": self.cs,
                "run_obj": "quality",
                "output_dir": "",
                "ta_run_limit": 100,
            }
        )
        self.stats = Stats(scenario=self.scenario)
        self.rh = RunHistory()
        self.ta = TargetAlgorithmRunner(lambda x: x["x1"] ** 2, stats=self.stats)

    def test_single_default_config_design(self):
        self.stats.start_timing()
        tj = TrajLogger(output_dir=None, stats=self.stats)

        dc = DefaultInitialDesign(
            configspace=self.cs,
            seed=12345,
            n_runs=self.scenario.ta_run_limit,
        )

        # should return only the default config
        configs = dc.select_configurations()
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0]["x1"], 1)

    def test_multi_config_design(self):
        self.stats.start_timing()
        _ = np.random.RandomState(seed=12345)

        configs = [
            Configuration(configuration_space=self.cs, values={"x1": 4}),
            Configuration(configuration_space=self.cs, values={"x1": 2}),
        ]
        dc = InitialDesign(
            configspace=self.cs,
            seed=12345,
            n_runs=self.scenario.ta_run_limit,
            configs=configs,
        )

        # selects multiple initial configurations to run
        # since the configs were passed to initial design, it should return the same
        init_configs = dc.select_configurations()
        self.assertEqual(len(init_configs), 2)
        self.assertEqual(init_configs, configs)

    def test_init_budget(self):
        self.stats.start_timing()
        _ = np.random.RandomState(seed=12345)

        kwargs = dict(
            configspace=self.cs,
            seed=12345,
            n_runs=self.scenario.ta_run_limit,
        )

        configs = [
            Configuration(configuration_space=self.cs, values={"x1": 4}),
            Configuration(configuration_space=self.cs, values={"x1": 2}),
        ]
        dc = InitialDesign(
            configs=configs,
            init_budget=3,
            **kwargs,
        )
        self.assertEqual(dc.init_budget, 3)

        dc = InitialDesign(
            init_budget=3,
            **kwargs,
        )
        self.assertEqual(dc.init_budget, 3)

        configs = [
            Configuration(configuration_space=self.cs, values={"x1": 4}),
            Configuration(configuration_space=self.cs, values={"x1": 2}),
        ]
        dc = InitialDesign(
            configs=configs,
            **kwargs,
        )
        self.assertEqual(dc.init_budget, 2)

        dc = InitialDesign(
            **kwargs,
        )
        self.assertEqual(dc.init_budget, 10)

        with self.assertRaisesRegex(
            ValueError,
            "Initial budget 200 cannot be higher than the run limit 100.",
        ):
            InitialDesign(init_budget=200, **kwargs)

        with self.assertRaisesRegex(
            ValueError,
            "Need to provide either argument `init_budget`, `configs` or `n_configs_per_hyperparameter`, "
            "but provided none of them.",
        ):
            InitialDesign(**kwargs, n_configs_per_hyperparameter=None)

    def test__select_configurations(self):
        kwargs = dict(
            configspace=self.cs,
            n_runs=1000,
            configs=None,
            n_configs_per_hyperparameter=None,
            max_config_ratio=0.25,
            init_budget=1,
            seed=1,
        )
        init_design = InitialDesign(**kwargs)
        with self.assertRaises(NotImplementedError):
            init_design._select_configurations()