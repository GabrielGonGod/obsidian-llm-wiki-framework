---
name: social-collect
description: 把抖音、小红书收藏夹里的视频/图文转成 Obsidian 素材卡。用于：抖音收藏、小红书收藏、社交平台素材入库、视频转字幕、视频转写、把短视频内容整理进知识库。
---

# social-collect：社交平台收藏 → Obsidian 素材卡

把抖音 / 小红书收藏夹里的内容抓进知识库。文字（标题、文案、标签）直接读，视频用语音转写补齐字幕，统一落成「素材卡」写入 `LLM知识库系统/inbox/`，再按 ingest 流程分拣。

## 两段式架构（重要）

沙盒**没有登录**用户的抖音/小红书账号，登录态只在用户 Mac 的浏览器里。所以：

1. **抓取（Chrome，已登录）**：用 Claude in Chrome 打开 douyin.com / xiaohongshu.com 的收藏页，逐条读取标题、作者、文案/简介、标签、视频链接。这一步拿“文字层”。
2. **转写（沙盒）**：把视频链接或本地视频交给转写脚本，yt-dlp 下载 → ffmpeg 抽音轨 → faster-whisper 转中文字幕 → 生成素材卡。

## 工具

脚本：`LLM知识库系统/tools/transcribe_social.py`（沙盒路径 `/sessions/<id>/mnt/光的本/LLM知识库系统/tools/`）

```bash
# 自动路线：给链接
python3 transcribe_social.py --url "<抖音/小红书分享链接>" --note "为什么收藏"

# 兜底路线：给本地视频文件（私密/登录可见内容，或链接下载失败时）
python3 transcribe_social.py --file "/path/to/video.mp4" --title "标题" --note "..."
```

依赖（沙盒首次需安装）：`pip3 install --break-system-packages yt-dlp faster-whisper`，ffmpeg 已自带。
环境变量可选：`WHISPER_MODEL`（tiny/base/small/medium，默认 small）、`OBS_INBOX`（输出目录）。

## 操作流程

1. 确认要处理哪个平台、哪一批收藏（最近 N 条 / 某个收藏夹）。
2. 用 Chrome 打开收藏页，读取条目；对每条拿到链接和文案。
3. 逐条调用脚本（自动路线优先；抖音签名失败则提示用户保存视频走 --file）。
4. 产出素材卡进 inbox 后，按 `LLM知识库系统/AGENTS.md` 的 ingest / capture-social 流程分发到 `光的房间稿件/素材/` 或 `灵感库/`。
5. 在 `LLM知识库系统/log.md` 追加一条 `## [日期] capture-social | 平台 N 条`。

## 注意

- 仅处理用户本人收藏、用于个人学习与创作参考；保留来源链接和作者，便于追溯与合规。
- 转写文本可能有错别字，标题/数据等关键信息以页面原文为准。
- 抖音视频地址带签名、可能需登录，下载失败属正常，回退为“仅元数据/仅链接”卡片或改用 --file。
