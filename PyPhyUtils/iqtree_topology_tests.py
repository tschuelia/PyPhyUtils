from .custom_types import *
from .iqtree import IQTree
from .iqtree_statstest_parser import get_iqtree_results
from .raxmlng import RAxMLNG
from .raxmlng_parser import get_raxmlng_num_unique_topos
from .utils import run_cmd, read_file_contents, write_trees_to_file

from tempfile import TemporaryDirectory


def get_iqtree_results_for_tree(iqtree_results: TreeIndexed[IqTreeMetrics], tree: NewickString, clusters: List):
    # returns the results for this eval_tree_id as well as the cluster ID
    for i, cluster in enumerate(clusters):
        if tree.strip() in cluster:
            return iqtree_results[i], i

    raise ValueError("This newick_string belongs to no cluster. newick_str: ", tree[:10])


class IQTreeTopologyTest:
    def __init__(self, iqtree_executable: Executable, raxmlng_executable: Executable):
        self.iqtree = IQTree(iqtree_executable)
        self.raxmlng = RAxMLNG(raxmlng_executable)

    def perform_topology_tests(
        self,
        msa_file: FilePath,
        model: Model,
        unfiltered_trees_file: FilePath,
        prefix: str,
        best_tree_file: FilePath = None,
        n_bootstrap_replicates: int = 10_000,
        **kwargs,
    ) -> Tuple[TreeIndexed[IqTreeMetrics], List]:
        filtered_trees, clusters = filter_tree_topologies(
            unfiltered_trees_file=unfiltered_trees_file, raxmlng=self.raxmlng
        )

        with TemporaryDirectory() as tmpdir:
            filtered_trees_file = tmpdir + "filtered.trees"
            write_trees_to_file(file_path=filtered_trees_file, trees=filtered_trees)

            topology_test_cmd = self.iqtree.get_tree_topology_test_cmd(
                msa_file=msa_file,
                model=model,
                treesfile=filtered_trees_file,
                prefix=prefix,
                best_tree_file=best_tree_file,
                n_bootstrap_replicates=n_bootstrap_replicates,
                **kwargs,
            )

            run_cmd(topology_test_cmd)

            iqtree_log_file = prefix + ".iqtree"
            return get_iqtree_results(iqtree_log_file), clusters
