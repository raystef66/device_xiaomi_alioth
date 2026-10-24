# SPDX-License-Identifier: Apache-2.0
"""Reject missing input stream descriptors before allocating a CamX session.

Alioth VTCam can submit a null stream descriptor for a generic Camera2 request.
Session::Initialize dereferences it and its early-failure destructor also assumes
later initialization. Validate the input before CHISession::Create allocates the
session, returning NULL through the existing caller error path. Valid descriptors
retain the original function prologue and processing. No camera IDs are hidden.
"""

import hashlib
import struct
from pathlib import Path

ORIGINAL_SHA256 = '21e4bb61dcd9bdef97d2d38fcfae1a59be15a6d951fc73b9fe785de86d027388'
PATCHED_SHA256 = '2e116c44ed926e8a787615fa9cf3cf8ec53b396612d99ff3adf04c862be42497'
SITE = 0x79d3b8
CAVE = 0x8c0640
# Input: x0 = CHISessionCreateData. For each non-realtime pipeline, reject a
# missing input descriptor array or null stream at offset 16 of its 40-byte
# entries. Only caller-saved x9-x14 and NZCV are scratch. Valid data executes
# the displaced stp x29,x30,[sp,#-48]! and resumes at SITE + 4; rejection returns
# NULL before allocation or stack changes. The payload has no relocations.
PAYLOAD = bytes.fromhex(
    'a00200b4092040b9290200340a0c40f92a0200b44b0940b94b0100354c1140b9'
    '0c0100344d0d40f96d0100b4ae0940f92e0100b4ada100918c05007181ffff54'
    '4ae100912905007161feff54fd7bbda94b73fb17e0031faac0035fd6'
)


def apply_session_guard(data):
    digest = hashlib.sha256(data).hexdigest()
    if digest == PATCHED_SHA256:
        return data
    if digest != ORIGINAL_SHA256:
        raise ValueError('Unsupported alioth camera HAL: ' + digest)

    b = bytearray(data)
    if b[SITE:SITE + 4] != bytes.fromhex('fd7bbda9'):
        raise ValueError('Unexpected CHISession::Create prologue')
    if b[CAVE:CAVE + len(PAYLOAD)] != bytes(len(PAYLOAD)):
        raise ValueError('Camera HAL RX padding is not empty')
    struct.pack_into('<I', b, SITE,
                     0x14000000 | (((CAVE - SITE) // 4) & 0x3ffffff))
    b[CAVE:CAVE + len(PAYLOAD)] = PAYLOAD

    phoff = struct.unpack_from('<Q', b, 32)[0]
    entsize, count = struct.unpack_from('<HH', b, 54)
    for i in range(count):
        off = phoff + i * entsize
        kind, flags, start, va, pa, filesz, memsz, align = struct.unpack_from(
            '<IIQQQQQQ', b, off)
        if kind == 1 and flags == 5 and start + filesz == CAVE:
            if filesz != memsz or CAVE + len(PAYLOAD) > 0x8c1000:
                raise ValueError('Unexpected camera HAL RX segment bounds')
            struct.pack_into('<QQ', b, off + 32,
                             filesz + len(PAYLOAD), memsz + len(PAYLOAD))
            break
    else:
        raise ValueError('Expected camera HAL RX segment not found')

    if hashlib.sha256(b).hexdigest() != PATCHED_SHA256:
        raise ValueError('Camera session guard output hash mismatch')
    return bytes(b)


def fixup_camera_session_streams(ctx, file, file_path, *args, **kwargs):
    path = Path(file_path)
    data = path.read_bytes()
    patched = apply_session_guard(data)
    if patched != data:
        path.write_bytes(patched)
