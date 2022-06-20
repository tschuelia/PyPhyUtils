from .custom_types import *
from .regex_constants import *
from .utils import *
import regex
import warnings


def _get_relevant_section(input_file: FilePath) -> str:
    content = read_file_contents(input_file)

    # now let's find the relevant lines
    # the relevant lines are only between the start and end string
    start_str = "USER TREES"
    end_str = "TIME STAMP"
    start = 0
    end = 0

    for i, line in enumerate(content):
        if start_str in line:
            start = i
        if end_str in line:
            end = i

    if start == end:
        raise ValueError(
            f"The section between START_STRING {start_str} and END_STRING {end_str} is empty. Please check the input file {input_file}."
        )

    return content[start:end]


def _get_names_of_performed_tests(table_section: str) -> List[str]:
    """
    Returns the names of the performed iqtree tests as stated in the table header.

    Args:
        table_section: String containing the iqtree test result table.

    Returns:
        A list of strings, each string is the name of a performed statistical test.

    Raises:
        ValueError if the section does not contain a table header matching the defined regex.
    """
    # table header is of form:
    # Tree      logL    deltaL  bp-RELL    p-KH     p-SH    p-WKH    p-WSH       c-ELW       p-AU
    table_header = rf"Tree{blanks}logL{blanks}deltaL{blanks}(?:({stat_test_name})\s*)*"
    table_header_re = regex.compile(table_header)

    test_names = []

    for line in table_section:
        line = line.strip()
        m = regex.match(table_header_re, line)
        if m:
            # m captures 2 groups: the first is Tree, logL, deltaL, the second are the tests
            test_names = m.captures(1)

    if not test_names:
        raise ValueError(
            "No line in the given section matches the regex. Compare the regex and the given section. Maybe the format has changed."
        )
    return test_names


def _get_cleaned_table_entries(
    table_section: str,
) -> List[Tuple]:
    """
    Returns the content of the table in the given section.

    Args:
        table_section: String containing the iqtree test result table.

    Returns:
        A list of tuples, each containing the tree_id, llh, deltaL and a list of test results.

    Raises:
        ValueError if the section does not contain table entries matching the defined regex.
    """
    # a table entry in the .iqtree file looks for example like this:
    # 5 -5708.931281 1.7785e-06  0.0051 -  0.498 +  0.987 +  0.498 +  0.987 +      0.05 +    0.453 +
    table_entry = rf"({tree_id_re}){blanks}({llh_re}){blanks}({deltaL_re}){blanks}(?:({test_result_re})\s*)*"
    table_entry_re = regex.compile(table_entry)

    entries = []
    for line in table_section:
        line = line.strip()
        # match the line against the regex defined above for a table entry
        m = regex.match(table_entry_re, line)
        if m:
            # if a match was found: capture the results in variables
            tree_id, llh, deltaL, result_group = m.groups()
            # to capture all test results individually we have to explicitly unpack it
            test_results = m.captures(4)
            entry = (tree_id, llh, deltaL, test_results)
            entries.append(entry)

    if not entries:
        raise ValueError(
            "No line in the given section matches the regex. Compare the regex and the given section. Maybe the format has changed."
        )

    return entries


def _get_default_entry() -> IqTreeMetrics:
    return {
        "deltaL": 0,
        "plausible": True,
        "tests": {
            "bp-RELL": {"score": 1, "significant": True},
            "p-KH": {"score": 1, "significant": True},
            "p-SH": {"score": 1, "significant": True},
            "p-WKH": {"score": 1, "significant": True},
            "p-WSH": {"score": 1, "significant": True},
            "c-ELW": {"score": 1, "significant": True},
            "p-AU": {"score": 1, "significant": True},
        },
    }


def get_iqtree_results(iqtree_file: FilePath) -> TreeIndexed[IqTreeMetrics]:
    """
    Returns a list of dicts, each dict contains the iqtree test results for the respective tree.

    Args:
        iqtree_file: Path to the iqtree test summary file.

    Returns:
        A list of dicts. Each dict contains the tree_id, llh, deltaL and all results of the performed
            iqtree tests.
    """
    try:
        section = _get_relevant_section(iqtree_file)
        entries = _get_cleaned_table_entries(section)
        test_names = _get_names_of_performed_tests(section)
    except ValueError as e:
        warnings.warn(str(e))
        warnings.warn("Falling back to default case.")
        return [_get_default_entry()]

    results = []

    for tree_id, llh, deltaL, test_results in entries:
        assert len(test_names) == len(test_results)

        data = {}
        data["logL"] = float(llh)
        data["deltaL"] = float(deltaL)
        data["tests"] = {}

        num_passed = 0

        for i, test in enumerate(test_names):
            test_result = test_results[i]
            score, significant = test_result.split(" ")
            score = score.strip()
            significant = significant.strip()
            data["tests"][test] = {}
            data["tests"][test]["score"] = float(score)
            data["tests"][test]["significant"] = True if significant == "+" else False

            if data["tests"][test]["significant"]:
                num_passed += 1

        data["plausible"] = num_passed == len(data["tests"].keys())

        results.append(data)
    return results
