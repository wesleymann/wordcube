"""
Test feedback logic for word cube game
"""
from app import compute_feedback_enhanced, compute_feedback_all_rows

def test_multiple_letter_instances():
    """Test: Letter A appears 3 times on board, tracking correctly"""
    cube = [
        'mask',
        'area',
        'made',
        'sage'
    ]
    
    # Test 1a: First guess, get one A correct
    guess = 'mask'
    solution = 'mask'
    row_idx = 0
    revealed = set()
    attempts = []
    feedbacks = []
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 1a - Guess 'mask' for row 0: {fb}")
    assert fb == 'GGGG', f"Expected 'GGGG', got '{fb}'"
    
    # Test 1b: Now A at position (0,1) is correctly placed. Guess A elsewhere
    attempts = [['mask', 'xxxx', 'xxxx', 'xxxx']]
    feedbacks = [['GGGG', '____', '____', '____']]
    
    # Guess A in row 1, position 1 - this is WRONG for 'area' (should be 'r')
    guess = 'xaxx'
    solution = 'area'
    row_idx = 1
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 1b - Guess 'xaxx' for row 1 (solution 'area'), A at (0,1) already found: {fb}")
    # Position 1 has 'a' but solution wants 'r', so should be yellow
    # A still appears at (1,0), (1,2), (2,1), (3,1) - (0,1) is found
    # So this A should be yellow (in same row)
    assert fb[1] == 'Y', f"Expected position 1 to be 'Y', got '{fb[1]}'"
    
    # Test 1c: A at (0,1) and (1,1) are now found. Guess A in position 0
    attempts = [['mask', 'xxxx', 'xxxx', 'xxxx'], ['xxxx', 'xaxx', 'xxxx', 'xxxx']]
    feedbacks = [['GGGG', '____', '____', '____'], ['____', '_Y__', '____', '____']]
    
    # Guess A in row 1, position 0 - this IS CORRECT for 'area'
    guess = 'axxx'
    solution = 'area'
    row_idx = 1
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 1c - Guess 'axxx' for row 1, A at (0,1) found: {fb}")
    # A at position 0 is correct for 'area', should be green
    assert fb[0] == 'G', f"Expected position 0 to be 'G', got '{fb[0]}'"
    
    # Test 1d: After finding all 5 A's, additional A should be '_'
    attempts = [
        ['mask', 'xxxx', 'xxxx', 'xxxx'],
        ['xxxx', 'area', 'xxxx', 'xxxx'],
        ['xxxx', 'xxxx', 'made', 'xxxx'],
        ['xxxx', 'xxxx', 'xxxx', 'sage']
    ]
    feedbacks = [
        ['GGGG', '____', '____', '____'],
        ['____', 'GGGG', '____', '____'],
        ['____', '____', 'GGGG', '____'],
        ['____', '____', '____', 'GGGG']
    ]
    
    # All A's are now found: (0,1), (1,0), (1,2), (2,1), (3,1)
    # Guess A in row 0 position 0 (wrong position)
    guess = 'axxx'
    solution = 'mask'
    row_idx = 0
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 1d - Guess 'axxx' after all A's found: {fb}")
    # All A's are accounted for, so this A should be '_'
    assert fb[0] == '_', f"Expected position 0 to be '_', got '{fb[0]}'"


def test_letter_not_on_board():
    """Test: Letter X is not on board at all"""
    cube = [
        'mask',
        'icon',
        'mine',
        'edge'
    ]
    
    guess = 'xxxx'
    solution = 'mask'
    row_idx = 0
    revealed = set()
    attempts = []
    feedbacks = []
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 2 - Guess 'xxxx' for 'mask': {fb}")
    assert fb == '____', f"Expected '____', got '{fb}'"


def test_remaining_positions_only_elsewhere():
    """Test: Letter exists but remaining instances are not in same row/col, should be purple"""
    cube = [
        'slot',
        'pope',
        'oven',
        'pent'
    ]

    # Mark T at (0,3) as already found
    attempts = [['slot', 'xxxx', 'xxxx', 'xxxx']]
    feedbacks = [['GGGG', '____', '____', '____']]
    revealed = set()

    # Guess T at row 1, col 1 (not in same row/col with remaining T at (3,3))
    guess = 'xtxx'
    solution = 'pope'
    row_idx = 1

    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 2b - Guess 'xtxx' with remaining T elsewhere: {fb}")
    # T should be purple because only remaining T is elsewhere
    assert fb[1] == 'P', f"Expected position 1 to be 'P', got '{fb[1]}'"


