"""Rank supplied social observations and extract opening-hook patterns."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import heapq
import json
import math
from pathlib import Path
import re
import unicodedata

WORD = re.compile(r"[^\W_]+", re.UNICODE)
DIGIT = re.compile(r"\d")
TRANSLATION = str.maketrans({"ي": "ی", "ك": "ک", "\u200c": " "})
PLATFORMS = {"instagram", "youtube", "tiktok", "facebook", "threads", "x", "pinterest", "linkedin"}


def words(value):
    value = unicodedata.normalize("NFKC", value).casefold().translate(TRANSLATION)
    return set(WORD.findall(value))


def hook_type(opening):
    if not opening.strip():
        return "unknown"
    if "?" in opening or "؟" in opening:
        return "question"
    if DIGIT.search(opening):
        return "number"
    if words(opening) & {"instead", "versus", "vs", "اما", "بجای", "به‌جای"}:
        return "contrast"
    return "statement"


def timestamp(value):
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.utcoffset() is None:
        raise ValueError("timestamps require a UTC offset")
    return date


def analyze(rows, query, now, limit):
    if limit < 1:
        raise ValueError("limit must be positive")
    terms = words(query)
    if not terms:
        raise ValueError("query must contain searchable words")
    latest = {}
    for row in rows:
        platform = row["platform"]
        if platform not in PLATFORMS:
            raise ValueError(f"unsupported platform: {platform}")
        published = timestamp(row["published_at"])
        observed = timestamp(row["observed_at"])
        views = row.get("views")
        if published > observed or observed > now:
            raise ValueError("expected published_at <= observed_at <= as_of")
        if views is not None and (type(views) is not int or views < 0):
            raise ValueError("views must be a nonnegative integer or null")
        key = platform, row["id"]
        if key not in latest or observed > latest[key][1]:
            latest[key] = published, observed, row

    cohorts = defaultdict(list)
    missing_views = 0
    for published, observed, row in latest.values():
        text = " ".join(row.get(field, "") for field in ("title", "caption", "opening"))
        if terms.isdisjoint(words(text)):
            continue
        if row.get("views") is None:
            missing_views += 1
            continue
        hours = max(1, (observed - published).total_seconds() / 3600)
        age = int(math.log2(hours))
        score = row["views"] / hours
        cohorts[row["platform"], age].append((score, row))

    candidates = []
    for (platform, age), cohort in cohorts.items():
        scores = Counter(score for score, _ in cohort)
        below, percentiles = 0, {}
        for score, count in sorted(scores.items()):
            percentiles[score] = (below + count / 2) / len(cohort)
            below += count
        for score, row in cohort:
            candidates.append({
                "platform": platform, "id": row["id"], "url": row["url"],
                "observed_at": row["observed_at"], "age_bucket": age,
                "cohort_size": len(cohort), "percentile": percentiles[score],
                "views_per_hour": round(score, 2),
                "hook_type": hook_type(row.get("opening", "")),
            })
    top = heapq.nsmallest(
        limit, candidates,
        key=lambda item: (-item["percentile"], -item["cohort_size"],
                          item["platform"], item["id"]),
    )
    patterns = Counter(item["hook_type"] for item in top if item["hook_type"] != "unknown")
    return {"query": query, "matched_rankable": len(candidates), "missing_views": missing_views,
            "top": top, "observed_hook_patterns": patterns,
            "experiment": {
                "change": "opening only",
                "variants": ["ask an original audience question", "open on an original visual result"],
                "hold_constant": ["topic", "body", "duration", "CTA"],
                "measure": "early retention on owned accounts",
            }}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 JSON Lines observations")
    parser.add_argument("--query", required=True)
    parser.add_argument("--as-of", type=timestamp)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    try:
        with args.input.open(encoding="utf-8") as source:
            rows = (json.loads(line) for line in source if line.strip())
            report = analyze(rows, args.query, args.as_of or datetime.now(timezone.utc), args.limit)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, f"Invalid observations: {error}\n")


if __name__ == "__main__":
    main()
