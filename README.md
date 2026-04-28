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

# Done. Results are in msa_results/
```

That's it. First run prompts for your [NVIDIA NIM API key](https://build.nvidia.com/colabfold/msa-search) (free) and saves it to `.msa-nim.env`. No need to set any env vars.

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
msa-nim run --db PDB70_220313      # add structural templates
```

## FASTA format

One sequence per `>` record. Files must end in `.fasta`, `.fa`, or `.faa`:

```fasta
>my_protein
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVG...

>another_protein
MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQR...
```

## Output

`msa_results/` contains `{name}_{db}.a3m` files — ready for AlphaFold, ColabFold, or OpenFold.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No .fasta files found` | Use `.fasta`, `.fa`, or `.faa` extensions |
| `422: Database not available` | Check spelling: `Uniref30_2302`, `colabfold_envdb_202108`, `PDB70_220313` |
| Interrupted run | Re-run with `--resume` |

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [MMseqs2-GPU](https://github.com/soedinglab/MMseqs2) — GPU-accelerated homology search
- [ColabFold](https://github.com/sokrypton/ColabFold) — MSA + structure prediction pipeline
- [NVIDIA NIM](https://developer.nvidia.com/nim) — Cloud inference microservices