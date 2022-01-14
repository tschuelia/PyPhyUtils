from .utils import *
from .regex_constants import *

import regex


def get_consel_results(consel_file: FilePath) -> TreeIndexed[ConselMetrics]:
    id_regex = rf"{blanks}({tree_id_re})"
    res_regex = rf"{blanks}({float_re})"
    consel_regex = rf"#{id_regex}{id_regex}{res_regex}{res_regex}{res_regex}\s*\|\s*{res_regex}{res_regex}{res_regex}{res_regex}{res_regex}{res_regex}"
    test_names = [""]

    unorderd_results = []

    for line in read_file_contents(consel_file):
        m = regex.match(consel_regex, line)
        if m:
            (
                rank,
                item,
                deltaL,
                pAU,
                bpMult,
                bpRELL,
                bayesPP,
                pKH,
                pSH,
                pWKH,
                pWSH,
            ) = m.groups()
            unorderd_results.append(
                (
                    item,
                    (
                        rank,
                        item,
                        deltaL,
                        pAU,
                        bpMult,
                        bpRELL,
                        bayesPP,
                        pKH,
                        pSH,
                        pWKH,
                        pWSH,
                    ),
                )
            )

    ordered_results = sorted(unorderd_results, key=lambda x: x[0])
    results = []

    for _, res in ordered_results:
        rank, treeid, deltaL, pAU, bpMult, bpRELL, bayesPP, pKH, pSH, pWKH, pWSH = res
        data = {
            "deltaL": float(deltaL),
            "rank": int(rank),
            "tests": {
                "bp-RELL": bpRELL,
                "p-KH": pKH,
                "p-SH": pSH,
                "p-WKH": pWKH,
                "p-WSH": pWSH,
                "p-AU": pAU,
                "bp-Mult": bpMult,
                "bayesPosteriorProb": bayesPP,
            },
        }
        results.append(data)

    return results

