import csv
import json
from typing import List
from pathlib import Path
from core.chunk_stats import ChunkStats
from datetime import datetime


def timestamp_to_str(ts: int) -> str:
    if ts == 0:
        return "从未访问"
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def sort_chunks(chunks: List[ChunkStats], by: str = "entity_count", reverse: bool = True) -> List[ChunkStats]:
    if by == "entity_count":
        return sorted(chunks, key=lambda c: c.entity_count, reverse=reverse)
    elif by == "block_entity_count":
        return sorted(chunks, key=lambda c: c.block_entity_count, reverse=reverse)
    else:
        return chunks


def export_csv(chunks: List[ChunkStats], filepath: Path):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["x", "z", "entity_count", "block_entity_count", "last_timestamp", "last_time", "region_file"])
        for c in chunks:
            writer.writerow([
                c.x, c.z, c.entity_count, c.block_entity_count,
                c.last_timestamp, timestamp_to_str(c.last_timestamp), str(c.region_file)
            ])


def export_json(chunks: List[ChunkStats], filepath: Path):
    data = []
    for c in chunks:
        data.append({
            "x": c.x,
            "z": c.z,
            "entity_count": c.entity_count,
            "block_entity_count": c.block_entity_count,
            "last_timestamp": c.last_timestamp,
            "last_time": timestamp_to_str(c.last_timestamp),
            "region_file": str(c.region_file)
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)