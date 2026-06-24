"""API Documentation page for TranscriptBuddy."""

from __future__ import annotations

import streamlit as st

from src.styles import inject_css

st.set_page_config(
    page_title="API Documentation — TranscriptBuddy",
    page_icon="📡",
    layout="centered",
)
inject_css()

st.markdown(
    """
    <div class="tb-hero" style="padding:2rem;">
        <h1 style="font-size:2.2rem;">API Documentation</h1>
        <p>REST API for YouTube transcripts, search, channels and playlists</p>
    </div>
    """,
    unsafe_allow_html=True,
)

BASE = "`http://localhost:8000`"

st.markdown(f"""
### Base URL

All API requests go to: {BASE}

### Quick Start

```bash
curl "http://localhost:8000/api/v2/youtube/transcript?video_url=dQw4w9WgXcQ"
```

---
""")

# ── Transcript ──────────────────────────────────────────────────────────
st.markdown("## Transcript")
st.markdown("""
```
GET /api/v2/youtube/transcript
```

Extract the transcript from a YouTube video.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video_url` | string | Yes | — | YouTube URL or video ID |
| `format` | string | No | `json` | `json` or `text` |
| `include_timestamp` | bool | No | `true` | Include timestamps |
| `send_metadata` | bool | No | `false` | Include video metadata |
""")

with st.expander("Example response (JSON with timestamps)"):
    st.code("""{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "transcript": [
    {
      "text": "Never gonna give you up",
      "start": 0.0,
      "duration": 4.12
    },
    {
      "text": "Never gonna let you down",
      "start": 4.12,
      "duration": 3.85
    }
  ]
}""", language="json")

with st.expander("Format & timestamp combinations"):
    st.markdown("""
| Format | include_timestamp | Output |
|--------|------------------|--------|
| `json` | `true` | Segments with `text`, `start`, `duration` |
| `json` | `false` | Segments with only `text` |
| `text` | `true` | Lines as `[123.45s] text` |
| `text` | `false` | Plain concatenated text |
""")

st.divider()

# ── Search ──────────────────────────────────────────────────────────────
st.markdown("## Search")
st.markdown("""
```
GET /api/v2/youtube/search
```

Search YouTube for videos or channels.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | — | Search query (1–200 chars) |
| `type` | string | No | `video` | `video` or `channel` |
""")

with st.expander("Example response"):
    st.code("""{
  "results": [
    {
      "type": "video",
      "videoId": "abc123xyz00",
      "title": "Example Video",
      "channelTitle": "Example Channel",
      "lengthText": "12:34",
      "viewCountText": "3.4M views",
      "thumbnails": [...]
    }
  ],
  "result_count": 20,
  "continuation_token": null,
  "has_more": false
}""", language="json")

st.divider()

# ── Channel ─────────────────────────────────────────────────────────────
st.markdown("## Channel Endpoints")

st.markdown("""
### Resolve Channel
```
GET /api/v2/youtube/channel/resolve
```
Resolve any @handle, URL, or UC… ID to a channel ID. **Free.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | string | Yes | @handle, channel URL, or UC… ID |
""")

with st.expander("Example response"):
    st.code("""{
  "channel_id": "UCAuUUnT6oDeKwE6v1NGQxug",
  "resolved_from": "@TED"
}""", language="json")

st.markdown("""
### Search Within Channel
```
GET /api/v2/youtube/channel/search
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | Yes | @handle, URL, or UC… ID |
| `q` | string | Yes | Search query |
""")

st.markdown("""
### Channel Videos
```
GET /api/v2/youtube/channel/videos
```
List all uploaded videos from a channel.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | Yes | @handle, URL, or UC… ID |
""")

st.markdown("""
### Channel Latest (RSS)
```
GET /api/v2/youtube/channel/latest
```
Get the latest ~15 videos via YouTube RSS feed. **Free.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `channel` | string | Yes | @handle, URL, or UC… ID |
""")

with st.expander("Example response"):
    st.code("""{
  "channel": {
    "channelId": "UCAuUUnT6oDeKwE6v1NGQxug",
    "title": "TED",
    "author": "TED",
    "url": "https://www.youtube.com/channel/UCAuUUnT6oDeKwE6v1NGQxug",
    "published": "2006-12-18T00:00:00Z"
  },
  "results": [
    {
      "videoId": "abc123xyz00",
      "title": "Latest Video",
      "published": "2026-01-30T16:00:00Z",
      "viewCount": "2287630",
      "thumbnail": { "url": "...", "width": "480", "height": "360" }
    }
  ],
  "result_count": 15
}""", language="json")

