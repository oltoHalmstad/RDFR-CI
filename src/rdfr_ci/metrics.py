
"""Small reusable metrics helpers for RDFR-CI experiments."""
from __future__ import annotations
import numpy as np

def event_ids_from_binary(labels):
    """Assign integer IDs to contiguous positive attack episodes; normal points get -1."""
    y = np.asarray(labels, dtype=int)
    out = np.full(len(y), -1, dtype=int)
    current = -1; in_event = False
    for i,v in enumerate(y):
        if v and not in_event:
            current += 1; in_event = True
        elif not v:
            in_event = False
        if v:
            out[i] = current
    return out

def sha256_file(path):
    import hashlib
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
