from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture

from pydub import AudioSegment

from io import BufferedReader
from base64 import b64encode

import subprocess
import os
from pathlib import Path

import Parse
import json
import asyncio

with open("config.json", "r") as f:
    cfg = json.load(f)

track_info, album_info = asyncio.run(Parse.main())
print(track_info, album_info)

tags_to_edit = {
    "title": track_info[0]["song_title"],
    "artist": track_info[0]["artist_name"],
    "album": track_info[0]["album_title"],
    "date": track_info[0]["year"],
    "genre": "Панк-рок, камеди-рок, альтернативный рок, поп-панк",
    "tracknumber": album_info[0]["track_number"],
    "musicbrainz_releasetrackid": album_info[0]["release_id"],
    "length": str(track_info[0]["length"])
}

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

def encodeWithFfmpeg(input_file, output_file, cover_path=None):
    input_file = str(Path(input_file))
    output_file = str(Path(output_file))
    cmd = [
        "ffmpeg", "-y",
        "-i", input_file,
        "-b:a", "96k",
        # "-q:a", "6"
    ]
    if cover_path:
        cover_path = str(Path(cover_path))
        cmd += [
            "-i", cover_path,
            "-map", "0", "-map", "1",
            "-c", "copy",
            "-id3v2_version", "3",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
        ]
    cmd.append(output_file)
    subprocess.run(cmd)

def editOpusTags(input_dir, audioname, tags_to_edit):
    audio = OggOpus(input_dir + audioname)
    for tag_name, tag_value in tags_to_edit.items():
        audio[tag_name] = tag_value
    audio.save()

    cover = Picture()
    cover.data = open("Photos//1.webp", "rb").read()
    cover.type = 3

    audio.tags["metadata_block_picture"] = b64encode(cover.write()).decode('ascii')
    audio.save()

def editMp3Tags(input_dir, audioname, tags_to_edit):
    audio = EasyID3(input_dir + audioname)

    for tag_name, tag_value in tags_to_edit.items():
        audio[tag_name] = tag_value
    audio.save()
    
    audio = MP3(input_dir + audioname, ID3 = ID3)
    audio.tags.delall("APIC")
    with BufferedReader(open(Path(os.path.expanduser(cfg["covers_path"]) + "cover.jpg"), "rb")) as fh:
        apic = APIC(data = fh.read(),
                    encoding = 3,
                    type = 3,
                    desc = "cover",
                    mime = "image/jpeg")
    audio.tags.add(apic)
    audio.save()

def fromMp3ToOpus(dir_from, dir_to):
    files = sorted(os.listdir(dir_from))
    for file in files:
        audio = AudioSegment.from_mp3(f"{dir_from}/{file}")
        audio.export(f"{dir_to}/{file}.ogg", format = "opus")
        editOpusTags(f"{dir_to}/", f"{file}.ogg", tags_to_edit)

def fromRawMp3ToClean(dir_from, dir_to):
    files = sorted(os.listdir(dir_from))
    for file in files:
        audio = AudioSegment.from_mp3(f"{dir_from}/{file}")
        audio.export(f"{dir_to}/{file.replace('.mp3', '')}_clean.mp3", format="mp3")
        editMp3Tags(f"{dir_to}/" , f"{file.replace(".mp3", "")}_clean.mp3", tags_to_edit)
        clean_name = f"{file.replace('.mp3', '')}_clean.mp3"
        try:
            newName = os.rename(f"{dir_to}/{clean_name}", f"{dir_to}/{tags_to_edit['title']} - {tags_to_edit['artist']}.mp3")
            encodeWithFfmpeg(
            input_file=f"{dir_to}/{newName}",
            output_file=f"{dir_to}/{newName}",
        )
        except Exception as e:
            print(f"Error: {e}")

async def main():
    pass

if __name__ == "__main__":
    pass