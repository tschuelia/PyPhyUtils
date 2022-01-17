from .custom_types import *


def _get_raxmlng_base_command(
    raxmlng_executable: Executable,
    msa: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> str:
    rerun_analysis = ["--redo"] if rerun_analysis else []

    additional_settings = []
    for key, value in kwargs.items():
        if value is None:
            additional_settings += [f"--{key}"]
        else:
            additional_settings += [f"--{key}", str(value)]

    return [
        raxmlng_executable,
        "--msa",
        msa,
        "--model",
        model,
        "--prefix",
        prefix,
        "--threads",
        str(threads),
        *rerun_analysis,
        *additional_settings,
    ]


def get_raxmlng_treesearch_command(
    raxmlng_executable: Executable,
    msa: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    num_pars_trees: int = 10,
    num_rand_trees: int = 10,
    rerun_analysis=False,
    **kwargs,
) -> str:
    if num_pars_trees == 0 and num_rand_trees == 0:
        raise ValueError("Error: num_pars_trees and num_rand_trees cannot both be 0.")
    elif num_pars_trees == 0:
        trees = f"rand{{{num_rand_trees}}}"
    elif num_rand_trees == 0:
        trees = f"pars{{{num_pars_trees}}}"
    else:
        trees = f"pars{{{num_pars_trees}}},rand{{{num_rand_trees}}}"

    base_command = _get_raxmlng_base_command(
        raxmlng_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )

    return base_command + ["--tree", trees]


def get_raxmlng_eval_command(
    raxmlng_executable: Executable,
    msa: FilePath,
    treefile: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> str:
    base_command = _get_raxmlng_base_command(
        raxmlng_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )

    return base_command + ["--eval", "--tree", treefile]


def get_raxmlng_rfdistance_command(
    raxmlng_executable: Executable,
    treesfile: FilePath,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> str:
    rerun_analysis = ["--redo"] if rerun_analysis else []

    additional_settings = []
    for key, value in kwargs.items():
        if value is None:
            additional_settings += [f"--{key}"]
        else:
            additional_settings += [f"--{key}", str(value)]

    return [
        raxmlng_executable,
        "--rfdist",
        treesfile,
        "--prefix",
        prefix,
        "--threads",
        str(threads),
        *rerun_analysis,
        *additional_settings,
    ]
