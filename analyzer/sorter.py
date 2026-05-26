import csv
import json
from typing import List, Dict, Any
from pathlib import Path
from core.chunk_stats import ChunkStats


def sort_chunks(chunks: List[ChunkStats], by: str = "entity_count", reverse: bool = True) -> List[ChunkStats]:
    """对区块列表排序，支持 entity_count 或 block_entity_count"""
    if by == "entity_count":
        return sorted(chunks, key=lambda c: c.entity_count, reverse=reverse)
    elif by == "block_entity_count":
        return sorted(chunks, key=lambda c: c.block_entity_count, reverse=reverse)
    else:
        return chunks


def export_csv(chunks: List[ChunkStats], filepath: Path):
    """导出为 CSV 文件"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["x", "z", "entity_count", "block_entity_count", "last_timestamp", "region_file"])
        for c in chunks:
            writer.writerow([c.x, c.z, c.entity_count, c.block_entity_count, c.last_timestamp, str(c.region_file)])


def export_json(chunks: List[ChunkStats], filepath: Path):
    """导出为 JSON 文件"""
    data = []
    for c in chunks:
        data.append({
            "x": c.x,
            "z": c.z,
            "entity_count": c.entity_count,
            "block_entity_count": c.block_entity_count,
            "last_timestamp": c.last_timestamp,
            "region_file": str(c.region_file)
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)