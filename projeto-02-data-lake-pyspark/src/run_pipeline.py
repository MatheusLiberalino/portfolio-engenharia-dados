from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


def run_script(script_name: str) -> None:
    subprocess.run([sys.executable, str(PROJECT_DIR / "src" / script_name)], check=True)


def main() -> None:
    print("1/2 Generating raw data...")
    run_script("generate_data.py")

    print("2/2 Building lakehouse layers...")
    run_script("build_lakehouse.py")

    print("Pipeline finished.")


if __name__ == "__main__":
    main()
