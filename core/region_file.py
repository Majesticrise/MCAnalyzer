import struct
from pathlib import Path
from typing import Tuple, List, Optional, BinaryIO


class RegionFile:
    SECTOR_SIZE = 4096
    CHUNK_HEADER_SIZE = 5   # 4字节长度 + 1字节压缩类型

    def __init__(self, path: Path):
        self.path = path
        self._file: Optional[BinaryIO] = None
        self._locations: List[Tuple[int, int]] = [(0, 0)] * 1024
        self._timestamps: List[int] = [0] * 1024

    def open(self):
        self._file = open(self.path, "rb")
        # 读取 location 表 (4096字节)
        loc_data = self._file.read(4096)
        if len(loc_data) < 4096:
            loc_data = loc_data.ljust(4096, b'\x00')
        
        for i in range(1024):
            base = i * 4
            offset_bytes = loc_data[base:base+3]
            offset = int.from_bytes(offset_bytes, 'big')
            sector_count = loc_data[base+3] if base+3 < len(loc_data) else 0
            self._locations[i] = (offset, sector_count)

        # 读取 timestamp 表 (4096字节)
        ts_data = self._file.read(4096)
        if len(ts_data) < 4096:
            ts_data = ts_data.ljust(4096, b'\x00')
        for i in range(1024):
            base = i * 4
            if base + 4 <= len(ts_data):
                self._timestamps[i] = int.from_bytes(ts_data[base:base+4], 'big')
            else:
                self._timestamps[i] = 0

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
        offset_sectors, sector_count = self._locations[index]
        if offset_sectors == 0 or sector_count == 0:
            return None
        if offset_sectors < 2:   # 头部占用扇区0和1
            return None
        pos = offset_sectors * self.SECTOR_SIZE
        if pos >= self._file.seek(0, 2):
            return None
        self._file.seek(pos)
        header = self._file.read(self.CHUNK_HEADER_SIZE)
        if len(header) < self.CHUNK_HEADER_SIZE:
            return None
        
        # 正确解析：前4字节 = 压缩数据长度（不含头部），第5字节 = 压缩类型
        data_length = int.from_bytes(header[0:4], 'big')
        compression_type = header[4]
        
        # 处理超大区块标志（最高位为1）
        if compression_type & 0x80:
            # 外部存储，暂时跳过
            return None
        
        if data_length == 0 or data_length > 1024 * 1024:
            return None
        
        compressed_data = self._file.read(data_length)
        if len(compressed_data) < data_length:
            return None
        
        # 返回格式：[压缩类型] + 压缩数据
        return bytes([compression_type]) + compressed_data