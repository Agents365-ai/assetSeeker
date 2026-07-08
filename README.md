# Asset Seeker — Online Creative Asset Search

[中文文档](README_CN.md)

Search free commercial-use creative assets across the internet — **photos, illustrations, icons, video footage, music, sound effects, and fonts** — from curated, license-vetted sources. Built for content creators who need high-quality assets without licensing headaches.

**Supported tools:** [Claude Code](https://claude.ai/code) · [OpenClaw](https://openclaw.ai/) (ClawHub) · [OpenCode](https://opencode.ai/) · [Codex](https://openai.com/index/introducing-codex/) — any coding agent that supports SKILL.md

## Features

- **7 asset types** — Photos, Icons, Videos, Music, Sound Effects, Fonts, Illustrations
- **API-powered search** — Pexels, Unsplash, Pixabay, Iconify, Freesound, Google Fonts
- **Zero-config icon search** — Iconify works without any API key (200+ sets, 300k+ icons)
- **License-aware** — Every result shows license type (CC0, MIT, Apache, etc.)
- **China accessibility** — Each source marked for Great Firewall accessibility
- **Human + machine output** — JSON for agents, text format for reading
- **Minimal dependencies** — Python stdlib only; `pip install requests` for best results

## Installation

**Claude Code (global):**
```bash
git clone https://github.com/Agents365-ai/assetSeeker.git ~/.claude/skills/assetSeeker
```

**Claude Code (project only):**
```bash
git clone https://github.com/Agents365-ai/assetSeeker.git .claude/skills/assetSeeker
```

**OpenClaw:**
```bash
git clone https://github.com/Agents365-ai/assetSeeker.git skills/assetSeeker
```

**SkillsMP:** Search `assetSeeker` on [skillsmp.com](https://skillsmp.com) for one-click install.

## Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.8+ | Search scripts |

No pip packages required — uses Python standard library (`urllib`, `json`).

## Quick Start

Tell your coding agent:

> "Find me a photo of mountains for a video thumbnail"

The agent will search across Pexels, Unsplash, and Pixabay (whichever has API keys set) and present results with licensing info.

### Setup API Keys

```bash
# At minimum — covers photos + videos (get at pexels.com/api — free, ~2 min)
export PEXELS_API_KEY="your-key"

# Optional: more photo sources
export UNSPLASH_ACCESS_KEY="your-key"
export PIXABAY_API_KEY="your-key"

# Optional: sound effects
export FREESOUND_API_KEY="your-key"

# Optional: fonts
export GOOGLE_FONTS_API_KEY="your-key"
```

**No API keys?** Icon search works without any key via Iconify (300k+ icons, 200+ sets).

### Common Commands

```bash
# Check available sources and API key status
python3 skills/assetSeeker/scripts/seek_assets.py sources

# Search photos
python3 skills/assetSeeker/scripts/seek_assets.py search photo "mountain sunset"

# Search icons (always works, no key needed)
python3 skills/assetSeeker/scripts/seek_assets.py search icon "laptop"

# Search videos
python3 skills/assetSeeker/scripts/seek_assets.py search video "city traffic"

# Search sound effects
python3 skills/assetSeeker/scripts/seek_assets.py search sfx "whoosh"

# Search fonts
python3 skills/assetSeeker/scripts/seek_assets.py search font "bold sans"

# Human-readable format
python3 skills/assetSeeker/scripts/seek_assets.py search photo "cat" --format text

# Download an asset
python3 skills/assetSeeker/scripts/seek_assets.py download <url> -o output.jpg
```

## Supported Sources

### Photos

| Source | API | Free Tier | License |
|--------|-----|-----------|---------|
| **Pexels** | ✅ Photo + Video | 200 req/hr, 20k/month | No attribution |
| **Unsplash** | ✅ Photo | 50 req/hr (demo) | Attribution appreciated |
| **Pixabay** | ✅ Photo + Video | Free | No attribution |

### Icons

| Source | API | Free Tier | License |
|--------|-----|-----------|---------|
| **Iconify** | ✅ Open API | **Unlimited, no registration** | Per-set (MIT/Apache/CC) |

### Video Footage

| Source | API | Free Tier | License |
|--------|-----|-----------|---------|
| **Pexels Video** | ✅ | 200 req/hr, 20k/month | No attribution |
| **Pixabay Video** | ✅ | Free | No attribution |

### Sound Effects & Music

| Source | API | Free Tier | License |
|--------|-----|-----------|---------|
| **Freesound** | ✅ | Free with token | Per-item |

### Fonts

| Source | API | Free Tier | License |
|--------|-----|-----------|---------|
| **Google Fonts** | ✅ Metadata API | Free | OFL |

> For sources without APIs (illustrations, music, emoji, PPT templates), see `references/asset_catalog.md` for the complete curated catalog.

## Environment Variables

```bash
# Photo & Video
export PEXELS_API_KEY="your-key"          # pexels.com/api

# Photo (optional)
export UNSPLASH_ACCESS_KEY="your-key"     # unsplash.com/developers
export PIXABAY_API_KEY="your-key"         # pixabay.com/api/docs

# Sound Effects (optional)
export FREESOUND_API_KEY="your-key"       # freesound.org/apiv2/apply
export FREESOUND_TOKEN="your-oauth-token" # For higher rate limits

# Fonts (optional)
export GOOGLE_FONTS_API_KEY="your-key"    # console.cloud.google.com

# Icons (optional — only for Noun Project)
export NOUN_PROJECT_KEY="your-key"
export NOUN_PROJECT_SECRET="your-secret"
```

## Related Skills

- **video-podcast-maker** — Video production pipeline that consumes these assets
- **imagenCN** — AI image generation when real photos don't fit

## Author

**Agents365-ai**

- Bilibili: https://space.bilibili.com/441831884
- GitHub: https://github.com/Agents365-ai

## License

[CC BY-NC 4.0](LICENSE)
