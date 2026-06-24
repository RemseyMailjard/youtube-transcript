"""YouTube channel RSS feed parser.

Haalt de laatste ~15 videos op via YouTube's publieke RSS feed.
Geen API key nodig, geen credits.
"""

from __future__ import annotations

import re
from typing import Any
from xml.etree import ElementTree

import requests

_UC_RE = re.compile(r"^UC[A-Za-z0-9_-]{22}$")

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}

_RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def _resolve_to_channel_id(input_value: str) -> str:
    """Resolve @handle of URL naar UC… channel ID voor RSS feed."""
    v = input_value.strip()
    if _UC_RE.match(v):
        return v

    if v.startswith("@"):
        url = f"https://www.youtube.com/{v}"
    elif "youtube.com" in v:
        url = v
    else:
        raise ValueError(f"Cannot resolve channel for RSS: {input_value!r}")

    resp = requests.get(url, timeout=15, allow_redirects=True)
    resp.raise_for_status()
    match = re.search(r'"externalId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"', resp.text)
    if not match:
        match = re.search(r'channel_id=(UC[A-Za-z0-9_-]{22})', resp.text)
    if not match:
        raise ValueError(f"Could not find channel ID in page: {input_value!r}")
    return match.group(1)


def get_channel_latest(channel: str) -> dict[str, Any]:
    """Haal de laatste ~15 videos op via YouTube RSS feed."""
    channel_id = _resolve_to_channel_id(channel)
    feed_url = _RSS_URL.format(channel_id=channel_id)

    resp = requests.get(feed_url, timeout=15)
    resp.raise_for_status()

    root = ElementTree.fromstring(resp.content)

    channel_info = {
        "channelId": channel_id,
        "title": _text(root, "atom:title"),
        "author": _text(root, "atom:author/atom:name"),
        "url": f"https://www.youtube.com/channel/{channel_id}",
        "published": _text(root, "atom:published"),
    }

    results: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", _NS):
        video_id = _text(entry, "yt:videoId")
        media_group = entry.find("media:group", _NS)

        thumbnail_url = ""
        if media_group is not None:
            thumb_el = media_group.find("media:thumbnail", _NS)
            if thumb_el is not None:
                thumbnail_url = thumb_el.get("url", "")

        media_community = None
        if media_group is not None:
            media_community = media_group.find("media:community", _NS)

        view_count = ""
        star_rating: dict[str, str] | None = None
        if media_community is not None:
            stats = media_community.find("media:statistics", _NS)
            if stats is not None:
                view_count = stats.get("views", "")
            rating = media_community.find("media:starRating", _NS)
            if rating is not None:
                star_rating = {
                    "average": rating.get("average", ""),
                    "count": rating.get("count", ""),
                    "min": rating.get("min", ""),
                    "max": rating.get("max", ""),
                }

        description = ""
        if media_group is not None:
            desc_el = media_group.find("media:description", _NS)
            if desc_el is not None and desc_el.text:
                description = desc_el.text

        results.append({
            "videoId": video_id,
            "title": _text(entry, "atom:title"),
            "channelId": channel_id,
            "author": channel_info["author"],
            "published": _text(entry, "atom:published"),
            "updated": _text(entry, "atom:updated"),
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "description": description,
            "thumbnail": {
                "url": thumbnail_url,
                "width": "480",
                "height": "360",
            },
            "viewCount": view_count,
            "starRating": star_rating,
        })

    return {
        "channel": channel_info,
        "results": results,
        "result_count": len(results),
    }


def _text(el: ElementTree.Element, path: str) -> str:
    found = el.find(path, _NS)
    if found is not None and found.text:
        return found.text
    return ""
