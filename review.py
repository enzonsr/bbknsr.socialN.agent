"""Local exact-revision approval and one-time handoff for a trusted operator."""
import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path


FORMATS = {"instagram": {"reel", "story", "feed"}, "youtube": {"short"}}
FIELDS = {"platform", "account", "format", "caption", "media", "audio_rights"}


def revision(manifest):
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.keys() != FIELDS:
        raise ValueError("Manifest must contain exactly: " + ", ".join(sorted(FIELDS)))
    if any(not isinstance(value, str) for value in data.values()):
        raise ValueError("Manifest values must be strings")
    if data["format"] not in FORMATS.get(data["platform"], set()):
        raise ValueError("Unsupported platform or format")
    if any(not data[key].strip() for key in FIELDS - {"caption"}):
        raise ValueError("Account, media and audio-rights evidence are required")
    media = manifest.parent / data["media"]
    if not media.is_file() or media.stat().st_size == 0:
        raise ValueError("Preview media must be a nonempty local file")
    with media.open("rb") as video:
        data["media_sha256"] = hashlib.file_digest(video, "sha256").hexdigest()
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest(), data


def record(database, action, digest):
    with closing(sqlite3.connect(database)) as db, db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS approvals "
            "(revision TEXT PRIMARY KEY, consumed INTEGER NOT NULL DEFAULT 0)"
        )
        if action == "approve":
            db.execute("INSERT OR IGNORE INTO approvals(revision) VALUES (?)", (digest,))
            return
        updated = db.execute(
            "UPDATE approvals SET consumed = 1 WHERE revision = ? AND consumed = 0",
            (digest,),
        )
        if updated.rowcount != 1:
            raise ValueError("This revision has no unused approval")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["preview", "approve", "handoff"])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--revision", help="Exact digest printed by preview")
    parser.add_argument("--database", type=Path, default=Path(".approvals.sqlite3"))
    args = parser.parse_args()
    try:
        digest, data = revision(args.manifest)
        if args.action != "preview":
            if args.revision != digest:
                raise ValueError("Review the preview and supply its exact revision")
            record(args.database, args.action, digest)
        print(json.dumps({"action": args.action, "revision": digest, **data},
                         ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
