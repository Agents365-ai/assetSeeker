# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language

All code, comments, and documentation must be in English (README_CN.md is the sole exception — it is the Chinese companion to README.md).

## Git Commits

Do NOT add "Co-Authored-By: Claude" to commit messages.

## What This Is

A Claude Code skill for searching free commercial-use creative assets online across curated, license-vetted sources. Covers 7 asset types: photos, illustrations, icons, video footage, music, sound effects, and fonts.

Backed by the research from the "创作者素材库大盘点" Bilibili video — every source has been verified for license terms, China accessibility, and API availability.

## Key APIs

- **Pexels** — Photo + Video, 200 req/hr (env: `PEXELS_API_KEY`)
- **Unsplash** — Photo, 50 req/hr (env: `UNSPLASH_ACCESS_KEY`)
- **Pixabay** — Photo + Video, free (env: `PIXABAY_API_KEY`)
- **Iconify** — Icons, unlimited, NO key needed
- **Freesound** — Sound effects + music, OAuth (env: `FREESOUND_API_KEY`)
- **Google Fonts** — Fonts, free (env: `GOOGLE_FONTS_API_KEY`)

## Project Structure

```
assetSeeker/
├── SKILL.md              # Main documentation (in skills/assetSeeker/)
├── README.md             # English README
├── README_CN.md          # Chinese README
├── CLAUDE.md             # This file
├── LICENSE               # CC BY-NC 4.0
├── .gitignore
└── skills/
    └── assetSeeker/
        ├── SKILL.md
        ├── references/
        │   └── asset_catalog.md   # Complete curated source catalog
        └── scripts/
            └── seek_assets.py     # Main CLI — search, sources, download
```

## Key Commands

```bash
# From repo root
python3 skills/assetSeeker/scripts/seek_assets.py sources
python3 skills/assetSeeker/scripts/seek_assets.py search photo "keyword"
python3 skills/assetSeeker/scripts/seek_assets.py search icon "keyword"
python3 skills/assetSeeker/scripts/seek_assets.py search video "keyword"
python3 skills/assetSeeker/scripts/seek_assets.py search sfx "keyword"
python3 skills/assetSeeker/scripts/seek_assets.py search font "keyword"
python3 skills/assetSeeker/scripts/seek_assets.py download <url> -o <path>
```

## Design Principles

- **Stdlib-first** — Uses only Python standard library (`urllib`, `json`, `argparse`, `pathlib`). No pip install needed.
- **Graceful degradation** — When an API key is missing, that source is skipped with a clear error message. Iconify always works.
- **JSON-first output** — Default is JSON for agent consumption; `--format text` for humans.
- **Single-file CLI** — Everything in `seek_assets.py`; modular by function, not by file.
