from .raxmlng import _get_raxmlng_base_command

from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from Bio.Phylo.TreeConstruction import DistanceCalculator
from collections import Counter
from itertools import product
import math
import numpy as np
from pathlib import Path
import random
import subprocess
from tempfile import TemporaryDirectory, NamedTemporaryFile


STATE_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,/:;<=>@[\\]^_{|}~"
GAP_CHARS = "-?."
DNA_CHARS = "ACTG"


def _convert_dna_msa_to_biopython_format(msa_file, tmpfile):
    """
    The unknonwn char in DNA MSA files for Biopython to work
    has to be "N" instead of "X" -> replace all occurences
    All "?" are gaps -> convert to "-"
    Also all "U" need to be "T"
    """
    with open(msa_file) as f:
        repl = f.read().replace("X", "N")
        repl = repl.replace("?", "-")
        repl = repl.replace("U", "T")
        repl = repl.upper()

    tmpfile.write(repl)


def _convert_aa_msa_to_biopython_format(msa_file, tmpfile):
    """
    The unknonwn char in AA MSA files for Biopython to work
    All "?" are gaps -> convert to "-"
    """
    with open(msa_file) as f:
        repl = f.read().replace("?", "-")
        repl = repl.upper()

    tmpfile.write(repl)


def _get_msa_file_format(msa_file):
    """
    For now: only support .fasta and .phy files
    TODO: include more file types
    """
    file_ending = Path(msa_file).suffix
    if file_ending == ".phy":
        return "phylip-relaxed"
    elif file_ending == ".fasta":
        return "fasta"
    raise ValueError(f"This file type is currently not supported: {file_ending}")


def read_alignment(msa_file, data_type="DNA"):
    with NamedTemporaryFile(mode="w") as tmpfile:
        if data_type == "DNA":
            _convert_dna_msa_to_biopython_format(msa_file, tmpfile)
        else:
            _convert_aa_msa_to_biopython_format(msa_file, tmpfile)

        tmpfile.flush()
        return AlignIO.read(tmpfile.name, format=_get_msa_file_format(msa_file))


def get_number_of_taxa(msa):
    return len(msa)


def get_number_of_sites(msa):
    return msa.get_alignment_length()


def remove_gaps_from_sequence(seq):
    for char in GAP_CHARS:
        seq = seq.replace(char, "")
    return seq


def get_column_entropy(column):
    # column_entropy = - sum(for every nucleotide x) {count(x)*log2(Prob(nuc x in col i))}
    column = remove_gaps_from_sequence(column).upper()
    entropy = 0

    for char in STATE_CHARS:
        count = str.count(column, char)
        if count == 0:
            entropy_x = 0
        else:
            prob = count / len(column)
            entropy_x = prob * math.log2(prob)

        entropy += entropy_x

    entropy = -entropy

    assert entropy >= 0, f"Entropy negative, check computation. Entropy is {entropy}"

    return entropy


def get_msa_column_entropies(msa):
    return [get_column_entropy(msa[:, i]) for i in range(msa.get_alignment_length())]


def get_msa_avg_entropy(msa):
    return np.mean(get_msa_column_entropies(msa))


def bollback_multinomial(msa):
    """
    Compute the bollback multinomial statistic on the msa file
    According to Bollback, JP: Bayesian model adequacy and choice in phylogenetics (2002)
    """
    msa_length = msa.get_alignment_length()

    sites = []
    for i in range(msa_length):
        sites.append(msa[:, i])

    site_counts = Counter(sites)
    mult = 0
    for i in site_counts:
        N_i = site_counts[i]
        mult += N_i * math.log(N_i)

    mult = mult - msa_length * math.log(msa_length)
    return mult


def _get_distance_matrix(msa, num_samples, data_type):
    """
    For large MSAs (i.e. more than num_samples taxa), computing the distance matrix
    is computationally very expensive.
    So for large MSAs, we rather compute the distance matrix on a subsample of at most num_samples sequences
    """
    if get_number_of_taxa(msa) > num_samples:
        sample_population = range(get_number_of_taxa(msa))
        selection = sorted(random.sample(sample_population, num_samples))
        msa = MultipleSeqAlignment([msa[el] for el in selection])

    model = "blastn" if data_type == "DNA" else "blosum62"
    calculator = DistanceCalculator(model=model)
    dm = calculator.get_distance(msa)
    return dm


