from .custom_types import *


def get_consel_tree_topology_test_command(
    makermt_executable: Executable,
    consel_executable: Executable,
    catpv_executable: Executable,
    prefix: str,
    **kwargs
) -> str:

    additional_settings = []
    for key, value in kwargs.items():
        if value is None:
            additional_settings += [f"-{key}"]
        else:
            additional_settings += [f"-{key}", str(value)]

    _makermt = [
        makermt_executable,
        "--puzzle",
        prefix
    ]

    _consel = [
        consel_executable,
        prefix
    ]

    _catpv = [
        catpv_executable,
        prefix,
        ">",
        prefix + ".consel"
    ]

    return _makermt, _consel, _catpv
