from .custom_types import *
import subprocess
from statistics import median


def tukeys_fence(values, k=3):
    values = sorted(values)

    if len(values) >= 2:
        midpoint = int(round(len(values) / 2.0))
        q1 = median(values[:midpoint])
        q3 = median(values[midpoint:])
        iqr = q3 - q1
        lower = q1 - (iqr * k)
        upper = q3 + (iqr * k)
    elif values:
        lower = upper = values[0]
    else:
        lower = upper = 0

    return lower, upper


def run_cmd(cmd: Command) -> None:
    try:
        subprocess.check_output(cmd)
    except Exception as e:
        print(f"Error running command \"{' '.join(cmd)}\"")
        raise e


def read_file_contents(file_path: FilePath) -> List[str]:
    with open(file_path) as f:
        content = f.readlines()

    return [l.strip() for l in content]


def write_trees_to_file(file_path: FilePath, trees: List[NewickString]) -> None:
    with open(file_path, "w") as f:
        f.write("\n".join([t.strip() for t in trees]))


def get_value_from_line(line: str, search_string: str) -> float:
    line = line.strip()
    if search_string in line:
        _, value = line.rsplit(" ", 1)
        return float(value)

    raise ValueError(
        f"The given line '{line}' does not contain the search string '{search_string}'."
    )


def get_single_value_from_file(input_file: FilePath, search_string: str) -> float:
    with open(input_file) as f:
        lines = f.readlines()

    for l in lines:
        if search_string in l:
            return get_value_from_line(l, search_string)

    raise ValueError(
        f"The given input file {input_file} does not contain the search string '{search_string}'."
    )
