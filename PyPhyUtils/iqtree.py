from .custom_types import *


class IQTree:
    def __init__(self, exe_path: Executable):
        self.exe_path = exe_path

    def _base_cmd(
        self, msa_file: FilePath, model: Model, prefix: FilePath, **kwargs
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
            msa_file,
            "-m",
            model,
            "-pre",
            prefix,
            *additional_settings,
        ]

    def get_treesearch_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        prefix: str,
        num_pars_trees: int = 10,
        **kwargs,
    ) -> Command:
        if num_pars_trees > 0:
            trees = ["-ninit", num_pars_trees]
        else:
            raise ValueError("Error: num_pars_trees must not be <= 0.")

        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )
        return base_command + trees

    def get_eval_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        treesfile: FilePath,
        prefix: str,
        **kwargs,
    ):
        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )
        return base_command + ["-te", treesfile]

    def get_iqtree_tree_topology_test_cmd(
        self,
        msa_file: FilePath,
        model: str,
        treesfile: FilePath,
        prefix: str,
        best_tree_file: FilePath = None,
        n_bootstrap_replicates: int = 10_000,
        **kwargs,
    ) -> List:
        best_tree = ["-te", best_tree_file] if best_tree_file else []

        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )

        return base_command + [
            "-z",
            treesfile,
            *best_tree,
            "-n",
            "0",
            "-zb",
            str(n_bootstrap_replicates),
            "-zw",
            "-au",
        ]
