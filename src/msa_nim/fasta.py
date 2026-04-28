"""FASTA parser for monomer protein sequences."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True)
class SequenceRecord:
    header: str
    sequence: str


@dataclass
class FastaEntry:
    """A FASTA file containing one or more monomer sequences."""
    source_file: Path
    records: list[SequenceRecord]

    @property
    def first_id(self) -> str:
        return self.records[0].header.split()[0] if self.records else "unknown"


def parse_fasta_text(text: str) -> list[SequenceRecord]:
    """Parse raw FASTA text into records."""
    records = []
    header = None
    seq_parts: list[str] = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append(SequenceRecord(header, "".join(seq_parts)))
            header = line[1:].strip()
            seq_parts = []
        else:
            seq_parts.append(line)
    if header is not None:
        records.append(SequenceRecord(header, "".join(seq_parts)))

    return records


def parse_fasta_file(path: Path) -> FastaEntry:
    """Parse a single FASTA file into a FastaEntry."""
    with open(path, "r") as f:
        text = f.read()
    records = parse_fasta_text(text)
    if not records:
        raise ValueError(f"No sequences found in {path}")
    return FastaEntry(source_file=path, records=records)


def discover_fasta_files(directory: Path) -> list[Path]:
    """Find all .fasta, .fa, .faa files in a directory (non-recursive)."""
    exts = {".fasta", ".fa", ".faa"}
    files = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in exts
    )
    return files