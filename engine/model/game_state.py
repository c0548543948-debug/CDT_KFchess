from engine.model.board import Board


class GameState:
    def __init__(self, board: Board):
        self.board: Board = board
        self.game_over: bool = False
        self.winner: str | None = None  # יכול להיות "white", "black" או None

    def clone(self) -> 'GameState':
        """מייצר עותק נפרד ועמוק של המצב (Snapshot) באופן בטוח לחלוטין"""
        # 1. שכפול עמוק של הלוח באמצעות מתודת ה-clone שלו
        cloned_board = self.board.clone()

        # 2. יצירת אובייקט GameState חדש עם הלוח המשוכפל והעתקת המשתנים
        new_state = GameState(cloned_board)
        new_state.game_over = self.game_over
        new_state.winner = self.winner

        return new_state