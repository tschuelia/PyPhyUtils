from .custom_types import *


class RAxML:
    def __init__(self, exe_path: Executable):
        self.exe_path = exe_path

    def _base_cmd(
        self,
        msa: FilePath,
        model: str,
        suffix: str,
        **kwargs,
    ) -> Command:
        additional_settings = []
        for key, value in kwargs.items():
            if value is None:
                additional_settings += [f"-{key}"]
            else:
                additional_settings += [f"-{key}", str(value)]

        return [
            self.exe_path,
            "-s",
            msa,
            "-m",
            model,
            "-n",
            suffix,
            *additional_settings,
        ]

    def get_tree_topology_test_command(
        self,
        msa: FilePath,
        treesfile: FilePath,
        model: str,
        suffix: str,
        test_algorithm: str,
        best_tree_file: FilePath = None,
        n_bootstrap_replicates: int = 10_000,
        bootstrap_seed: int = 1,
        **kwargs,
    ) -> Command:

        algo = ["-f"]
        if test_algorithm == "ELW":
            algo += ["W"]
        elif test_algorithm == "SH":
            algo += ["H"]
        elif test_algorithm == "sitelh":
            algo += ["G"]
        else:
            raise ValueError(
                f"Error: unrecognized topology test algorithm {test_algorithm}. Available options are `ELW` and `SH`."
            )

        best_tree = ["-t", best_tree_file] if best_tree_file else []

        base_command = self._base_cmd(msa, model, suffix, **kwargs)

        return base_command + [
            *algo,
            "-z",
            treesfile,
            *best_tree,
            "-N",
            str(n_bootstrap_replicates),
            "-b",
            str(bootstrap_seed),
        ]
