"""
CLI to scrape web sources for Compliso dataset.

Uses FireCrawl for web pages, direct download for PDFs.
Saves to true_data/ or noisy_data/ based on authority tier.

Usage:
    python -m app.ingestion.scrapers.cli               # scrape all sources
    python -m app.ingestion.scrapers.cli --tier 1       # government only
    python -m app.ingestion.scrapers.cli --category gst  # GST only
    python -m app.ingestion.scrapers.cli --dry-run       # preview only
    python -m app.ingestion.scrapers.cli --ingest        # scrape + ingest
"""

import argparse
import os
import sys
import time
from pathlib import Path

import logfire
import requests
from dotenv import load_dotenv

load_dotenv()

logfire.configure(service_name="compliso-scraper")

from app.ingestion.scrapers.sources import (
    ALL_SOURCES,
    Source,
    estimate_credits,
)

FIRE_CRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def authority_to_dir(tier: int) -> Path:
    """Map authority tier to data directory."""
    return DATA_DIR / ("true_data" if tier <= 2 else "noisy_data")


def sanitise_filename(name: str) -> str:
    """Turn a source name into a safe filename."""
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    return safe.strip().replace(" ", "_").lower()[:80]


def fetch_pdf(source: Source) -> Path | None:
    """Download a PDF source directly via HTTP."""
    dest_dir = authority_to_dir(source.authority_tier)
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{sanitise_filename(source.name)}.pdf"
    dest_path = dest_dir / filename

    if dest_path.exists():
        logfire.info(f"Already exists, skipping: {filename}")
        return dest_path

    logfire.info(f"Downloading PDF: {source.url}")
    try:
        resp = requests.get(source.url, timeout=60, headers={
            "User-Agent": "Compliso/1.0 (RAG dataset collector; educational use)"
        })
        resp.raise_for_status()
        dest_path.write_bytes(resp.content)
        logfire.info(f"Saved: {dest_path}")
        time.sleep(1)
        return dest_path
    except Exception as e:
        logfire.error(f"Failed to download {source.url}: {e}")
        return None


def fetch_webpage_firecrawl(source: Source) -> Path | None:
    """Scrape a web page using FireCrawl API."""
    if not FIRE_CRAWL_API_KEY:
        logfire.warning("FIRECRAWL_API_KEY not set, skipping web pages")
        return None

    dest_dir = authority_to_dir(source.authority_tier)
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{sanitise_filename(source.name)}.md"
    dest_path = dest_dir / filename

    if dest_path.exists():
        logfire.info(f"Already exists, skipping: {filename}")
        return dest_path

    logfire.info(f"Scraping: {source.url}")
    try:
        from firecrawl import Firecrawl
        app = Firecrawl(api_key=FIRE_CRAWL_API_KEY)
        result = app.scrape(source.url, formats=["markdown"])
        content = result.markdown or ""
        if not content:
            logfire.warning(f"No markdown content for {source.url}")
            return None
        dest_path.write_text(content, encoding="utf-8")
        logfire.info(f"Saved: {dest_path}")
        time.sleep(1)
        return dest_path
    except ImportError:
        logfire.error("firecrawl-py not installed; run: pip install firecrawl-py")
        return None
    except Exception as e:
        logfire.error(f"FireCrawl failed for {source.url}: {e}")
        return None


def fetch_source(source: Source, dry_run: bool = False) -> Path | None:
    """Fetch a single source by the appropriate method."""
    if dry_run:
        method = "FireCrawl" if source.doc_type == "web_page" else "HTTP download"
        dest = authority_to_dir(source.authority_tier)
        print(f"  [{method}] {source.name} → {dest.name}/{sanitise_filename(source.name)}.{'md' if source.doc_type == 'web_page' else 'pdf'}")
        return None

    if source.doc_type == "pdf":
        return fetch_pdf(source)
    else:
        return fetch_webpage_firecrawl(source)


def run_ingestion():
    """Run the ingestion pipeline on the updated data."""
    logfire.info("Running ingestion pipeline...")
    from app.ingestion.processor import run_universal_ingestion
    summary = run_universal_ingestion(str(DATA_DIR), wipe=False)
    logfire.info("Ingestion complete", **summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Compliso web data scraper")
    parser.add_argument("--tier", type=int, help="Authority tier to scrape (1-5)")
    parser.add_argument("--category", type=str, help="Category to scrape (gst, msme, payment)")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be scraped")
    parser.add_argument("--ingest", action="store_true", help="Run ingestion after scraping")
    args = parser.parse_args()

    # Filter sources
    sources = ALL_SOURCES
    if args.tier:
        sources = [s for s in sources if s.authority_tier == args.tier]
    if args.category:
        sources = [s for s in sources if s.category == args.category]

    if not sources:
        print("No sources match filter.")
        sys.exit(1)

    # Budget
    if args.dry_run:
        print(f"\nSources to scrape: {len(sources)}")
        print(f"Web pages (FireCrawl): {sum(1 for s in sources if s.doc_type == 'web_page')}")
        print(f"PDFs (direct DL): {sum(1 for s in sources if s.doc_type == 'pdf')}")
        if FIRE_CRAWL_API_KEY:
            credits = estimate_credits(sources)
            print(f"Estimated FireCrawl credits: {credits}")
        else:
            print("FIRECRAWL_API_KEY not set — will only download PDFs")
        print()

    # Scrape
    results = {"success": 0, "failed": 0, "skipped": 0}

    for source in sources:
        print(f"\n[{source.authority_tier}] {source.name}")
        path = fetch_source(source, dry_run=args.dry_run)
        if path:
            results["success"] += 1
        elif not args.dry_run:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    if not args.dry_run:
        print(f"\nScraping complete: {results['success']} saved, {results['failed']} failed")
        if args.ingest:
            summary = run_ingestion()
            print(f"Ingestion: {summary['success']} success, {summary['failed']} failed")
    else:
        print("\nDry run complete. Remove --dry-run to execute.")


if __name__ == "__main__":
    main()
