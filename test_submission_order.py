"""
Test that feedback considers all greens in current submission, not just previous rows
"""
from app import compute_feedback_all_rows

def test_same_submission_greens():
    """Test: Row 0 feedback should consider greens from rows 1-3 in same submission"""
    cube = [
        'mill',  # actual solution
        'idea',
        'most',
        'else'
    ]
    
    guesses = [
        'tied',  # E at position 2 - should be absent, not yellow
        'idea',  # perfect match
        'most',  # perfect match
        'else'   # perfect match
    ]
    
    revealed = set()
    attempts = []
    feedbacks = []
    
    result = compute_feedback_all_rows(guesses, cube, revealed, attempts, feedbacks)
    
    print(f"Cube:")
    for row in cube:
        print(f"  {row}")
    print(f"\nGuesses:")
    for row in guesses:
        print(f"  {row}")
    print(f"\nFeedback:")
    for i, fb in enumerate(result):
        print(f"  Row {i}: {fb}")
    
    # Row 0: TIED vs MILL
    # T at (0,0): exists at (2,3) but (2,3) is green in current submission -> absent
    # I at (0,1): correct -> green
    # E at (0,2): exists at (1,2) but (1,2) is green in current submission -> absent
    # D at (0,3): exists at (1,1) but (1,1) is green in current submission -> absent
    expected_row0 = '_G__'
    
    print(f"\nRow 0 expected: {expected_row0}")
    print(f"Row 0 got:      {result[0]}")
    
    assert result[0] == expected_row0, f"Row 0: Expected '{expected_row0}', got '{result[0]}'"
    print("✓ Test passed!")

if __name__ == '__main__':
    test_same_submission_greens()
