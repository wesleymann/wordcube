from flask import Flask, render_template, request, redirect, url_for, session
import random
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# expose Python builtin helpers to Jinja templates (safe convenience)
app.jinja_env.globals['enumerate'] = enumerate

CANDIDATE_CUBES = os.path.join('word_lists', 'word_cubes.txt')
CUBES_FILE = CANDIDATE_CUBES if os.path.exists(CANDIDATE_CUBES) else 'word_cubes.txt'
MAX_ATTEMPTS = 6


def load_cubes():
    cubes = []
    if not os.path.exists(CUBES_FILE):
        return cubes
    with open(CUBES_FILE, 'r') as f:
        text = f.read()
    blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
    for b in blocks:
        rows = [line.replace(' ', '').lower() for line in b.splitlines() if line.strip()]
        if len(rows) == 4 and all(len(r) == 4 for r in rows):
            cubes.append(rows)
    return cubes


def compute_feedback(guess, solution):
    # Legacy feedback function (kept for backward compatibility)
    GR = 'G'
    YL = 'Y'
    result = ['_'] * 4
    sol = list(solution)
    for i, ch in enumerate(guess):
        if ch == sol[i]:
            result[i] = GR
            sol[i] = None
    for i, ch in enumerate(guess):
        if result[i] == GR:
            continue
        if ch in sol:
            result[i] = YL
            sol[sol.index(ch)] = None
        else:
            result[i] = '_'
    return ''.join(result)


def compute_feedback_all_rows(guesses, cube, revealed, attempts, feedbacks):
    """Compute feedback for all 4 rows, including previously found correct positions"""
    all_feedback = []

    # Precompute greens for the entire current submission so row order doesn't affect feedback
    submission_greens = set()
    for r in range(4):
        guess_row = guesses[r]
        solution_row = cube[r]
        for c, ch in enumerate(guess_row):
            if ch != ' ' and ch == solution_row[c]:
                submission_greens.add((r, c))

    for row_idx in range(4):
        fb = compute_feedback_enhanced(
            guesses[row_idx],
            cube[row_idx],
            cube,
            row_idx,
            revealed,
            attempts,
            feedbacks,
            all_feedback,
            submission_greens,
        )
        all_feedback.append(fb)

    return all_feedback


def compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, current_feedback, submission_greens=None):
    """
    Three-pass feedback logic:
    Pass 1 (Green): Mark all letters that are correct at this position
    Pass 2 (Yellow): Mark letters that are NOT green, AND match elsewhere in same row/column, AND that instance is not already green
    Pass 3 (Purple): Mark letters that are NOT green/yellow, BUT exist somewhere on the puzzle
    Revealed positions are shown as '_' (absent/black) regardless of feedback type.
    """
    result = ['_'] * 4
    revealed_set = set(revealed)
    revealed_in_row = {c for (r, c) in revealed if r == row_idx}
    
    # Collect all green positions from previous attempts and (optionally) full current submission
    all_greens = set()
    if submission_greens is not None:
        all_greens.update(submission_greens)
    for attempt_idx, fb_rows in enumerate(feedbacks):
        for row_idx_fb, fb_chars in enumerate(fb_rows):
            for char_idx, fb_char in enumerate(fb_chars):
                if fb_char == 'G':
                    all_greens.add((row_idx_fb, char_idx))
    
    # Include greens from current submission rows already processed (legacy fallback)
    if submission_greens is None:
        for row_idx_fb, fb_chars in enumerate(current_feedback):
            for char_idx, fb_char in enumerate(fb_chars):
                if fb_char == 'G':
                    all_greens.add((row_idx_fb, char_idx))
    
    # PASS 1: Mark correct positions (green)
    for i, ch in enumerate(guess):
        if ch == ' ':
            result[i] = '_'
        elif ch == solution[i]:
            result[i] = 'G'
            all_greens.add((row_idx, i))
    
    # PASS 2: Mark yellow (in same row or column, but not green, AND not all instances matched)
    for i, ch in enumerate(guess):
        if ch == ' ' or result[i] == 'G':
            continue
        
        # Check same row: does this letter exist elsewhere in the row AND not already matched green?
        in_row = False
        for c in range(4):
            if c == i or (row_idx, c) in revealed_set:
                continue
            if cube[row_idx][c] == ch and (row_idx, c) not in all_greens:
                in_row = True
                break
        
        # Check same column: does this letter exist elsewhere (other rows) AND not already matched green?
        in_col = False
        for r in range(4):
            if r == row_idx or (r, i) in revealed_set:
                continue
            if cube[r][i] == ch and (r, i) not in all_greens:
                in_col = True
                break
        
        if in_row or in_col:
            result[i] = 'Y'
    
    # PASS 3: Mark purple (exists on puzzle, but not in same row/col, not green, not yellow)
    for i, ch in enumerate(guess):
        if ch == ' ' or result[i] in ['G', 'Y']:
            continue
        
        # Check if letter exists anywhere else on the grid (not in same row/col, not revealed, not already green)
        found_elsewhere = False
        for r in range(4):
            for c in range(4):
                if cube[r][c] == ch and (r, c) not in revealed_set and (r, c) not in all_greens:
                    # Skip current position and same row/col (those were checked in yellow)
                    if r == row_idx or c == i:
                        continue
                    found_elsewhere = True
                    break
            if found_elsewhere:
                break
        
        result[i] = 'P' if found_elsewhere else '_'
    
    return ''.join(result)

