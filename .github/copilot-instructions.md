# Copilot instructions — Wordcube

Purpose: Quickly orient an AI coding assistant to this small Flask-based word-cube project and provide precise, actionable editing guidance.

**Quick Start**
- Run dev server: `python app.py` (opens on 127.0.0.1:5000).
- Generate cubes (if missing): `python3 main2.py` — writes `word_cubes.txt` from `word_list_wordfreq.txt`.
- CLI game: `python3 wordcube_game.py` (use `--reveal` to print cube + revealed letters).

**Big picture**
- Single Flask app (`app.py`) serves a 4x4 cube guessing game. Frontend lives in `templates/` and `static/`.
- Cubes are precomputed by `main2.py` and stored in `word_cubes.txt`. Each cube is a block of 4 lines (rows) separated by a blank line.
- Session state keys: `cube`, `revealed`, `attempts`, `feedbacks`, `solved`, `shake` (see `app.py` routing logic).

**Data shapes & conventions**
- Cube in-memory: list of 4 lowercase strings (each length 4). e.g. [`'game','area','made','edge'`].
- `revealed`: stored as a list of (row, col) pairs; templates expect tuples like `(r,c)`.
- `load_cubes()` strips spaces and lowercases rows; file format is space-separated letters per row and blank-line separated cubes.
- Feedback API: functions return 4-char strings using `'G'` (green/correct), `'Y'` (purple/same row or column), `'P'` (yellow/elsewhere), `'_'` (absent). See `compute_feedback` in [app.py](app.py) and `feedback` in [wordcube_game.py](wordcube_game.py).
- Feedback colors: `'G'` = green (correct position), `'Y'` = purple (same row/column), `'P'` = yellow (elsewhere on grid), `'_'` = white (absent).

**Key files to inspect when changing behavior**
- `app.py` — Flask routes, session management, `compute_feedback`, form handling (`/guess` expects hidden `row0..row3`).
- `main2.py` — cube generation logic and word-list handling (prefix pruning). Use this to regenerate `word_cubes.txt`.
- `wordcube_game.py` — CLI reference implementation; mirrors server logic (useful for unit-test examples).
- `templates/index.html` — JS assembles hidden inputs `row{i}-hidden` from `.board-input` inputs in row-major order; feedback coloring applied via `data-fb` and classes.

**Editing rules for AI agents (do not violate these lightly)**
- Keep feedback logic consistent: when modifying `compute_feedback` update `wordcube_game.py`'s `feedback` too.
- Do not assume persistent sessions: `app.secret_key = os.urandom(24)` — sessions reset every process start. If you need persistent sessions for testing, ask the user before changing the secret behavior.
- File-format changes: preserve the simple blank-line-separated format of `word_cubes.txt` — `load_cubes()` relies on that.
- Frontend/back-end contract: the form submits four hidden fields named `row0..row3` (lowercase words, no spaces). Changing field names requires updating `templates/index.html` and `app.py` together.
- **Color scheme**: All feedback colors are defined as CSS variables in `static/style.css` `:root` block (`--correct`, `--present`, `--elsewhere`, `--revealed`, `--keyboard-absent`). The `forceColors()` function in `templates/index.html` reads these via `getComputedStyle()`. **To change colors in the future, only edit the CSS variables — no JS changes needed.**

**Developer workflows & debug tips**
- Local run: `python app.py` and visit http://127.0.0.1:5000/.
- If the web UI reports "No cubes found", run `python3 main2.py` and re-run the server.
- Use `python3 wordcube_game.py --reveal` to get a reproducible cube and revealed positions for reproducing UI behavior.
- Logs: the Flask process prints simple prints from `main2.py` when generating cubes — use those to validate cube counts.

**Suggested low-risk AI tasks**
- Add unit tests for `compute_feedback` using examples from `wordcube_game.py` (mirrored behavior).
- Add a small `dev.env` or config to set a stable `SECRET_KEY` for local testing (only after user OK).
- Add a `Makefile` or `scripts/` helper for `generate-cubes` and `run-server` to standardize workflows.

If anything above is unclear or you want me to expand an area (tests, CI, or a small refactor), tell me which part to focus on next.
