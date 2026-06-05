# 抖音/小红书收藏 → Obsidian 素材卡

把抖音、小红书**收藏夹里的视频/图文**，自动提取成结构化的 Obsidian 素材卡，沉淀进你的知识库供 LLM（Claude / Codex / ChatGPT）使用。

> 这是一个**聚焦的工具项目**：只做"社交平台收藏 → 素材卡"这一件事。

## 解决什么问题

抖音、小红书的收藏夹会越攒越多、看过就忘。这套工具把每条收藏变成一张带**视频内容总结 + 文案 + 标签 + 来源链接**的 Markdown 卡片，让收藏真正可检索、可复用、可喂给 AI 做选题和创作。

## 核心方法（实测要点）

1. **在已登录的浏览器里操作收藏页**（路径：抖音「我的」→收藏→视频）。
   - ⚠️ 不要用 `douyin.com/video/{id}` 网址直接打开单条——会被重定向到推荐流，打开的不是你的收藏。
2. **点开收藏卡片 → 右侧「问AI / 视频总结」**：平台自带的 AI 会生成结构化内容总结，这是做素材卡的最佳来源。
3. 也可用 `tools/transcribe_social.py` 做**本地语音转写**兜底（yt-dlp 下载 + ffmpeg 抽音轨 + faster-whisper 转字幕）。
4. **用视频ID台账去重**（`docs/抖音深挖-进度台账示例.md`）：支持断点续传，并能从"清积压"自然过渡到"只处理新增"的持续监控。
5. **用关键词规则给收藏分类**（`docs/抖音收藏-用途分类规则.md`）：`素材 / 待看 / 娱乐 / 广告`，只对"素材"深挖建卡，避免把影视解说、追剧、广告也做成卡。
6. 支持**排除作者**（如你自己的账号），不重复处理。

## 目录

```
skills/social-collect/SKILL.md   # 收藏入库技能（Claude/Cowork 可直接调用）
tools/transcribe_social.py       # 视频转写脚本（yt-dlp + ffmpeg + faster-whisper）
docs/
  抖音收藏-用途分类规则.md         # 用途分类的关键词规则（可调）
  抖音深挖-进度台账示例.md         # 断点续传台账示例（按视频ID去重）
examples/                         # 由公开短视频生成的素材卡样例
```

## 依赖

```bash
pip install --break-system-packages yt-dlp faster-whisper   # ffmpeg 需另装
```
浏览器侧需要能在已登录会话里操作收藏页（如 Claude in Chrome 或手动配合）。

## 素材卡长这样

见 `examples/`。每张卡含 frontmatter（平台/链接/作者/收藏日期）+ 视频总结 + 我的判断 + 可用于哪个稿件。

## 致谢与许可

知识沉淀的思路受 Andrej Karpathy 的 [llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 启发。欢迎 fork、提 issue、一起迭代。

MIT License.
