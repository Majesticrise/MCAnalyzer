MCAnalyzer 是一个 Minecraft 存档卡顿分析工具，可以扫描 Java版 世界的区块，统计每个区块的实体数量、方块实体数量，找出导致卡顿的问题区块，并生成热力图和 CSV 数据报告。

功能特点

高效扫描，遍历世界存档的所有 .mca 文件，提取区块数据。
问题识别，可自定义实体数和方块实体数阈值，自动标记高负载区块。
多种输出，支持命令行表格，CSV，JSON 导出。
热力图，生成交互式 HTML 热力图，自动缩放到问题区块周围。
跨维度，可扫描主世界，下界，末地或全部。
多线程，可使用多线程加速扫描。
零依赖回退，内置简易 NBT 解析器，无需安装任何库即可运行，推荐安装 nbtlib 提升速度。

安装与运行

方式一，使用已编译的 EXE 文件，无需 Python 环境。
1. 下载 MCAnalyzer.exe。
2. 打开命令提示符（CMD）或 PowerShell。
3. 运行命令：MCAnalyzer.exe --world "你的世界存档路径"

方式二，从源码运行，需要 Python 3.9 或更高版本。
1. 获取源码。
2. 可选安装依赖：pip install tabulate nbtlib
3. 运行：python mcanalyzer.py --world "你的世界存档路径"

如果不安装任何依赖，程序会自动使用内置解析器，但速度较慢。

使用方法

基本命令格式（EXE 或 Python 脚本通用）：
MCAnalyzer.exe --world <世界存档路径> [选项]

常用示例

扫描主世界，输出表格和热力图：
MCAnalyzer.exe --world ./saves/MyWorld

只导出 CSV，不生成地图：
MCAnalyzer.exe --world ./world --format csv --no-map

扫描所有维度，实体阈值设为 100：
MCAnalyzer.exe --world ./world --dimension all --entity-threshold 100

使用 4 线程加速，输出详细日志：
MCAnalyzer.exe --world ./world --threads 4 --verbose

输出 JSON 格式：
MCAnalyzer.exe --world ./world --format json

命令行参数说明

--world 或 -w，世界存档路径，必须。
--output 或 -o，输出目录，默认 ./output。
--entity-threshold 或 -e，实体数阈值，默认 200。
--block-entity-threshold 或 -b，方块实体数阈值，默认 500。
--format，输出格式，可选 table，csv，json，all，默认 table。
--no-map，不生成热力图。
--dimension，扫描维度，可选 overworld，nether，end，all，默认 overworld。
--verbose 或 -v，显示详细日志。
--threads，扫描线程数，默认 1。

输出文件

在输出目录（默认 ./output）下生成：
all_chunks.csv 和 all_chunks.json，所有区块的完整统计。
problem_chunks.csv 和 problem_chunks.json，超出阈值的区块列表。
heatmap.html，实体数量热力图，鼠标悬停显示区块坐标与实体数。

CSV 文件包含字段：x，z，entity_count，block_entity_count，last_timestamp，region_file。

工作原理

1. 解析区域文件，读取 region 文件夹下的 .mca 文件头，获取每个区块的偏移量和压缩信息。
2. 提取区块数据，解压并解析 NBT 结构，统计 entities 和 block_entities 列表长度。
3. 分析与报告，根据阈值过滤，排序输出，并生成可视化图表。

注意事项

仅支持 Minecraft Java版 1.13 及以上版本（扁平化后的区块格式）。
不支持外部存储的超大区块（.mcc 文件），此类区块很少见，程序会安全跳过。
扫描大型世界（数万个区块）时，建议使用 --threads 选项并安装 nbtlib 以提高速度。
中文路径可能出现编码问题，建议将存档复制到英文路径后再运行。

开发与贡献

项目结构：
mcanalyzer/
  core/          区域文件解析，NBT处理
  analyzer/      统计，排序，过滤
  report/        控制台表格，热力图生成
  utils/         日志，参数解析
  mcanalyzer.py  主入口
欢迎提交 Issue 和 Pull Request。

许可证

MIT 许可证，可自由使用和修改。

致谢

Minecraft Wiki 提供的区域文件格式说明。
参考开源项目 MCA Selector 和 NBT 的解析思路。

如果觉得这个工具有帮助，欢迎给个 Star 支持一下。