#!/usr/bin/env python3
"""
MCAnalyzer - Minecraft 存档卡顿分析器
主入口脚本 - 增强诊断版
"""

import sys
import argparse
import time
from pathlib import Path

# 在最开始打印启动标记，检查脚本是否被执行
print("=== MCAnalyzer started ===", flush=True)

# 尝试导入模块，若失败则打印详细错误
try:
    from utils.logger import setup_logger
    print("✓ utils.logger imported", flush=True)
except Exception as e:
    print(f"✗ Failed to import utils.logger: {e}", flush=True)
    sys.exit(1)

try:
    from core.region_scanner import scan_world
    print("✓ core.region_scanner imported", flush=True)
except Exception as e:
    print(f"✗ Failed to import core.region_scanner: {e}", flush=True)
    sys.exit(1)

try:
    from analyzer.metrics import identify_problem_chunks
    from analyzer.sorter import sort_chunks, export_csv, export_json
    print("✓ analyzer modules imported", flush=True)
except Exception as e:
    print(f"✗ Failed to import analyzer modules: {e}", flush=True)
    sys.exit(1)

try:
    from report.console import print_top_chunks
    from report.heatmap import generate_heatmap
    print("✓ report modules imported", flush=True)
except Exception as e:
    print(f"✗ Failed to import report modules: {e}", flush=True)
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="MCAnalyzer - 分析 Minecraft 存档中的卡顿区块",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mcanalyzer.py --world ./world
  mcanalyzer.py --world ./world --entity-threshold 100 --output ./my_report
  mcanalyzer.py --world ./world --no-map --format json
        """
    )
    parser.add_argument("--world", "-w", required=True, help="Minecraft 世界存档路径（包含 region 文件夹）")
    parser.add_argument("--output", "-o", default="./output", help="输出目录（默认 ./output）")
    parser.add_argument("--entity-threshold", "-e", type=int, default=200, help="实体数量阈值（默认 200）")
    parser.add_argument("--block-entity-threshold", "-b", type=int, default=500, help="方块实体数量阈值（默认 500）")
    parser.add_argument("--format", choices=["table", "csv", "json", "all"], default="table", help="输出格式（默认 table）")
    parser.add_argument("--no-map", action="store_true", help="不生成热力图")
    parser.add_argument("--dimension", choices=["overworld", "nether", "end", "all"], default="overworld", help="要扫描的维度（默认仅主世界）")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    parser.add_argument("--threads", type=int, default=1, help="扫描时使用的线程数（默认 1）")
    return parser.parse_args()


def main():
    print(">>> Entering main()", flush=True)
    args = parse_args()
    print(f">>> Arguments parsed: world={args.world}, verbose={args.verbose}", flush=True)

    # 临时使用 print 输出直到 logger 生效
    log_level = "DEBUG" if args.verbose else "INFO"
    try:
        logger = setup_logger(level=log_level)
        print(">>> Logger setup completed", flush=True)
    except Exception as e:
        print(f"!!! Logger setup failed: {e}", flush=True)
        # 创建一个简单的 fallback logger
        class DummyLogger:
            def info(self, msg): print(f"[INFO] {msg}", flush=True)
            def debug(self, msg): print(f"[DEBUG] {msg}", flush=True)
            def warning(self, msg): print(f"[WARNING] {msg}", flush=True)
            def error(self, msg): print(f"[ERROR] {msg}", flush=True)
            def exception(self, msg): print(f"[EXCEPTION] {msg}", flush=True)
        logger = DummyLogger()

    world_path = Path(args.world)
    if not world_path.exists():
        logger.error(f"世界路径不存在: {world_path}")
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"开始扫描世界: {world_path}")
    start_time = time.time()

    try:
        chunks = scan_world(world_path, dimension=args.dimension, max_threads=args.threads)
        logger.info(f"扫描完成，共找到 {len(chunks)} 个区块")
    except Exception as e:
        logger.exception(f"扫描失败: {e}")
        sys.exit(1)

    problem_chunks = identify_problem_chunks(
        chunks,
        entity_threshold=args.entity_threshold,
        block_entity_threshold=args.block_entity_threshold
    )
    logger.info(f"发现 {len(problem_chunks)} 个问题区块")

    sorted_chunks = sort_chunks(problem_chunks, by="entity_count", reverse=True)

    if args.format in ("csv", "all"):
        csv_path = output_dir / "all_chunks.csv"
        export_csv(chunks, csv_path)
        logger.info(f"所有区块数据已导出到 {csv_path}")
        if problem_chunks:
            problem_csv = output_dir / "problem_chunks.csv"
            export_csv(problem_chunks, problem_csv)
            logger.info(f"问题区块数据已导出到 {problem_csv}")

    if args.format in ("json", "all"):
        json_path = output_dir / "all_chunks.json"
        export_json(chunks, json_path)
        logger.info(f"所有区块数据已导出到 {json_path}")
        if problem_chunks:
            problem_json = output_dir / "problem_chunks.json"
            export_json(problem_chunks, problem_json)
            logger.info(f"问题区块数据已导出到 {problem_json}")

    if args.format in ("table", "all"):
        print_top_chunks(sorted_chunks, top_n=20)

    if not args.no_map:
        map_path = output_dir / "heatmap.html"
        generate_heatmap(chunks, map_path, entity_threshold=args.entity_threshold)
        logger.info(f"热力图已生成: {map_path}")

    elapsed = time.time() - start_time
    logger.info(f"分析完成，耗时 {elapsed:.2f} 秒")


if __name__ == "__main__":
    main()