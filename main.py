from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from pydub import AudioSegment
from io import BufferedReader
from base64 import b64encode
from pathlib import Path
import subprocess
import os

ZWSP = "\u200B"

tags_to_edit = {
    'title': ["Рустем\u200B"],
    'artist': ["Валентин Стрыкало\u200B"],
    'album': ['Смирись и расслабься!\u200B'],
    'date': ['2012'],
    'genre': ['Панк-рок, камеди-рок, альтернативный рок, поп-панк']
}

def encode_with_ffmpeg(input_file, output_file, cover_path=None):
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

def edit_opus_tags(input_dir, audioname, tags_to_edit):
    audio = OggOpus(input_dir + audioname)
    for tag_name, tag_value in tags_to_edit.items():
        audio[tag_name] = tag_value
    audio.save()

    cover = Picture()
    cover.data = open("Photos//1.webp", "rb").read()
    cover.type = 3

    audio.tags["metadata_block_picture"] = b64encode(cover.write()).decode('ascii')
    audio.save()

def edit_mp3_tags(input_dir, audioname, tags_to_edit):
    audio = EasyID3(input_dir + audioname)
    for tag_name, tag_value in tags_to_edit.items():
        audio[tag_name] = tag_value
    audio.save()
    
    audio = MP3(input_dir + audioname, ID3 = ID3)
    audio.tags.delall("APIC")
    with BufferedReader(open(f"Photos//1.webp", "rb")) as fh:
        apic = APIC(data = fh.read(),
                    encoding = 3,
                    type = 3,
                    desc = "cover",
                    mime = "image/webp")
    audio.tags.add(apic)
    audio.save()

def from_mp3_to_opus(dir_from, dir_to):
    files = sorted(os.listdir(dir_from))
    for file in files:
        audio = AudioSegment.from_mp3(f"{dir_from}/{file}")
        audio.export(f"{dir_to}/{file}.ogg", format = "opus")
        edit_opus_tags(f"{dir_to}/", f"{file}.ogg", tags_to_edit)

def from_raw_mp3_to_clean(dir_from, dir_to):
    files = sorted(os.listdir(dir_from))
    for file in files:
        audio = AudioSegment.from_mp3(f"{dir_from}/{file}")
        audio.export(f"{dir_to}/{file.replace('.mp3', '')}_clean.mp3", format="mp3")
        edit_mp3_tags(f"{dir_to}/" , f"{file.replace('.mp3', '')}_clean.mp3", tags_to_edit)

        clean_name = f"{file.replace('.mp3', '')}_clean.mp3"
        encode_with_ffmpeg(
            input_file=f"{dir_to}/{clean_name}",
            output_file=f"{dir_to}/{file.replace('.mp3', '')}_processed.mp3",
        )

while True:
    choose = int(input("\n1 - да\n~$ "))

    match(choose):
        case 1:
            dir_from = input("Введите исходную директорию: ")
            dir_to = input("Введите конечную директорию: ")
            from_raw_mp3_to_clean(dir_from, dir_to)
        case 2:
            print("Поки!")
            break