from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build


def fetch_viral_candidates(api_key: str, channel_id: str, max_results: int = 15) -> list[dict[str, Any]]:
    youtube = build('youtube', 'v3', developerKey=api_key)

    search_req = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=max_results,
        order='viewCount',
        type='video',
    )
    search_resp = search_req.execute()

    video_ids = [item['id']['videoId'] for item in search_resp.get('items', [])]
    if not video_ids:
        return []

    videos_resp = youtube.videos().list(part='snippet,statistics', id=','.join(video_ids)).execute()

    result = []
    for item in videos_resp.get('items', []):
        stats = item.get('statistics', {})
        snippet = item.get('snippet', {})
        tags = snippet.get('tags', [])
        result.append(
            {
                'video_id': item['id'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'hashtags': ' '.join([f'#{t}' for t in tags[:15]]),
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
            }
        )
    return result


def compute_engagement(item: dict[str, Any]) -> float:
    views = max(item['views'], 1)
    weighted = (item['likes'] * 1.0) + (item['comments'] * 2.0)
    return round(weighted / views, 5)
