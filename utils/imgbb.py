import httpx
from pydantic import HttpUrl

from core import settings


async def upload(file_base64: str) -> str | HttpUrl:
    async with httpx.AsyncClient() as client:
        url = "https://api.imgbb.com/1/upload"
        params = {
            "key": settings.IMGBB_API_KEY,
            "image": file_base64,
        }
        response = await client.post(url, data=params)
        result = response.json()
        print(result)
        if response.status_code == 200:
            return result["data"]["url"]
        else:
            raise ValueError(f"Failed to upload image: {result['error']['message']}")
