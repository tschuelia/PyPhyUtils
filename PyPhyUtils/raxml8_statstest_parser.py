from .utils import *

import regex

sh_regex = r"Tree:\s+\d+ Likelihood:\s+([-+]?\d+(?:\.\d+)?(?:[e][-+]?\d+)?)\s+D\(LH\):\s+([-+]?\d+(?:\.\d+)?(?:[e][-+]?\d+)?)\s+SD:\s+([-+]?\d+(?:\.\d+)?(?:[e][-+]?\d+)?)\s+Significantly\s+Worse:\s+([a-zA-Z]+)\s+\(5%\),\s+([a-zA-Z]+)\s+\(2%\),\s+([a-zA-Z]+)\.*"
sh_regex = regex.compile(sh_regex)


def get_raxml_shtest_results(raxml_file: FilePath) -> TreeIndexed[RaxMetrics]:
    content = read_file_contents(raxml_file)
    results = []
    for line in content:
        if line.startswith("Tree"):
            m = regex.match(sh_regex, line)
            if m:
                llh, delta_llh, sd = (float(el) for el in m.groups()[:3])
                sign_five, sign_two, sign_one = (
                    True if el.lower() == "no" else False for el in m.groups()[3:]
                )

                results.append(
                    {
                        "llh": llh,
                        "deltaL": delta_llh,
                        "sd": sd,
                        "significant": {
                            "5%": sign_five,
                            "2%": sign_two,
                            "1%": sign_one,
                        },
                    }
                )
    return results


def get_raxml_elwtest_results(raxml_file: FilePath) -> TreeIndexed[RaxMetrics]:
    content = read_file_contents(raxml_file)
    likelihoods = []
    for line in content:
        if line.startswith("Original"):
            _, llh = line.rsplit(" ", 1)
            llh = float(llh.strip())
            likelihoods.append(llh)

    test_result_section = []
    for i, line in enumerate(content):
        if line.startswith("Tree"):
            test_result_section = content[i+1:i+1 + len(likelihoods)]

    posterior_probs = [-1.] * len(likelihoods)
    cumulative_probs = [-1.] * len(likelihoods)
    for line in test_result_section:
        tree_id, posterior_prob, cumulative_prob = line.split()

        posterior_probs[int(tree_id)] = float(posterior_prob)
        cumulative_probs[int(tree_id)] = float(cumulative_prob)

    results = []
    for llh, post_prob, cum_prob in zip(likelihoods, posterior_probs, cumulative_probs):
        results.append({
            "llh": llh,
            "c-ELW": post_prob,
            "cumulative_c-elw": cum_prob
        })
    return results

