import os
import json
import acoustid

import asyncio
import logging

import tor_utils as tor
import musicbrainz_api as mb_api
import covers

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

def clear_terminal():
    print('\033[2J\033[H', end='')

async def main():
    with open("config.json", "r") as f:
        cfg = json.load(f)
    clear_terminal()
    tor.start_tor()

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
    # with open("trackInfo1.json", "w", encoding="utf-8") as f:
        # json.dump(track_info, f, indent=2, ensure_ascii=False)

    # with open("albumInfo1.json", "w", encoding="utf-8") as f:
        # json.dump(album_info, f, indent=2, ensure_ascii=False)

    return track_info, album_info, release_id

if __name__ == "__main__":
    asyncio.run(main())