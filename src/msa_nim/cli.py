"""Click-based CLI for msa-nim."""

import click
from pathlib import Path

from msa_nim import __version__
from msa_nim.config import resolve_api_key
from msa_nim.client import NimClient, CLOUD_DATABASES
from msa_nim.fasta import discover_fasta_files, parse_fasta_file, FastaEntry, SequenceRecord
from msa_nim.batch import BatchRunner
from msa_nim.pdb import fetch_pdb_sequences


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="msa-nim")
@click.pass_context
def cli(ctx):
    """msa-nim: Generate A3M MSA alignments via NVIDIA NIM MSA-Search."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path), default=Path("."))
@click.option("-o", "--outdir", type=click.Path(path_type=Path), default=Path("msa_results"), help="Output directory (default: msa_results).")
@click.option("--db", "databases", multiple=True, default=None, help="Databases to search (default: Uniref30_2302 colabfold_envdb_202108).")
@click.option("--resume", is_flag=True, default=False, help="Skip already-completed sequences.")
@click.option("-j", "--jobs", type=int, default=1, help="Max parallel API calls (default: 1).")
@click.option("--key", "api_key", default=None, envvar="NIM_API_KEY", help="NVIDIA NIM API key.")
@click.option("--timeout", type=int, default=900, help="API timeout in seconds (default: 900).")
def run(
    directory: Path,
    outdir: Path,
    databases,
    resume: bool,
    jobs: int,
    api_key: str | None,
    timeout: int,
):
    """Run MSA search on all FASTA files in DIRECTORY.

    Every sequence in every FASTA file is submitted as a
    separate monomer MSA job to the NVIDIA cloud NIM.
    """
    if api_key is None:
        try:
            api_key = resolve_api_key()
        except RuntimeError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise click.Abort()

    db_list = None
    if databases:
        db_list = list(databases)
    else:
        db_list = [CLOUD_DATABASES["uniref30"], CLOUD_DATABASES["colabfold_envdb"]]

    fasta_files = discover_fasta_files(directory)
    if not fasta_files:
        click.echo(f"No .fasta / .fa / .faa files found in {directory.resolve()}")
        raise click.Abort()

    click.echo(f"Found {len(fasta_files)} FASTA file(s) in {directory.resolve()}")
    click.echo(f"Databases: {', '.join(db_list)}")
    click.echo(f"Output: {outdir.resolve()}")
    click.echo(f"Parallel jobs: {jobs}")
    if resume:
        click.echo("Resume mode: ON")
    click.echo("")

    entries = []
    for fp in fasta_files:
        try:
            entry = parse_fasta_file(fp)
            entries.append(entry)
            click.echo(f"  {fp.name}: {len(entry.records)} sequence(s)")
        except ValueError as exc:
            click.echo(f"  [SKIP] {fp.name}: {exc}", err=True)

    if not entries:
        click.echo("No valid sequences to process.")
        raise click.Abort()

    client = NimClient(api_key=api_key, timeout=timeout)
    runner = BatchRunner(
        client=client,
        out_dir=outdir,
        databases=db_list,
        resume=resume,
        max_workers=jobs,
    )
    runner.run(entries)


@cli.command()
@click.argument("pdb_ids", nargs=-1, required=True)
@click.option("-o", "--outdir", type=click.Path(path_type=Path), default=Path("msa_results"), help="Output directory (default: msa_results).")
@click.option("--db", "databases", multiple=True, default=None, help="Databases to search (default: Uniref30_2302 colabfold_envdb_202108).")
@click.option("--chain", "chains", multiple=True, default=None, help="Specific chain(s) to process (e.g. --chain A --chain B). Process all chains if omitted.")
@click.option("--resume", is_flag=True, default=False, help="Skip already-completed sequences.")
@click.option("-j", "--jobs", type=int, default=1, help="Max parallel API calls (default: 1).")
@click.option("--key", "api_key", default=None, envvar="NIM_API_KEY", help="NVIDIA NIM API key.")
@click.option("--timeout", type=int, default=900, help="API timeout in seconds (default: 900).")
def pdb(
    pdb_ids,
    outdir: Path,
    databases,
    chains,
    resume: bool,
    jobs: int,
    api_key: str | None,
    timeout: int,
):
    """Fetch sequences from PDB and run MSA search.

    Provide one or more PDB IDs (e.g. 7DKF, 6HBB). Optionally
    specify chains with --chain A to only process specific chains.

    Examples:

        msa-nim pdb 7DKF

        msa-nim pdb 7DKF --chain A --chain B

        msa-nim pdb 7DKF 6HBB 1ABC
    """
    if api_key is None:
        try:
            api_key = resolve_api_key()
        except RuntimeError as exc:
            click.echo(f"Error: {exc}", err=True)
            raise click.Abort()

    db_list = None
    if databases:
        db_list = list(databases)
    else:
        db_list = [CLOUD_DATABASES["uniref30"], CLOUD_DATABASES["colabfold_envdb"]]

    all_records = []
    for pdb_id in pdb_ids:
        pdb_id = pdb_id.strip().upper()
        try:
            fetched = fetch_pdb_sequences(pdb_id)
            # If user specified chains, filter
            if chains:
                chain_set = set(c.upper() for c in chains)
                fetched = [c for c in fetched if c.chain in chain_set]
                if not fetched:
                    available = ", ".join(sorted(set(
                        fetch_pdb_sequences(pdb_id)[0].chain
                        for _ in [1]
                        for c in [fetch_pdb_sequences(pdb_id)]
                        for c in c
                    ))) if fetch_pdb_sequences(pdb_id) else "none"
                    click.echo(f"  [SKIP] {pdb_id}: chains {', '.join(chain_set)} not found", err=True)
                    continue
            for chain in fetched:
                click.echo(f"  {pdb_id} chain {chain.chain}: {chain.description} ({len(chain.sequence)} aa)")
                all_records.append(SequenceRecord(
                    header=f"{pdb_id}_{chain.chain}|{chain.description}",
                    sequence=chain.sequence,
                ))
        except ValueError as exc:
            click.echo(f"  [SKIP] {pdb_id}: {exc}", err=True)

    if not all_records:
        click.echo("No valid PDB sequences to process.")
        raise click.Abort()

    click.echo(f"\nFetched {len(all_records)} chain(s) from {len(pdb_ids)} PDB entry/entries")
    click.echo(f"Databases: {', '.join(db_list)}")
    click.echo(f"Output: {outdir.resolve()}")
    click.echo("")

    # Build a synthetic FastaEntry from PDB records
    entry = FastaEntry(source_file=Path("pdb_input"), records=all_records)

    client = NimClient(api_key=api_key, timeout=timeout)
    runner = BatchRunner(
        client=client,
        out_dir=outdir,
        databases=db_list,
        resume=resume,
        max_workers=jobs,
    )
    runner.run([entry])


@cli.command()
def init():
    """Create a .msa-nim.env template with your NVIDIA NIM API key."""
    env_path = Path(".msa-nim.env")
    if env_path.exists():
        click.echo(".msa-nim.env already exists.")
        return
    env_path.write_text("# Get your free API key at https://build.nvidia.com/colabfold/msa-search\nNIM_API_KEY=nvapi-...\n")
    click.echo("Created .msa-nim.env — edit it and add your NVIDIA NIM API key.")


def main():
    cli()


if __name__ == "__main__":
    main()