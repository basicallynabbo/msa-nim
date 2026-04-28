"""Fetch protein sequences from PDB IDs via RCSB."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

import requests


RCSB_FASTA_URL = "https://www.rcsb.org/fasta/entry/{pdb_id}"


@dataclass(frozen=True)
class PdbChain:
    pdb_id: str
    chain: str
    description: str
    sequence: str


def fetch_pdb_sequences(pdb_id: str) -> list[PdbChain]:
    """Fetch all protein chains from a PDB entry via RCSB.

    pdb_id can be a plain ID like '7DKF' or with a chain like '7DKF_A'.
    If a chain is specified, only that chain is returned.
    """
    pdb_id = pdb_id.strip().upper()
    if not re.match(r"^[0-9A-Z]{4}$", pdb_id[:4]):
        raise ValueError(f"Invalid PDB ID: {pdb_id[:4]}")

    # Parse optional chain specifier (e.g. 7DKF_A)
    target_chain = None
    if len(pdb_id) > 4:
        suffix = pdb_id[4:]
        if suffix.startswith("_"):
            target_chain = suffix[1:].upper()
        else:
            target_chain = suffix.upper()
        pdb_id_clean = pdb_id[:4]
    else:
        pdb_id_clean = pdb_id

    resp = requests.get(RCSB_FASTA_URL.format(pdb_id=pdb_id_clean), timeout=30)
    if resp.status_code == 404:
        raise ValueError(f"PDB ID not found: {pdb_id_clean}")
    resp.raise_for_status()

    chains = _parse_rcsb_fasta(resp.text, pdb_id_clean)

    if not chains:
        raise ValueError(f"No protein sequences found for PDB ID: {pdb_id_clean}")

    if target_chain:
        matching = [c for c in chains if c.chain == target_chain]
        if not matching:
            available = ", ".join(sorted(set(c.chain for c in chains)))
            raise ValueError(
                f"Chain {target_chain} not found in {pdb_id_clean}. "
                f"Available chains: {available}"
            )
        return matching

    return chains


def _parse_rcsb_fasta(text: str, pdb_id: str) -> list[PdbChain]:
    """Parse RCSB FASTA response into PdbChain objects.

    RCSB headers look like:
    >7DKF_1|Chains A, L|Description|Organism
    The chain labels after 'Chains ' are comma-separated.
    """
    chains = []
    header = None
    seq_parts: list[str] = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None and seq_parts:
                _flush_chain(chains, header, "".join(seq_parts), pdb_id)
            header = line[1:].strip()
            seq_parts = []
        else:
            seq_parts.append(line)

    if header is not None and seq_parts:
        _flush_chain(chains, header, "".join(seq_parts), pdb_id)

    return chains


def _flush_chain(chains: list[PdbChain], header: str, sequence: str, pdb_id: str):
    """Parse a single FASTA record header from RCSB.

    Format: {PDB}_{entity}|Chains X, Y, Z|Description|Organism (taxid)
    """
    parts = header.split("|")
    description = ""
    chain_str = ""
    for part in parts:
        p = part.strip()
        if p.startswith("Chains "):
            chain_str = p[7:].strip()
        elif p.startswith("Chain "):
            chain_str = p[6:].strip()
        else:
            if description:
                description += " | " + p
            else:
                description = p

    if not chain_str:
        chain_str = "A"

    for ch in chain_str.split(","):
        ch = ch.strip()
        if ch:
            chains.append(PdbChain(
                pdb_id=pdb_id,
                chain=ch,
                description=description,
                sequence=sequence,
            ))