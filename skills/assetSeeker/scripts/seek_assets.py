#!/usr/bin/env python3
"""Asset Seeker — Search free commercial-use creative assets online.

Queries Pexels, Unsplash, Pixabay, Iconify, Freesound, and Google Fonts
through their public APIs. Iconify works without any API key.

Usage:
    python seek_assets.py sources                    # List sources + key status
    python seek_assets.py search photo "mountain"    # Search photos
    python seek_assets.py search icon "laptop"       # Search icons
    python seek_assets.py search video "city"        # Search video footage
    python seek_assets.py search sfx "whoosh"        # Search sound effects
    python seek_assets.py search font "bold sans"    # Search fonts
    python seek_assets.py download <url> -o out.jpg  # Download asset
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SOURCE_CONFIG = {
    "pexels": {
        "label": "Pexels",
        "types": ["photo", "video"],
        "base": "https://api.pexels.com",
        "env_key": "PEXELS_API_KEY",
        "free_tier": "200 req/hr, 20k/month",
        "china_access": True,
        "license": "No attribution required",
    },
    "unsplash": {
        "label": "Unsplash",
        "types": ["photo"],
        "base": "https://api.unsplash.com",
        "env_key": "UNSPLASH_ACCESS_KEY",
        "free_tier": "50 req/hr (demo)",
        "china_access": True,
        "license": "Attribution appreciated",
    },
    "pixabay": {
        "label": "Pixabay",
        "types": ["photo", "video"],
        "base": "https://pixabay.com/api",
        "env_key": "PIXABAY_API_KEY",
        "free_tier": "Free",
        "china_access": True,
        "license": "No attribution required",
        "note": "Music has NO API — web download only",
    },
    "iconify": {
        "label": "Iconify",
        "types": ["icon"],
        "base": "https://api.iconify.design",
        "env_key": None,  # No key needed
        "free_tier": "Unlimited, no registration",
        "china_access": True,
        "license": "Varies by icon set (mostly MIT / CC-BY / Apache)",
    },
    "freesound": {
        "label": "Freesound",
        "types": ["sfx", "music"],
        "base": "https://freesound.org/apiv2",
        "env_key": "FREESOUND_API_KEY",
        "free_tier": "Free with OAuth token",
        "china_access": True,
        "license": "Check per item (mostly CC0 / CC-BY)",
    },
    "google-fonts": {
        "label": "Google Fonts",
        "types": ["font"],
        "base": "https://www.googleapis.com/webfonts/v1",
        "env_key": "GOOGLE_FONTS_API_KEY",
        "free_tier": "Free",
        "china_access": True,
        "license": "OFL (Open Font License)",
    },
    "noun-project": {
        "label": "Noun Project",
        "types": ["icon"],
        "base": "https://api.thenounproject.com/v2",
        "env_key": "NOUN_PROJECT_KEY",
        "free_tier": "5,000/month",
        "china_access": True,
        "license": "Per-icon license",
    },
}

# Maps user-facing type -> list of source names in priority order
TYPE_TO_SOURCES: dict[str, list[str]] = {
    "photo": ["pexels", "unsplash", "pixabay"],
    "icon": ["iconify", "noun-project"],
    "video": ["pexels", "pixabay"],
    "sfx": ["freesound"],
    "music": ["freesound"],
    "font": ["google-fonts"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_key(source: str) -> str | None:
    """Get API key for a source from env var, or None."""
    conf = SOURCE_CONFIG.get(source, {})
    env_key = conf.get("env_key")
    if not env_key:
        return None  # source doesn't need one
    return os.environ.get(env_key)


def _api_get(url: str, headers: dict | None = None) -> Any:
    """Make a GET request and return parsed JSON."""
    merged = {"User-Agent": "assetSeeker/1.0"}
    if headers:
        merged.update(headers)
    req = urllib.request.Request(url, headers=merged)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": body[:300]}
    except urllib.error.URLError as e:
        return {"error": f"Request failed: {e.reason}"}


def _download_file(url: str, output: str) -> bool:
    """Download a file from url to output path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "assetSeeker/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            Path(output).write_bytes(resp.read())
        return True
    except Exception as e:
        print(f"Download error: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Source-specific search functions
# ---------------------------------------------------------------------------


def _search_pexels(args: argparse.Namespace) -> list[dict]:
    """Search Pexels photos or videos."""
    key = _get_key("pexels")
    if not key:
        return [{"error": "PEXELS_API_KEY not set. Get one at https://www.pexels.com/api/"}]

    if args.type == "video":
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(args.keyword)}&per_page={args.max_results}"
    else:
        url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(args.keyword)}&per_page={args.max_results}"
        if args.orientation:
            url += f"&orientation={args.orientation}"
        if args.color:
            url += f"&color={args.color}"

    # Pexels uses camelCase for orientation; remap if needed
    if args.orientation == "landscape":
        url = url.replace("&orientation=landscape", "&orientation=landscape")
    elif args.orientation == "portrait":
        url = url.replace("&orientation=portrait", "&orientation=portrait")
    elif args.orientation == "square":
        url = url.replace("&orientation=square", "&orientation=square")

    data = _api_get(url, {"Authorization": key})
    if "error" in data:
        return [data]

    items = data.get("photos") or data.get("videos") or []
    results: list[dict] = []
    for item in items:
        if args.type == "video":
            # Pick best-quality video file
            video_files = sorted(item.get("video_files", []), key=lambda f: f.get("width", 0) * f.get("height", 0), reverse=True)
            best = video_files[0] if video_files else {}
            results.append({
                "id": item.get("id"),
                "source": "pexels",
                "type": "video",
                "url": item.get("url", ""),
                "preview": item.get("image", ""),
                "download_url": best.get("link", ""),
                "width": best.get("width"),
                "height": best.get("height"),
                "duration": item.get("duration"),
                "photographer": item.get("user", {}).get("name", ""),
                "photographer_url": item.get("user", {}).get("url", ""),
            })
        else:
            results.append({
                "id": item.get("id"),
                "source": "pexels",
                "type": "photo",
                "url": item.get("url", ""),
                "preview": item.get("src", {}).get("large", ""),
                "download_url": item.get("src", {}).get("original", ""),
                "width": item.get("width"),
                "height": item.get("height"),
                "photographer": item.get("photographer", ""),
                "photographer_url": item.get("photographer_url", ""),
                "alt": item.get("alt", ""),
                "avg_color": item.get("avg_color", ""),
            })
    return results


