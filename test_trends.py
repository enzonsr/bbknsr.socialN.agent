import unittest

from trends import analyze, timestamp


NOW = timestamp("2026-11-22T18:00:00Z")


def observation(identifier, platform, views, opening="زیتون چطور سرو شود؟", **changes):
    return {
        "id": identifier, "platform": platform, "views": views, "opening": opening,
        "url": f"https://example.test/{identifier}", "title": "زيتون",
        "published_at": "2026-11-22T12:00:00Z", "observed_at": "2026-11-22T17:00:00Z",
        **changes,
    }


class TrendTests(unittest.TestCase):
    def test_ranks_within_platform_and_deduplicates(self):
        rows = [
            observation("a", "instagram", 1, observed_at="2026-11-22T16:00:00Z"),
            observation("a", "instagram", 120),
            observation("b", "instagram", 10),
            observation("c", "youtube", 9_000_000, opening=""),
            observation("d", "youtube", None),
        ]
        report = analyze(rows, "زیتون", NOW, 3)
        self.assertEqual([row["id"] for row in report["top"]], ["a", "c", "b"])
        self.assertEqual(report["missing_views"], 1)
        self.assertEqual(report["observed_hook_patterns"], {"question": 2})

    def test_topic_and_ties(self):
        rows = [
            observation("b", "youtube", 20, opening="۳ روش سرو"),
            observation("a", "youtube", 20),
            observation("c", "youtube", 100, opening="پیاز", title="پیاز"),
        ]
        report = analyze(rows, "زیتون", NOW, 2)
        self.assertEqual([row["percentile"] for row in report["top"]], [0.5, 0.5])
        self.assertEqual(report["observed_hook_patterns"], {"question": 1, "number": 1})

    def test_rejects_future_observation(self):
        row = observation("a", "instagram", 10, observed_at="2026-11-22T19:00:00Z")
        with self.assertRaises(ValueError):
            analyze([row], "زیتون", NOW, 2)
