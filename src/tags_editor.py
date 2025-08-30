from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
# from mutagen.oggopus import OggOpus
# from mutagen.flac import Picture

from pydub import AudioSegment

from io import BufferedReader
# from base64 import b64encode

from pathlib import Path
import subprocess
import asyncio
import json
import os

import requests_and_stuff as ras

with open("config.json", "r") as f:
    cfg = json.load(f)

def encode_with_ffmpeg(input_file, output_file, cover_path=None):
    input_file  = str(Path(input_file))
    output_file = str(Path(output_file))
    temp_output = str(Path(output_file).with_name("temp_encoded.mp3"))

    cmd = ["ffmpeg", "-y", "-i", input_file]

    if cover_path:
        cover_path = str(Path(cover_path))
        cmd += [
            "-i", cover_path,
            "-map", "0:a", "-map", "1:v",
            "-c:a", "libmp3lame", "-b:a", "96k",
            "-c:v", "copy",
            "-id3v2_version", "3",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
        ]
    else:
        cmd += [
            "-map", "0:a",
            "-c:a", "libmp3lame", "-b:a", "96k",
            "-id3v2_version", "3",
        ]

    cmd.append(temp_output)

    subprocess.run(cmd, check=True)

    os.replace(temp_output, output_file)

# def edit_opus_tags(input_dir, audioname, tags_to_edit):
#     audio = OggOpus(input_dir + audioname)
#     for tag_name, tag_value in tags_to_edit.items():
#         audio[tag_name] = tag_value
#     audio.save()

#     cover = Picture()
#     cover.data = open("Photos//1.webp", "rb").read()
#     cover.type = 3

#     audio.tags["metadata_block_picture"] = b64encode(cover.write()).decode('ascii')
#     audio.save()

# def from_mp3_to_opus(dir_from, dir_to):
#     files = sorted(os.listdir(dir_from))
#     for file in files:
#         audio = AudioSegment.from_mp3(f"{dir_from}/{file}")
#         audio.export(f"{dir_to}/{file}.ogg", format = "opus")
#         edit_opus_tags(f"{dir_to}/", f"{file}.ogg", tags_to_edit)

def edit_mp3_tags(input_dir, audioname, tags_to_edit, release_id):
    audio = EasyID3(input_dir + audioname)

    for tag_name, tag_value in tags_to_edit.items():
        audio[tag_name] = tag_value
    audio.save()
    
    audio = MP3(input_dir + audioname, ID3 = ID3)
    audio.tags.delall("APIC")
    with BufferedReader(open(Path(os.path.expanduser(cfg["covers_path"]) + f"{release_id}.jpg"), "rb")) as fh:
        apic = APIC(data = fh.read(),
                    encoding = 3,
                    type = 3,
                    desc = "cover",
                    mime = "image/jpeg")
    audio.tags.add(apic)
    audio.save()

def from_raw_mp3_to_clean(file_name, dir_from, dir_to, tags_to_edit, release_id):
    audio = AudioSegment.from_mp3(os.path.join(dir_from, file_name))

    clean_name = f"{file_name.replace('.mp3', '')}_clean.mp3"

    audio.export(os.path.join(dir_to, clean_name), format="mp3")
    edit_mp3_tags(f"{dir_to}/", f"{clean_name}", tags_to_edit, release_id)
    
    new_name = f"{tags_to_edit['title']} - {tags_to_edit['artist']}.mp3"
        
    old_path = f"{dir_to}/{clean_name}"
    new_path = f"{dir_to}/{new_name}"
        
    os.rename(old_path, new_path)
    try:
        encode_with_ffmpeg(
            input_file = new_path,
            output_file = new_path,
        )
    except Exception as e:
        print(f"Error: {e}")

def build_tags(track_info, album_info):
    return {
        "title": track_info[0]["song_title"],
        "artist": track_info[0]["artist_name"],
        "album": track_info[0]["album_title"],
        "date": track_info[0]["year"],
        "genre": "Панк-рок, камеди-рок, альтернативный рок, поп-панк",
        "tracknumber": album_info[0]["track_number"],
        "musicbrainz_releasetrackid": album_info[0]["release_id"],
        "length": str(track_info[0]["length"])
    }

async def process_one(file_name, dir_from, dir_to):
    # track_info, album_info, release_id = await ras.dev_main()
    track_info, album_info, release_id = await ras.main(dir_from, file_name)

    tags_to_edit = build_tags(track_info, album_info)

    await asyncio.to_thread(from_raw_mp3_to_clean, file_name, dir_from, dir_to, tags_to_edit, release_id)

async def main():
    # dir_from = input("Введите исходную директорию: ")
    # dir_to = input("Введите конечную директорию: ")

    dir_from = "/home/lima148/Documents/Scripts/Python/MusicTagEditor/test/"
    dir_to = "/home/lima148/Documents/Scripts/Python/MusicTagEditor/mp3/"

    files = sorted(os.listdir(dir_from))
    for file_name in files:
        await process_one(file_name, dir_from, dir_to)

# if __name__ == "__main__":
    # asyncio.run(main())