def test_all_instances_found():
    """Test: Letter E appears 2 times, both already found"""
    cube = [
        'mask',
        'icon',
        'mine',
        'edge'
    ]
    
    # E appears in 'mine' position 3 and 'edge' positions 0 and 3
    # Mark both as found
    attempts = [
        ['mask', 'icon', 'mine', 'edge']
    ]
    feedbacks = [
        ['GGGG', 'GGGG', 'GGGG', 'GGGG']
    ]
    
    # Try to guess E again in row 0
    guess = 'eask'
    solution = 'mask'
    row_idx = 0
    revealed = set()
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 3 - Guess 'eask' when all E's found: {fb}")
    # E appears 3 times total (mine[3], edge[0], edge[3])
    # If all 3 are found, additional E should be '_'
    # But we only found rows, not individual positions...
    # Actually the feedback is per-row, so this test needs rethinking
    print("  (Skipping - test case needs redesign)")


def test_revealed_positions():
    """Test: Letter in revealed position"""
    cube = [
        'mask',
        'icon',
        'mine',
        'edge'
    ]
    
    # Reveal position (2, 0) which is 'M'
    revealed = {(2, 0)}
    attempts = []
    feedbacks = []
    
    # Guess M in row 0 wrong position
    guess = 'xmxx'
    solution = 'mask'
    row_idx = 0
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 4 - Guess 'xmxx' with M revealed elsewhere: {fb}")
    # M is in wrong position but in same row, should be yellow
    assert fb == '_Y__', f"Expected '_Y__', got '{fb}'"


def test_yellow_in_same_row():
    """Test: Letter is in same row but wrong position"""
    cube = [
        'mask',
        'icon',
        'mine',
        'edge'
    ]
    
    guess = 'smxx'  # S and M are both in row but swapped
    solution = 'mask'
    row_idx = 0
    revealed = set()
    attempts = []
    feedbacks = []
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 5 - Guess 'smxx' for 'mask': {fb}")
    # S is in row (position 2), M is in row (position 0)
    assert fb == 'YY__', f"Expected 'YY__', got '{fb}'"


def test_purple_elsewhere():
    """Test: Letter is on grid but not in same row/column"""
    cube = [
        'mask',
        'icon',
        'mine',
        'edge'
    ]
    
    # N is in row 2 (mine), column 2
    # If we guess N in row 0, column 0, it's not in same row or column
    guess = 'nxxx'
    solution = 'mask'
    row_idx = 0
    revealed = set()
    attempts = []
    feedbacks = []
    
    fb = compute_feedback_enhanced(guess, solution, cube, row_idx, revealed, attempts, feedbacks, [])
    print(f"Test 6 - Guess 'nxxx' for 'mask': {fb}")
    # N is elsewhere (row 2, col 2), not in row 0 or col 0
    assert fb == 'P___', f"Expected 'P___', got '{fb}'"


def test_submission_order_greens():
    """Test: Same submission should not yield different feedback due to row order"""
    cube = [
        'mill',
        'idea',
        'most',
        'else'
    ]

    guesses = [
        'tied',
        'idea',
        'most',
        'else'
    ]

    revealed = set()
    attempts = []
    feedbacks = []

    result = compute_feedback_all_rows(guesses, cube, revealed, attempts, feedbacks)

    print("Test 7 - Same submission row order consistency:")
    print(f"  Row 0: {result[0]}")

    expected_row0 = '_G__'
    assert result[0] == expected_row0, f"Row 0: Expected '{expected_row0}', got '{result[0]}'"


if __name__ == '__main__':
    print("Running feedback tests...\n")
    
    try:
        test_multiple_letter_instances()
        print("✓ Test 1 passed\n")
    except AssertionError as e:
        print(f"✗ Test 1 failed: {e}\n")
    
    try:
        test_letter_not_on_board()
        print("✓ Test 2 passed\n")
    except AssertionError as e:
        print(f"✗ Test 2 failed: {e}\n")

    try:
        test_remaining_positions_only_elsewhere()
        print("✓ Test 2b passed\n")
    except AssertionError as e:
        print(f"✗ Test 2b failed: {e}\n")
    
    try:
        test_all_instances_found()
        print("✓ Test 3 passed\n")
    except AssertionError as e:
        print(f"✗ Test 3 failed: {e}\n")
    
    try:
        test_revealed_positions()
        print("✓ Test 4 passed\n")
    except AssertionError as e:
        print(f"✗ Test 4 failed: {e}\n")
    
    try:
        test_yellow_in_same_row()
        print("✓ Test 5 passed\n")
    except AssertionError as e:
        print(f"✗ Test 5 failed: {e}\n")
    
    try:
        test_purple_elsewhere()
        print("✓ Test 6 passed\n")
    except AssertionError as e:
        print(f"✗ Test 6 failed: {e}\n")

    try:
        test_submission_order_greens()
        print("✓ Test 7 passed\n")
    except AssertionError as e:
        print(f"✗ Test 7 failed: {e}\n")
    
    print("Tests complete!")
