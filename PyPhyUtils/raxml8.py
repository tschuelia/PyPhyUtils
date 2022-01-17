from .custom_types import *


def _get_raxml_base_command(
    raxml_executable: Executable,
    msa: FilePath,
    model: str,
    suffix: str,
    threads: int = 2,
    **kwargs,
) -> str:
    additional_settings = []
    for key, value in kwargs.items():
        if value is None:
            additional_settings += [f"-{key}"]
        else:
            additional_settings += [f"-{key}", str(value)]

    return [
        raxml_executable,
        "-s",
        msa,
        "-m",
        model,
        "-n",
        suffix,
        "-T",
        str(threads),
        *additional_settings,
    ]


def get_raxml_tree_topology_test_command(
    raxml_executable: Executable,
    msa: FilePath,
    treesfile: FilePath,
    model: str,
    suffix: str,
    test_algorithm: str,
    best_tree_file: FilePath = None,
    threads: int = 2,
    n_bootstrap_replicates: int = 10_000,
    **kwargs,
) -> str:

    algo = ["-f"]
    if test_algorithm == "ELW":
        algo += ["W"]
    elif test_algorithm == "SH":
        algo += ["H"]
    else:
        raise ValueError(
            f"Error: unrecognized topology test algorithm {test_algorithm}. Available options are `ELW` and `SH`."
        )

    best_tree = ["-t", best_tree_file] if best_tree_file else []

    base_command = _get_raxml_base_command(
        raxml_executable, msa, model, suffix, threads, **kwargs
    )

    return base_command + [
        *algo,
        "-z",
        treesfile,
        *best_tree,
        "-N",
        str(n_bootstrap_replicates),
    ]
