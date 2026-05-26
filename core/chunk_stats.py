from dataclasses import dataclass
from pathlib import Path


@dataclass
class ChunkStats:
    """区块统计数据"""
    x: int                     # 区块 X 坐标
    z: int                     # 区块 Z 坐标
    entity_count: int          # 实体数量
    block_entity_count: int    # 方块实体数量
    last_timestamp: int        # 最后访问时间（Unix 时间戳）
    region_file: Path          # 所属 .mca 文件路径