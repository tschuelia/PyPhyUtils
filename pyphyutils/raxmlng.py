from .custom_types import *


class RAxMLNG:
    def __init__(self, exe_path: Executable):
        self.exe_path = exe_path

    def _base_cmd(
        self, msa_file: FilePath, model: Model, prefix: FilePath, **kwargs
    ) -> Command:
        additional_settings = []
        for key, value in kwargs.items():
            if value is None:
                additional_settings += [f"--{key}"]
            else:
                additional_settings += [f"--{key}", str(value)]

        return [
            self.exe_path,
            "--msa",
            msa_file,
            "--model",
            model,
            "--prefix",
            prefix,
            *additional_settings,
        ]

    def get_alignment_parse_cmd(
        self, msa_file: FilePath, model: Model, prefix: str, **kwargs
    ) -> Command:
        return self._base_cmd(msa_file, model, prefix, parse=None, **kwargs)

    def get_rfdist_cmd(self, trees_file: FilePath, prefix: str, **kwargs) -> Command:
        additional_settings = []
        for key, value in kwargs.items():
            if value is None:
                additional_settings += [f"--{key}"]
            else:
                additional_settings += [f"--{key}", str(value)]

        cmd = [
            self.exe_path,
            "--rfdist",
            trees_file,
            "--prefix",
            prefix,
            *additional_settings,
        ]
        return cmd

    def get_infer_parsimony_trees_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        prefix: str,
        n_trees: int = 100,
        **kwargs,
    ) -> Command:
        cmd = self._base_cmd(
            msa_file, model, prefix, start=None, tree=f"pars{{{n_trees}}}", **kwargs
        )
        return cmd

    def get_treesearch_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        prefix: str,
        num_pars_trees: int = 10,
        num_rand_trees: int = 10,
        **kwargs,
    ):
        if num_pars_trees == 0 and num_rand_trees == 0:
            raise ValueError(
                "Error: num_pars_trees and num_rand_trees cannot both be 0."
            )
        elif num_pars_trees == 0:
            trees = f"rand{{{num_rand_trees}}}"
        elif num_rand_trees == 0:
            trees = f"pars{{{num_pars_trees}}}"
        else:
            trees = f"pars{{{num_pars_trees}}},rand{{{num_rand_trees}}}"

        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )

        return base_command + ["--tree", trees]

    def get_eval_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        treesfile: FilePath,
        prefix: str,
        **kwargs,
    ) -> Command:
        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )

        return base_command + ["--eval", "--tree", treesfile]