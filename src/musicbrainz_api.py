import parsers as parse
import httpx
import json

async def get_musicbrainz_data(recording_id):
    url = f"https://musicbrainz.org/ws/2/recording/{recording_id}"

    params = {
        "inc": "artists+releases+tags",
        "fmt": "json"
    }

    headers = {
        "User-Agent": "MyMusicTagger/1.0 (myemail@example.com)"
    }

    transport = httpx.AsyncHTTPTransport(
        proxy="socks5h://127.0.0.1:9050"
    )

    async with httpx.AsyncClient(transport=transport, timeout=15) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # with open("trackInfo.json", "w", encoding="utf-8") as f:
                # json.dump(data, f, indent=2, ensure_ascii=False)

            print("Информация о треке была получена")
            return parse.parse_track_info(data)
        except httpx.HTTPStatusError as e:
            return {"error": "HTTP error", "details": repr(e)}
        except httpx.RequestError as e:
            cause = e.__cause__
            cause_msg = f"{type(cause).__name__}: {cause}" if cause else repr(e)
            return {"error": "Request error", "details": cause_msg}


async def get_track_number_in_release(release_id, recording_id):
    url = f"https://musicbrainz.org/ws/2/release/{release_id}"

    params = {
        "inc": "recordings",
        "fmt": "json"
    }

    headers = {
        "User-Agent": "MyMusicTagger/1.0 (myemail@example.com)"
    }

    proxy = "socks5h://127.0.0.1:9050"
    transport = httpx.AsyncHTTPTransport(proxy=proxy)

    async with httpx.AsyncClient(transport=transport, timeout=15) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            # with open("albumInfo.json", "w", encoding="utf-8") as f:
                # json.dump(data, f, indent=2, ensure_ascii=False)

            print("Информация об альбоме была получена")
            return parse.parse_album_info(data, release_id, recording_id)
        except httpx.HTTPStatusError as e:
            return {"error": "HTTP error", "details": repr(e)}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": repr(e)}