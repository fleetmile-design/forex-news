# Forex News — Docker konteineris

Pilna Forex ekonomikos naujienų rinkimo sistema Docker konteineryje su FastAPI backend'u ir WebUI administravimo panele.

## Funkcijos

- 🔄 Automatinis naujienų rinkimas iš kelių šaltinių (Forex Factory, Investing.com, DailyFX)
- 📊 Sentimentų analizė (Bullish / Bearish / Neutral) pagal Actual vs Forecast
- 🖥️ WebUI administravimo panelė (Tailwind CSS + HTMX)
- 📥 CSV eksportas
- 🔌 REST API su JSON atsakymais
- 🐳 Docker Compose palaikymas su duomenų persistencija

## Paleidimas

```bash
git clone https://github.com/fleetmile-design/forex-news.git
cd forex-news
docker-compose up -d --build
# Pasiekiama: http://192.168.0.187:8000
```

## API endpoint'ai

| Metodas | Kelias | Aprašymas |
|---------|--------|-----------|
| GET | `/` | WebUI administravimo panelė |
| POST | `/api/fetch` | Paleisti naujienų rinkimą fone |
| GET | `/api/news` | JSON naujienų sąrašas |
| GET | `/api/news-table` | HTML fragmentas lentelei (HTMX) |
| GET | `/api/logs` | HTML fragmentas logams (HTMX) |
| GET | `/api/stats` | JSON statistika |
| GET | `/api/download/csv` | CSV failo atsisiuntimas |

### Pavyzdžiai

```bash
# Paleisti naujienų rinkimą
curl -X POST http://192.168.0.187:8000/api/fetch

# Gauti naujienas JSON formatu
curl http://192.168.0.187:8000/api/news

# Gauti statistiką
curl http://192.168.0.187:8000/api/stats
```

## Projekto struktūra

```
forex-news/
├── app/
│   ├── __init__.py       # Python paketo žymeklis
│   ├── main.py           # FastAPI pagrindinis failas su visais maršrutais
│   ├── scrapers.py       # Naujienų rinkimo moduliai
│   ├── processor.py      # Sentimentų analizė
│   ├── schemas.py        # Pydantic duomenų modeliai
│   └── storage.py        # Duomenų saugykla (in-memory + CSV eksportas)
├── templates/
│   └── index.html        # WebUI administravimo panelė
├── data/                 # CSV failai (Docker Volume)
├── logs/                 # Sistemos logai
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Migracija į kitą Linux serverį

```bash
# Eksportuoti Docker image
docker save forex_news_service -o forex_news_service.tar

# Perkelti failą į naują serverį
scp forex_news_service.tar user@NEW_SERVER:/home/user/

# Naujame serveryje
docker load -i forex_news_service.tar
docker-compose up -d
```
