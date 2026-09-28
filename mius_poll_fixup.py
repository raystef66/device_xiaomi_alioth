# SPDX-License-Identifier: Apache-2.0
"""Keep Alioth MIUS idle poll timeouts inside pollEvents."""
import hashlib
from pathlib import Path

STOCK_SHA256 = "86e673baa9169d5d07c51f8c196bbe4cf307f99036e3beaa7dfe5449d016ae1f"
PATCHED_SHA256 = "7576242d762f250353ecc72dd21a74389738bb6a1d0c37f807071b0b48b435ee"


def fixup_mius_poll_timeout(ctx, file, file_path, *args, **kwargs):
    path = Path(file_path)
    data = bytearray(path.read_bytes())
    digest = hashlib.sha256(data).hexdigest()
    if digest == PATCHED_SHA256:
        return
    if digest != STOCK_SHA256:
        raise ValueError("Unsupported Alioth MIUS blob: " + digest)
    # poll(fd, 1, 8000) returns zero when no event arrives. The stock
    # cbz w25 jumps to -EIO. Retry poll instead, after the existing flush
    # check and mutex unlock. Negative returns and revents errors are unchanged.
    # 0x4960: cbz w25, 0x499c -> cbz w25, 0x4930
    data[0x4960:0x4964] = bytes.fromhex("99feff34")
    if hashlib.sha256(data).hexdigest() != PATCHED_SHA256:
        raise ValueError("Unexpected MIUS patch result")
    path.write_bytes(data)
