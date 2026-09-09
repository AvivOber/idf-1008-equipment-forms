# טופס 1008 (פלס"מ) - גדוד 429

Self-service generator for the battalion's equipment receipt form (helmet +
vest, issued daily). A soldier types their name, the app looks them up in
the unit roster and immediately returns a filled-in PDF - issuer details
(Arik Brod) and today's date are filled automatically.

This is a standalone project, independent of any other repo/codebase.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Fonts: place `NotoSansHebrew-Regular.ttf` and `NotoSansHebrew-Bold.ttf` in
`assets/fonts/` (already included in this repo).

## Roster

Add your unit's roster as `data/roster.xlsx` or `data/roster.csv` (see
`data/roster.example.csv` for the expected columns: `full_name`,
`personal_number`, `rank` - Hebrew headers like `שם מלא` / `שם ומשפחה`,
`מספר אישי` / `מ.א.`, `דרגה` also work). This file is gitignored on purpose
since it holds soldiers' personal numbers - don't commit a real roster.

On a hosted deploy (no local filesystem access), upload/replace the roster
from a browser at `/admin` - see "Deploying" below.

## Environment variables

- `ADMIN_PASSWORD` - password for the `/admin` roster-upload page. Set this
  on whatever host runs the app; the code default (`changeme`) is not safe
  to leave in place.
- `SECRET_KEY` - Flask session signing key. Any random string; only matters
  for a real deploy.

## Run the web page

```bash
python app.py
```

Open http://localhost:5000, type a name, get the signed PDF immediately.

## Batch-generate for the whole roster

```bash
python generate_batch.py
```

Generates a PDF per soldier in `output/`.

## Deploying (no local Python needed)

The `Procfile` (`web: gunicorn app:app`) works as-is on Render, Railway, or
any host that reads a Procfile / lets you set a start command and build
command (`pip install -r requirements.txt`). After the first deploy, open
`https://<your-app-url>/admin` in a browser, enter `ADMIN_PASSWORD`, and
upload the roster file - the app has no roster until you do this once.

Note: most free hosting tiers use an ephemeral filesystem, so a roster
uploaded via `/admin` can be wiped by the next deploy (a new code push) -
re-upload it via `/admin` after any redeploy.

## Coordinates

`config.py` documents where every field lands on the page and how it was
measured directly off `assets/template.pdf` - see the comment at the top of
that file before changing any coordinate.
