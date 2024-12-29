from fastapi import FastAPI, Header, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import redis

db = redis.Redis(decode_responses=True)


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

tasks = [
    {"id": 123, "name": "one-two-three"},
    {"id": 456, "name": "four-five-six"},
    {"id": 789, "name": "seven-eight-nine"},
]


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, response: Response, hx_request: Optional[str] = Header(None)
):
    context = {"request": request, "tasks": tasks}
    return templates.TemplateResponse("index.html", context)


@app.post("/start/{id}")
async def start(
    request: Request,
    response: Response,
    id: str,
    hx_request: Optional[str] = Header(None),
):
    db.set(f"progress_{id}", 0)
    context = {"request": request, "id": id}
    return templates.TemplateResponse("start.html", context)


@app.get("/job/progress/{id}")
async def job(
    request: Request,
    response: Response,
    id: str,
    hx_request: Optional[str] = Header(None),
):
    current = db.get(f"progress_{id}")
    progress = int(current)
    if progress < 100:
        progress = progress + 10
        db.set(f"progress_{id}", progress)
        context = {"request": request, "progress": progress, "id": id}
        return templates.TemplateResponse("progress.html", context)
    if progress == 100:
        context = {"request": request, "progress": progress, "id": id}
        response.headers["HX-Trigger"] = "done"
        return templates.TemplateResponse(
            "progress.html", context, headers=response.headers
        )


@app.get("/job/{id}")
async def job(
    request: Request,
    response: Response,
    id: str,
    hx_request: Optional[str] = Header(None),
):
    context = {"request": request, "id": id}
    return templates.TemplateResponse("complete.html", context)
