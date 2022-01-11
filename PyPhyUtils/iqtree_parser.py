from .utils import *
import regex


def get_iqtree_run_param_value(line: str, param_identifier: str) -> float:
    iqtree_run_param_regex = regex.compile(
        rf"/*-{param_identifier}\s+(\d+(?:\.\d+)?(?:[e][-+]?\d+)?)/*"
    )
    value = regex.search(iqtree_run_param_regex, line).groups()[0]
    return float(value)


def get_iqtree_llh(iqtree_file: FilePath) -> float:
    STR = "BEST SCORE FOUND :"
    return get_single_value_from_file(iqtree_file, STR)


def get_iqtree_cpu_time(log_file: FilePath) -> float:
    content = read_file_contents(log_file)

    for line in content:
        if not "Total CPU time used:" in line:
            continue

        # correct line looks like this: "Total CPU time used: 0.530 sec (0h:0m:0s)"
        value = line.split(" ")[4]
        return float(value)

    raise ValueError(
        f"The given input file {log_file} does not contain the cpu time."
    )

