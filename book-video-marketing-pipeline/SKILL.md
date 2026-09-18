---
name: book-video-marketing-pipeline
description: Analyze book-marketing or account-level viral-video spreadsheets and turn representative videos into an evidence-based Chinese report, timestamped original-footage mashup scripts, and portrait rough-cut MP4s. Use when the user uploads an XLSX/CSV of Douyin, WeChat Channels, Xiaohongshu, Bilibili, YouTube, or similar videos and wants reusable themes, structures, quotes, scripts, or rough cuts for another book campaign. Requires real video downloads and FunASR transcription; do not use for invented ad copy or polished final editing.
---

# 图书爆款视频营销流水线

把一份爆款视频表格处理成同一证据链上的四类交付物：代表视频清单、分析报告、原声混剪脚本、竖屏粗剪成片。一次下载、一次转写，后续全部复用，避免重复分析和反复改表。

## 输入与默认值

- 必需：含视频链接的 XLSX/CSV。列名可以不同，但必须能定位真实视频。
- 可选：书名/商品、销量或销售额、点赞/评论/收藏/转发、营销目标、禁用表达、已有书籍资料。
- 未指定时：最多分析 30 条；多本书且有销量时每本先取销量最高 3 条，再补足整体代表样本；输出 4 条脚本，其中 2 条具有营销导向、2 条不带营销导向。
- 只有账号热度数据、没有销量时，按点赞及评论/收藏/转发的综合互动选择代表视频，不得把“高赞”写成“高转化”。

## 必须调用的能力

1. 先读取并使用 **video-copy-analyzer**，执行视频下载、FunASR 真实音频转写、字幕校正和三维分析。
2. 处理 XLSX/CSV 时使用 **Spreadsheets**。
3. 生成 DOCX 报告时使用 **documents**，完成渲染检查。
4. 交付报告和视频时使用 **openai-library:library** 保存。

若当前环境缺少其中某项能力，明确说明缺失项并完成仍可验证的部分；不得用标题、简介或人工猜测冒充逐字字幕。

## 最短工作流

1. **建立唯一素材清单**：去重链接/视频 ID，识别书名、销量与互动字段。可运行：
   `python scripts/select_representative_videos.py <表格> --output <代表视频.csv> --limit 30 --per-book 3`
   其中 `--per-book` 表示每本优先纳入数量；若用户要求严格的单本上限，再加 `--max-per-book <数量>`。
2. **下载并转写一次**：为每条代表视频保存原视频、FunASR 带时间戳结果和校正版逐字稿。下载失败时先尝试同一公开链接的合法替代获取方式；仍失败则换用下一条同排名候选并在清单中注明。
3. **形成证据表**：每个可用片段只保留一条标准记录：逐字文案、起止时间码、视频链接、视频 ID、本地素材路径、指标和主题标签。
4. **分析与写报告**：读取 [分析与报告标准](references/analysis-report.md)。合并非重点视频，只对代表视频逐条深挖。
5. **搭建原声脚本**：读取 [脚本与粗剪标准](references/scripts-and-roughcuts.md)。口播句只能来自证据表，允许删减完整句群和重排，不得改写成新口播。
6. **生成剪辑清单并粗剪**：把每条脚本落成 EDL JSON，运行：
   `python scripts/build_roughcut.py <剪辑清单.json> <输出.mp4>`
7. **一次性验收并交付**：检查链接/时间码/逐字稿一致性、脚本逻辑、首句顺序、音画流、成片时长、9:16 画面和明显长静音。只修复已发现的问题，不重新走完整流程。

## 不可妥协的证据规则

- 所有具体文案旁必须同时给出 **原视频链接 + 源视频时间码**。
- 金句榜来自真实逐字字幕。先按语义合并近义重复，再统计“覆盖视频数”和“出现次数”；同一视频连续重复不得虚增频次。
- 报告中的高转化结论只有在销量/订单/销售额数据支持时成立；否则写“高互动”或“高传播”。
- 营销脚本没有可用的原声促单句时，不得自创口播。可将营销意图放在非口播的封面、书卡或结尾卡，并明确标注为后期包装。
- 全部概念用中文：用“开场抓力、情绪推进、信任建立、观点转折、转化动作”，不写 Hook、Emotion、CTA 等英文术语。

## 停止条件

- 缺少真实链接或视频文件：请求补充，停止字幕与粗剪环节。
- 目标平台要求登录：只在用户授权后使用已登录浏览器；不得绕过权限。
- 无法下载某条视频：记录失败原因并替换样本；不得无限重试。
- 音频不清或 FunASR 低置信：标为“需人工听校”，不得把不确定句子列入金句或直接用于成片。
- 用户只要报告或脚本时，在对应阶段停止，不擅自制作视频。

## 交付清单

- 代表视频清单（含筛选理由、指标、链接、转写状态）
- 分析报告 DOCX（含金句 Top 5/10、结构与主题、证据引用、其余视频合并观察）
- 混剪脚本/EDL（逐句原文、输出时间线、源时间码、链接、营销属性）
- 每条脚本对应的 1080×1920 H.264/AAC 粗剪 MP4
- 简短质量说明：成功/替换/需人工复核的视频数量，以及任何未完成项
