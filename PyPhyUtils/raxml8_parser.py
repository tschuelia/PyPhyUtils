from utils import *


def get_raxml_execution_time(raxml_file: FilePath) -> float:
    content = read_file_contents(raxml_file)
    for line in content:
        if line.startswith("Total execution"):
            _, time = line.rsplit(" ", 1)
            return float(time)
