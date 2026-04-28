# msa-nim

<p align="center">
  <b>Generate A3M alignments for AlphaFold — no GPUs, no database downloads</b><br><br>
  <a href="https://pypi.org/project/msa-nim/"><img src="https://img.shields.io/pypi/v/msa-nim.svg" alt="PyPI"></a>
  <a href="https://build.nvidia.com/colabfold/msa-search"><img src="https://img.shields.io/badge/NVIDIA-API_Key-blue" alt="NVIDIA API"></a>
</p>

---

## Install

```bash
pip install msa-nim
```

## Get an API key

Grab a free key from [NVIDIA](https://build.nvidia.com/colabfold/msa-search), then:

```bash
export NIM_API_KEY="nvapi-..."
```

Or save it permanently:

```bash
msa-nim init   # creates .msa-nim.env — paste your key there
```

## Usage

### From a FASTA file

```bash
msa-nim run
```

Finds all `.fasta` / `.fa` / `.faa` files in the current directory and outputs `.a3m` files to `msa_results/`.

```fasta
>my_protein
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEK...
```

Multiple `>` records in one file each get their own MSA.

### From a PDB ID

```bash
msa-nim pdb 7DKF              # all chains
msa-nim pdb 7DKF --chain A    # specific chain
msa-nim pdb 7DKF 6HBB 1ABC    # multiple IDs
```

### Common options

```bash
msa-nim run /path/to/fastas       # custom input directory
msa-nim run -o my_output          # custom output directory
msa-nim run --resume               # skip already-completed sequences
msa-nim run --db Uniref30_2302 --db PDB70_220313   # override databases
```

## Databases

Defaults match **ColabFold** (UniRef30 + ColabFold env DB). Add `PDB70_220313` with `--db` for structural templates.

| Database | Name | Purpose |
|----------|------|---------|
| UniRef30 | `Uniref30_2302` | MSA profile (default) |
| ColabFoldDB | `colabfold_envdb_202108` | Metagenomic search (default) |
| PDB70 | `PDB70_220313` | Structural templates (opt-in) |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NIM_API_KEY is required` | Set the env var or run `msa-nim init` |
| `No .fasta files found` | Use `.fasta`, `.fa`, or `.faa` extensions |
| `422: Database not available` | Check spelling/casing (see table above) |
| Interrupted run | Re-run with `--resume` |

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [MMseqs2-GPU](https://github.com/soedinglab/MMseqs2) — GPU-accelerated homology search
- [ColabFold](https://github.com/sokrypton/ColabFold) — MSA + structure prediction pipeline
- [NVIDIA NIM](https://developer.nvidia.com/nim) — Cloud inference microservices