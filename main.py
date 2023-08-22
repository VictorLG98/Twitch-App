from twitchAPI.twitch import Twitch
import asyncio
from twitchAPI.helper import first
from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.responses import HTMLResponse

# Configuración de la API de Twitch
CLIENT_ID = "ijaeafck79lqn9tv0u3zrwuu8qbnyx"
CLIENT_SECRET = "6tlw8ne0hdbluyonhnknvu5ir3zarq"
OAUTH_TOKEN = "zsj3ginup6nkxh4v70syrezagw8suh"  # Necesario para algunas consultas

async def get_live_streams():
    twitch = await Twitch(CLIENT_ID, CLIENT_SECRET)
    await twitch.authenticate_app([])
    streams = twitch.get_streams(first=10, language='es', stream_type='live')
    stream_list = []
    contador = 0
    async for stream in streams:
        if contador == 10:
            break
        
        stream_data = {
            "user_name": stream.user_name,
            "game_name": stream.game_name,
            "user_id": stream.id,
            "type": stream.type,
            "title": stream.title,
            "tags": stream.tags,
            "viewer_count": stream.viewer_count,
            "started_at": stream.started_at.strftime('%Y-%m-%d'),
            "language": stream.language,
            "thumbnail_url": stream.thumbnail_url.replace("{width}", "800").replace("{height}", "500")
        }
        stream_list.append(stream_data)
        contador += 1
    await twitch.close()
    return stream_list

async def get_clips():
    twitch = await Twitch(CLIENT_ID, CLIENT_SECRET)
    twitch.authenticate_app([])
    games = twitch.get_top_games(first=1)
    games_ids = []

    x = 0
    async for game in games:
        if x == 10:
            break
        games_ids.append(game.id)
        x += 1

    clip_list = []
    cont = 0
    for id in games_ids:
        clips = twitch.get_clips(first=1, game_id=id)
        async for clip in clips:
            if cont == 10:
                break
            clip_data = {
                "url": clip.url,
                "embeded_url": clip.embed_url,
                "creator_name": clip.creator_name,
                "title": clip.title,
                "view_count": clip.view_count,
                "thumbnail_url": clip.thumbnail_url,
                "duration": clip.duration
            }
            clip_list.append(clip_data)
            cont += 1
    await twitch.close()
    return clip_list

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/live_streams", response_class=HTMLResponse)
async def live_streams(request: Request):
    streams_data = await get_live_streams()
    return templates.TemplateResponse("live_streams.html", {"request": request, "streams": streams_data})

@app.get("/clips", response_class=HTMLResponse)
async def clips(request: Request):
    clips_data = await get_clips()
    return templates.TemplateResponse("clips.html", {"request": request, "clips": clips_data})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
