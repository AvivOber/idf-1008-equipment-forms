# טופס 1008 (פלס"מ) - גדוד 429

Self-service generator for the battalion's equipment receipt form (helmet +
vest, issued daily). A soldier types their name, the app looks them up in
the unit roster and immediately returns a filled-in PDF - issuer details
(Arik Bord) and today's date are filled automatically.

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
`personal_number`, `rank` - Hebrew headers like `שם מלא`, `מספר אישי`,
`דרגה` also work). This file is gitignored on purpose since it holds
soldiers' personal numbers - don't commit a real roster.

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

## Coordinates

`config.py` documents where every field lands on the page and how it was
measured directly off `assets/template.pdf` - see the comment at the top of
that file before changing any coordinate.
