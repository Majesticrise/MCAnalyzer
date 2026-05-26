from pathlib import Path
from typing import List, Dict, Tuple
from core.chunk_stats import ChunkStats


def generate_heatmap(chunks: List[ChunkStats], output_path: Path, entity_threshold: int):
    """生成 HTML 热力图（Canvas 网格）"""
    if not chunks:
        # 生成一个空地图的提示
        html = "<html><body><h1>没有区块数据</h1></body></html>"
        output_path.write_text(html, encoding='utf-8')
        return

    # 找出坐标范围
    min_x = min(c.x for c in chunks)
    max_x = max(c.x for c in chunks)
    min_z = min(c.z for c in chunks)
    max_z = max(c.z for c in chunks)
    width = max_x - min_x + 1
    height = max_z - min_z + 1

    # 限制网格最大尺寸（防止过大）
    MAX_SIZE = 500
    if width > MAX_SIZE or height > MAX_SIZE:
        # 如果太大，不显示每个格子，而显示统计信息
        html = f"<html><body><h1>世界太大，无法显示热力图</h1><p>区块范围 X: {min_x}~{max_x}, Z: {min_z}~{max_z}</p></body></html>"
        output_path.write_text(html, encoding='utf-8')
        return

    # 构建数据网格
    grid = [[0] * width for _ in range(height)]
    for c in chunks:
        gx = c.x - min_x
        gz = c.z - min_z
        grid[gz][gx] = c.entity_count

    # 颜色映射函数（返回颜色字符串）
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

    # 生成 HTML
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
        .legend {{ display: flex; margin-bottom: 20px; align-items: center; }}
        .legend-color {{ width: 20px; height: 20px; margin-right: 5px; }}
        .legend-item {{ display: flex; align-items: center; margin-right: 20px; }}
    </style>
</head>
<body>
    <h2>MCAnalyzer - 实体数量热力图</h2>
    <div class="legend">
        <div class="legend-item"><div class="legend-color" style="background:#eeeeee;"></div> 0</div>
        <div class="legend-item"><div class="legend-color" style="background:#c6dbef;"></div> 1-49</div>
        <div class="legend-item"><div class="legend-color" style="background:#9ecae1;"></div> 50-99</div>
        <div class="legend-item"><div class="legend-color" style="background:#6baed6;"></div> 100-199</div>
        <div class="legend-item"><div class="legend-color" style="background:#4292c6;"></div> 200-499</div>
        <div class="legend-item"><div class="legend-color" style="background:#08519c;"></div> >=500</div>
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