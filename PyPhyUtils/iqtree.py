from custom_types import *


def _get_iqtree_base_command(
    iqtree_executable: Executable,
    msa: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> str:
    rerun_analysis = "-redo" if rerun_analysis else ""
    additional_settings = ""
    for key, value in kwargs.items():
        additional_settings += f"-{key} {value}"

    return (
        f"{iqtree_executable} "
        f"-s {msa} "
        f"-m {model} "
        f"-pre {prefix} "
        f"-nt {threads} "
        f"{rerun_analysis} "
        f"{additional_settings}"
    )


def get_iqtree_treesearch_command(
    iqtree_executable: Executable,
    msa: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    num_pars_trees: int = 10,
    rerun_analysis=False,
    **kwargs,
) -> str:
    if num_pars_trees > 0:
        trees = f"-ninit {num_pars_trees}"
    else:
        raise ValueError("Error: num_pars_trees must not be <= 0.")

    base_command = _get_iqtree_base_command(
        iqtree_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )

    return f"{base_command} {trees}"


def get_iqtree_eval_command(
    iqtree_executable: Executable,
    msa: FilePath,
    treefile: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    **kwargs,
) -> str:

    base_command = _get_iqtree_base_command(
        iqtree_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )

    return f"{base_command} -te {treefile}"


def get_iqtree_tree_topology_test_command(
    iqtree_executable: Executable,
    msa: FilePath,
    treesfile: FilePath,
    model: str,
    prefix: str,
    threads: int = 2,
    rerun_analysis=False,
    best_tree_file: FilePath = None,
    n_bootstrap_replicates=10_000,
    **kwargs,
) -> str:

    best_tree = f"-te {best_tree_file}" if best_tree_file else ""

    base_command = _get_iqtree_base_command(
        iqtree_executable, msa, model, prefix, threads, rerun_analysis, **kwargs
    )

    return f"{base_command} -z {treesfile} {best_tree} -n 0 -zb {n_bootstrap_replicates} -zw -au"


print(
    get_iqtree_tree_topology_test_command(
        "iqtree",
        msa="/Users/julia/Desktop/Promotion/StatisticalTests/input_files/D354/D354.phy",
        model="GTR+G",
        prefix="/tmp/prefix",
        threads=2,
        treesfile="/Users/julia/Desktop/Promotion/StatisticalTests/input_files/D354/un_trees.ordered",
        best_tree_file="/Users/julia/Desktop/Promotion/StatisticalTests/input_files/D354/best.tree",
        rerun_analysis=True,
        seed=42
    )
)