def treelikeness_score(msa, data_type):
    """
    Compute the treelikeness score according to
    δ Plots: A Tool for Analyzing Phylogenetic Distance Data, Holland, Huber, Dress and Moulton (2002)
    https://doi.org/10.1093/oxfordjournals.molbev.a004030
    """
    num_samples = min(get_number_of_taxa(msa), 100)
    dm = _get_distance_matrix(msa, num_samples, data_type)

    options = list(range(len(dm)))

    frac = num_samples // 4
    X = options[:frac]
    Y = options[frac:2 * frac]
    U = options[2 * frac:3 * frac]
    V = options[3 * frac:]

    res = product(X, Y, U, V)
    deltas = []
    for x, y, u, v in res:
        dxv = np.abs(dm[x, v])
        dyu = np.abs(dm[y, u])
        dxu = np.abs(dm[x, u])
        dyv = np.abs(dm[y, v])
        dxy = np.abs(dm[x, y])
        duv = np.abs(dm[u, v])

        # assert dm[x, v] >= 0, (x, v, dm[x, v])
        # assert dm[y, u] >= 0, (y, u, dm[y, u])
        # assert dm[x, u] >= 0, (x, u, dm[x, u])
        # assert dm[y, v] >= 0, (y, v, dm[y, v])
        # assert dm[x, y] >= 0, (x, y, dm[x, y])
        # assert dm[u, v] >= 0, (u, v, dm[u, v])

        dxv_yu = dxv + dyu
        dxu_yv = dxu + dyv
        dxy_uv = dxy + duv

        vals = sorted([dxv_yu, dxu_yv, dxy_uv])
        smallest = vals[0]
        intermediate = vals[1]
        largest = vals[2]

        numerator = largest - intermediate
        denominator = largest - smallest

        if denominator == 0:
            delta = 0
        else:
            delta = numerator / denominator
        assert delta >= 0
        assert delta <= 1
        deltas.append(delta)

    return np.mean(deltas)


def _run_raxmlng_alignment_parse(msa_file, raxmlng_executable, model, tmpdir):
    cmd = _get_raxmlng_base_command(
        raxmlng_executable=raxmlng_executable,
        msa=msa_file,
        model=model,
        prefix=tmpdir,
        threads=1
    )

    subprocess.check_output(cmd)


def get_number_of_patterns(msa_file, raxmlng_executable="raxml-ng", model="GTR+G"):
    """
    The easiest way to get the number of patterns for the msa_file is to run
    raxml-ng with the --parse option and parse the results.
    """
    with TemporaryDirectory() as tmpdir:
        _run_raxmlng_alignment_parse(msa_file, raxmlng_executable, model, tmpdir)

        log_file = tmpdir + ".raxml.log"

        for line in open(log_file).readlines():
            line = line.strip()
            if not line.startswith("Alignment sites"):
                continue
            # Alignment sites / patterns: 1940 / 933
            _, numbers = line.split(":")
            sites, patterns = numbers.split("/")
            return int(patterns)


def get_percentage_of_invariant_sites(msa_file, raxmlng_executable="raxml-ng", model="GTR+G"):
    """
    The easiest way to get the number of patterns for the msa_file is to run
    raxml-ng with the --parse option and parse the results.
    """
    with TemporaryDirectory() as tmpdir:
        _run_raxmlng_alignment_parse(msa_file, raxmlng_executable, model, tmpdir)

        log_file = tmpdir + ".raxml.log"

        for line in open(log_file).readlines():
            line = line.strip()
            if not line.startswith("Invariant sites"):
                continue
            # Invariant sites: 80.77 %
            _, number = line.split(":")
            percentage, _ = number.strip().split(" ")
            return float(percentage) / 100.0


def get_percentage_of_gaps(msa_file, raxmlng_executable="raxml-ng", model="GTR+G"):
    """
    The easiest way to get the number of patterns for the msa_file is to run
    raxml-ng with the --parse option and parse the results.
    """
    with TemporaryDirectory() as tmpdir:
        _run_raxmlng_alignment_parse(msa_file, raxmlng_executable, model, tmpdir)

        log_file = tmpdir + ".raxml.log"

        for line in open(log_file).readlines():
            line = line.strip()
            if not line.startswith("Gaps"):
                continue
            # Gaps: 20.05 %
            _, number = line.split(":")
            percentage, _ = number.strip().split(" ")
            return float(percentage) / 100.0


def get_character_frequencies(msa):
    counts = {}

    for char in STATE_CHARS:
        counts[char] = 0

    for sequence in msa:
        sequence = sequence.seq

        for char in STATE_CHARS:
            counts[char] += sequence.count(char)

    return counts

