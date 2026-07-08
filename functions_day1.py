import sys


# פונקציית עזר - קליטת המטריצה והפקודות ללא בדיקות תקינות
def parse_input():
    test_input = """Board:
    wK . .
    . . bP
    . . .
    Commands:
    print board
    click 50 50
    click 150 150
    wait 500
    print board"""
    #lines = sys.stdin.read().splitlines()
    lines=test_input.splitlines()
    board_rows = []
    commands = []
    in_board = False
    in_commands = False

    for line in lines:
        line = line.strip()

        if line == "Board:":
            in_board = True
            continue

        if line == "Commands:":
            in_board = False
            in_commands = True
            continue

        if in_board and line:
            pieces = line.split()
            board_rows.append(pieces)

        if in_commands and line:
            commands.append(line)

    if not board_rows:
        return None, None

    return board_rows, commands


# פונקציה להדפסת מטריצת משחק
def print_board(mat_game):
    for row in mat_game:
        print(" ".join(row))


# תרגיל 1 - בדיקת תקינות הלוח
def validate_board(board_rows):
    if not board_rows:
        return None

    # בדיקת אורך השורות
    expected_width = len(board_rows[0])
    for row in board_rows:
        if len(row) != expected_width:
            print("ERROR ROW_WIDTH_MISMATCH")
            return None

    # בדיקת טוקנים חוקיים
    valid_colors = {'w', 'b'}
    valid_pieces = {'K', 'Q', 'R', 'B', 'N', 'P'}

    for row in board_rows:
        for token in row:
            if token == '.':
                continue
            if len(token) == 2 and token[0] in valid_colors and token[1] in valid_pieces:
                continue
            print("ERROR UNKNOWN_TOKEN")
            return None

    return board_rows


# בדיקת גבולות קואורדינטות
def validate_coordinates(row, col, max_row, max_col):
    if row < 0 or col < 0 or row > max_row or col > max_col:
        return False
    return True


# ביצוע פקודות - תרגיל 2
def execute_commands():
    board_row, commands = parse_input()
    if board_row is None or commands is None:
        return

    mat_game = validate_board(board_row)
    if mat_game is None:
        return  # אם הלוח לא תקין, הוולידציה כבר הדפיסה שגיאה ונעצרנו

    selected_location = None
    color = None
    clock = 0

    # ביצוע הפקודות
    for command in commands:
        command = command.split()
        if not command:
            continue

        if command[0] == "print" and command[1] == "board":
            print_board(mat_game)
            continue

        if command[0] == "wait":
            clock += int(command[1])
            continue

        if command[0] == "click":
            # x קובע עמודה (col), y קובע שורה (row)
            col = int(command[1]) // 100
            row = int(command[2]) // 100

            # האם המיקומים בגבולות המטריצה
            if not validate_coordinates(row, col, len(mat_game) - 1, len(mat_game[0]) - 1):
                continue

            current_piece = mat_game[row][col]

            # מצב א': עדיין לא נבחר חייל
            if selected_location is None:
                if current_piece != ".":
                    selected_location = (row, col)
                    color = current_piece[0]  # שמירת צבע החייל שנבחר
                continue

            # מצב ב': כבר יש חייל נבחר קודם לכן
            # 1. החלפת בחירה (לחצו על חייל אחר מאותו הצבע)
            if current_piece != "." and current_piece[0] == color:
                selected_location = (row, col)
                continue

            # 2. ביצוע תנועה (לחצו על משבצת ריקה או על כלי אויב)
            prev_row, prev_col = selected_location
            mat_game[row][col] = mat_game[prev_row][prev_col]
            mat_game[prev_row][prev_col] = "."

            # איפוס הבחירה לאחר תנועה
            selected_location = None
            color = None


# הפעלת התוכנית
if __name__ == "__main__":
    execute_commands()