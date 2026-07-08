# Asset Seeker — 在线创作素材搜索引擎

[English](README.md)

跨多个平台搜索免费商用创作素材 — **图片、插画、图标、视频空镜、背景音乐、音效、字体** — 全部经过版权审核，标注授权协议和国内可访问性。专为内容创作者设计，让你专注于创作而非找素材和躲版权。

**支持工具：** [Claude Code](https://claude.ai/code) · [OpenClaw](https://openclaw.ai/) (ClawHub) · [OpenCode](https://opencode.ai/) · [Codex](https://openai.com/index/introducing-codex/) — 任何支持 SKILL.md 的 coding agent

> 本技能基于 [创作者素材库大盘点](https://space.bilibili.com/441831884) 视频的完整调研，每一条来源都核验过版权协议、国内直连情况和 API 可用性。

## 功能特点

- **7 大类素材搜索** — 图片、图标、视频、音乐、音效、字体、插画
- **API 直搜** — 对接 Pexels、Unsplash、Pixabay、Iconify、Freesound、Google Fonts 官方接口
- **图标搜索零门槛** — Iconify 无需任何 API Key，200+ 图标集 30 万+ 图标直接搜
- **版权即显示** — 每条结果标注授权协议（CC0 / MIT / Apache / CC-BY）
- **国内可访问性** — 每个来源标注国内能否直连
- **双格式输出** — JSON 给 agent 消费，text 格式人类可读
- **极简依赖** — Python 标准库即用，不需要 pip install

## 安装

**Claude Code（全局）：**
```bash
git clone https://github.com/Agents365-ai/assetSeeker.git ~/.claude/skills/assetSeeker
```

**Claude Code（仅当前项目）：**
```bash
git clone https://github.com/Agents365-ai/assetSeeker.git .claude/skills/assetSeeker
```

**OpenClaw：**
```bash
git clone https://github.com/Agents365-ai/assetSeeker.git skills/assetSeeker
```

**SkillsMP：** 在 [skillsmp.com](https://skillsmp.com) 搜索 `assetSeeker`，一键安装。

## 环境要求

| 软件 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 搜索脚本 |

无需额外 pip 包 — 仅使用 Python 标准库（`urllib`、`json`）。

## 快速开始

告诉你的 coding agent：

> "帮我找一张 mountain sunset 的照片，做封面用"

agent 会自动搜索 Pexels（如果你设了 key），展示结果并附版权信息。

### 配置 API Key

```bash
# 最推荐 — 覆盖图片+视频 （pexels.com/api 免费申请，约 2 分钟）
export PEXELS_API_KEY="your-key"

# 可选：更多图源
export UNSPLASH_ACCESS_KEY="your-key"
export PIXABAY_API_KEY="your-key"

# 可选：音效
export FREESOUND_API_KEY="your-key"

# 可选：字体
export GOOGLE_FONTS_API_KEY="your-key"
```

**没有任何 API Key？** 图标搜索通过 Iconify 零配置直接可用（30 万+ 图标）。

### 常用命令

```bash
# 查看所有来源和 Key 配置状态
python3 skills/assetSeeker/scripts/seek_assets.py sources

# 搜图片（自动用 Pexels + Unsplash + Pixabay）
python3 skills/assetSeeker/scripts/seek_assets.py search photo "mountain sunset"

# 搜图标（无需 Key！始终可用）
python3 skills/assetSeeker/scripts/seek_assets.py search icon "laptop"

# 搜视频空镜
python3 skills/assetSeeker/scripts/seek_assets.py search video "city traffic"

# 搜音效
python3 skills/assetSeeker/scripts/seek_assets.py search sfx "whoosh"

# 搜字体
python3 skills/assetSeeker/scripts/seek_assets.py search font "bold sans"

# 人类可读格式
python3 skills/assetSeeker/scripts/seek_assets.py search photo "cat" --format text

# 限定来源
python3 skills/assetSeeker/scripts/seek_assets.py search photo "sunset" --source pexels

# 限定方向
python3 skills/assetSeeker/scripts/seek_assets.py search photo "portrait" --orientation portrait

# 下载单个素材
python3 skills/assetSeeker/scripts/seek_assets.py download <url> -o output.jpg
```

## 支持的来源

### 图片

| 来源 | API | 免费额度 | 授权 |
|------|-----|---------|------|
| **Pexels** | ✅ 图+视频 | 200次/时、2万/月 | 免署名 |
| **Unsplash** | ✅ 图片 | 50次/时（demo） | 建议署名 |
| **Pixabay** | ✅ 图+视频 | 免费 | 免署名 |

### 图标

| 来源 | API | 免费额度 | 授权 |
|------|-----|---------|------|
| **Iconify** | ✅ 开放API | **无限，免注册** | 各图标集自定（MIT/Apache/CC） |

### 视频空镜

| 来源 | API | 免费额度 | 授权 |
|------|-----|---------|------|
| **Pexels Video** | ✅ | 200次/时、2万/月 | 免署名 |
| **Pixabay Video** | ✅ | 免费 | 免署名 |

### 音效/音乐

| 来源 | API | 免费额度 | 授权 |
|------|-----|---------|------|
| **Freesound** | ✅ | 免费（需token） | 逐条自定 |

### 字体

| 来源 | API | 免费额度 | 授权 |
|------|-----|---------|------|
| **Google Fonts** | ✅ 元数据API | 免费 | OFL |

> 无 API 的来源（插画、音乐、emoji、PPT 模板等），详见 `references/asset_catalog.md` 完整精选目录。

## 环境变量

```bash
# 图片+视频（推荐首先配置）
export PEXELS_API_KEY="your-key"          # pexels.com/api

# 图片（可选）
export UNSPLASH_ACCESS_KEY="your-key"     # unsplash.com/developers
export PIXABAY_API_KEY="your-key"         # pixabay.com/api/docs

# 音效（可选）
export FREESOUND_API_KEY="your-key"       # freesound.org/apiv2/apply
export FREESOUND_TOKEN="your-oauth-token" # 提高限额

# 字体（可选）
export GOOGLE_FONTS_API_KEY="your-key"    # console.cloud.google.com

# 图标（可选 — 仅 Noun Project 需要）
export NOUN_PROJECT_KEY="your-key"
export NOUN_PROJECT_SECRET="your-secret"
```

## 典型使用场景

1. **做视频封面** — "找一张科技感、深色背景的横版照片" → `search photo "technology dark" --orientation landscape`
2. **PPT 配图** — "搜个 laptop 图标，要 MIT 协议的描边风格" → `search icon "laptop"`（过滤 lucide / tabler）
3. **视频 B-roll** — "找城市航拍空镜" → `search video "drone city"`
4. **转场音效** — "搜 whoosh 音效" → `search sfx "whoosh"`
5. **标题字体** — "有没有粗体非衬线中文字体" → `search font "sans bold"`
6. **没有 key 时** — "至少帮我搜图标" → Iconify 零配置直接用

## 相关技能

- **video-podcast-maker** — 视频制作流水线，本技能为其供素材
- **imagenCN** — 当真实照片不适用时，AI 生图补充

## 👤 作者

**Agents365-ai**

- B站: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai

## 📄 开源协议

[CC BY-NC 4.0](LICENSE)
