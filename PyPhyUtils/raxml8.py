from .custom_types import *


def _get_raxml_base_command(
    raxml_executable: Executable,
    msa: FilePath,
    model: str,
    suffix: str,
    threads: int = 2,
    **kwargs,
) -> str:
    additional_settings = ""
    for key, value in kwargs.items():
        additional_settings += f"--{key} {value} "

    return (
        f"{raxml_executable} "
        f"-s {msa} "
        f"-m {model} "
        f"-n {suffix} "
        f"-T {threads} "
        f"{additional_settings}"
    )


def get_raxml_tree_topology_test_command(
    raxml_executable: Executable,
    msa: FilePath,
    treesfile: FilePath,
    model: str,
    suffix: str,
    test_algorithm: str,
    best_tree_file: FilePath = None,
    threads: int = 2,
    n_bootstrap_replicates=10_000,
    **kwargs,
) -> str:

    algo = "-f "
    if test_algorithm == "ELW":
        algo += "W"
    elif test_algorithm == "SH":
        algo += "H"
    else:
        raise ValueError(f"Error: unrecognized topology test algorithm {test_algorithm}. Available options are `ELW` and `SH`.")

    best_tree = f"-t {best_tree_file}" if best_tree_file else ""

    base_command = _get_raxml_base_command(
        raxml_executable, msa, model, suffix, threads, **kwargs
    )

    return f"{base_command} {algo} -z {treesfile} {best_tree} -N {n_bootstrap_replicates}"
