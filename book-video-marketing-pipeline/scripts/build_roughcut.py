#!/usr/bin/env python3
"""Build a portrait hard-cut MP4 from a timestamped JSON edit decision list."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def seconds(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    parts = text.split(":")
    try:
        if len(parts) == 3:
            hours, minutes, secs = parts
            return int(hours) * 3600 + int(minutes) * 60 + float(secs)
        if len(parts) == 2:
            minutes, secs = parts
            return int(minutes) * 60 + float(secs)
        return float(text)
    except ValueError as exc:
        raise ValueError(f"无效时间码：{value}") from exc


def probe(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def validate_segments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_segments = payload.get("segments")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ValueError("EDL 必须包含非空 segments 数组。")
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_segments, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"第 {index} 个片段不是对象。")
        source = Path(str(raw.get("source_path", ""))).expanduser().resolve()
        if not source.is_file():
            raise ValueError(f"第 {index} 个片段素材不存在：{source}")
        start = seconds(raw.get("start"))
        end = seconds(raw.get("end"))
        if start < 0 or end <= start:
            raise ValueError(f"第 {index} 个片段时间无效：{start}–{end}")
        metadata = probe(source)
        duration = float(metadata.get("format", {}).get("duration", 0))
        stream_types = {stream.get("codec_type") for stream in metadata.get("streams", [])}
        if "video" not in stream_types or "audio" not in stream_types:
            raise ValueError(f"第 {index} 个片段必须同时包含音频和视频流：{source}")
        if end > duration + 0.05:
            raise ValueError(f"第 {index} 个片段结束时间 {end:.3f}s 超过素材时长 {duration:.3f}s")
        validated.append({"source": source, "start": start, "duration": end - start})
    return validated


def build_command(segments: list[dict[str, Any]], output: Path, overwrite: bool) -> list[str]:
    command = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y" if overwrite else "-n"]
    for segment in segments:
        command += [
            "-ss",
            f"{segment['start']:.3f}",
            "-t",
            f"{segment['duration']:.3f}",
            "-i",
            str(segment["source"]),
        ]

    filters: list[str] = []
    concat_inputs: list[str] = []
    for index in range(len(segments)):
        filters.append(
            f"[{index}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=30,format=yuv420p[v{index}]"
        )
        filters.append(f"[{index}:a]aresample=48000:async=1:first_pts=0[a{index}]")
        concat_inputs.append(f"[v{index}][a{index}]")
    filters.append("".join(concat_inputs) + f"concat=n={len(segments)}:v=1:a=1[v][a]")

    command += [
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(output),
    ]
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="根据 EDL JSON 生成 1080×1920 原声硬切粗剪。")
    parser.add_argument("edl", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的输出文件")
    parser.add_argument("--dry-run", action="store_true", help="只验证并打印 FFmpeg 命令")
    args = parser.parse_args()

    if not args.edl.is_file():
        parser.error(f"EDL 不存在：{args.edl}")
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise SystemExit(f"缺少 {binary}，无法生成粗剪。")
    with args.edl.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    segments = validate_segments(payload)
    output = args.output.expanduser().resolve()
    if output.exists() and not args.overwrite and not args.dry_run:
        raise SystemExit(f"输出已存在：{output}。如需覆盖请加 --overwrite。")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = build_command(segments, output, args.overwrite)
    if args.dry_run:
        print(json.dumps(command, ensure_ascii=False))
        return 0
    subprocess.run(command, check=True)
    metadata = probe(output)
    duration = float(metadata.get("format", {}).get("duration", 0))
    print(f"粗剪完成：{output}（{duration:.2f} 秒）")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(str(exc))

