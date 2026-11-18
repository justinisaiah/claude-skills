#!/usr/bin/env python3
"""iPhone Duo stock tracker for selected Apple Stores.

Polls Apple's fulfillment-messages endpoint (the same one apple.com uses for
"Pickup" availability) and reports when a configured model becomes available
for pickup at one of the configured stores.

Standard library only. Usage:
    python3 tracker.py                 # poll forever using config.json
    python3 tracker.py --once          # single check, then exit
    python3 tracker.py --config my.json --interval 120
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

FULFILLMENT_URL = "https://www.apple.com/shop/fulfillment-messages"
USER_AGENT = "Mozilla/5.0 (compatible; stock-tracker/1.0)"
PLACEHOLDER_PREFIX = "TODO"


@dataclass
class StoreAvailability:
    store_name: str
    store_number: str
    part_number: str
    model_label: str
    available: bool
    quote: str


def load_config(path: Path) -> dict:
    with path.open() as f:
        cfg = json.load(f)
    problems = []
    for s in cfg.get("stores", []):
        if str(s.get("store_number", "")).startswith(PLACEHOLDER_PREFIX):
            problems.append(f"store '{s.get('name')}' has no store_number")
    for m in cfg.get("models", []):
        if str(m.get("part_number", "")).startswith(PLACEHOLDER_PREFIX):
            problems.append(f"model '{m.get('label')}' has no part_number")
    if problems:
        raise SystemExit("Config incomplete:\n  - " + "\n  - ".join(problems))
    return cfg


def build_url(store_number: str, part_numbers: list[str], zip_code: str) -> str:
    params = {"store": store_number, "location": zip_code}
    for i, part in enumerate(part_numbers):
        params[f"parts.{i}"] = part
    return f"{FULFILLMENT_URL}?{urllib.parse.urlencode(params)}"


def fetch_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_availability(payload: dict, store_number: str, models: list[dict]) -> list[StoreAvailability]:
    """Extract per-part pickup availability from a fulfillment-messages response.

    Expected shape: body.content.pickupMessage.stores[] each with storeNumber,
    storeName and partsAvailability{<part>: {pickupDisplay: "available"|"unavailable"}}.
    """
    results: list[StoreAvailability] = []
    stores = (
        payload.get("body", {})
        .get("content", {})
        .get("pickupMessage", {})
        .get("stores", [])
    )
    for store in stores:
        if str(store.get("storeNumber", "")) != store_number:
            continue
        parts = store.get("partsAvailability", {})
        for model in models:
            info = parts.get(model["part_number"], {})
            display = info.get("pickupDisplay", "unknown")
            results.append(
                StoreAvailability(
                    store_name=store.get("storeName", store_number),
                    store_number=store_number,
                    part_number=model["part_number"],
                    model_label=model["label"],
                    available=display == "available",
                    quote=info.get("pickupSearchQuote", display),
                )
            )
    return results


def check_once(cfg: dict) -> list[StoreAvailability]:
    all_results: list[StoreAvailability] = []
    part_numbers = [m["part_number"] for m in cfg["models"]]
    for store in cfg["stores"]:
        url = build_url(store["store_number"], part_numbers, cfg["zip_code"])
        try:
            payload = fetch_json(url)
        except Exception as exc:  # network or JSON error: report and keep going
            print(f"[{ts()}] WARN {store['name']}: request failed: {exc}", file=sys.stderr)
            continue
        all_results.extend(parse_availability(payload, store["store_number"], cfg["models"]))
    return all_results


def notify(cfg: dict, message: str) -> None:
    print(f"[{ts()}] {message}", flush=True)
    topic = os.environ.get("NTFY_TOPIC") or cfg.get("ntfy_topic")
    if topic:
        try:
            req = urllib.request.Request(
                f"https://ntfy.sh/{urllib.parse.quote(topic)}",
                data=message.encode("utf-8"),
                headers={"Title": "iPhone Duo in stock", "Priority": "high"},
            )
            urllib.request.urlopen(req, timeout=10).read()
        except Exception as exc:
            print(f"[{ts()}] WARN ntfy push failed: {exc}", file=sys.stderr)


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cfg: dict, interval: int, once: bool) -> None:
    previously_available: set[tuple[str, str]] = set()
    while True:
        results = check_once(cfg)
        now_available = {(r.store_number, r.part_number) for r in results if r.available}
        for r in results:
            key = (r.store_number, r.part_number)
            if r.available and key not in previously_available:
                notify(cfg, f"IN STOCK for pickup: {r.model_label} at {r.store_name} ({r.quote})")
        if not results:
            print(f"[{ts()}] no results returned", flush=True)
        else:
            summary = ", ".join(
                f"{r.store_name.split()[-1]}/{r.model_label}={'yes' if r.available else 'no'}"
                for r in results
            )
            print(f"[{ts()}] {summary}", flush=True)
        previously_available = now_available
        if once:
            return
        time.sleep(interval)


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, default=here / "config.json")
    parser.add_argument("--interval", type=int, default=None, help="seconds between checks")
    parser.add_argument("--once", action="store_true", help="check once and exit")
    args = parser.parse_args()

    cfg = load_config(args.config)
    interval = args.interval or cfg.get("interval_seconds", 300)
    try:
        run(cfg, interval, args.once)
    except KeyboardInterrupt:
        print("\nstopped", flush=True)


if __name__ == "__main__":
    main()
