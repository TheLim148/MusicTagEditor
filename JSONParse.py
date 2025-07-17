import json
import acoustid
import httpx
import asyncio
import socket
import subprocess
import time
import os

def isTorRunning(host="127.0.0.1", port=9050):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

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
            return data
        except httpx.HTTPStatusError as e:
            return {"error": "HTTP error", "details": repr(e)}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": repr(e)}


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
            return data
            # for medium in data.get("media", []):
            #     for track in medium.get("tracks", []):
            #         if track["recording"]["id"] == recording_id:
            #             return {
            #                 "track_number": track["number"],
            #                 "track_title": track["title"],
            #                 "medium_title": medium.get("title", "Unknown Medium"),
            #                 "release_id": release_id
            #             }

            # return {"error": "Track not found in release"}

        except httpx.HTTPStatusError as e:
            return {"error": "HTTP error", "details": str(e)}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": str(e)}

API_KEY = "hv3SsHefpw"
USER_API_KEY = "FnlllFTowF"

JSON_TEMPLATE = '''
            "albums": [
                {
                    "albumTitle": "",
                    "date": ,
                    "genres": [],
                    "coverPath": "",
                    "tracks": [
                        {
                            "title": "", "trackno": , "lenght": , "fingerprint": ""
                        }
                    ]
                }
            ]
'''

    # for score, recording_id, title, artist in acoustid.match(API_KEY, os.path.join("testFolder", "1.mp3")):
    #     print(f"\n{score}, {recording_id}, {title}, {artist}")

# duration, fingerprint = acoustid.fingerprint_file("testFolder\\1​.mp3")

# dataa = acoustid.lookup(API_KEY, fingerprint, duration)
# print(dataa)

# print(duration, fingerprint)

def printData(dataFile):
    with open(dataFile, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for artist in data["artists"]:
        print(f"{artist["name"]}")
        if "albums" in artist:
            for album in artist["albums"]:
                if "albumTitle" in album or "date" in album:
                    print(f"|-{album["albumTitle"]}")
                    print(f"|-{album["date"]}")
                    for genre in album["genres"]:
                        print(f"|---{genre}")
                    for track in album["tracks"]:
                        print(f"|---{track["trackno"]}, {track["title"]}, {track["length"]}")
                else:
                    print("|-(нету названия или даты)")
        else:
            print("|-(нету альбомов)")

def writeToData(dataFile, foo):
    with open(dataFile, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # foo
    # JSON_TEMPLATE

    with open(dataFile, "w", encoding="utf-8") as f:
        json.dump(data, foo, indent=2)

async def main():
    recording_id = "200f0b3f-5001-4b86-a95d-75bec48c293b"

    release_id = "0a91eab7-f566-4dd2-93b9-8b69a3f0f891"
    result1 = await get_track_number_in_release(release_id, recording_id)

    result = await get_musicbrainz_data(recording_id)
    with open("trackInfo.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    with open("albumInfo.json", "w", encoding="utf-8") as f:
        json.dump(result1, f, indent=2, ensure_ascii=False)

    print(result)

if __name__ == "__main__":
    if isTorRunning():
        print("Tor is already runnig")
    else:
        print("Trying to start Tor")
        with open("config.json", "r") as f:
            cfg = json.load(f)
        subprocess.Popen(
            [cfg["tor_path"], "-f", cfg["torrc_path"]],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        time.sleep(5)
    
    asyncio.run(main())