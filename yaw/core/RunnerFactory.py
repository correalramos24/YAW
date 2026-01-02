
from yaw.core.AbstractRunner import AbstractRunner
from utils.utils_py import is_list
from utils.logger import MyLogger

from itertools import product
from typing import List


class RunnerFactory:
    @staticmethod
    def derive(runner: AbstractRunner) -> List[AbstractRunner]:
        deriving_params = [(p, v) for p, v in runner.get_params_values().items()
                           if is_list(v) and p not in runner.get_multivalue_params()]

        if len(deriving_params) < 1:
            return [runner]
        deriving_p_names = [p for p, _ in deriving_params]

        MyLogger.log(f"Deriving recipies using {runner.mode}!")
        join_op = product if runner.mode == "cartesian" else zip
        deriving_values = list(
            join_op(*[getattr(runner, param) for param, _ in deriving_params])
        )

        variations = [
            {**runner.get_params_values(), **dict(zip(deriving_p_names, variation))} 
            for variation in deriving_values
        ]
        m = runner.mirror
        if m != 0:
            MyLogger.log(f"Adding {m} mirror recipies!")
            MyLogger.log(f"Found {len(deriving_values)*m} recipies.")
        else:
            MyLogger.log(f"Found {len(deriving_values)} recipies.")
        return [runner.__class__(**variation) for variation in variations] * m
