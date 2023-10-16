import os
import uuid
import json
import requests
from os import environ as env
from os.path import join, dirname
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "uploads")
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Path to the JSON file storing counters
COUNTERS_FILE = "counters.json"


@app.get("/")
async def home(request: Request):
    c = get_counters()
    s = get_folder_size(UPLOAD_PATH) / 1024 / 1024
    stats = [c["uploads"], c["downloads"], f"{int(s / 1024)} GB" if s > 1000 else f"{int(s)} MB"]
    return templates.TemplateResponse("home.html", {"request": request, "stats": stats})


@app.get("/upload")
async def gen_e_alias(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/API/v1/GUI/Upload")
async def upload_zip_file(r: Request, file: UploadFile, background_tasks: BackgroundTasks):

    token = (await r.form())['cf-turnstile-response']
    verify_id = (await r.form())['verify_id']
    ip = r.client.host

    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    body = {'secret': env.get('TURNSTILE_SECRET_KEY'), 'response': token, 'remoteip': ip}
    result = requests.post(url, json=body).json()
    result["verify_id"] = verify_id

    if not file.filename.endswith(".zip"):
        return JSONResponse(content={"error": "Uploaded file must be a ZIP file."}, status_code=400)
    random_filename = str(uuid.uuid4())[:32] + ".zip"
    file_path = os.path.join(UPLOAD_PATH, random_filename)
    def save_file():
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    background_tasks.add_task(save_file)
    increment_upload_counter()
    return JSONResponse(content={"filename": random_filename}, status_code=200)


@app.get("/download/{pack_name}")
async def download_pack(pack_name: str, request: Request):
    increment_download_counter()
    pack_path = os.path.join(UPLOAD_PATH, pack_name)
    return FileResponse(pack_path, headers={"Content-Disposition": f"attachment; filename={pack_name}"})


def increment_upload_counter():
    counters = get_counters()
    counters["uploads"] += 1
    save_counters(counters)


def increment_download_counter():
    counters = get_counters()
    counters["downloads"] += 1
    save_counters(counters)


def get_counters():
    try:
        with open(COUNTERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"uploads": 0, "downloads": 0}


def save_counters(counters):
    with open(COUNTERS_FILE, "w") as f:
        json.dump(counters, f)


def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size
