from pathlib import Path
from typing import List
from core.chunk_stats import ChunkStats


def generate_heatmap(chunks: List[ChunkStats], output_path: Path, entity_threshold: int):
    """生成 HTML 热力图（Canvas 网格），若世界过大则自动缩放到问题区块周围"""
    if not chunks:
        html = "<html><body><h1>没有区块数据</h1></body></html>"
        output_path.write_text(html, encoding='utf-8')
        return

    # 筛选问题区块（实体数 >= threshold）
    problem_chunks = [c for c in chunks if c.entity_count >= entity_threshold]

    # 决定显示范围：如果有问题区块，则显示其周围区域；否则显示全图（但会受尺寸限制）
    if problem_chunks:
        # 计算问题区块的边界，并向外扩展 16 个区块（保证能看到周围环境）
        min_x = min(c.x for c in problem_chunks) - 16
        max_x = max(c.x for c in problem_chunks) + 16
        min_z = min(c.z for c in problem_chunks) - 16
        max_z = max(c.z for c in problem_chunks) + 16
        title_suffix = f"（聚焦问题区块，共 {len(problem_chunks)} 个，实体≥{entity_threshold}）"
    else:
        # 没有问题区块，显示全图（但可能很大）
        min_x = min(c.x for c in chunks)
        max_x = max(c.x for c in chunks)
        min_z = min(c.z for c in chunks)
        max_z = max(c.z for c in chunks)
        title_suffix = "（无问题区块，显示全图）"

    width = max_x - min_x + 1
    height = max_z - min_z + 1

    # 限制网格最大尺寸（防止浏览器卡顿）
    MAX_SIZE = 10240
    if width > MAX_SIZE or height > MAX_SIZE:
        # 如果缩放后仍然太大，给出文字报告
        html = f"""<html><body>
        <h1>世界范围仍然过大，无法显示热力图</h1>
        <p>区块范围 X: {min_x}~{max_x} (宽度 {width})，Z: {min_z}~{max_z} (高度 {height})</p>
        <p>当前实体阈值: {entity_threshold}，问题区块数: {len(problem_chunks)}</p>
        <p>你可以：<br>
        - 提高 --entity-threshold 以减少问题区块数量<br>
        - 使用 --format csv 导出数据后用其他工具分析<br>
        - 手动指定更小的区域（后续版本支持）</p>
        <h2>问题区块列表（前50）</h2>
        <table border="1" cellpadding="5">
        <tr><th>X</th><th>Z</th><th>实体数</th><th>方块实体数</th><th>最后访问时间</th></tr>
        {''.join(f'<tr><td>{c.x}</td><td>{c.z}</td><td>{c.entity_count}</td><td>{c.block_entity_count}</td><td>{c.last_timestamp}</td></tr>' for c in problem_chunks[:50])}
        </table>
        </body></html>"""
        output_path.write_text(html, encoding='utf-8')
        return

    # 构建数据网格（只包含显示范围内的区块）
    # 为了提高性能，先创建一个字典：坐标 -> ChunkStats
    chunk_map = {(c.x, c.z): c for c in chunks}

    grid = [[0] * width for _ in range(height)]
    for x in range(min_x, max_x + 1):
        for z in range(min_z, max_z + 1):
            c = chunk_map.get((x, z))
            if c:
                gx = x - min_x
                gz = z - min_z
                grid[gz][gx] = c.entity_count

    # 颜色映射函数
    def get_color(value):
        if value == 0:
            return "#eeeeee"
        elif value < 50:
            return "#c6dbef"
        elif value < 100:
            return "#9ecae1"
        elif value < 200:
            return "#6baed6"
        elif value < 500:
            return "#4292c6"
        else:
            return "#08519c"

    cell_size = 10  # px
    map_width = width * cell_size
    map_height = height * cell_size

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>MCAnalyzer - 区块实体热力图</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h2 {{ margin-bottom: 10px; }}
        .tooltip {{ position: absolute; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 4px; pointer-events: none; font-size: 12px; display: none; }}
        .legend {{ display: flex; margin-bottom: 20px; align-items: center; flex-wrap: wrap; }}
        .legend-color {{ width: 20px; height: 20px; margin-right: 5px; }}
        .legend-item {{ display: flex; align-items: center; margin-right: 20px; }}
        .info {{ margin-bottom: 20px; color: #555; }}
    </style>
</head>
<body>
    <h2>MCAnalyzer - 实体数量热力图 {title_suffix}</h2>
    <div class="info">
        <span>显示范围 X: {min_x} ~ {max_x}, Z: {min_z} ~ {max_z}</span>
        <span style="margin-left: 20px;">总区块数: {len(chunks)} | 问题区块数: {len(problem_chunks)}</span>
    </div>
    <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background:#eeeeee;"></div> 0</div>
        <div class="legend-item"><div class="legend-color" style="background:#c6dbef;"></div> 1-49</div>
        <div class="legend-item"><div class="legend-color" style="background:#9ecae1;"></div> 50-99</div>
        <div class="legend-item"><div class="legend-color" style="background:#6baed6;"></div> 100-199</div>
        <div class="legend-item"><div class="legend-color" style="background:#4292c6;"></div> 200-499</div>
        <div class="legend-item"><div class="legend-color" style="background:#08519c;"></div> ≥500</div>
    </div>
    <canvas id="heatmap" width="{map_width}" height="{map_height}" style="border:1px solid #ccc;"></canvas>
    <div class="tooltip" id="tooltip"></div>
    <script>
        const grid = {grid};
        const minX = {min_x};
        const minZ = {min_z};
        const cellSize = {cell_size};
        const canvas = document.getElementById('heatmap');
        const ctx = canvas.getContext('2d');
        const tooltip = document.getElementById('tooltip');

        function draw() {{
            for (let z = 0; z < {height}; z++) {{
                for (let x = 0; x < {width}; x++) {{
                    let value = grid[z][x];
                    let color;
                    if (value === 0) color = '#eeeeee';
                    else if (value < 50) color = '#c6dbef';
                    else if (value < 100) color = '#9ecae1';
                    else if (value < 200) color = '#6baed6';
                    else if (value < 500) color = '#4292c6';
                    else color = '#08519c';
                    ctx.fillStyle = color;
                    ctx.fillRect(x * cellSize, z * cellSize, cellSize-1, cellSize-1);
                }}
            }}
        }}

        function getMousePos(canvas, evt) {{
            var rect = canvas.getBoundingClientRect();
            var scaleX = canvas.width / rect.width;
            var scaleY = canvas.height / rect.height;
            return {{
                x: (evt.clientX - rect.left) * scaleX,
                y: (evt.clientY - rect.top) * scaleY
            }};
        }}

        canvas.addEventListener('mousemove', function(e) {{
            var pos = getMousePos(canvas, e);
            var gridX = Math.floor(pos.x / cellSize);
            var gridZ = Math.floor(pos.y / cellSize);
            if (gridX >= 0 && gridX < {width} && gridZ >= 0 && gridZ < {height}) {{
                var entityCount = grid[gridZ][gridX];
                var worldX = minX + gridX;
                var worldZ = minZ + gridZ;
                tooltip.style.display = 'block';
                tooltip.style.left = (e.clientX + 15) + 'px';
                tooltip.style.top = (e.clientY - 30) + 'px';
                tooltip.innerHTML = `区块 ({{worldX}}, {{worldZ}})<br>实体数: ${{entityCount}}`;
            }} else {{
                tooltip.style.display = 'none';
            }}
        }});

        canvas.addEventListener('mouseleave', function() {{
            tooltip.style.display = 'none';
        }});

        draw();
    </script>
</body>
</html>"""
    output_path.write_text(html, encoding='utf-8')