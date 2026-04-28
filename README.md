# msa-nim

<p align="center">
  <b>A3M alignments for AlphaFold — no GPUs, no database downloads</b><br><br>
  <a href="https://pypi.org/project/msa-nim/"><img src="https://img.shields.io/pypi/v/msa-nim.svg" alt="PyPI"></a>
  <a href="https://build.nvidia.com/colabfold/msa-search"><img src="https://img.shields.io/badge/NVIDIA-API_Key-blue" alt="NVIDIA API"></a>
</p>

---

## Install

```bash
pip install msa-nim
```

## Quick start

```bash
# 1. Install
pip install msa-nim

# 2. Put your .fasta files in a folder
cd my_proteins/

# 3. Run — it'll ask for your API key on first use and save it
msa-nim run

# Done. A3M files are in msa_results/
```

First run prompts for your [NVIDIA NIM API key](https://build.nvidia.com/colabfold/msa-search) (free) and saves it to `.msa-nim.env` for future runs. Same MSA engine as ColabFold — just without the 1.4 TB database download.

## From a PDB ID

No FASTA file needed:

```bash
msa-nim pdb 7DKF              # all chains
msa-nim pdb 7DKF --chain A    # specific chain
msa-nim pdb 7DKF 6HBB 1ABC    # multiple IDs
```

## Options

```bash
msa-nim run /path/to/fastas       # custom input directory
msa-nim run -o my_output          # custom output directory
msa-nim run --resume               # retry crashed/interrupted run
msa-nim run -j 2                   # parallel jobs (paid API tier only)
msa-nim run --db PDB70_220313      # add structural templates
```

> **Note:** The free NVIDIA tier rate-limits to ~1 request at a time. Use `-j 1` (default) on free tier; `-j 2+` only helps on paid plans.

## FASTA format

One sequence per `>` record. Files must end in `.fasta`, `.fa`, or `.faa`:

```fasta
>my_protein
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVG...

>another_protein
MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQR...
```

## Output

`msa_results/` contains one `{name}.a3m` file per query — the combined UniRef + environmental MSA, ready for AlphaFold, ColabFold, or OpenFold.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No .fasta files found` | Use `.fasta`, `.fa`, or `.faa` extensions |
| `422: Database not available` | Check spelling: `Uniref30_2302`, `colabfold_envdb_202108`, `PDB70_220313` |
| Interrupted run | Re-run with `--resume` |
| Rate limiting (429) | Free tier is ~1 req/sec; use default `-j 1` |

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [MMseqs2-GPU](https://github.com/soedinglab/MMseqs2) — GPU-accelerated homology search
- [ColabFold](https://github.com/sokrypton/ColabFold) — MSA + structure prediction pipeline
- [NVIDIA NIM](https://developer.nvidia.com/nim) — Cloud inference microservices