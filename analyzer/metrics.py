from typing import List
from core.chunk_stats import ChunkStats


def identify_problem_chunks(chunks: List[ChunkStats], entity_threshold: int, block_entity_threshold: int) -> List[ChunkStats]:
    """筛选出实体数或方块实体数超过阈值的区块"""
    return [
        c for c in chunks
        if c.entity_count >= entity_threshold or c.block_entity_count >= block_entity_threshold
    ]