def _search_unsplash(args: argparse.Namespace) -> list[dict]:
    """Search Unsplash photos."""
    key = _get_key("unsplash")
    if not key:
        return [{"error": "UNSPLASH_ACCESS_KEY not set. Get one at https://unsplash.com/developers"}]

    url = f"https://api.unsplash.com/search/photos?query={urllib.parse.quote(args.keyword)}&per_page={args.max_results}"
    if args.orientation:
        url += f"&orientation={args.orientation}"

    data = _api_get(url, {"Authorization": f"Client-ID {key}"})
    if "error" in data:
        return [data]

    results: list[dict] = []
    for item in data.get("results", []):
        results.append({
            "id": item.get("id"),
            "source": "unsplash",
            "type": "photo",
            "url": item.get("links", {}).get("html", ""),
            "preview": item.get("urls", {}).get("regular", ""),
            "download_url": item.get("urls", {}).get("full", ""),
            "width": item.get("width"),
            "height": item.get("height"),
            "photographer": item.get("user", {}).get("name", ""),
            "photographer_url": f"https://unsplash.com/@{item.get('user', {}).get('username', '')}",
            "alt": item.get("alt_description") or item.get("description") or "",
            "color": item.get("color", ""),
            "likes": item.get("likes", 0),
        })
    return results


