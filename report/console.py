from typing import List
from core.chunk_stats import ChunkStats

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def print_top_chunks(chunks: List[ChunkStats], top_n: int = 20):
    """在控制台打印 top N 问题区块"""
    if not chunks:
        print("没有找到任何区块数据。")
        return

    top = chunks[:top_n]
    headers = ["#", "X", "Z", "实体数", "方块实体数", "最后访问时间"]
    rows = []
    for i, c in enumerate(top, 1):
        rows.append([i, c.x, c.z, c.entity_count, c.block_entity_count, c.last_timestamp])

    if HAS_TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        # 简单打印
        print("\n===== 问题区块 TOP {} =====".format(top_n))
        for row in rows:
            print(f"{row[0]:2}. ({row[1]}, {row[2]}) : 实体 {row[3]}, 方块实体 {row[4]}, 时间 {row[5]}")