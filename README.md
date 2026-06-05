# Obsidian LLM-Wiki 框架

一套让 LLM（Claude / Codex / ChatGPT 等）持续维护 Obsidian 知识库的**规则 + 模板 + 技能 + 工作流**。
灵感来自 Andrej Karpathy 的 [llm-wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：LLM 不只是检索文件，而是持续构建并维护一个会增长、会交叉引用、会更新旧结论的 Markdown 知识库。

> 本仓库只含**可复用的框架与方法**，不含任何作者的私人笔记、资料或收藏内容。

## 核心理念

- **三层结构**：`raw/`（原始证据层，只读）→ LLM 编译的 `wiki/`（结构化知识层）→ schema（`AGENTS.md` / `CLAUDE.md`，告诉 LLM 怎么维护）。
- **inbox 是单层平盆收件箱**：分不清就无脑丢进去，分类是 AI 的工作，不是录入者的工作。
- **index.md + log.md**：内容索引 + 时间线日志（`## [YYYY-MM-DD] action | title`）。
- 人负责记录、判断、取舍、创作；LLM 负责整理、归并、交叉引用、查漏补缺、维护索引和日志。

## 目录

```
AGENTS.md                  # 所有 AI 的入口规则（通用）
CLAUDE.md                  # Claude 专用入口（与 AGENTS 一致）
docs/
  知识库维护规则.md         # 完整规则：结构、页面类型、工作流、质量规则
  inbox说明.md             # 单层平盆收件箱的用法
  抖音收藏-用途分类规则.md   # 社交收藏的用途分类规则（素材/待看/娱乐/广告）
  抖音深挖-进度台账示例.md   # 断点续传台账示例（按视频ID去重）
模板/                       # Obsidian 笔记模板（Templater 语法）
  灵感卡 / 素材卡 / 知识卡 / 主题页 / 稿件项目 / 历史稿件索引卡 / 片段卡 ...
skills/social-collect/      # 把抖音/小红书收藏转成素材卡的技能
tools/transcribe_social.py  # 视频转写脚本（yt-dlp + ffmpeg + faster-whisper）
examples/                   # 由公开短视频生成的素材卡样例
```

## 工作流（见 docs/知识库维护规则.md）

- **capture**：快速记录灵感，不因分类犹豫而中断。
- **ingest**：资料入库 → 判断去向（raw/知识管理/wiki/queries）→ 更新索引和日志。
- **capture-social**：把抖音/小红书收藏夹的视频/图文转成素材卡（两段式：浏览器抓取 + 可选本地转写）。
- **query**：基于知识库提问，好答案回填成新页面。
- **lint**：定期体检——找断链、孤立页、被新资料推翻的旧结论。

## social-collect 技能要点

把社交平台收藏沉淀进知识库的实战方法：

1. 用浏览器在**已登录**的收藏页操作（不要用 `video/{id}` 网址直开单条——会被重定向到推荐流）。
2. 点开卡片 → 平台自带的「AI 视频总结」是做素材卡最佳来源；也可用 `tools/transcribe_social.py` 本地语音转写兜底。
3. 用**视频ID台账**去重，支持断点续传与"只处理新增"的持续监控。
4. 用关键词规则把收藏分成 `素材 / 待看 / 娱乐 / 广告`，只对"素材"深挖建卡。

## 怎么用

1. 把 `AGENTS.md`、`CLAUDE.md`、`模板/` 放到你的 Obsidian vault 根目录。
2. 让你的 LLM 先读 `AGENTS.md` 和 `docs/知识库维护规则.md`，按需调整规则与目录命名。
3. 需要社交收藏入库时，参考 `skills/social-collect` 和 `tools/transcribe_social.py`。
4. 和你的 LLM 共同演进这套 schema —— 这正是 Karpathy 模式的精神。

## 致谢

- 模式来源：Andrej Karpathy, *llm-wiki*。
- 本框架由用户与 AI 在实际使用中打磨而成，欢迎 fork、迭代、提 issue。

## License

MIT
