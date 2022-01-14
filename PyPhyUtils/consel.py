from .custom_types import *
import os


def get_consel_tree_topology_test_command(
    makermt_executable: Executable,
    consel_executable: Executable,
    catpv_executable: Executable,
    prefix: str,
) -> str:
    if not os.path.exists(prefix + ".sitelh"):
        raise ValueError(f"Error: Consel requires the site loglikelihood as file with name {prefix}.sitelh")

    return f"{makermt_executable} --puzzle {prefix} && {consel_executable} {prefix} && {catpv_executable} {prefix} > {prefix}.consel"
