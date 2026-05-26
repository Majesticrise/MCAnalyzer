import zlib
import gzip
import io
from typing import Tuple

from .simple_nbt import parse_nbt


def decompress_chunk(data: bytes) -> bytes:
    if len(data) < 1:
        raise ValueError("Empty data")
    compression = data[0]
    if compression == 0:
        raise ValueError("Compression type 0: empty or unused chunk")
    compressed = data[1:]
    if compression == 1:
        with gzip.open(io.BytesIO(compressed), 'rb') as f:
            return f.read()
    elif compression == 2:
        return zlib.decompress(compressed)
    elif compression == 3:
        return zlib.decompress(compressed, -zlib.MAX_WBITS)
    else:
        raise ValueError(f"Unknown compression type: {compression}")


def get_entity_and_blockentity_count(nbt_data: bytes) -> Tuple[int, int]:
    return parse_nbt(nbt_data)