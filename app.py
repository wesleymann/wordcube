from flask import Flask, render_template, request, redirect, url_for, session
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

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


def compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks):
    """
    Enhanced feedback with Purple highlighting.
    - 'G' = correct position
    - 'Y' = present in the same row or column (wrong position)
    - 'P' = present elsewhere on grid (not in row/column)
    - '_' = not on grid at all
    
    Ignores revealed (black) letters and letters already marked green in any previous attempt.
    Treats spaces as empty (not matching anything).
    """
    result = ['_'] * 4
    
    # Collect all letters that have been marked green in any previous attempt
    green_letters_found = set()
    for attempt_idx, fb_rows in enumerate(feedbacks):
        for row_idx_fb, fb_chars in enumerate(fb_rows):
            for char_idx, fb_char in enumerate(fb_chars):
                if fb_char == 'G':
                    letter = attempts[attempt_idx][row_idx_fb][char_idx]
                    green_letters_found.add(letter)
    
    # Build set of revealed positions for this row
    revealed_in_row = {c for (r, c) in revealed if r == row_idx}
    
    # First pass: mark correct positions (skip spaces)
    for i, ch in enumerate(guess):
        if ch == ' ':
            result[i] = '_'
        elif ch == solution[i]:
            result[i] = 'G'
    
    # Build grid without revealed letters for yellow/purple checks
    cube_for_check = []
    for r in range(4):
        row_for_check = ''
        for c in range(4):
            if (r, c) not in revealed:
                row_for_check += cube[r][c]
            else:
                row_for_check += ''  # skip revealed positions
        cube_for_check.append(row_for_check)
    
    cube_flat = ''.join(cube_for_check)
    
    # Second pass: check for yellow/purple (skip spaces, skip letters already green)
    for i, ch in enumerate(guess):
        if ch == ' ':
            result[i] = '_'
            continue
        if result[i] == 'G':
            continue  # already correct, skip
        
        # Skip if this letter has already been found correctly
        if ch in green_letters_found:
            result[i] = '_'
            continue
        
        col_idx = i
        
        # Skip if this position is revealed
        if i in revealed_in_row:
            result[i] = '_'
            continue
        
        # Check: in same row (but not revealed positions)?
        in_row = ch in [cube[row_idx][c] for c in range(4) if c not in revealed_in_row]
        
        # Check: in same column (but not revealed positions)?
        in_col = any(ch == cube[r][col_idx] for r in range(4) if r != row_idx and (r, col_idx) not in revealed)
        
        if in_row or in_col:
            result[i] = 'Y'
        elif ch in cube_flat:
            result[i] = 'P'
        else:
            result[i] = '_'
    
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
    # show shake animation once if the last submission was incorrect
    shake = session.pop('shake', False)
    return render_template('index.html', cube=cube, revealed=revealed,
                           attempts=attempts, feedbacks=feedbacks,
                           max_attempts=MAX_ATTEMPTS, solved=solved,
                           shake=shake, guessed_letters=guessed_letters)


@app.route('/new')
def new_game():
    cubes = load_cubes()
    if not cubes:
        return "No cubes found. Please run main2.py to generate word_cubes.txt", 500
    cube = random.choice(cubes)
    # reveal 4 random positions
    all_pos = [(r, c) for r in range(4) for c in range(4)]
    revealed = random.sample(all_pos, 4)
    session['cube'] = cube
    session['revealed'] = revealed
    session['attempts'] = []
    session['feedbacks'] = []
    session['solved'] = False
    session['guessed_letters'] = []
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
    fbs = [compute_feedback_enhanced(guesses[i], cube[i], cube, i, revealed, attempts, feedbacks) for i in range(4)]
    attempts.append(guesses)
    feedbacks.append(fbs)
    session['attempts'] = attempts
    session['feedbacks'] = feedbacks
    # Extract absent letters from all feedbacks
    guessed_letters = []
    for attempt_idx, fb_rows in enumerate(feedbacks):
        for row_idx, fb_chars in enumerate(fb_rows):
            for char_idx, fb_char in enumerate(fb_chars):
                if fb_char == '_':
                    letter = attempts[attempt_idx][row_idx][char_idx]
                    if letter and letter != ' ' and letter not in guessed_letters:
                        guessed_letters.append(letter)
    session['guessed_letters'] = guessed_letters
    # solved if all green
    if all(fb == 'G' * 4 for fb in fbs):
        session['solved'] = True
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
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=8000)
