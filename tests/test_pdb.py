"""Tests for PDB sequence fetcher."""

from msa_nim.pdb import _parse_rcsb_fasta


def test_parse_single_chain():
    text = ">6HBB_1|Chains A, B|Hemoglobin subunit alpha|Homo sapiens\nMKWVTFISLL\n"
    chains = _parse_rcsb_fasta(text, "6HBB")
    assert len(chains) == 2
    assert chains[0].chain == "A"
    assert chains[1].chain == "B"
    assert chains[0].sequence == "MKWVTFISLL"
    assert "Hemoglobin" in chains[0].description


def test_parse_single_chain_label():
    text = ">1ABC_1|Chain A|Some protein|E. coli\nACDEFGHIK\n"
    chains = _parse_rcsb_fasta(text, "1ABC")
    assert len(chains) == 1
    assert chains[0].chain == "A"
    assert chains[0].sequence == "ACDEFGHIK"


def test_parse_multiline_sequence():
    text = ">1ABC_1|Chain A|Test protein\nMKWVTF\nISLLFL\n"
    chains = _parse_rcsb_fasta(text, "1ABC")
    assert len(chains) == 1
    assert chains[0].sequence == "MKWVTFISLLFL"