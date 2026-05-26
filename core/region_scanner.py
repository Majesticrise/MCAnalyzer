import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from .region_file import RegionFile
from .chunk_parser import decompress_chunk, get_entity_and_blockentity_count
from .chunk_stats import ChunkStats
from utils.logger import setup_logger

logger = setup_logger()


def scan_world(world_path: Path, dimension: str = "overworld", max_threads: int = 1) -> List[ChunkStats]:
    """
    扫描整个世界，返回所有区块的统计数据
    dimension: "overworld", "nether", "end", "all"
    """
    results = []
    region_dirs = []
    if dimension == "overworld" or dimension == "all":
        region_dirs.append(world_path / "region")
    if dimension == "nether" or dimension == "all":
        region_dirs.append(world_path / "DIM-1" / "region")
    if dimension == "end" or dimension == "all":
        region_dirs.append(world_path / "DIM1" / "region")

    tasks = []
    for region_dir in region_dirs:
        if not region_dir.exists():
            logger.warning(f"目录不存在，跳过: {region_dir}")
            continue
        mca_files = list(region_dir.glob("*.mca"))
        for mca in mca_files:
            tasks.append(mca)

    if max_threads <= 1:
        for mca in tasks:
            results.extend(scan_region_file(mca))
    else:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_mca = {executor.submit(scan_region_file, mca): mca for mca in tasks}
            for future in as_completed(future_to_mca):
                results.extend(future.result())
    return results


def scan_region_file(mca_path: Path) -> List[ChunkStats]:
    """扫描单个 .mca 文件，返回其中所有区块的统计"""
    region = RegionFile(mca_path)
    region.open()
    chunks = []
    # 从文件名解析区域坐标 (r.X.Z.mca)
    try:
        name = mca_path.stem
        parts = name.split('.')
        if len(parts) == 3 and parts[0] == 'r':
            base_x = int(parts[1]) * 32
            base_z = int(parts[2]) * 32
        else:
            base_x = 0
            base_z = 0
    except:
        base_x = 0
        base_z = 0

    for idx in range(1024):
        timestamp = region.get_chunk_timestamp(idx)
        if timestamp == 0:
            continue  # 空区块
        chunk_data = region.get_chunk_data(idx)
        if chunk_data is None:
            continue
        try:
            decompressed = decompress_chunk(chunk_data)
            entity_count, block_entity_count = get_entity_and_blockentity_count(decompressed)
        except Exception as e:
            logger.debug(f"解析区块失败 {mca_path} idx {idx}: {e}")
            continue
        # 计算区块绝对坐标
        local_x = idx % 32
        local_z = idx // 32
        world_x = base_x + local_x
        world_z = base_z + local_z
        chunks.append(ChunkStats(
            x=world_x,
            z=world_z,
            entity_count=entity_count,
            block_entity_count=block_entity_count,
            last_timestamp=timestamp,
            region_file=mca_path
        ))
    region.close()
    return chunks