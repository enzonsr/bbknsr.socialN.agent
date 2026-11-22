import json
import tempfile
import unittest
from pathlib import Path

from review import record, revision


class ReviewTests(unittest.TestCase):
    def test_approval_is_required_and_consumed_once(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "approvals.db"
            with self.assertRaises(ValueError):
                record(database, "handoff", "original")
            record(database, "approve", "original")
            with self.assertRaises(ValueError):
                record(database, "handoff", "edited")
            record(database, "handoff", "original")
            record(database, "approve", "original")
            with self.assertRaises(ValueError):
                record(database, "handoff", "original")

    def test_revision_changes_with_media_and_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "draft.json"
            media = manifest.with_name("preview.mp4")
            media.write_bytes(b"original")
            fields = dict(platform="instagram", format="reel", account="brand",
                          caption="Draft", media=media.name, audio_rights="silent")
            manifest.write_text(json.dumps(fields))
            original, _ = revision(manifest)
            media.write_bytes(b"replacement")
            edited, _ = revision(manifest)
            self.assertNotEqual(original, edited)
            fields["account"] = "another-brand"
            manifest.write_text(json.dumps(fields))
            redirected, _ = revision(manifest)
            self.assertNotEqual(edited, redirected)
