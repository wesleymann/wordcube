#!/usr/bin/env python3
"""Generate 4x4 word cubes into `word_lists/word_cubes.txt`.

This is a lightly modified copy of the project's `main2.py` that prefers
`word_lists/word_list_wordfreq.txt` when present and writes output into
`word_lists/word_cubes.txt`.
"""
import os
from collections import defaultdict


def load_word_list(filename='word_list_10000.txt', top_n=None):
    tried = []

    def read_file(path):
        with open(path, 'r') as f:
            return [w.strip().lower() for w in f if w.strip()]

    if filename in (None, 'system'):
        system_paths = ['/usr/share/dict/words', '/usr/dict/words', '/usr/dict/web2']
        for p in system_paths:
            tried.append(p)
            if os.path.exists(p):
                print(f"Using system dictionary: {p}")
                words = read_file(p)
                break
        else:
            filename = 'word_list_10000.txt'

    if filename and filename not in (None, 'system'):
        tried.append(filename)
        if os.path.exists(filename):
            print(f"Using word list file: {filename}")
            words = read_file(filename)
        else:
            fallback = 'word_list_tiny.txt'
            tried.append(fallback)
            if os.path.exists(fallback):
                print(f"{filename} not found — falling back to {fallback}.")
                words = read_file(fallback)
            else:
                raise FileNotFoundError(f"None of these files exist: {tried}")

    words = [w for w in words if len(w) == 4 and w.isalpha()]
    if top_n:
        words = words[:top_n]
    return words


def build_prefix_map(words):
    pm = defaultdict(list)
    for w in words:
        for i in range(5):
            pm[w[:i]].append(w)
    return pm


def find_word_cubes(words, N=4, max_results=None):
    prefix_map = build_prefix_map(words)
    word_set = set(words)
    results = []

    def candidates_for_next(rows):
        k = len(rows)
        if k == 0:
            return words
        needed_prefixes = [''.join(rows[i][j] for i in range(k)) for j in range(N)]
        pools = [(len(prefix_map.get(pref, [])), idx) for idx, pref in enumerate(needed_prefixes)]
        pools.sort()
        _, best_j = pools[0]
        base_list = prefix_map.get(needed_prefixes[best_j], [])
        good = []
        for w in base_list:
            ok = True
            for j in range(N):
                pref = needed_prefixes[j] + w[j]
                if pref not in prefix_map:
                    ok = False
                    break
            if ok:
                good.append(w)
        return good

    def backtrack(rows, used):
        if max_results and len(results) >= max_results:
            return
        k = len(rows)
        if k == N:
            cols = [''.join(rows[r][c] for r in range(N)) for c in range(N)]
            if all(c in word_set for c in cols) and len(set(rows + cols)) == 2 * N:
                results.append(rows.copy())
            return

        for candidate in candidates_for_next(rows):
            if candidate in used:
                continue
            used.add(candidate)
            rows.append(candidate)
            backtrack(rows, used)
            rows.pop()
            used.remove(candidate)

    for w in words:
        backtrack([w], {w})
        if max_results and len(results) >= max_results:
            break

    return results


def main():
    base = os.path.dirname(__file__)
    wordlists_dir = os.path.normpath(os.path.join(base, '..', 'word_lists'))
    preferred = os.path.join(wordlists_dir, 'word_list_wordfreq.txt')
    if os.path.exists(preferred):
        words = load_word_list(filename=preferred, top_n=10000)
        print(f"Loaded {len(words)} words from {preferred}.")
    else:
        words = load_word_list(filename='word_list_wordfreq.txt', top_n=10000)
        print(f"Loaded {len(words)} words from word_list_wordfreq.txt.")

    N = 4
    squares = find_word_cubes(words, N=N, max_results=None)

    # filtering
    total_before = len(squares)
    valid_squares = []
    discarded = []
    for sq in squares:
        rows = sq
        cols = [''.join(sq[r][c] for r in range(N)) for c in range(N)]
        if len(set(rows)) != N:
            discarded.append(("duplicate_row", sq))
            continue
        if len(set(cols)) != N:
            discarded.append(("duplicate_col", sq))
            continue
        if set(rows).intersection(set(cols)):
            discarded.append(("row_equals_column", sq))
            continue
        valid_squares.append(sq)

    out_file_dir = wordlists_dir
    os.makedirs(out_file_dir, exist_ok=True)
    out_file = os.path.join(out_file_dir, 'word_cubes.txt')
    with open(out_file, 'w') as f:
        for sq in valid_squares:
            for row in sq:
                f.write(' '.join(row) + '\n')
            f.write('\n')
    print(f"Wrote {len(valid_squares)} word cubes to {out_file}")


if __name__ == '__main__':
    main()
