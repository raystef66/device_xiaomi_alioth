#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Decode the stock camera license into the build output directory."""

import base64
from pathlib import Path
import sys


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: decode_license INPUT OUTPUT")
    encoded = b"".join(Path(sys.argv[1]).read_bytes().split())
    Path(sys.argv[2]).write_bytes(base64.b64decode(encoded, validate=True))


if __name__ == "__main__":
    main()
