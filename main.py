from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from mutagen.oggopus import OggOpus
from pydub import AudioSegment
import os

files = os.listdir("TracksMP3")

def edit_tags(file_path, tags_to_edit):
    audio = OggOpus(file_path)
    for tag_name, tag_value in tags_to_edit.items():
        audio[tag_name] = tag_value
    audio.save()


def from_mp3_to_opus():
    for file in files:
        audio = AudioSegment.from_mp3("TracksMP3\\" + file)
        audio.export(f"TracksOPUS\\{file}.opus", format = "opus")
        edit_tags(f"TracksOPUS\\{file}.opus", tags_to_edit)

tags_to_edit = {
    'title': ['Title'],
    'artist': ['Artist'],
    'album': ['Album'],
    'date': ['X'],
    'genre': ['genre']
}

if __name__ == "__main__":
    from_mp3_to_opus()