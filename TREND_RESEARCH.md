# Trend research

Run `python trends.py observations.jsonl --query 'زیتون olive' --limit 10`.

Each line is one observation. Use a platform-native ID consistently and record
timestamps with a timezone offset. Example fixture:

```json
{"platform":"instagram","id":"example","url":"https://example.test/video","title":"زیتون","caption":"Olive tasting","opening":"۳ روش سرو زیتون","published_at":"2026-11-22T12:00:00Z","observed_at":"2026-11-22T17:00:00Z","views":120}
```

The CLI keeps the newest snapshot per platform and ID, filters by matching
any normalized query word, and ranks view velocity within each platform and
logarithmic age band. Percentiles describe the input cohort only. A singleton
has percentile 0.5. Unknown views are counted separately. The report excludes
opening text and preserves source links, observed hook categories and cohort
sizes. The experiment changes the opening and holds the body and CTA constant.

Use approved exports or official APIs to produce observations. Supply a real
first spoken or visible line as `opening`; leave it empty if unavailable.
This CLI applies lexical rules. It does not transcribe videos, infer retention,
establish causation, generate video, connect accounts or publish anything.

## Upstream review

- [Postiz](https://github.com/gitroomhq/postiz-app) demonstrates social provider adapters and scheduling. Use the adapter design as a reference and avoid vendoring its application.
- [Mixpost](https://github.com/inovector/mixpost) is an MIT-licensed reference for calendars and scheduling. Its application runtime is separate from this Python research pipeline.
- [PySceneDetect](https://github.com/Breakthrough/PySceneDetect/blob/main/LICENSE) is BSD-3-Clause. Evaluate as an optional next step for detecting cuts in authorized local media.
- [Google API Python Client](https://github.com/googleapis/google-api-python-client) is an official client for a future YouTube discovery adapter.

No upstream code is vendored in this implementation.