@app.route('/')
def index():
    if 'cube' not in session:
        return redirect(url_for('new_game'))
    cube = session['cube']
    revealed = set(tuple(p) for p in session.get('revealed', []))
    attempts = session.get('attempts', [])
    feedbacks = session.get('feedbacks', [])
    solved = session.get('solved', False)
    guessed_letters = session.get('guessed_letters', [])
    start_time = session.get('start_time')
    end_time = session.get('end_time')
    # show shake animation once if the last submission was incorrect
    shake = session.pop('shake', False)
    return render_template('index.html', cube=cube, revealed=revealed,
                           attempts=attempts, feedbacks=feedbacks,
                           max_attempts=MAX_ATTEMPTS, solved=solved,
                           shake=shake, guessed_letters=guessed_letters,
                           start_time=start_time, end_time=end_time)


@app.route('/new', methods=['GET', 'POST'])
def new_game():
    if request.method == 'GET':
        return render_template('new_game.html')

    level = request.form.get('level', 'hard').lower()
    reveal_counts = {
        'easy': 8,
        'medium': 6,
        'hard': 4,
        'insane': 0,
    }
    reveal_count = reveal_counts.get(level, 4)

    cubes = load_cubes()
    if not cubes:
        return "No cubes found. Please run main2.py to generate word_cubes.txt", 500
    cube = random.choice(cubes)
    # reveal N random positions based on difficulty
    all_pos = [(r, c) for r in range(4) for c in range(4)]
    revealed = random.sample(all_pos, reveal_count) if reveal_count > 0 else []
    session['cube'] = cube
    session['revealed'] = revealed
    session['difficulty'] = level
    session['attempts'] = []
    session['feedbacks'] = []
    session['solved'] = False
    session['guessed_letters'] = []
    session['start_time'] = time.time()
    session['end_time'] = None
    return redirect(url_for('index'))


@app.route('/guess', methods=['POST'])
def guess():
    if 'cube' not in session:
        return redirect(url_for('new_game'))
    cube = session['cube']
    if session.get('solved'):
        return redirect(url_for('index'))
    guesses = []
    for i in range(4):
        v = request.form.get(f'row{i}', '').lower()
        # Allow partial submissions with spaces; validate length and characters
        if len(v) != 4 or not all(c.isalpha() or c == ' ' for c in v):
            return redirect(url_for('index'))
        guesses.append(v)
    # compute feedbacks with enhanced logic (G/Y/P/_)
    revealed = set(tuple(p) for p in session.get('revealed', []))
    attempts = session.get('attempts', [])
    feedbacks = session.get('feedbacks', [])
    
    fbs = compute_feedback_all_rows(guesses, cube, revealed, attempts, feedbacks)
    
    attempts.append(guesses)
    feedbacks.append(fbs)
    session['attempts'] = attempts
    session['feedbacks'] = feedbacks
    
    # Track which positions have been correctly placed
    correctly_placed_positions = set()
    for attempt_idx, fb_rows in enumerate(feedbacks):
        for row_idx_fb, fb_chars in enumerate(fb_rows):
            for char_idx, fb_char in enumerate(fb_chars):
                if fb_char == 'G':
                    correctly_placed_positions.add((row_idx_fb, char_idx))
    
    # Extract letters that got '_' feedback
    guessed_letters = []
    for attempt_idx, fb_rows in enumerate(feedbacks):
        for row_idx, fb_chars in enumerate(fb_rows):
            for char_idx, fb_char in enumerate(fb_chars):
                if fb_char == '_':
                    letter = attempts[attempt_idx][row_idx][char_idx]
                    if letter and letter != ' ' and letter not in guessed_letters:
                        # Check if there are any remaining instances of this letter
                        remaining = False
                        for r in range(4):
                            for c in range(4):
                                if cube[r][c] == letter and (r, c) not in correctly_placed_positions and (r, c) not in revealed:
                                    remaining = True
                                    break
                            if remaining:
                                break
                        # Add to guessed letters if no remaining instances
                        if not remaining:
                            guessed_letters.append(letter)
    session['guessed_letters'] = guessed_letters
    # solved if all green
    if all(fb == 'G' * 4 for fb in fbs):
        session['solved'] = True
        if not session.get('end_time'):
            session['end_time'] = time.time()
    else:
        # trigger a one-time shake animation client-side
        session['shake'] = True
    # out of attempts resets allowed but stays on page
    return redirect(url_for('index'))


@app.route('/reveal_answer')
def reveal_answer():
    if 'cube' not in session:
        return redirect(url_for('new_game'))
    session['revealed'] = [(r, c) for r in range(4) for c in range(4)]
    session['solved'] = True
    if not session.get('end_time'):
        session['end_time'] = time.time()
    return redirect(url_for('index'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
