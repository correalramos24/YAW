
from utils.utils_py import is_list
from utils.logger import MyLogger

from .AbstractRunner import AbstractRunner

from pathlib import Path
from itertools import product
from typing import List, Type, Iterable


_RUNNER_REGISTRY: dict[str, Type[AbstractRunner]] = {}


def register_runner(cls: Type[AbstractRunner]):
    if not issubclass(cls, AbstractRunner):
        raise TypeError(f"{cls.__name__} is not a subclass of AbstractRunner")

    name = str.lower(cls.__name__)
    if name in _RUNNER_REGISTRY:
        raise ValueError(f"Runner '{name}' is already used!")

    _RUNNER_REGISTRY[name] = cls
    return cls


class RunnerFactory:
    def parse(recipie: Path) -> AbstractRunner:
        return None

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

    @staticmethod
    def generate(runner_name: str) -> None:
        if runner_name not in _RUNNER_REGISTRY:
            MyLogger.critical(f"Cannot generate template for {runner_name}")
            exit(1)
        else:
            _RUNNER_REGISTRY[runner_name].generate_yaml_template()

    @staticmethod
    def get_runners() -> Iterable[str]:
        return [str(k) for k in _RUNNER_REGISTRY.keys()]

    def all_params() -> Iterable[str]:
        aux = list(_RUNNER_REGISTRY.values())
        return {param for runner in aux for param in runner.get_parameters()}
