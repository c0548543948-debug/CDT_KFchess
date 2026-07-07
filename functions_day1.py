import sys


#תרגיל 1
def validate_board():
    # 1. קריאת כל הקלט מה-VPL ופיצול לשורות
    print("enter the validate_board()")
    test_input = """Board:
    wK . . bK
    . wP bP .
    wR . . bR
    Commands:
    print board"""

    # פיצול לפי שורות (כמו שעשינו קודם)
    lines = test_input.splitlines()
    #lines = sys.stdin.read().splitlines()

    board_rows = []
    in_board = False

    # 2. חילוץ שורות הלוח
    for line in lines:
        line = line.strip()

        if line == "Board:":
            in_board = True
            continue

        if line == "Commands:":
            in_board = False
            continue

        if in_board and line:
            pieces = line.split()
            board_rows.append(pieces)

    # אם הלוח ריק, אין מה להמשיך
    if not board_rows:
        return

    # 3. בדיקת אורך השורות (טסט 5)
    # ניקח את האורך של השורה הראשונה כבסיס להשוואה
    expected_width = len(board_rows[0])
    for row in board_rows:
        if len(row) != expected_width:
            print("ERROR ROW_WIDTH_MISMATCH")
            return

    # 4. בדיקת טוקנים חוקיים (טסט 4)
    valid_colors = {'w', 'b'}
    valid_pieces = {'K', 'Q', 'R', 'B', 'N', 'P'}

    for row in board_rows:
        for token in row:
            # אם זו נקודה, זה תקין
            if token == '.':
                continue
            # אם זה כלי, הוא חייב להיות באורך 2, עם צבע חוקי וכלי חוקי
            if len(token) == 2 and token[0] in valid_colors and token[1] in valid_pieces:
                continue
            # אם הגענו לכאן, הטוקן לא חוקי!
            print("ERROR UNKNOWN_TOKEN")
            return

    # 5. הדפסת הלוח בפורמט קנוני (טסט 2 ו-3)
    # נדפיס את הלוח רק אם הפקודה 'print board' קיימת בקלט
    # (הערה: לפי הטסטים, פשוט מדפיסים את הלוח כשהכל תקין)
    for row in board_rows:
        print(" ".join(row))

    #החזרת המטריצה בשביל התרגיל הבא
    return board_rows

#תרגיל 2
def click_mapping_controller_selection():
    mat_board=validate_board()
