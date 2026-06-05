#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音 / 小红书 收藏内容 → Obsidian 素材卡。

用法：
    python3 transcribe_social.py --url "<分享链接>" [--note "我为什么收藏它"]
    python3 transcribe_social.py --file "/path/to/video.mp4" [--title "标题"] [--note "..."]

流程：
    1) 有 --url：用 yt-dlp 下载视频 + 抓取标题/作者/文案/标签等元数据。
    2) ffmpeg 抽音轨 → faster-whisper 转中文字幕文本。
    3) 套用「素材卡」frontmatter，写入 inbox（待 LLM 分拣）。

注意：
    - 沙盒未登录你的账号，只能处理“公开可访问”的链接；私密/登录可见内容请改用 --file。
    - 抖音链接带签名，偶有失败属正常，失败会回退为“仅元数据/仅链接”卡片。
"""
import argparse, json, os, re, subprocess, sys, datetime, tempfile, glob

INBOX = os.environ.get(
    "OBS_INBOX",
    "/sessions/kind-quirky-fermi/mnt/光的本/LLM知识库系统/inbox",
)
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")  # tiny/base/small/medium


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def safe_name(s, maxlen=60):
    s = re.sub(r"[\\/:*?\"<>|\n\r\t]", " ", s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return (s or "未命名")[:maxlen]


def fetch(url, workdir):
    """用 yt-dlp 下载视频并取元数据。返回 (meta dict, video_path or None)。"""
    meta = {}
    # 先取元数据（不下载），失败也不致命
    info = run(["python3", "-m", "yt_dlp", "-J", "--no-warnings", url])
    if info.returncode == 0 and info.stdout.strip():
        try:
            j = json.loads(info.stdout)
            meta = {
                "title": j.get("title") or j.get("description", "")[:40],
                "uploader": j.get("uploader") or j.get("creator") or "",
                "description": j.get("description") or "",
                "tags": j.get("tags") or [],
                "webpage_url": j.get("webpage_url") or url,
                "duration": j.get("duration"),
            }
        except Exception:
            pass
    # 下载视频
    out_tmpl = os.path.join(workdir, "video.%(ext)s")
    dl = run(["python3", "-m", "yt_dlp", "--no-warnings", "-o", out_tmpl, url])
    vids = glob.glob(os.path.join(workdir, "video.*"))
    vids = [v for v in vids if not v.endswith(".json")]
    return meta, (vids[0] if vids and dl.returncode == 0 else None)


def transcribe(video_path, workdir):
    """ffmpeg 抽音轨 → faster-whisper。返回转写文本或 None。"""
    audio = os.path.join(workdir, "audio.wav")
    a = run(["ffmpeg", "-y", "-i", video_path, "-ar", "16000", "-ac", "1", audio])
    if a.returncode != 0 or not os.path.exists(audio):
        return None
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return "[转写引擎 faster-whisper 尚未安装，请先 pip install faster-whisper]"
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio, language="zh", vad_filter=True)
    return "\n".join(seg.text.strip() for seg in segments).strip() or None


def platform_of(url):
    if not url:
        return "本地视频"
    if "douyin" in url or "iesdouyin" in url:
        return "抖音"
    if "xiaohongshu" in url or "xhslink" in url:
        return "小红书"
    return "其他"


def build_card(title, platform, url, uploader, desc, tags, transcript, note):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    tagline = " ".join("#" + t for t in (tags or [])[:10])
    fm = [
        "---",
        "类型: source",
        "状态: raw",
        "领域:",
        f"来源: {platform}",
        f"平台: {platform}",
        f"链接: {url or ''}",
        f"作者: {uploader or ''}",
        f"收藏日期: {today}",
        f"已转写: {'是' if transcript else '否'}",
        f"创建时间: {now}",
        "---",
        "",
        f"# {title}",
        "",
        "## 来源",
        f"- 平台：{platform}",
        f"- 作者：{uploader or '未知'}",
        f"- 链接：{url or '（本地视频）'}",
        f"- 标签：{tagline or '无'}",
        "",
        "## 文案/简介",
        (desc.strip() or "（无）"),
        "",
        "## 视频转写",
        (transcript or "（未转写或转写失败）"),
        "",
        "## 我的判断",
        (note or ""),
        "",
        "## 可用于",
        "- [[光的房间稿件/稿件索引]]",
        "",
    ]
    return "\n".join(fm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--file")
    ap.add_argument("--title")
    ap.add_argument("--note", default="")
    ap.add_argument("--inbox", default=INBOX)
    args = ap.parse_args()
    if not args.url and not args.file:
        sys.exit("需要 --url 或 --file")

    with tempfile.TemporaryDirectory() as workdir:
        meta, video = {}, args.file
        if args.url:
            meta, video = fetch(args.url, workdir)
        title = args.title or meta.get("title") or "社交收藏"
        transcript = transcribe(video, workdir) if video else None
        card = build_card(
            title=safe_name(title),
            platform=platform_of(args.url),
            url=meta.get("webpage_url", args.url),
            uploader=meta.get("uploader", ""),
            desc=meta.get("description", ""),
            tags=meta.get("tags", []),
            transcript=transcript,
            note=args.note,
        )

    os.makedirs(args.inbox, exist_ok=True)
    fname = f"{datetime.datetime.now():%Y%m%d-%H%M%S}-{safe_name(title,30)}.md"
    path = os.path.join(args.inbox, fname)
    with open(path, "w", encoding="utf-8") as f:
        f.write(card)
    print("已写入：", path)
    print("转写：", "成功" if transcript and not transcript.startswith("[") else "无/失败")


if __name__ == "__main__":
    main()