def _search_pixabay(args: argparse.Namespace) -> list[dict]:
    """Search Pixabay photos or videos."""
    key = _get_key("pixabay")
    if not key:
        return [{"error": "PIXABAY_API_KEY not set. Get one at https://pixabay.com/api/docs/"}]

    if args.type == "video":
        url = f"https://pixabay.com/api/videos/?key={key}&q={urllib.parse.quote(args.keyword)}&per_page={args.max_results}"
    else:
        url = f"https://pixabay.com/api/?key={key}&q={urllib.parse.quote(args.keyword)}&per_page={args.max_results}"
    if args.orientation:
        url += f"&orientation={args.orientation}"

    data = _api_get(url)
    if "error" in data:
        return [data]

    items = data.get("hits", [])
    results: list[dict] = []
    for item in items:
        if args.type == "video":
            # Pick medium or large quality
            videos = item.get("videos", {})
            best = videos.get("large") or videos.get("medium") or videos.get("small") or {}
            results.append({
                "id": item.get("id"),
                "source": "pixabay",
                "type": "video",
                "url": item.get("pageURL", ""),
                "preview": videos.get("medium", {}).get("thumbnail", ""),
                "download_url": best.get("url", ""),
                "width": best.get("width"),
                "height": best.get("height"),
                "duration": item.get("duration"),
                "user": item.get("user", ""),
                "tags": item.get("tags", ""),
            })
        else:
            results.append({
                "id": item.get("id"),
                "source": "pixabay",
                "type": "photo",
                "url": item.get("pageURL", ""),
                "preview": item.get("webformatURL", ""),
                "download_url": item.get("largeImageURL", ""),
                "width": item.get("imageWidth"),
                "height": item.get("imageHeight"),
                "user": item.get("user", ""),
                "tags": item.get("tags", ""),
                "likes": item.get("likes", 0),
                "downloads": item.get("downloads", 0),
            })
    return results


def _search_iconify(args: argparse.Namespace) -> list[dict]:
    """Search Iconify icons — no API key needed."""
    keyword = args.keyword.strip()
    if len(keyword) < 2:
        return [{"error": "Icon search needs at least 2 characters"}]

    # Iconify search API: /search?query=...&limit=...
    url = f"https://api.iconify.design/search?query={urllib.parse.quote(keyword)}&limit={args.max_results}"
    data = _api_get(url)
    if "error" in data:
        return [data]

    results: list[dict] = []
    for item in data.get("icons", []):
        prefix, _, name = item.partition(":")
        results.append({
            "id": item,
            "source": "iconify",
            "type": "icon",
            "prefix": prefix,
            "name": name,
            "svg_url": f"https://api.iconify.design/{item}.svg",
            "usage_html": f'<span class="iconify" data-icon="{item}"></span>',
            "preview_url": f"https://api.iconify.design/{item}.svg?width=64&height=64",
            "collections": data.get("collections", {}),
        })

    # Attach collection name for each prefix
    collections = data.get("collections", {})
    for r in results:
        col = collections.get(r["prefix"], {})
        r["collection_name"] = col.get("name", r["prefix"])
        r["collection_license"] = col.get("license", {}).get("title", "Unknown")

    return results


def _search_freesound(args: argparse.Namespace) -> list[dict]:
    """Search Freesound for SFX or music."""
    key = _get_key("freesound")
    if not key:
        return [{"error": "FREESOUND_API_KEY not set. Get one at https://freesound.org/apiv2/apply/"}]

    token = os.environ.get("FREESOUND_TOKEN", key)
    auth_header = f"Bearer {token}" if token else f"Token {key}"
    url = f"https://freesound.org/apiv2/search/text/?query={urllib.parse.quote(args.keyword)}&page_size={min(args.max_results, 30)}&fields=id,name,url,previews,license,username,duration,download,tags"

    # Filter for music vs sfx
    if args.type == "music":
        url += "&filter=tag:music"
    elif args.type == "sfx":
        url += "&filter=tag:sfx"

    data = _api_get(url, {"Authorization": auth_header})
    if "error" in data:
        return [data]

    results: list[dict] = []
    for item in data.get("results", []):
        previews = item.get("previews", {})
        results.append({
            "id": item.get("id"),
            "source": "freesound",
            "type": args.type,
            "name": item.get("name", ""),
            "url": item.get("url", ""),
            "preview_url": previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3", ""),
            "download_url": item.get("download", ""),
            "duration": item.get("duration"),
            "license": item.get("license", ""),
            "username": item.get("username", ""),
            "tags": item.get("tags", []),
        })
    return results


