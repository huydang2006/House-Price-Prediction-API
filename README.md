# Mini House-Price Prediction API

## How to run

1. Install the dependencies:
   ```
   pip install fastapi "uvicorn[standard]"
   ```
2. Go into `backend/` and start the server:
   ```
   cd backend
   uvicorn main:app --reload
   ```
3. Open the form in your browser:
   ```
   http://127.0.0.1:8000/static/house_form.html
   ```

## Answers

**Calling `/predict` without `location`:**
It still works because `location` has a default value (`"other"`) in
the endpoint. If it's not in the URL, FastAPI just uses the default
instead of asking for it.

**Calling `/predict` without `area`:**
This gives a 422 error because `area` has no default value, so
FastAPI treats it as required. When it's missing, FastAPI rejects the
request before the function even runs, and tells you which field was
missing.

**Why a relative URL works in the fetch() call:**
Since `house_form.html` is served by FastAPI itself (at
`127.0.0.1:8000/static/house_form.html`), the page and the `/predict`
API are on the same host and port. So `/predict` alone is enough —
the browser fills in the rest automatically, and there's no
cross-origin request happening.