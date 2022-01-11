from utils import *

import regex


def get_raxmlng_run_param_value(line: str, param_identifier: str) -> float:
    raxmlng_run_param_regex = regex.compile(
        rf"/*--{param_identifier}\s+(\d+(?:\.\d+)?(?:[e][-+]?\d+)?)/*"
    )
    value = regex.search(raxmlng_run_param_regex, line).groups()[0]
    return float(value)


def get_raxmlng_seed(raxmlng_file: FilePath) -> int:
    STR = "random seed:"
    return int(get_single_value_from_file(raxmlng_file, STR))


def get_raxmlng_final_llh(raxmlng_file: FilePath) -> float:
    STR = "Final LogLikelihood:"
    return get_single_value_from_file(raxmlng_file, STR)


def get_raxmlng_elapsed_time(log_file: FilePath) -> float:
    content = read_file_contents(log_file)

    for line in content:
        if not "Elapsed time:" in line:
            continue
        # two cases now:
        # either the run was cancelled an rescheduled
        if "restarts" in line:
            # line looks like this: "Elapsed time: 5562.869 seconds (this run) / 91413.668 seconds (total with restarts)"
            _, right = line.split("/")
            value = right.split(" ")[1]
            return float(value)

        # ...or the run ran in one sitting...
        else:
            # line looks like this: "Elapsed time: 63514.086 seconds"
            value = line.split(" ")[2]
            return float(value)

    raise ValueError(
        f"The given input file {log_file} does not contain the elapsed time."
    )


def get_raxmlng_starting_tree_type(log_file: FilePath) -> str:
    content = read_file_contents(log_file)

    for line in content:
        if not line.startswith("start tree"):
            continue
        # start tree(s): random (1)
        return line.split()[2].strip()