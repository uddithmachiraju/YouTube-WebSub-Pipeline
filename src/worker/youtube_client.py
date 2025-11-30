import asyncio

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.logging import LoggerMixin, setup_logging
from src.config.settings import get_settings

setup_logging()
settings = get_settings()


class YoutubeClient(LoggerMixin):
    """API Client for fetching YouTube metadata."""

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self) -> None:
        """Initialize the YouTube client."""

        self.api_key = settings.google_gemini_api_key
        if not self.api_key:
            self.logger.error("Google Gemini API key is not set in the configuration.")
            raise ValueError("Google Gemini API key is required.")
        self.client = httpx.AsyncClient(base_url=self.BASE_URL)
        self._rate_limit_lock = asyncio.Semaphore(10)  # Limiting to 10 concurrent requests

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def fetch_video_metadata(self, video_id: str) -> dict | None:
        """Fetch metadata for a given YouTube video ID."""

        async with self._rate_limit_lock:
            try:
                response = await self.client.get(
                    f"{self.BASE_URL}/videos",
                    params={
                        "part": "snippet,contentDetails,statistics",
                        "id": video_id,
                        "key": self.api_key,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                items = data.get("items", [])
                if not items:
                    self.logger.warning(f"No metadata found for video ID: {video_id}")
                    return None
                return items[0]
            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP error while fetching video {video_id}: {e}")
                raise
            except httpx.RequestError as e:
                self.logger.error(f"Request error while fetching video {video_id}: {e}")
                raise

    async def get_channel_videos(self, channel_id: str, max_results: int = 5) -> list[dict]:
        """Get a list of videos for a given channel ID."""

        async with self._rate_limit_lock:
            try:
                response = await self.client.get(
                    f"{self.BASE_URL}/search",
                    params={
                        "part": "snippet",
                        "channelId": channel_id,
                        "maxResults": max_results,
                        "order": "date",
                        "type": "video",
                        "key": self.api_key,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return [
                    item["id"]["videoId"]
                    for item in data.get("items", [])
                    if "videoId" in item["id"]
                ]
            except httpx.HTTPStatusError as e:
                self.logger.error(f"HTTP error while fetching videos for channel {channel_id}: {e}")
                raise
            except httpx.RequestError as e:
                self.logger.error(
                    f"Request error while fetching videos for channel {channel_id}: {e}"
                )
                raise

    async def close(self) -> None:
        """Close the HTTP client session."""

        await self.client.aclose()


if __name__ == "__main__":

    async def main():
        youtube_client = YoutubeClient()
        video_id = "OCW4I4PAs9k"
        metadata = await youtube_client.fetch_video_metadata(video_id)
        print(metadata)
        await youtube_client.close()

    asyncio.run(main())
