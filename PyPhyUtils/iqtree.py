from .custom_types import *


def _get_iqtree_base_command(
    iqtree_executable: Executable,
    msa: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> List:
    rerun_analysis = ["-redo"] if rerun_analysis else []

    additional_settings = []
    for key, value in kwargs.items():
        if value is None:
            additional_settings += [f"-{key}"]
        else:
            additional_settings += [f"-{key}", str(value)]

    return [
        iqtree_executable,
        "-s",
        msa,
        "-m",
        model,
        "-pre",
        prefix,
        "-nt",
        str(threads),
        *rerun_analysis,
        *additional_settings,
    ]


def get_iqtree_treesearch_command(
    iqtree_executable: Executable,
    msa: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    num_pars_trees: int = 10,
    rerun_analysis=False,
    **kwargs,
) -> List:
    if num_pars_trees > 0:
        trees = ["-ninit", num_pars_trees]
    else:
        raise ValueError("Error: num_pars_trees must not be <= 0.")

    base_command = _get_iqtree_base_command(
        iqtree_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )

    return base_command + trees


def get_iqtree_eval_command(
    iqtree_executable: Executable,
    msa: FilePath,
    treefile: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> List:

    base_command = _get_iqtree_base_command(
        iqtree_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )
    return base_command + ["-te", treefile]


def get_iqtree_tree_topology_test_command(
    iqtree_executable: Executable,
    msa: FilePath,
    treesfile: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    best_tree_file: FilePath = None,
    n_bootstrap_replicates: int = 10_000,
    **kwargs,
) -> List:

    best_tree = ["-te", best_tree_file] if best_tree_file else []

    base_command = _get_iqtree_base_command(
        iqtree_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
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
