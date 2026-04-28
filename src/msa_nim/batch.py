"""Batch orchestration engine."""

from __future__ import annotations

import json
from pathlib import Path

from art import text2art

from msa_nim.client import NimClient, DEFAULT_MSA_DATABASES
from msa_nim.fasta import FastaEntry
from msa_nim.progress import ProgressTracker


BANNER_FONT = "small"

POKEMON_FRAMES = [
    "  ∧,_,∧   ",
    "  ( ◕ ◕ ) ",
    "  ( ◕‿◕ ) ",
    "  (◕▽◕)   ",
    "  /^^^\\    ",
    "  ( > < )  ",
    "  ( -_-)zz ",
    "  ⚡ ⊛ ⚡  ",
    "  Zzz...   ",
    "  \\^^/     ",
]


PIKACHU_BANNER = r"""     /\_/\
    ( o.o )
     > ^ <"""


def _sanitize_id(name: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name)


def _write_a3m(out_dir: Path, base_name: str, db_name: str, a3m_text: str) -> Path:
    safe_db = _sanitize_id(db_name)
    path = out_dir / f"{base_name}_{safe_db}.a3m"
    with open(path, "w") as f:
        f.write(a3m_text)
    return path


def _write_raw_json(out_dir: Path, base_name: str, data: dict) -> Path:
    path = out_dir / f"{base_name}_raw.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def _count_sequences(a3m_text: str) -> int:
    return sum(1 for line in a3m_text.splitlines() if line.startswith(">"))


def _print_banner(databases: list[str], out_dir: Path, total_jobs: int):
    banner = text2art("msa-nim", font=BANNER_FONT)
    print(PIKACHU_BANNER)
    print(banner)
    print("    Powered by NVIDIA NIM + MMseqs2-GPU")
    print()
    print(f"    Jobs:       {total_jobs}")
    print(f"    Databases:  {', '.join(databases)}")
    print(f"    Output:     {out_dir.resolve()}")
    print()


class BatchRunner:
    def __init__(
        self,
        client: NimClient,
        out_dir: Path,
        databases: list[str] | None = None,
        resume: bool = False,
        max_workers: int = 1,
    ):
        self.client = client
        self.out_dir = out_dir
        self.databases = databases or DEFAULT_MSA_DATABASES
        self.resume = resume
        self.max_workers = max_workers
        self.tracker = ProgressTracker(out_dir)

    def run(self, entries: list[FastaEntry]):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        jobs = self._build_jobs(entries)

        if not jobs:
            print("No jobs to run.")
            return

        total = len(jobs)

        if self.resume:
            already_done = total - len(jobs)
            jobs = [j for j in jobs if not self.tracker.is_done(j["key"])]
            print(f"Resuming: {already_done} already done, {len(jobs)} remaining.")
            if not jobs:
                self._print_summary(total)
                return

        _print_banner(self.databases, self.out_dir, len(jobs))

        failed_keys = []

        try:
            for i, job in enumerate(jobs):
                frame = POKEMON_FRAMES[i % len(POKEMON_FRAMES)]
                pct = int((i / len(jobs)) * 100)
                bar_filled = int(30 * (i / len(jobs)))
                bar_empty = 30 - bar_filled
                bar = "\u2588" * bar_filled + "\u2591" * bar_empty

                print(
                    f"\r{frame} [{bar}] {pct:3d}% ({i}/{len(jobs)})",
                    end="", flush=True,
                )
                try:
                    result = self.client.search_monomer(
                        job["sequence"], databases=self.databases
                    )
                    self._save_result(job["base_name"], result)
                    self.tracker.mark_done(job["key"])
                except Exception as exc:
                    self.tracker.mark_failed(job["key"])
                    failed_keys.append((job["key"], str(exc)))

            bar = "\u2588" * 30
            frame = POKEMON_FRAMES[-1]
            print(
                f"\r{frame} [{bar}] 100% ({len(jobs)}/{len(jobs)})"
            )
        except KeyboardInterrupt:
            print("\n\n  Interrupted! Progress saved. Re-run with --resume to continue.")
            self._print_summary(total)
            return

        self._print_summary(total, failed=failed_keys)

    def _print_summary(self, total: int, failed: list[tuple[str, str]] | None = None):
        done = len(self.tracker.state.completed)
        fail_count = len(self.tracker.state.failed)
        remaining = total - done - fail_count

        SAD_PIKACHU = r"""     /\_/\
    ( >_< )
     >   <"""

        HAPPY_PIKACHU = r"""     /\_/\
    ( ^.^ )
     > ^ <"""

        print()
        if fail_count > 0:
            print(SAD_PIKACHU)
            print()
            print(f"  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510")
            print(f"  \u2502  {done}/{total} done  \u00b7  {fail_count} failed", end="")
            if remaining > 0:
                print(f"  \u00b7  {remaining} pending", end="")
            print()
            print(f"  \u2502")
            print(f"  \u2502  Results: {self.out_dir.resolve()}")
            for key, err in (failed or []):
                short = key if len(key) <= 45 else "..." + key[-42:]
                print(f"  \u2502  \u2717 {short}")
            print(f"  \u2502")
            print(f"  \u2502  \u2139 Re-run with --resume to retry failures")
            print(f"  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518")
        else:
            print(HAPPY_PIKACHU)
            print()
            print(f"  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510")
            print(f"  \u2502  {done}/{total} done")
            print(f"  \u2502  Results: {self.out_dir.resolve()}")
            if remaining > 0:
                print(f"  \u2502  {remaining} not started")
            print(f"  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518")

    def _build_jobs(self, entries: list[FastaEntry]) -> list[dict]:
        jobs = []
        for entry in entries:
            for rec in entry.records:
                seq_id = rec.header.split()[0]
                key = f"{entry.source_file.name}:{seq_id}"
                base = _sanitize_id(seq_id)
                jobs.append({
                    "key": key,
                    "sequence": rec.sequence,
                    "base_name": base,
                    "source": entry.source_file.name,
                })
        return jobs

    def _save_result(self, base: str, result):
        for db_name, a3m_text in result.alignments.items():
            path = _write_a3m(self.out_dir, base, db_name, a3m_text)
            n_seqs = _count_sequences(a3m_text)
            print(f"\n    \u2713 {path.name} ({n_seqs} seqs)")

        if result.raw:
            _write_raw_json(self.out_dir, base, result.raw)