st.divider()

# ── Playlist ────────────────────────────────────────────────────────────
st.markdown("## Playlist")
st.markdown("""
```
GET /api/v2/youtube/playlist/videos
```
List videos in a playlist.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `playlist` | string | Yes | Playlist URL or ID (PL…, UU…, LL…) |
""")

with st.expander("Example response"):
    st.code("""{
  "results": [
    {
      "videoId": "abc123xyz00",
      "title": "Playlist Video",
      "channelTitle": "TED",
      "lengthText": "10:05",
      "viewCountText": "1.5M views",
      "thumbnails": [...]
    }
  ],
  "playlist_info": {
    "title": "Best Tech of 2025",
    "numVideos": "47",
    "ownerName": "TED"
  },
  "continuation_token": null,
  "has_more": false
}""", language="json")

st.divider()

# ── Error handling ──────────────────────────────────────────────────────
st.markdown("## Error Handling")
st.markdown("""
All errors return JSON:

```json
{
  "detail": {
    "detail": "Human-readable error message",
    "code": "ERROR_CODE"
  }
}
```

| Status | Meaning | Code |
|--------|---------|------|
| `200` | Success | — |
| `400` | Bad request | `INVALID_INPUT` |
| `404` | Not found / no transcript | `VIDEO_NOT_FOUND`, `NO_TRANSCRIPT`, `TRANSCRIPTS_DISABLED` |
| `408` | Blocked by YouTube | `REQUEST_BLOCKED` |
| `422` | Invalid URL | `INVALID_URL` |
| `500` | Server error | `INTERNAL_ERROR` |
""")

st.divider()

# ── Code examples ───────────────────────────────────────────────────────
st.markdown("## Code Examples")

tab_py, tab_js, tab_curl = st.tabs(["Python", "JavaScript", "cURL"])

with tab_py:
    st.code("""import requests

BASE = "http://localhost:8000/api/v2"

# Get transcript
resp = requests.get(f"{BASE}/youtube/transcript", params={
    "video_url": "dQw4w9WgXcQ",
    "format": "json",
    "include_timestamp": True,
})
data = resp.json()

for segment in data["transcript"]:
    print(f"[{segment['start']}s] {segment['text']}")

# Search videos
resp = requests.get(f"{BASE}/youtube/search", params={
    "q": "python tutorial",
    "type": "video",
})
for video in resp.json()["results"]:
    print(f"{video['title']} ({video['videoId']})")

# Channel latest
resp = requests.get(f"{BASE}/youtube/channel/latest", params={
    "channel": "@TED",
})
for video in resp.json()["results"]:
    print(f"{video['title']} - {video['viewCount']} views")
""", language="python")

with tab_js:
    st.code("""const BASE = "http://localhost:8000/api/v2";

// Get transcript
const resp = await fetch(
  `${BASE}/youtube/transcript?video_url=dQw4w9WgXcQ`
);
const data = await resp.json();
data.transcript.forEach(s => console.log(`[${s.start}s] ${s.text}`));

// Search
const search = await fetch(
  `${BASE}/youtube/search?q=python+tutorial&type=video`
);
const results = await search.json();
results.results.forEach(v => console.log(v.title));
""", language="javascript")

with tab_curl:
    st.code("""# Get transcript
curl "http://localhost:8000/api/v2/youtube/transcript?video_url=dQw4w9WgXcQ"

# Search videos
curl "http://localhost:8000/api/v2/youtube/search?q=python+tutorial&type=video"

# Channel resolve
curl "http://localhost:8000/api/v2/youtube/channel/resolve?input=@TED"

# Channel latest (RSS)
curl "http://localhost:8000/api/v2/youtube/channel/latest?channel=@TED"

# Channel videos
curl "http://localhost:8000/api/v2/youtube/channel/videos?channel=@TED"

# Playlist
curl "http://localhost:8000/api/v2/youtube/playlist/videos?playlist=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
""", language="bash")

st.divider()

st.markdown("## Interactive Docs")
st.info("Start the API server with `uv run uvicorn api:app --port 8000` and visit "
        "[localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.")

st.markdown(
    """
    <div class="tb-footer">
        <p>Built by <a href="https://www.linkedin.com/in/remseymailjard/" target="_blank">Remsey Mailjard</a>
        · Powered by FastAPI, youtube-transcript-api &amp; yt-dlp</p>
    </div>
    """,
    unsafe_allow_html=True,
)
