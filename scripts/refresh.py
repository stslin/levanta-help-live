#!/usr/bin/env python3
"""
refresh.py — rebuild the reference files in this skill from the live
https://knowledge.levanta.io/llms.txt index.

v2 (2026-08): Levanta's knowledge base was restructured into nested
sub-collections (e.g. "Creator Accounts" -> "Getting Started", "Payments &
Taxes", "Creator API", ...). Several sub-collection names are reused under
both "Creator Accounts" and "Seller Accounts" (e.g. both have a "Getting
Started" and a "Payments & Taxes"). This version tracks the FULL
(top-section, sub-section) hierarchy so same-named subsections under
different top-level sections are never merged together. Only sub-sections
named "Creator API" / "Seller API" are pulled out into api.md; everything
else under a top-level section is written into that section's single file
(creators.md / sellers.md / sellers_zh.md), with sub-section names kept as
in-file headings.

Run this whenever the knowledge base has changed and you want to refresh the
bundled snapshot. After running, re-package the skill folder (e.g. zip it into
a .skill file) and reinstall in Claude.

Usage:
    # From inside the skill folder:
    python3 scripts/refresh.py

    # Or with a custom llms.txt URL:
    python3 scripts/refresh.py --llms-url https://knowledge.levanta.io/llms.txt

Dependencies: beautifulsoup4, html2text
    pip install beautifulsoup4 html2text
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

try:
    from bs4 import BeautifulSoup
    import html2text
except ImportError:
    sys.exit("Missing dependencies. Run: pip install beautifulsoup4 html2text")

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Map TOP-LEVEL llms.txt section headers -> output filename + metadata.
# New top-level sections in the llms.txt will fall through to "misc.md"
# until mapped here.
#
# "api_subsections" lists the names of ### sub-sections under this top-level
# section that should be pulled OUT into a separate file (api.md) instead of
# being folded into the top-level section's own file. Every other
# sub-section under this top-level section stays in the top-level file, with
# the sub-section name kept as an in-file heading.
SECTION_MAP = {
    "Creator Accounts": {
        "file": "creators.md",
        "heading": "Levanta Knowledge Base — Creator Articles",
        "intro": (
            "Creator-facing articles: applying to the platform, profile setup, "
            "generating affiliate links, getting paid, reporting, partnerships, "
            "samples, tiers, team management, and FAQs."
        ),
        "api_subsections": {
            "Creator API": {"file": "api.md", "section_heading": "Creator API"},
        },
    },
    "Seller Accounts": {
        "file": "sellers.md",
        "heading": "Levanta Knowledge Base — Seller Articles",
        "intro": (
            "Seller-facing articles: onboarding, Amazon/Shopify integration, "
            "activating brands and products, commissions, campaigns (CPC, Deals, "
            "Creator Connections, Paid Placements), payments, taxes, reporting, "
            "and FAQs."
        ),
        "api_subsections": {
            "Seller API": {"file": "api.md", "section_heading": "Seller API"},
        },
    },
    "Seller Articles (中文)": {
        "file": "sellers_zh.md",
        "heading": "Levanta 知识库 — 卖家文章 (中文)",
        "intro": (
            "Chinese-language translations of the seller articles. Use when the "
            "user writes in Chinese or asks for Chinese documentation."
        ),
    },
    # fallback for any top-level section not listed above
    "__default__": {
        "file": "misc.md",
        "heading": "Levanta Knowledge Base — Miscellaneous",
        "intro": "Articles not yet mapped to a specific reference file.",
    },
}

API_HEADING = "Levanta Knowledge Base — API Documentation"
API_INTRO = (
    "Creator API and Seller API — prerequisites, authentication, webhooks, "
    "and links to the full Swagger docs at api-docs.levanta.io."
)


def fetch(url, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt == retries - 1:
                return f"ERROR: {e}"
            time.sleep(1 + attempt)


LINK_RE = re.compile(r"-\s*\[([^\]]+)\]\(([^)]+)\)")


def parse_llms_txt(text):
    """Parse llms.txt preserving the FULL hierarchy.

    Returns: {top_section_name: {"direct": [(title,url), ...],
                                  "sub": {sub_section_name: [(title,url), ...]}}}

    '## Section' starts a new top-level section (direct bucket + fresh sub map).
    '### Subsection' starts a sub-section *within the current top-level
    section only* — critically, two different top-level sections can each
    have their own sub-section of the same name without colliding, because
    the sub-section dict lives inside its parent's entry.
    Links before any '###' (but after a '##') go into that section's
    "direct" bucket.
    """
    sections = {}
    current = None
    current_sub = None
    for line in text.splitlines():
        m2 = re.match(r"^##\s+(.+?)\s*$", line)
        m3 = re.match(r"^###\s+(.+?)\s*$", line)
        if m2:
            current = m2.group(1).strip()
            current_sub = None
            sections.setdefault(current, {"direct": [], "sub": {}})
            continue
        if m3:
            if current is None:
                # Malformed llms.txt (### before any ##) — ignore.
                current_sub = None
                continue
            current_sub = m3.group(1).strip()
            sections[current]["sub"].setdefault(current_sub, [])
            continue
        link = LINK_RE.search(line)
        if link:
            if current is None:
                continue
            title, url = link.group(1).strip(), link.group(2).strip()
            if current_sub is not None:
                sections[current]["sub"][current_sub].append((title, url))
            else:
                sections[current]["direct"].append((title, url))
    # Drop empty top-level sections
    return {
        k: v for k, v in sections.items()
        if v["direct"] or any(v["sub"].values())
    }


def extract_article(html):
    soup = BeautifulSoup(html, "html.parser")
    article = (
        soup.select_one("article")
        or soup.select_one('[class*="article"]')
        or soup.select_one('[class*="content"]')
        or soup.select_one("main")
        or soup.body
    )
    for tag in article.select(
        "nav, header, footer, script, style, aside, "
        ".sidebar, [class*='nav'], [class*='footer']"
    ):
        tag.decompose()
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.body_width = 0
    h2t.ignore_images = True
    h2t.skip_internal_links = True
    md = h2t.handle(str(article))

    # Collapse consecutive blank lines
    lines = [ln.rstrip() for ln in md.split("\n")]
    out, blank = [], False
    for ln in lines:
        if not ln.strip():
            if blank:
                continue
            blank = True
        else:
            blank = False
        out.append(ln)
    return title, "\n".join(out).strip()


def fetch_article(entry):
    title_hint, url = entry
    html = fetch(url)
    if html.startswith("ERROR:"):
        return {"title": title_hint, "url": url, "error": html, "markdown": None}
    title, md = extract_article(html)
    return {"title": title or title_hint, "url": url, "markdown": md}


def build_reference_file(out_path, heading, intro, section_groups):
    """Write a reference file. section_groups is an ordered list of
    (subsection_heading_or_None, [article_dicts]). subsection_heading is
    None for articles that sit directly under the top-level section (no
    sub-heading needed)."""
    lines = [f"# {heading}", "", intro, "",
             f"Source: <https://knowledge.levanta.io>",
             f"Snapshot date: {date.today().isoformat()}", "",
             "---", "", "## Table of contents", ""]

    flat = []
    for sh, arts in section_groups:
        if sh:
            flat.append(("section", sh))
        flat.extend(("article", a) for a in arts)

    counter = 0
    for kind, item in flat:
        if kind == "section":
            lines.append(f"\n### {item}\n")
        else:
            counter += 1
            t = item.get("title", "Untitled").strip()
            lines.append(f"{counter}. [{t}](#{counter})")
    lines.extend(["", "---", ""])

    counter = 0
    for kind, item in flat:
        if kind == "section":
            lines.append(f"# {item}\n")
        else:
            counter += 1
            t = item.get("title", "Untitled").strip()
            url = item.get("url", "")
            md = item.get("markdown") or "_(could not fetch)_"
            lines.extend([
                f'<a id="{counter}"></a>', "",
                f"## {counter}. {t}", "",
                f"**Source:** <{url}>", "",
                md.strip(), "",
                "---", "",
            ])
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--llms-url", default="https://knowledge.levanta.io/llms.txt")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--skill-root", default=None,
                    help="Skill root directory (defaults to script's parent)")
    args = ap.parse_args()

    skill_root = Path(args.skill_root) if args.skill_root else Path(__file__).resolve().parent.parent
    ref_dir = skill_root / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {args.llms_url}")
    text = fetch(args.llms_url)
    if text.startswith("ERROR:"):
        sys.exit(f"Failed to fetch llms.txt: {text}")

    sections = parse_llms_txt(text)
    total = sum(len(v["direct"]) + sum(len(a) for a in v["sub"].values())
                for v in sections.values())
    print(f"Found {len(sections)} top-level section(s), {total} article(s):")
    for s, v in sections.items():
        n = len(v["direct"]) + sum(len(a) for a in v["sub"].values())
        print(f"  - {s}: {n}")
        for sub_name, arts in v["sub"].items():
            print(f"      · {sub_name}: {len(arts)}")

    # file_bundles: filename -> list of (subsection_heading_or_None, [entries as (title,url)])
    file_bundles = {}
    file_meta = {}

    for top_name, data in sections.items():
        meta = SECTION_MAP.get(top_name)
        if not meta:
            print(f"  (unmapped top-level section -> misc.md): {top_name}")
            meta = SECTION_MAP["__default__"]
        fn = meta["file"]
        file_meta.setdefault(fn, meta)
        api_subs = meta.get("api_subsections", {})

        # Direct articles (no sub-heading) go straight into the file.
        if data["direct"]:
            file_bundles.setdefault(fn, []).append((None, list(data["direct"])))

        for sub_name, arts in data["sub"].items():
            if sub_name in api_subs:
                api_meta = api_subs[sub_name]
                api_fn = api_meta["file"]
                file_meta.setdefault(api_fn, {
                    "file": api_fn, "heading": API_HEADING, "intro": API_INTRO,
                })
                file_bundles.setdefault(api_fn, []).append(
                    (api_meta.get("section_heading", sub_name), list(arts))
                )
            else:
                file_bundles.setdefault(fn, []).append((sub_name, list(arts)))

    # Fetch all articles in parallel
    all_entries = []
    for fn, groups in file_bundles.items():
        for gi, (sh, entries) in enumerate(groups):
            for ei, (t, u) in enumerate(entries):
                all_entries.append((fn, gi, ei, t, u))

    print(f"\nFetching {len(all_entries)} articles in parallel…")
    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(fetch_article, (t, u)): (fn, gi, ei)
                for (fn, gi, ei, t, u) in all_entries}
        done = 0
        for fut in as_completed(futs):
            key = futs[fut]
            r = fut.result()
            results[key] = r
            done += 1
            status = "ERR" if r.get("error") else "OK"
            print(f"  [{done}/{len(all_entries)}] {status} {r.get('title', '')[:70]}")

    # Assemble reference files
    print()
    for fn, groups in file_bundles.items():
        meta = file_meta.get(fn, SECTION_MAP["__default__"])
        section_groups = []
        for gi, (sh, entries) in enumerate(groups):
            arts = [results[(fn, gi, ei)] for ei in range(len(entries))]
            section_groups.append((sh, arts))
        build_reference_file(ref_dir / fn, meta["heading"], meta["intro"], section_groups)
        n_articles = sum(len(a) for _, a in section_groups)
        size = (ref_dir / fn).stat().st_size
        print(f"  Wrote {ref_dir / fn} ({size:,} bytes, {n_articles} articles)")

    # Write a manifest for debugging
    manifest = {
        "snapshot_date": date.today().isoformat(),
        "llms_url": args.llms_url,
        "top_level_sections": {
            s: {"direct": len(v["direct"]),
                "sub": {sn: len(a) for sn, a in v["sub"].items()}}
            for s, v in sections.items()
        },
        "total_articles": total,
    }
    (skill_root / "scripts" / "last_refresh.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n✅ Done. Snapshot date: {manifest['snapshot_date']}")


if __name__ == "__main__":
    main()
