#!/usr/bin/env python3
"""
check_dead_links.py
Linkography URL health and redirect checker.

Reads:
    _data/linkography.yaml

Writes:
    _reports/link-check-YYYY-MM-DD.csv

Does not modify the YAML database.
"""

import csv
import sys
import time
import urllib.request
import urllib.error
import socket
import argparse

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "_data" / "linkography.yaml"
ALLOWLIST_FILE = ROOT / "_data" / "redirect_allowlist.yaml"
REPORT_DIR = ROOT / "_reports"

TIMEOUT = 20
MAX_WORKERS = 5
MAX_REDIRECTS = 10

USER_AGENT = (
    "Linkography-LinkChecker/1.0 "
    "(public resource directory; contact: links.davemitchner.com)"
)
# --------------------------------------------------
# Load Allowed Redirect List
# --------------------------------------------------


def load_redirect_allowlist():

    if not ALLOWLIST_FILE.exists():
        return []

    with ALLOWLIST_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    return data.get("approved_redirects", [])
    
# --------------------------------------------------
# URL NORMALIZATION
# --------------------------------------------------


def normalize_url(url):

    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    port = parsed.port
    path = parsed.path or "/"
    query = parsed.query

    # Treat www and non-www hostnames as equivalent.
    if hostname.startswith("www."):
        hostname = hostname[4:]

    # Ignore one harmless trailing slash difference.
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    # Normalize default ports.
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None

    # Return comparable URL components.
    return scheme, hostname, port, path, query

# --------------------------------------------------
# REDIRECT TRACKING
# --------------------------------------------------

class TrackingRedirectHandler(urllib.request.HTTPRedirectHandler):

    def __init__(self):
        super().__init__()
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):

        self.chain.append({
            "status": code,
            "from": req.full_url,
            "to": newurl,
        })

        return super().redirect_request(
            req, fp, code, msg, headers, newurl
        )

# --------------------------------------------------
# CHECK WHETHER ONE REDIRECT IS APPROVED
# --------------------------------------------------

def redirect_is_approved(redirect, redirect_allowlist):

    source = normalize_url(redirect["from"])
    destination = normalize_url(redirect["to"])

    source_scheme, source_host, source_port, source_path, source_query = source
    dest_scheme, dest_host, dest_port, dest_path, dest_query = destination

    # Only approve HTTP-to-HTTPS scheme changes.
    if source_scheme != dest_scheme:
        if not (source_scheme == "http" and dest_scheme == "https"):
            return False

    # Automatically approve harmless URL changes.
    same_location = (
        source_host == dest_host
        and source_port == dest_port
        and source_path == dest_path
        and source_query == dest_query
    )

    if same_location:
        return True

    # Check explicit exceptions in the YAML allowlist.
    for rule in redirect_allowlist:

        allowed_source = normalize_url(
            "https://" + str(rule.get("source", ""))
        )[1]

        allowed_destination = normalize_url(
            "https://" + str(rule.get("destination", ""))
        )[1]

        if source_host != allowed_source:
            continue

        if dest_host != allowed_destination:
            continue

        if source_port != dest_port:
            continue

        # Path changes require explicit permission.
        if source_path != dest_path and not rule.get("allow_path_change", False):
            continue

        # Query strings must always remain unchanged.
        if source_query != dest_query:
            continue

        return True

    return False

# --------------------------------------------------
# CLASSIFICATION
# --------------------------------------------------

def classify(status, redirects, error, redirect_allowlist):

    if error:
        return "INVESTIGATE"

    if status in (404, 410):
        return "LIKELY DEAD"

    if status is None:
        return "INVESTIGATE"

    if status == 200 or 200 <= status < 300:

        unapproved_redirects = [
            redirect
            for redirect in redirects
            if not redirect_is_approved(redirect, redirect_allowlist)
        ]

        if len(unapproved_redirects) > 1:
            return "REVIEW MULTIPLE REDIRECTS"

        if len(unapproved_redirects) == 1:
            return "REVIEW REDIRECT"

        return "OK"

    if 300 <= status < 400:
        return "INVESTIGATE REDIRECT"

    if status in (403, 429):
        return "INVESTIGATE - BLOCKED / RATE LIMITED"

    if status >= 500:
        return "INVESTIGATE - SERVER ERROR"

    if 400 <= status < 500:
        return "INVESTIGATE - HTTP ERROR"

    return "INVESTIGATE"


