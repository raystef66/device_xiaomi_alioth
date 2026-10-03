# SPDX-License-Identifier: Apache-2.0
"""Extract unchanged 24 kHz Alioth RAM samples for the common effect loader.

Stock marker 0_click, 3_thud and 2_tick supply CLICK, THUD and LIGHT_TICK.
No generated envelope, gain alteration, or mapping of chirp/spin/LOW_TICK.
"""
import hashlib
import struct
from pathlib import Path

STOCK_SHA256 = "7e31b22b591d5f45dcf262529b71fd2b5b3277f98553414b54d3b69d7255d4c4"
WAVEFORMS = {'vendor/etc/vibrator/primitive_effect_1.bin': (0, 'dcb60279196fcd747381e41c162ad0a745bc0c685e80b7d04d801486f0d1d248'), 'vendor/etc/vibrator/primitive_effect_2.bin': (3, '7e3918dffe74a7b3f0c47afd1d9882297b17414f8baca76a860203f6f19cb745'), 'vendor/etc/vibrator/primitive_effect_7.bin': (2, '15b1a3b72399ea4ebe96f71bae6a60e1e7fc705a831f367f0957942e43fda1c0')}


def fixup_aw8697_waveform(ctx, file, file_path, *args, **kwargs):
    path = Path(file_path)
    data = path.read_bytes()
    slot, expected = WAVEFORMS[file.dst]
    digest = hashlib.sha256(data).hexdigest()
    if digest == expected:
        return
    if digest != STOCK_SHA256:
        raise ValueError("Unsupported Alioth RAM bank: " + digest)
    base = int.from_bytes(data[2:4], "big")
    start, end = struct.unpack_from(">HH", data, 5 + slot * 4)
    waveform = data[start - base + 4:end - base + 5]
    if hashlib.sha256(waveform).hexdigest() != expected:
        raise ValueError("Unexpected Alioth waveform slice")
    path.write_bytes(waveform)