def _search_google_fonts(args: argparse.Namespace) -> list[dict]:
    """Search Google Fonts."""
    key = _get_key("google-fonts")
    if not key:
        return [{"error": "GOOGLE_FONTS_API_KEY not set. Get one at https://console.cloud.google.com/"}]

    url = f"https://www.googleapis.com/webfonts/v1/webfonts?key={key}&sort=popularity"
    data = _api_get(url)
    if "error" in data:
        return [data]

    keyword = args.keyword.lower()
    items = data.get("items", [])

    # Filter by keyword match in family name or category
    matched: list[dict] = []
    for f in items:
        family = f.get("family", "").lower()
        category = (f.get("category", "") or "").lower()
        if keyword in family or keyword in category:
            variants = f.get("variants", [])
            matched.append({
                "family": f.get("family"),
                "source": "google-fonts",
                "type": "font",
                "category": f.get("category", ""),
                "variants": variants,
                "variants_count": len(variants),
                "subsets": f.get("subsets", []),
                "version": f.get("version", ""),
                "last_modified": f.get("lastModified", ""),
                "css_link": f"https://fonts.googleapis.com/css2?family={urllib.parse.quote(f.get('family', '').replace(' ', '+'))}",
                "popularity": f.get("popularity", ""),
            })
        if len(matched) >= args.max_results:
            break

    return matched


def _search_noun_project(args: argparse.Namespace) -> list[dict]:
    """Search Noun Project icons (requires OAuth1 — simplified to key+secret)."""
    key = os.environ.get("NOUN_PROJECT_KEY")
    secret = os.environ.get("NOUN_PROJECT_SECRET")
    if not key or not secret:
        return [{"error": "NOUN_PROJECT_KEY / NOUN_PROJECT_SECRET not set. Get them at https://thenounproject.com/developers/"}]

    # Noun Project uses OAuth1; do a simple GET with the key as query param for the public API
    url = f"https://api.thenounproject.com/v2/icon?query={urllib.parse.quote(args.keyword)}&limit={min(args.max_results, 20)}"
    # Basic auth via OAuth1 is complex; use the simpler approach with key+secret as query params
    # Many Noun Project API users just use the key/secret via OAuth1 library
    # For simplicity, we'll return a helpful error if not achievable
    return [{
        "error": "Noun Project requires OAuth1 signing. Use Iconify for zero-config icon search instead.",
        "hint": "Iconify has 300k+ icons and works without any API key.",
    }]


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

SEARCHERS = {
    "pexels": _search_pexels,
    "unsplash": _search_unsplash,
    "pixabay": _search_pixabay,
    "iconify": _search_iconify,
    "freesound": _search_freesound,
    "google-fonts": _search_google_fonts,
    "noun-project": _search_noun_project,
}


def _available_sources(asset_type: str) -> list[str]:
    """Return configured sources for the given type, filtering by API key availability.
    Always includes sources that don't need a key (Iconify).
    """
    candidates = TYPE_TO_SOURCES.get(asset_type, [])
    available: list[str] = []
    for src in candidates:
        conf = SOURCE_CONFIG.get(src, {})
        if conf.get("env_key") is None:
            # No key needed — always available
            available.append(src)
        elif _get_key(src):
            available.append(src)
    return available


