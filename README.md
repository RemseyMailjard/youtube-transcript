# 🎬 TranscriptBuddy

> Turn YouTube videos into clean transcripts.

Een professionele, lokaal draaiende Streamlit-app rond
[`youtube-transcript-api`](https://pypi.org/project/youtube-transcript-api/).
De transcript-logica is bewust gescheiden van de UI zodat dezelfde modules
later 1-op-1 hergebruikt kunnen worden in een Azure Function (HTTP-trigger)
of andere API.

## ✨ Features

- Plak een YouTube URL of losse video-ID (`watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`).
- Configureerbare taalvoorkeur (standaard `nl` → `en`, kies uit 7 talen).
- Metadata-overzicht: video-id, taal, regels, woorden, datum/tijd, duur.
- Tabs voor platte tekst, tabel-view (start/duur/regel) en ruwe JSON.
- Downloads in `.txt`, `.md` en `.json` via Streamlit download buttons.
- Optioneel automatisch opslaan in `output/`.
- Caching met `st.cache_data`, met expliciete "opnieuw ophalen"-knop.
- Nette foutafhandeling voor: ongeldige invoer, video niet beschikbaar,
  transcripties uitgeschakeld, geen transcript in gekozen talen,
  YouTube-IP-blokkades en overige netwerkfouten.

## 📁 Projectstructuur

```text
YouTubeTranscriptCalling/
├── app.py                  # Streamlit UI (alle glue, geen logica)
├── main.py                 # Dunne CLI-shim over src/
├── pyproject.toml          # uv-managed dependencies
├── uv.lock
├── README.md
├── .gitignore
├── output/                 # at-runtime, opgenomen in .gitignore
└── src/
    ├── __init__.py
    ├── models.py           # TranscriptResult, TranscriptSnippet
    ├── youtube_utils.py    # URL/ID parsing
    ├── transcript_service.py  # fetch + orchestrator (Azure-ready)
    └── export_service.py   # .txt / .md / .json serialisatie + disk-IO
```

## 🚀 Lokaal opzetten

Vereisten: Python 3.11+ en [`uv`](https://docs.astral.sh/uv/).

```powershell
# in de projectmap
uv sync
```

## ▶️ Streamlit-app starten

```powershell
uv run streamlit run app.py
```

De app opent op http://localhost:8501.

## 🖥️ CLI gebruiken (optioneel)

```powershell
# Standaard: nl -> en, output naar output/transcript_<id>_<ts>.txt
uv run python main.py "https://www.youtube.com/watch?v=9-zxCfKKxyU"

# Andere taalvolgorde en JSON-export
uv run python main.py 9-zxCfKKxyU --languages de en --format json
```

## ☁️ Deploy naar Streamlit Community Cloud

1. Push de repo naar GitHub.
2. Maak een nieuwe app aan op [share.streamlit.io](https://share.streamlit.io).
3. Wijs naar `app.py`.
4. Streamlit Cloud leest `pyproject.toml` / `requirements.txt` automatisch.
   Genereer indien nodig een `requirements.txt`:
   ```powershell
   uv export --format requirements-txt --no-hashes > requirements.txt
   ```
5. **Let op:** YouTube blokkeert vaak cloud-IP's. Reken op `RequestBlocked`
   of `IpBlocked` errors en configureer eventueel een residential proxy
   (zie pakket-docs over `WebshareProxyConfig` / `GenericProxyConfig`).

## ☁️ Klaar voor Azure Function (HTTP-trigger)

De hele truc: [`get_transcript`](src/transcript_service.py) doet geen disk-IO
en levert een `TranscriptResult` op. Een Azure Function wordt dan:

```python
import azure.functions as func
from src.transcript_service import get_transcript
from src.export_service import to_json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="transcript", methods=["GET", "POST"])
def transcript(req: func.HttpRequest) -> func.HttpResponse:
    video = req.params.get("video") or (req.get_json(silent=True) or {}).get("video")
    if not video:
        return func.HttpResponse("Missing 'video' parameter", status_code=400)
    try:
        result = get_transcript(video)
    except ValueError as e:
        return func.HttpResponse(str(e), status_code=400)
    except Exception as e:
        return func.HttpResponse(f"{type(e).__name__}: {e}", status_code=502)
    return func.HttpResponse(
        body=to_json(result),
        mimetype="application/json",
        status_code=200,
    )
```

## ⚠️ Beperkingen

- Niet elke video heeft een transcript (uploader kan dit uitschakelen).
- YouTube blokkeert vaak verkeer vanaf cloud / datacenter IP's.
- Dit pakket gebruikt een ongedocumenteerd deel van de YouTube API; de
  upstream library wordt actief onderhouden maar kan tijdelijk breken.
