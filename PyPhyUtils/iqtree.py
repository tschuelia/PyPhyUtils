from .custom_types import *
from .utils import read_file_contents, run_cmd
from .raxmlng import RAxMLNG
from .raxmlng_parser import get_raxmlng_num_unique_topos

from tempfile import TemporaryDirectory


def get_rfdist_clusters(log_path, all_trees):
    content = read_file_contents(log_path)
    clusters = []

    for line in content:
        line = line.strip()
        if not line.startswith("["):
            continue
        # the line is a string representation of a list of ints
        # like this: [1, 2, 3, 4, ]
        tree_ids = eval(line)
        cluster = set()

        for id in tree_ids:
            cluster.add(all_trees[id])

        clusters.append(cluster)

    if len(clusters) == 0:
        raise RuntimeError(
            "The given RAxML-NG logfile does not contain the clusters, make sure to use the adapted version of RAxML-NG that is available here: https://github.com/tschuelia/raxml-ng"
        )

    return clusters


def filter_tree_topologies(
    unfiltered_trees_file: FilePath,
    raxmlng: RAxMLNG,
) -> Tuple[List[NewickString], List]:
    tree_strings = read_file_contents(unfiltered_trees_file)
    num_trees = len(tree_strings)

    if num_trees > 1:
        with TemporaryDirectory() as tmpdir:
            raxmlng_prefix = tmpdir + "raxmlng_rfdist"
            raxmlng_rfdist_cmd = raxmlng.get_rfdist_cmd(
                trees_file=unfiltered_trees_file, prefix=raxmlng_prefix
            )
            run_cmd(raxmlng_rfdist_cmd)
            raxmlng_log_file = raxmlng_prefix + ".raxml.log"
            num_topos = get_raxmlng_num_unique_topos(raxmlng_log_file)

            if num_topos > 1:
                clusters = get_rfdist_clusters(raxmlng_log_file, tree_strings)

                assert len(clusters) == num_topos
            else:
                clusters = [set(tree_strings)]

    else:
        clusters = [set(tree_strings)]

    # for each cluster: keep only one tree as representative of the cluster
    filtered_trees = [next(iter(cluster)) for cluster in clusters]

    # sanity checks
    assert sum([len(s) for s in clusters]) <= num_trees

    return filtered_trees, clusters


class IQTree:
    def __init__(self, exe_path: Executable):
        self.exe_path = exe_path

    def _base_cmd(
        self, msa_file: FilePath, model: Model, prefix: FilePath, **kwargs
    ) -> Command:
        additional_settings = []
        for key, value in kwargs.items():
            if value is None:
                additional_settings += [f"-{key}"]
            else:
                additional_settings += [f"-{key}", str(value)]

        return [
            self.exe_path,
            "-s",
            msa_file,
            "-m",
            model,
            "-pre",
            prefix,
            *additional_settings,
        ]

    def get_treesearch_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        prefix: str,
        num_pars_trees: int = 10,
        **kwargs,
    ) -> Command:
        if num_pars_trees > 0:
            trees = ["-ninit", num_pars_trees]
        else:
            raise ValueError("Error: num_pars_trees must not be <= 0.")

        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )
        return base_command + trees

    def get_eval_cmd(
        self,
        msa_file: FilePath,
        model: Model,
        treesfile: FilePath,
        prefix: str,
        **kwargs,
    ):
        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )
        return base_command + ["-te", treesfile]

    def get_tree_topology_test_cmd(
        self,
        msa_file: FilePath,
        model: str,
        treesfile: FilePath,
        prefix: str,
        best_tree_file: FilePath = None,
        n_bootstrap_replicates: int = 10_000,
        **kwargs,
    ) -> List:
        best_tree = ["-te", best_tree_file] if best_tree_file else []

        base_command = self._base_cmd(
            msa_file=msa_file, model=model, prefix=prefix, **kwargs
        )

        return base_command + [
            "-z",
            treesfile,
            *best_tree,
            "-n",
            "0",
            "-zb",
            str(n_bootstrap_replicates),
            "-zw",
            "-au",
        ]