def _source_status() -> dict[str, dict]:
    """Return status of all sources."""
    status: dict[str, dict] = {}
    for name, conf in SOURCE_CONFIG.items():
        env = conf.get("env_key")
        if env:
            has = bool(os.environ.get(env))
        else:
            has = True  # no key needed
        status[name] = {
            "label": conf["label"],
            "types": conf["types"],
            "has_api_key": has,
            "free_tier": conf.get("free_tier", ""),
            "china_access": conf.get("china_access", True),
            "license": conf.get("license", ""),
            "note": conf.get("note", ""),
            "env_var": env,
        }
    return status


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_sources(args: argparse.Namespace) -> None:
    """List sources and their API key status."""
    status = _source_status()
    if args.type:
        status = {k: v for k, v in status.items() if args.type in v["types"]}

    if args.format == "text":
        print(f"{'Source':<18} {'Types':<22} {'Key?':<6} {'Free Tier':<28} {'China':<6}")
        print("-" * 82)
        for name, s in status.items():
            types = ",".join(s["types"])
            key = "✓" if s["has_api_key"] else ("N/A" if s["env_var"] is None else "✗")
            china = "✓" if s["china_access"] else "⚠️"
            print(f"{name:<18} {types:<22} {key:<6} {s['free_tier']:<28} {china:<6}")
        print(f"\n{len(status)} sources listed")
    else:
        print(json.dumps(status, ensure_ascii=False, indent=2))


