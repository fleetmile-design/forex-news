import os
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import processor, scrapers, storage
from app.schemas import ForexNews

app = FastAPI(title="Forex Intelligence")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Background task
# ---------------------------------------------------------------------------

async def _do_fetch() -> None:
    storage.add_log("Pradedamas naujienų rinkimas...")
    try:
        news = await scrapers.collect_all_news()
        for item in news:
            sentiment, _ = processor.calculate_sentiment(item)
            item["sentiment"] = sentiment
        storage.news_db.clear()
        storage.news_db.extend(news)
        storage.add_log(f"Surinkta {len(news)} naujienų iš {len(set(n['source'] for n in news))} šaltinių.")
    except Exception as exc:
        storage.add_log(f"Klaida renkant naujienas: {exc}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    stats = storage.get_stats()
    return templates.TemplateResponse("index.html", {"request": request, "stats": stats})


@app.post("/api/fetch")
async def trigger_fetch(background_tasks: BackgroundTasks):
    storage.add_log("Fetch užklausa gauta.")
    background_tasks.add_task(_do_fetch)
    return {"status": "started"}


@app.get("/api/news", response_model=List[ForexNews])
async def get_news():
    return [ForexNews(**item) for item in storage.news_db]


@app.get("/api/news-table", response_class=HTMLResponse)
async def news_table():
    rows = []
    for item in storage.news_db:
        sentiment, css = processor.calculate_sentiment(item)
        importance = item.get("importance", "")
        if importance == "High":
            badge_css = "bg-red-900/50 text-red-300"
        elif importance == "Medium":
            badge_css = "bg-yellow-900/50 text-yellow-300"
        else:
            badge_css = "bg-gray-700 text-gray-300"

        af = f"{item.get('actual', '-')} / {item.get('forecast', '-')}"
        rows.append(
            f"<tr class='border-b border-gray-700 hover:bg-gray-800'>"
            f"<td class='py-2 px-3 text-gray-400 text-xs'>{item.get('timestamp', '')[:16]}</td>"
            f"<td class='py-2 px-3 font-mono font-bold text-white'>{item.get('currency', '')}</td>"
            f"<td class='py-2 px-3 text-gray-200'>{item.get('event', '')}</td>"
            f"<td class='py-2 px-3'><span class='px-2 py-0.5 rounded text-xs {badge_css}'>{importance}</span></td>"
            f"<td class='py-2 px-3 text-gray-300 text-xs font-mono'>{af}</td>"
            f"<td class='py-2 px-3 text-xs {css}'>{item.get('sentiment', 'Pending')}</td>"
            f"</tr>"
        )
    return HTMLResponse("\n".join(rows) if rows else "<tr><td colspan='6' class='py-4 text-center text-gray-500'>Nėra duomenų. Paleiskite srauto rinkimą.</td></tr>")


@app.get("/api/logs", response_class=HTMLResponse)
async def get_logs():
    logs = storage.get_logs()
    lines = "\n".join(logs) if logs else "[SYSTEM] Laukiama duomenų..."
    return HTMLResponse(f"<pre class='whitespace-pre-wrap'>{lines}</pre>")


@app.get("/api/stats")
async def get_stats():
    return storage.get_stats()


@app.get("/api/download/csv")
async def download_csv():
    filepath = str(DATA_DIR / "forex_news.csv")
    storage.export_csv(filepath)
    return FileResponse(filepath, media_type="text/csv", filename="forex_news.csv")
