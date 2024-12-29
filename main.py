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


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, response: Response, hx_request: Optional[str] = Header(None)
):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@app.post("/start")
async def start(
    request: Request, response: Response, hx_request: Optional[str] = Header(None)
):
    db.set("progress", 0)
    context = {"request": request}
    return templates.TemplateResponse("start.html", context)


@app.get("/job/progress")
async def job(
    request: Request, response: Response, hx_request: Optional[str] = Header(None)
):
    current = db.get("progress")
    progress = int(current)
    if progress < 100:
        progress = progress + 10
        db.set("progress", progress)
        context = {"request": request, "progress": progress}
        return templates.TemplateResponse("progress.html", context)
    if progress == 100:
        context = {"request": request, "progress": progress}
        response.headers["HX-Trigger"] = "done"
        return templates.TemplateResponse(
            "progress.html", context, headers=response.headers
        )


@app.get("/job")
async def job(
    request: Request, response: Response, hx_request: Optional[str] = Header(None)
):
    context = {"request": request}
    return templates.TemplateResponse("complete.html", context)