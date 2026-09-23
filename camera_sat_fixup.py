# SPDX-License-Identifier: Apache-2.0
"""Refresh CHI full/DS4/DS16 buffer dimensions for each physical camera.

Paired with the MiuiCamera 4K EIS guard. This does not fix ultrawide 4K
or make the ultrawide sensor deliver 60fps. Reject unknown blob revisions.
"""
import hashlib
import struct
from pathlib import Path


def fixup_sat_buffers(ctx, file, file_path, *args, **kwargs):
    path = Path(file_path)
    b = bytearray(path.read_bytes())
    digest = hashlib.sha256(b).hexdigest()
    if digest == '8927747617c3729e2590ee06e3c9c1416182dab909647a7af044764459c76224':
     return
    if digest != 'adacef93c060f2ec9e05024613e196dae6a1a605741478743487334453164a10':
     raise ValueError('Unsupported alioth CHI blob: ' + digest)
    site=0x2886f0;cave=0x2d8330
    assert b[site:site+4]==bytes.fromhex('914100f8')
    payload=bytes.fromhex('914100f8af0317f8b00313f8f18300f9edc0fe17')
    assert b[cave:cave+len(payload)]==bytes(len(payload))
    struct.pack_into('<I',b,site,0x14000000|(((cave-site)//4)&0x3ffffff));b[cave:cave+len(payload)]=payload
    phoff=struct.unpack_from('<Q',b,32)[0];entsize,num=struct.unpack_from('<HH',b,54)
    found=False
    for i in range(num):
     o=phoff+i*entsize;typ,flags,off,va,pa,fs,ms,align=struct.unpack_from('<IIQQQQQQ',b,o)
     if typ==1 and flags==5 and off+fs==cave:
      assert fs==ms;struct.pack_into('<QQ',b,o+32,fs+len(payload),ms+len(payload));found=True
    assert found
    assert hashlib.sha256(b).hexdigest()=='8927747617c3729e2590ee06e3c9c1416182dab909647a7af044764459c76224'
    path.write_bytes(b)
