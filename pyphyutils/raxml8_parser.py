from .utils import *


def get_raxml_execution_time(raxml_file: FilePath) -> float:
    for line in read_file_contents(raxml_file):
        if line.startswith("Total execution"):
            _, time = line.rsplit(" ", 1)
            return float(time)
