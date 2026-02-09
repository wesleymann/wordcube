# Wordcube

Small Flask-based 4x4 word-cube guessing game with color-coded feedback.

Layout
- `app.py` — Flask web app (core server).
- `wordcube_game.py` — CLI reference implementation and test helper.
- `static/`, `templates/` — frontend assets.
- `generators/` — helper scripts to create word lists and cubes:
  - `generators/generate_word_list.py` — produce `word_lists/word_list_wordfreq.txt` using `wordfreq`.
  - `generators/generate_cubes.py` — build `word_lists/word_cubes.txt` from a word list.
- `word_lists/` — (optional) place to store word-list and generated cube files. The app and CLI prefer files here if present but fall back to root filenames for compatibility.

Quick start
1. Generate a word list (optional):
```
python3 generators/generate_word_list.py
```
2. Generate cubes (if none exist):
```
python3 generators/generate_cubes.py
```
3. Run the server:
```
python app.py
```

Notes for contributors
- Keep feedback logic in sync: `app.py`'s `compute_feedback` and `wordcube_game.py`'s `feedback` implement the same rules.
- The server uses short-lived Flask sessions (random `SECRET_KEY` by default). If you need persistent sessions for testing, add a stable secret via environment variables.
