"""Front-page image entry for news-image-20261119.

This program ships the finished 19 November 2026 front page. The artwork
is rendered offline ahead of time and stored next to this file as entry.png;
all this program does is copy that image into the output directory, so it
never touches the network and produces identical bytes on every run.

Usage:
    python3 main.py [output-directory]

With no argument, the output directory comes from the MAKEFUN_OUTPUT_DIR
environment variable, falling back to /output.
"""

import os
import shutil
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parent
IMAGE_NAME = "entry.png"


def resolve_output_dir(argv):
    """Pick the output directory from argv, the environment, or the default."""
    if len(argv) > 1:
        return Path(argv[1])
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main(argv):
    target_dir = resolve_output_dir(argv)
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE_DIR / IMAGE_NAME, target_dir / IMAGE_NAME)


if __name__ == "__main__":
    main(sys.argv)
