#!/usr/bin/env python3
"""Generate a frequency-based 4-letter word list into `word_lists/`.

This wraps the original `get_list` helper and writes to `word_lists/word_list_wordfreq.txt`.
If `word_lists/` does not exist it will be created.
"""
import os
from wordfreq import top_n_list


OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'word_lists')
OUT_DIR = os.path.normpath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)

try:
    all_common = top_n_list("en", n_top=50000)
except TypeError:
    all_common = top_n_list("en", 50000)

words = [w for w in all_common if len(w) == 4]
out_file = os.path.join(OUT_DIR, 'word_list_wordfreq.txt')
with open(out_file, 'w') as f:
    for w in words:
        f.write(w + '\n')
print(f"Wrote {len(words)} 4-letter words to {out_file}")
