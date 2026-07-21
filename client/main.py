import sys
from engine.model import GameState
from engine.real_time import RealTimeArbiter
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper
from input.controller import GameController
from engine.io_utils.board_printer import BoardPrinter
from engine.io_utils import BoardParser

def read_board_section():
    lines = []
    reading_board = False
    for line in sys.stdin:
        trimmed = line.strip()
        if trimmed.lower() == "board:":
            reading_board = True
            continue
        if trimmed.lower() == "commands:" or (trimmed == "" and reading_board):
            break
        if reading_board:
            lines.append(line.rstrip('\r\n'))
    return lines

def main():
    board_lines = read_board_section()
    if not board_lines:
        return
    try:
        board = BoardParser.parse("\n".join(board_lines))
    except ValueError as e:
        print(f"ERROR {e}")
        return

    game_state = GameState(board)
    arbiter = RealTimeArbiter()
    engine = GameEngine(game_state, arbiter)
    mapper = BoardMapper()
    controller = GameController(engine, mapper)
    clock = 0

    for line in sys.stdin:
        cmd = line.strip()
        if not cmd:
            continue
        parts = cmd.split()
        op = parts[0].lower()

        if op == "click" and len(parts) == 3:
            controller.handle_click(int(parts[1]), int(parts[2]))

        elif op == "wait" and len(parts) == 2:
            ms = int(parts[1])
            clock += ms
            engine.wait(ms)

        elif op == "jump" and len(parts) == 3:
            x, y = int(parts[1]), int(parts[2])
            controller.handle_click(x, y)   # לחיצה ראשונה — בחירה
            controller.handle_click(x, y)   # לחיצה שנייה — קפיצה

        elif op == "print" and len(parts) == 2 and parts[1].lower() == "board":
            print(BoardPrinter.print_board(engine.get_snapshot().board))

if __name__ == "__main__":
    main()
