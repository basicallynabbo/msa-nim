# msa-nim

<p align="center">
  <img src="https://developer-blogs.nvidia.com/wp-content/uploads/2025/03/protein-sequence-alignment.png" alt="Protein Sequence Alignment" width="600"/>
</p>

<p align="center">
  <b>Zero-hassle A3M generation with NVIDIA NIM + MMseqs2-GPU</b><br>
  <a href="https://build.nvidia.com/colabfold/msa-search">Get API Key</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#usage">Usage</a> &bull;
  <a href="#database-info">Databases</a>
</p>

---

## What is this?

`msa-nim` is a lightweight, open-source CLI that generates **A3M multiple sequence alignments** for protein sequences using NVIDIA's cloud-hosted **MSA-Search NIM** (powered by GPU-accelerated MMseqs2).

- **No GPUs required**
- **No 1.4 TB database downloads**
- **Just your NVIDIA API key** and a folder of FASTA files

Drop your `.fasta` files into a folder, run one command, and get `.a3m` files ready for AlphaFold, ColabFold, or OpenFold.

---

## Prerequisites

- Python **3.9+**
- A **free NVIDIA NIM API key** &mdash; [get it here](https://build.nvidia.com/colabfold/msa-search)

---

## Installation

```bash
# Clone
git clone https://github.com/nabbo/msa-nim.git
cd msa-nim

# Install
pip install -e .

# Verify
msa-nim --version
```

---

## Quick Start

### 1. Set your API key

```bash
export NIM_API_KEY="nvapi-..."
```

Or create a config file:

```bash
msa-nim init
# edit .msa-nim.env and paste your key
```

> Get your free API key at [build.nvidia.com/colabfold/msa-search](https://build.nvidia.com/colabfold/msa-search).

### 2. Prepare your FASTA files

Put protein sequences in `.fasta`, `.fa`, or `.faa` files. Each `>` record becomes one MSA job.

**Single sequence:**
```fasta
>my_protein
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

**Multiple sequences in one file (each gets its own MSA):**
```fasta
>protein_A
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVG...

>protein_B
SGSMKTAISLPDETFDRVSRRASELGMSRSEFFTKAAQR...

>protein_C
MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRF...
```

> **Note:** The NVIDIA cloud NIM only supports protein sequences (20 standard amino acids + `X`). DNA and RNA are not supported. Each sequence is processed independently as a monomer MSA search.

### 3. Run

```bash
cd my_proteins/
msa-nim run
```

Done. A `msa_results/` folder appears with your `.a3m` files.

### Or: run directly from a PDB ID

No FASTA file needed — just give a PDB ID and the tool fetches the sequence automatically:

```bash
# All chains of a PDB entry
msa-nim pdb 7DKF

# Specific chain only
msa-nim pdb 7DKF --chain A

# Multiple PDB IDs at once
msa-nim pdb 7DKF 6HBB 1ABC

# Specific chains from specific entries
msa-nim pdb 7DKF --chain A --chain B
```

---

## Usage

```bash
# Run on FASTA files in the current directory
msa-nim run

# Target a specific folder
msa-nim run /path/to/my_fastas

# Custom output directory
msa-nim run -o my_alignments

# Resume a crashed run (skips already-completed sequences)
msa-nim run --resume

# Override databases
msa-nim run --db Uniref30_2302 --db PDB70_220313

# === PDB mode ===

# All chains from a PDB entry
msa-nim pdb 7DKF

# Specific chain only
msa-nim pdb 7DKF --chain A

# Multiple PDB IDs
msa-nim pdb 7DKF 6HBB 1ABC

# Specific chains + custom output dir
msa-nim pdb 7DKF --chain A --chain B -o my_msas
```

### Full options

```
msa-nim run [OPTIONS] [DIRECTORY]

Options:
  -o, --outdir PATH    Output directory (default: msa_results).
  --db TEXT            Database to search (repeatable; default: Uniref30_2302 colabfold_envdb_202108).
  --resume             Skip already-completed sequences.
  -j, --jobs INTEGER   Max parallel API calls (default: 1).
  --key TEXT           NVIDIA NIM API key.
  --timeout INTEGER    API timeout in seconds (default: 900).
```

### API key resolution

`msa-nim` looks for your key in this order:

1. `--key` flag or `NIM_API_KEY` environment variable
2. `.msa-nim.env` file in the working directory
3. `~/.config/msa-nim/config` global config file
4. Interactive prompt (if running in a terminal)

### Output files

| File | Description |
|------|-------------|
| `{id}_{db}.a3m` | MSA alignment in A3M format (ready for AlphaFold/ColabFold) |
| `{id}_raw.json` | Full API response (for debugging) |
| `.msa-nim-progress.json` | Resume tracking (auto-managed) |

### PDB mode output

When using `msa-nim pdb`, output files are named `{PDBID}_{CHAIN}_{DB}.a3m`. For example:

```
7DKF_A_Uniref30_2302.a3m
7DKF_A_colabfold_envdb_202108.a3m
7DKF_B_Uniref30_2302.a3m
7DKF_B_colabfold_envdb_202108.a3m
```

---

## Database info

`msa-nim` defaults to the same databases as **ColabFold**:

| Database | Cloud name | Purpose |
|----------|------------|---------|
| UniRef30 | `Uniref30_2302` | Builds profile + first-pass MSA |
| ColabFoldDB | `colabfold_envdb_202108` | Environmental metagenomic search |
| PDB70 | `PDB70_220313` | Structural templates (opt-in with `--db`) |

Use `--db` to override or add databases.

---

## Example walkthrough

```bash
# 1. Set your key
export NIM_API_KEY=nvapi-...

# 2. Create a FASTA file
cat > proteins.fasta << 'EOF'
>sp|P69905|HBA_HUMAN
VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR

>sp|P68871|HBB_HUMAN
MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH
EOF

# 3. Run
msa-nim run

# Output:
#   msa_results/HBA_HUMAN_Uniref30_2302.a3m
#   msa_results/HBA_HUMAN_colabfold_envdb_202108.a3m
#   msa_results/HBB_HUMAN_Uniref30_2302.a3m
#   msa_results/HBB_HUMAN_colabfold_envdb_202108.a3m
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Error: NIM_API_KEY is required` | Set `export NIM_API_KEY=nvapi-...` or run `msa-nim init` |
| `No .fasta files found` | Files must have `.fasta`, `.fa`, or `.faa` extension |
| `422: Database [x] is not available` | Check available databases with the correct casing (see [database info](#database-info)) |
| Run was interrupted | Re-run with `msa-nim run --resume` |

---

## Project structure

```
src/msa_nim/
  cli.py       # Click CLI commands (run, pdb, init)
  client.py    # NVIDIA API wrapper + retry logic
  pdb.py       # PDB sequence fetcher (RCSB)
  fasta.py     # FASTA parsing
  batch.py     # Batch orchestration + progress UI
  progress.py  # Resume tracking
  config.py    # API key resolution
```

---

## License

MIT &mdash; see [LICENSE](LICENSE).

## Acknowledgements

- [MMseqs2-GPU](https://github.com/soedinglab/MMseqs2) &mdash; GPU-accelerated homology search
- [ColabFold](https://github.com/sokrypton/ColabFold) &mdash; MSA + structure prediction pipeline
- [NVIDIA NIM](https://developer.nvidia.com/nim) &mdash; Cloud inference microservices