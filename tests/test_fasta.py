"""Tests for FASTA parser."""

import pytest
from pathlib import Path

from msa_nim.fasta import parse_fasta_text, parse_fasta_file, FastaEntry


def test_parse_single_sequence():
    text = ">seq1\nMKWVTFISLL\nFLFSSAYSRG\n"
    records = parse_fasta_text(text)
    assert len(records) == 1
    assert records[0].header == "seq1"
    assert records[0].sequence == "MKWVTFISLLFLFSSAYSRG"


def test_parse_multiple_sequences():
    text = ">A\nMKWVTFIS\n>B\nSGSMKTAIS\n"
    records = parse_fasta_text(text)
    assert len(records) == 2
    assert records[0].header == "A"
    assert records[1].sequence == "SGSMKTAIS"


def test_fasta_entry_first_id():
    entry = FastaEntry(source_file=Path("test.fa"), records=parse_fasta_text(">seq1\nMKW\n"))
    assert entry.first_id == "seq1"


def test_parse_empty_file(tmp_path):
    f = tmp_path / "empty.fa"
    f.write_text("")
    with pytest.raises(ValueError):
        parse_fasta_file(f)