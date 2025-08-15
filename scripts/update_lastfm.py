import os, re, datetime, requests

README_FILE = "README.md"
START = r"<!--LASTFM:START-->"
END = r"<!--LASTFM:END-->"
USER = os.getenv("LASTFM_USER")
API_KEY = os.getenv("LASTFM_API_KEY")

if not USER or not API_KEY:
    raise SystemExit("Faltan variables de entorno: LASTFM_USER o LASTFM_API_KEY")

url = (
    "https://ws.audioscrobbler.com/2.0/"
    f"?method=user.getrecenttracks&user={USER}&api_key={API_KEY}&format=json&limit=1"
)
res = requests.get(url, timeout=20)
res.raise_for_status()
data = res.json()

try:
    track = data["recenttracks"]["track"][0]
    artist = track["artist"]["#text"]
    title = track["name"]
    album = track.get("album", {}).get("#text", "")
    link = track.get("url", "")
    nowplaying = track.get("@attr", {}).get("nowplaying") == "true"
    ts = track.get("date", {}).get("uts")
    when = "Reproduciendo ahora" if nowplaying else (
        datetime.datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M") if ts else "Reciente"
    )
    body = f"**{title}** — {artist}" + (f" · *{album}*" if album else "")
    if link:
        body = f"[{body}]({link})"
    track_info = f"{body}  \n_{when}_"
except Exception:
    track_info = "_No se pudo obtener la información de Last.fm_"

with open(README_FILE, "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(rf"{START}.*?{END}", re.S)
replacement = f"{START}\n{track_info}\n{END}"
new_content = re.sub(pattern, replacement, content)

if new_content != content:
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README actualizado con la última canción.")
else:
    print("Sin cambios.")
