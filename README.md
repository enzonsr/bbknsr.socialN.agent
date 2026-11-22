# bbknsr.socialN.agent

An editorial skill and local approval prototype for Instagram and YouTube short-form content. The skill covers trend research, original content development, audio rights and inbound sales. The Python 3.11+ CLI previews a revision, records local operator approval and emits a one-time manual handoff. It makes no external calls.

## Quick start

Load `skills/bbknsr-socialn-agent/SKILL.md` in a compatible agent. Create a JSON manifest next to your rendered video, for example:

```json
{
  "platform": "instagram",
  "account": "your-business-account",
  "format": "reel",
  "caption": "How to build an olive tasting board in 20 seconds",
  "media": "preview.mp4",
  "audio_rights": "Silent export"
}
```

```sh
python review.py preview draft.json
python review.py approve draft.json --revision DIGEST_FROM_PREVIEW
python review.py handoff draft.json --revision DIGEST_FROM_PREVIEW
python -m unittest -v
```

The digest binds the caption, format, account, audio-rights declaration and media contents. Handoff consumes approval atomically. The local operator account and writable filesystem are the trust boundary. Keep the database and approval command inaccessible to a drafting agent. Audio rights are an operator declaration. For server publishing, add authenticated owner approval, immutable media storage, a durable outbox, platform receipts and reconciliation before any live sends.

## Integration roadmap

| Stage | Scope |
|---|---|
| 1 | Read-only YouTube search by niche plus video statistics, and Instagram owner insights or eligible discovery endpoints. Track sources and data gaps. The YouTube `mostPopular` chart is limited to music, movies and gaming. |
| 2 | Original 15–35 second previews, burned-in Persian subtitles, variants for Reel, Story, feed and Short, and licensed or original audio per platform. |
| 3 | Publish only the approved revision to the exact destination. Meta professional-account permissions and Story eligibility vary. Verify YouTube OAuth, project upload eligibility and visibility before enabling live publishing. |
| 4 | Instagram inbound webhook verification and event deduplication, catalog-backed replies, pending orders, hosted checkout and verified payment callbacks. Use a separate policy for any public YouTube comment reply. |

## Upstream candidates

- [Google API Python Client](https://github.com/googleapis/google-api-python-client) is the official Python client candidate for YouTube integration.
- [MoviePy](https://github.com/Zulko/moviepy) is a candidate for local composition and rendering. Verify shaping and caption placement on Persian samples before selecting a rendering pipeline.

The prototype uses Python's standard library. Contributions should identify upstream sources and their licenses, include synthetic fixtures and keep tokens, customer conversations and private catalog data out of the repository.

[Meta Instagram API](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api) · [YouTube chart changes](https://developers.google.com/youtube/v3/revision_history) · [YouTube upload](https://developers.google.com/youtube/v3/docs/videos/insert)
