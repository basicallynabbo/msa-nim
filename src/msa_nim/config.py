"""Configuration / API key resolution."""

import os
import sys
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "msa-nim"
GLOBAL_CONFIG = CONFIG_DIR / "config"
LOCAL_ENV = Path(".msa-nim.env")


def _read_key_from_file(path: Path) -> str | None:
    """Read NIM_API_KEY from a key=value file."""
    if not path.exists():
        return None
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("NIM_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        return None
    return None


def resolve_api_key() -> str:
    """
    Resolve NVIDIA NIM API key from (in order):
      1. NIM_API_KEY environment variable
      2. .msa-nim.env in current working directory
      3. ~/.config/msa-nim/config
      4. Interactive prompt (if TTY)
    """
    # 1. Environment variable
    key = os.environ.get("NIM_API_KEY")
    if key:
        return key

    # 2. Local .env file
    key = _read_key_from_file(LOCAL_ENV)
    if key:
        return key

    # 3. Global config
    key = _read_key_from_file(GLOBAL_CONFIG)
    if key:
        return key

    # 4. Interactive prompt (saves to .msa-nim.env for future use)
    if sys.stdin.isatty():
        print("\nNVIDIA NIM API key not found.")
        print("Get your free key at: https://build.nvidia.com/colabfold/msa-search")
        key = input("Paste your NIM_API_KEY: ").strip()
        if key:
            LOCAL_ENV.write_text(
                "# NVIDIA NIM API key (auto-saved by msa-nim)\n"
                "# Get your free key at: https://build.nvidia.com/colabfold/msa-search\n"
                f"NIM_API_KEY={key}\n"
            )
            print(f"Saved to {LOCAL_ENV.resolve()}")
            return key

    raise RuntimeError(
        "NIM_API_KEY is required. Set it via:\n"
        "  export NIM_API_KEY=nvapi-...\n"
        "  echo 'NIM_API_KEY=nvapi-...' > .msa-nim.env\n"
        "Or run `msa-nim run` in a terminal to be prompted interactively.\n"
        "Get your key at: https://build.nvidia.com/colabfold/msa-search"
    )
