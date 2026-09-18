# 图书爆款视频营销流水线

这是一个面向图书营销工作的 Codex Skill。输入带有视频链接和传播/销售数据的 Excel 或 CSV 后，它会调用视频分析能力完成代表视频筛选、视频下载、FunASR 逐字转写、爆款规律分析、原声混剪脚本和竖屏粗剪成片。

它适合这样的任务：

- 分析一本或多本书的带货爆款视频；
- 分析作者、出版社或图书账号的高赞视频；
- 从真实字幕中统计反复出现的金句；
- 为新书营销寻找可复用的主题和视频结构；
- 只用原视频语句搭建混剪脚本；
- 根据视频链接和源时间码生成粗剪成片。

## 工作流程

1. 读取 XLSX/CSV，识别书名、视频链接、销量、销售额和互动数据。
2. 对链接和视频 ID 去重，默认最多选择 30 条代表视频。
3. 调用 `video-copy-analyzer` 下载视频，并用 FunASR 生成带时间码逐字稿。
4. 建立唯一证据表，统一管理原话、时间码、链接和本地素材。
5. 输出中文分析报告、金句 Top 5/10 和可复用的内容结构。
6. 默认生成 4 条原声混剪脚本：2 条营销导向、2 条内容导向。
7. 根据剪辑清单生成 1080×1920、H.264/AAC 的竖屏硬切粗剪。

## 核心原则

- 金句、脚本和粗剪必须以真实视频和 FunASR 字幕为依据。
- 所有具体文案必须标注原视频链接和源视频时间码。
- 没有销售数据时，只能写“高互动”或“高传播”，不能写“高转化”。
- 人物口播只能删减或重排原句，不能由 AI 改写或补写。
- 报告使用“开场抓力、情绪推进、信任建立、转化动作”等中文概念。
- 同一视频只下载和转写一次，报告、脚本和剪辑共用同一证据表。

## 仓库结构

```text
book-video-marketing-pipeline/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   └── icon.svg
├── references/
│   ├── analysis-report.md
│   └── scripts-and-roughcuts.md
└── scripts/
    ├── select_representative_videos.py
    └── build_roughcut.py
```

## 使用方法

将 `book-video-marketing-pipeline/` 作为完整 Skill 安装到支持 Codex Skills 的环境，然后调用：

> 请使用 `$book-video-marketing-pipeline`，分析我上传的爆款视频表格，下载代表视频并用 FunASR 转写，生成分析报告、4 条原声混剪脚本以及对应的粗剪成片。

最少需要上传一份包含真实视频链接的 XLSX 或 CSV。若希望按转化筛选，表格还应包含书名、销量或销售额。

## 代表视频筛选脚本

```bash
python book-video-marketing-pipeline/scripts/select_representative_videos.py \
  data.xlsx \
  --output selected.csv \
  --limit 30 \
  --per-book 3
```

- `--limit`：整体最多入选数量。
- `--per-book`：每本书优先纳入数量，不是严格上限。
- `--max-per-book`：可选，每本书严格最多入选数量。

脚本兼容 XLSX、XLSM 和 CSV，并识别“万、千、亿、w、k”以及“5000-1w”等常见数据写法。

## 粗剪脚本

先生成剪辑清单：

```json
{
  "title": "示例脚本",
  "segments": [
    {
      "source_path": "/absolute/path/video.mp4",
      "start": "00:00:28.000",
      "end": "00:00:42.000",
      "quote": "视频中的逐字原话",
      "source_url": "https://example.com/video"
    }
  ]
}
```

再执行：

```bash
python book-video-marketing-pipeline/scripts/build_roughcut.py \
  edit-list.json \
  roughcut.mp4
```

本地需要安装 Python 3、FFmpeg 和 FFprobe；读取 XLSX 时需要 `openpyxl`。视频下载和 FunASR 转写由 `video-copy-analyzer` Skill 提供。

## 隐私与素材

仓库不包含任何用户表格、下载视频、逐字稿、报告、测试成片或平台登录信息。使用时请确保拥有下载、分析和剪辑相关素材的合法权限。

