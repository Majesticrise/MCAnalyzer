import struct
from pathlib import Path
from typing import Tuple, List, Optional, BinaryIO


class RegionFile:
    SECTOR_SIZE = 4096
    CHUNK_HEADER_SIZE = 5

    def __init__(self, path: Path):
        self.path = path
        self._file: Optional[BinaryIO] = None
        self._locations: List[Tuple[int, int]] = [(0, 0)] * 1024
        self._timestamps: List[int] = [0] * 1024

    def open(self):
        self._file = open(self.path, "rb")
        loc_data = self._file.read(4096)
        for i in range(1024):
            offset_bytes = loc_data[i*4:i*4+3]
            offset = struct.unpack(">I", offset_bytes + b'\x00')[0]
            sector_count = loc_data[i*4+3]
            self._locations[i] = (offset, sector_count)

        ts_data = self._file.read(4096)
        for i in range(1024):
            self._timestamps[i] = struct.unpack(">I", ts_data[i*4:i*4+4])[0]

    def close(self):
        if self._file:
            self._file.close()

    def get_chunk_timestamp(self, index: int) -> int:
        if 0 <= index < 1024:
            return self._timestamps[index]
        return 0

    def get_chunk_data(self, index: int) -> Optional[bytes]:
        if not self._file:
            raise RuntimeError("File not opened")
        offset, sector_count = self._locations[index]
        if offset == 0 or sector_count == 0:
            return None
        pos = offset * self.SECTOR_SIZE
        self._file.seek(pos)
        header = self._file.read(self.CHUNK_HEADER_SIZE)
        if len(header) < self.CHUNK_HEADER_SIZE:
            return None
        compression_type = header[0]
        length = struct.unpack(">I", header[1:5])[0]
        data = self._file.read(length)
        if len(data) < length:
            return None
        return bytes([compression_type]) + data