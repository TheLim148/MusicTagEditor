import json
import acoustid
import httpx
import asyncio
import socket

import subprocess

import logging

import time
import os

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

logging.basicConfig(
    level=logging.DEBUG,
    filename="debug_log.txt",
    filemode="w",
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

# for score, recording_id, title, artist in acoustid.match(API_KEY, os.path.join("testFolder", "1.mp3")):
#     print(f"\n{score}, {recording_id}, {title}, {artist}")

# duration, fingerprint = acoustid.fingerprint_file("testFolder\\1​.mp3")

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

def send_newnym():
    with socket.create_connection(("127.0.0.1", 9051)) as s:
        s.sendall(b'AUTHENTICATE \"\"\r\nSIGNAL NEWNYM\r\nQUIT\r\n')

def isTorRunning(host="127.0.0.1", port=9050):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

def clear_terminal():
    print('\033[2J\033[H', end='')

def parse_track_info(data):
    if "releases" not in data or not data["releases"]:
        return {"error": "No releases found"}

    results = []
    
    for release in data.get("releases", []):
        for artist in release.get("artist-credit", []):
            if release.get("status") == "Official":
                results.append({
                    "release_id": release.get("id", ""),
                    "album_title": release.get("title", ""),
                    "year": release.get("date", "").split("-")[0],
                    "artist_name": artist.get("name", ""),
                    "tags": release.get("tags", []),
                    "length": data.get("length", 0),
                    "song_title": data.get("title", "")
                })
    return results

# def parse_album_info(data):

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
            return parse_track_info(data)
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
            for medium in data.get("media", []):
                for track in medium.get("tracks", []):
                    if track["recording"]["id"] == recording_id:
                        return {
                            "track_number": track["number"],
                            "track_title": track["title"],
                            "medium_title": medium.get("title", "Unknown Medium"),
                            "release_id": release_id
                        }
            return {"error": "Track not found in release"}

        except httpx.HTTPStatusError as e:
            return {"error": "HTTP error", "details": repr(e)}
        except httpx.RequestError as e:
            return {"error": "Request error", "details": repr(e)}

async def main():
    match = next(acoustid.match(API_KEY, os.path.join("testFolder", "1.mp3")), "")
    if match:
        score, recording_id, title, artist = match
    else:
        raise ValueError("Совпадений не найдено")
    
    max_attempts = 12
    max_newnym_retries = 3

    attempts = 0
    newnym_attempts = 0
    
    while attempts < max_attempts:
        result = await get_musicbrainz_data(recording_id)
        
        if isinstance(result, dict) and "error" in result:
            attempts += 1
            print(f"Попытка {attempts}/{max_attempts} | {result}")
            await asyncio.sleep(1)

            if attempts % 3 == 0:
                newnym_attempts += 1

                if newnym_attempts > max_newnym_retries:
                    raise ValueError("Не удалось получить данные после смены цепочки")

                send_newnym()
                print("Перезапуск цепочки... подождите 3 секунды")
                await asyncio.sleep(3)

            continue

        if isinstance(result, list) and result:
            release_id = result[0]["release_id"]
            break
    
    result1 = await get_track_number_in_release(release_id, recording_id)

    with open("trackInfo1.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    with open("albumInfo1.json", "w", encoding="utf-8") as f:
        json.dump(result1, f, indent=2, ensure_ascii=False)

    print(result)

if __name__ == "__main__":
    clear_terminal()
    
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

# recording_ids = list(acoustid.match(API_KEY, os.path.join("testFolder", "1.mp3")))
# recording_id = "200f0b3f-5001-4b86-a95d-75bec48c293b"
# release_id = "0a91eab7-f566-4dd2-93b9-8b69a3f0f891"