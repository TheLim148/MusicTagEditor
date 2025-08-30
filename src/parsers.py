import json

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

def parse_album_info(data, release_id, recording_id):
    results = []

    for medium in data.get("media", []):
        for track in medium.get("tracks", []):
            if track["recording"]["id"] == recording_id:
                results.append({
                    "track_number": track["number"],
                    "track_title": track["title"],
                    "medium_title": medium.get("title", "Unknown Medium"),
                    "release_id": release_id
                })
    return results

### --- ###

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

    with open(dataFile, "w", encoding="utf-8") as f:
        json.dump(data, foo, indent=2)