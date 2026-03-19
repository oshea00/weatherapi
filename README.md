# Basic API wrapper
Wraps weather.gov API

## Start the API

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -e .
```

3. Start the API server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

4. Open the API:
- Swagger UI: `http://localhost:8000/docs`
- Example request: `http://localhost:8000/weather?city=Seattle`

Weather endpoint:
- GET `/weather?city=<city>&state=<state>&country=<country>`
- `city` is required
- `state` is optional
- `country` is optional and defaults to `USA`
