import zlib
import gzip
import io
from typing import Tuple, List, Any

# 优先使用 nbtlib，如果失败则回退到简易解析器
try:
    import nbtlib
    HAS_NBTLIB = True
except ImportError:
    HAS_NBTLIB = False
    from .simple_nbt import parse_nbt


def decompress_chunk(data: bytes) -> bytes:
    if len(data) < 1:
        raise ValueError("Empty data")
    compression = data[0]
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
    if HAS_NBTLIB:
        try:
            root = nbtlib.load(io.BytesIO(nbt_data))
            # 获取 Level 标签
            if "Level" in root:
                level = root["Level"]
            else:
                level = root

            # 获取实体列表，确保是列表类型
            entities_obj = level.get("Entities")
            if entities_obj is None:
                entities: List[Any] = []
            else:
                entities = list(entities_obj)  # 转换为列表确保类型

            # 获取方块实体列表
            tile_obj = level.get("TileEntities")
            if tile_obj is None:
                tile_obj = level.get("block_entities")
            if tile_obj is None:
                tile_entities: List[Any] = []
            else:
                tile_entities = list(tile_obj)

            return len(entities), len(tile_entities)
        except Exception:
            # 回退到简易解析器
            return parse_nbt(nbt_data)
    else:
        return parse_nbt(nbt_data)