def cmd_search(args: argparse.Namespace) -> None:
    """Search assets across configured sources."""
    asset_type = args.type

    if asset_type not in TYPE_TO_SOURCES:
        valid = ", ".join(TYPE_TO_SOURCES.keys())
        print(json.dumps({"error": f"Unknown type: {asset_type}", "valid_types": valid.split(", ")}, ensure_ascii=False))
        sys.exit(1)

    # Determine which sources to use
    if args.source:
        sources = [args.source]
    else:
        sources = _available_sources(asset_type)

    if not sources:
        print(json.dumps({
            "error": f"No API keys configured for {asset_type} sources.",
            "hint": "Set at least PEXELS_API_KEY (https://www.pexels.com/api/). Iconify works for icons without any key.",
            "available_sources": _source_status(),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    all_results: dict[str, list[dict]] = {}
    total = 0

    for src in sources:
        searcher = SEARCHERS.get(src)
        if not searcher:
            continue
        try:
            results = searcher(args)
        except Exception as e:
            results = [{"error": f"{src}: {e}"}]
        all_results[src] = results
        total += len(results) if not any("error" in r for r in results) else 0

    output: dict[str, Any] = {
        "keyword": args.keyword,
        "type": asset_type,
        "total_results": total,
        "sources_queried": sources,
    }

    if args.format == "text":
        _print_search_text(args.keyword, asset_type, all_results)
    else:
        for src, results in all_results.items():
            conf = SOURCE_CONFIG.get(src, {})
            output[src] = {
                "label": conf.get("label", src),
                "count": len(results),
                "license": conf.get("license", ""),
                "results": results,
            }
        print(json.dumps(output, ensure_ascii=False, indent=2))


def _print_search_text(keyword: str, asset_type: str, all_results: dict[str, list[dict]]) -> None:
    """Human-readable search output."""
    print(f"Search: {asset_type} \"{keyword}\"\n")
    for src, results in all_results.items():
        conf = SOURCE_CONFIG.get(src, {})
        label = conf.get("label", src)
        has_err = any("error" in r for r in results)
        if has_err:
            for r in results:
                if "error" in r:
                    print(f"[{label}] ⚠️  {r['error']}")
                    if "hint" in r:
                        print(f"       → {r['hint']}")
            print()
            continue

        print(f"─── {label} ({len(results)} results) | License: {conf.get('license', 'N/A')} ───")
        for i, r in enumerate(results, 1):
            if asset_type == "photo":
                print(f"  {i}. {r.get('alt', r.get('tags', 'Photo'))[:60]}")
                print(f"     {r.get('width')}×{r.get('height')} | {r.get('photographer') or r.get('user', '')}")
                print(f"     Preview: {r.get('preview', '')[:100]}")
                print(f"     Download: {r.get('download_url', '')[:100]}")
            elif asset_type == "video":
                dur = r.get("duration", 0)
                print(f"  {i}. {r.get('url', '')[:80]}")
                print(f"     {r.get('width')}×{r.get('height')} | {dur:.0f}s | by {r.get('photographer') or r.get('user', '')}")
                print(f"     Download: {r.get('download_url', '')[:100]}")
            elif asset_type == "icon":
                print(f"  {i}. {r.get('id', '')} [{r.get('collection_name', '')}]")
                print(f"     SVG: {r.get('svg_url', '')}")
                print(f"     License: {r.get('collection_license', '')}")
            elif asset_type in ("sfx", "music"):
                dur = r.get("duration", 0)
                print(f"  {i}. {r.get('name', '')[:60]} ({dur:.1f}s)")
                print(f"     License: {r.get('license', '')} | by {r.get('username', '')}")
                print(f"     Preview: {r.get('preview_url', '')[:100]}")
            elif asset_type == "font":
                print(f"  {i}. {r.get('family', '')} ({r.get('category', '')})")
                print(f"     Variants: {', '.join(r.get('variants', []))}")
                print(f"     CSS: {r.get('css_link', '')}")
        print()


def cmd_download(args: argparse.Namespace) -> None:
    """Download a single asset from a URL."""
    url = args.url
    output = args.output
    if not output:
        # Infer from URL
        output = url.split("/")[-1].split("?")[0] or "download"

    print(f"Downloading {url} → {output} …", file=sys.stderr)
    ok = _download_file(url, output)
    if ok:
        size = Path(output).stat().st_size
        print(json.dumps({"status": "ok", "file": output, "size_bytes": size}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "error", "file": output, "message": "Download failed"}, ensure_ascii=False))
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Asset Seeker — Search free commercial-use creative assets online",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  seek_assets.py sources
  seek_assets.py search photo "mountain sunset"
  seek_assets.py search icon "laptop" --format text
  seek_assets.py search video "city traffic" --source pexels
  seek_assets.py search sfx "whoosh" --max 5
  seek_assets.py search font "bold sans"
  seek_assets.py download https://example.com/photo.jpg -o bg.jpg
        """,
    )

    sub = parser.add_subparsers(dest="command")

    # sources
    p_src = sub.add_parser("sources", help="List sources and API key status")
    p_src.add_argument("--type", help="Filter by asset type (photo, icon, video, sfx, font)")
    p_src.add_argument("--format", choices=["json", "text"], default="text")
    p_src.set_defaults(func=cmd_sources)

    # search
    p_search = sub.add_parser("search", help="Search for assets")
    p_search.add_argument("type", help=f"Asset type: {', '.join(TYPE_TO_SOURCES.keys())}")
    p_search.add_argument("keyword", help="Search keyword")
    p_search.add_argument("--max", type=int, dest="max_results", default=10, help="Max results per source (default: 10)")
    p_search.add_argument("--source", help="Specific source to query (e.g., pexels, iconify)")
    p_search.add_argument("--orientation", choices=["landscape", "portrait", "square"], help="Photo/video orientation filter")
    p_search.add_argument("--color", help="Photo color filter (Pexels/Pixabay only)")
    p_search.add_argument("--format", choices=["json", "text"], default="json")
    p_search.set_defaults(func=cmd_search)

    # download
    p_dl = sub.add_parser("download", help="Download a single asset")
    p_dl.add_argument("url", help="Asset URL")
    p_dl.add_argument("-o", "--output", help="Output file path")
    p_dl.set_defaults(func=cmd_download)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