# --------------------------------------------------
# CHECK ONE URL
# --------------------------------------------------

def check_url(resource, redirect_allowlist):

    title = str(resource.get("title", "Untitled"))
    url = str(resource.get("url", "")).strip()
    category = str(resource.get("category", ""))
    resource_id = str(resource.get("id", ""))

    result = {
        "title": title,
        "id": resource_id,
        "category": category,
        "original_url": url,
        "final_url": "",
        "status": "",
        "classification": "",
        "redirect_count": 0,
        "redirect_chain": "",
        "error": "",
    }

    if not url.startswith(("http://", "https://")):
        result["classification"] = "INVALID URL"
        result["error"] = "URL is missing or is not HTTP/HTTPS"
        return result

    redirect_handler = TrackingRedirectHandler()

    opener = urllib.request.build_opener(redirect_handler)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Range": "bytes=0-0",
        },
        method="GET",
    )

    status = None
    final_url = url
    error = ""

    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            status = response.status
            final_url = response.geturl()

            # Read only a tiny portion of the response.
            response.read(1)

    except urllib.error.HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        exc.close()

    except (
        urllib.error.URLError,
        socket.timeout,
        TimeoutError,
        OSError,
        ValueError,
    ) as exc:
        error = str(exc)
        if isinstance(exc, urllib.error.URLError):
            error = str(exc.reason)

        final_url = getattr(exc, "url", "") or url

    redirects = redirect_handler.chain

    result["final_url"] = final_url
    result["status"] = status if status is not None else ""
    result["redirect_count"] = len(redirects)
    result["error"] = error

    result["redirect_chain"] = " | ".join(
        f'{item["status"]}: {item["from"]} -> {item["to"]}'
        for item in redirects
    )

    result["classification"] = classify(
        status, redirects, error, redirect_allowlist
    )

    return result


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Check Linkography resource URLs."
    )

    parser.add_argument(
        "--output",
        help="Optional custom CSV report path."
    )

    args = parser.parse_args()

    if not INPUT_FILE.exists():
        print(f"ERROR: Cannot find {INPUT_FILE}")
        sys.exit(1)

    print("\nLINKOGRAPHY DEAD LINK CHECKER")
    print("=" * 45)

    print(f"Reading: {INPUT_FILE}")

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            resources = yaml.safe_load(file)

    except yaml.YAMLError as exc:
        print(f"YAML ERROR: {exc}")
        sys.exit(1)

    if not isinstance(resources, list):
        print("ERROR: Expected a YAML list of resources.")
        sys.exit(1)

    print(f"Resources found: {len(resources)}")
    
    redirect_allowlist = load_redirect_allowlist()

    print(f"Approved redirect rules: {len(redirect_allowlist)}")
    print("Checking URLs...\n")

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(check_url, resource, redirect_allowlist): resource
            for resource in resources
        }

        for future in as_completed(futures):

            try:
                result = future.result()
                results.append(result)

                print(
                    f'[{result["classification"]}] '
                    f'{result["title"]} '
                    f'({result["status"]})'
                )

            except Exception as exc:
                resource = futures[future]

                print(
                    f'[ERROR] {resource.get("title", "Unknown")}: {exc}'
                )

    # Preserve the original YAML order in the report.
    order = {
        str(resource.get("id", "")): index
        for index, resource in enumerate(resources)
    }

    results.sort(
        key=lambda item: order.get(item["id"], 999999)
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    output_file = (
        Path(args.output).resolve()
        if args.output
        else REPORT_DIR / f"link-check-{report_date}.csv"
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "title",
        "id",
        "category",
        "original_url",
        "final_url",
        "status",
        "classification",
        "redirect_count",
        "redirect_chain",
        "error",
    ]

    with open(output_file, "w", newline="", encoding="utf-8-sig") as file:

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    counts = {}

    for result in results:
        classification = result["classification"]
        counts[classification] = counts.get(classification, 0) + 1

    print("\n" + "=" * 45)
    print("CHECK COMPLETE")
    print("=" * 45)

    for classification, count in sorted(counts.items()):
        print(f"{classification}: {count}")

    print(f"\nTotal resources: {len(results)}")
    print(f"Report saved: {output_file}")

    print("\nNo YAML records were modified.")


if __name__ == "__main__":
    main()
