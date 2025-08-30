import os
import json
import acoustid

import asyncio
import logging

import musicbrainz_api as mb_api
import tor_utils as tor
import covers
import parsers as parse

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
                            "title": "", "trackno": , "length": , "fingerprint": ""
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

def clear_terminal():
    print('\033[2J\033[H', end='')

async def main(dir_from, file_name):
    with open("config.json", "r") as f:
        cfg = json.load(f)
    clear_terminal()
    tor.start_tor()

    match = next(acoustid.match(API_KEY, os.path.join(dir_from, file_name)), "")
    if match:
        score, recording_id, title, artist = match
    else:
        raise ValueError("Совпадений не найдено")
    
    max_attempts = 12
    max_newnym_retries = 3

    attempts = 0
    newnym_attempts = 0

    while attempts < max_attempts:
        track_info = await mb_api.get_musicbrainz_data(recording_id)

        if isinstance(track_info, dict) and "error" in track_info:
            attempts += 1
            print(f"Попытка {attempts}/{max_attempts} | {track_info}")
            await asyncio.sleep(1)

            if attempts % 3 == 0:
                newnym_attempts += 1

                if newnym_attempts > max_newnym_retries:
                    raise ValueError("Не удалось получить данные после смены цепочки")

                tor.send_newnym()
                print("Перезапуск цепочки... подождите 3 секунды")
                await asyncio.sleep(3)

            continue

        if isinstance(track_info, list) and track_info:
            release_id = track_info[0]["release_id"]
            break
    
    album_info = await mb_api.get_track_number_in_release(release_id, recording_id)
    cover_url = await covers.get_cover_url(release_id)
    await covers.download_image(cover_url, cfg["covers_path"] + f"{release_id}.jpg")

    '''
    TRACK_INFO
    "release_id"
    "album_title"
    "year"
    "artist_name"
    "tags"
    "length"
    "song_title"

    ALBUM_INFO
    "track_number"
    "track_title"
    "medium_title"
    "release_id"
    '''
    
    return track_info, album_info, release_id

async def dev_main():
    with open("trackInfo.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        track_info = parse.parse_track_info(data)
    
    release_id = track_info[0]["release_id"]

    match = next(acoustid.match(API_KEY, os.path.join("test", "1.mp3")), "")
    if match:
        score, recording_id, title, artist = match
    else:
        raise ValueError("Совпадений не найдено")

    with open("albumInfo.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        album_info = parse.parse_album_info(data, release_id, recording_id)

    return track_info, album_info, release_id

# if __name__ == "__main__":
#     asyncio.run(main())