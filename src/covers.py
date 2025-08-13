from pathlib import Path
import httpx
import os

async def get_cover_url(release_id):
    url = f"https://coverartarchive.org/release/{release_id}"
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            for image in data.get("images", []):
                if image.get("front"):
                    return image.get("image")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return None

async def download_image(url, path_to_save):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        with open (Path(os.path.expanduser(path_to_save)), "wb") as f:
            f.write(response.content)