"""news-image-20261119 entry, v1 (Python 3.13, standard library only).

Writes the v1 front-page image to /output/entry.png. The image is rendered
offline by render_v1.py and held beside this file; this program only copies
it, so it needs no network and writes the same bytes on every run.

Usage:
    python3 main.py [output-dir]

The output directory defaults to $MAKEFUN_OUTPUT_DIR, else /output.
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv):
    if len(argv) > 1:
        out_dir = Path(argv[1])
    else:
        out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / "entry.png", out_dir / "entry.png")


if __name__ == "__main__":
    main(sys.argv)
