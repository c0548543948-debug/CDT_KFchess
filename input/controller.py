from __future__ import annotations
from model.position import Position
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper

class GameController:
    def __init__(self, game_engine: GameEngine, board_mapper: BoardMapper):
        self._engine = game_engine
        self._mapper = board_mapper
        self._selected_position = None

    def handle_click(self, x: int, y: int) -> None:
        clicked_pos = self._mapper.to_board_position(x, y)
        current_board = self._engine.get_snapshot().board

        if not current_board.is_in_bounds(clicked_pos):
            self._selected_position = None
            return

        clicked_piece = current_board.get_piece_at(clicked_pos)

        # אין כלי מסומן — לחיצה ראשונה
        if self._selected_position is None:
            if clicked_piece is not None:
                self._selected_position = clicked_pos
            return

        source_pos = self._selected_position
        source_piece = current_board.get_piece_at(source_pos)

        # לחיצה כפולה על אותו כלי → קפיצה הגנתית
        if clicked_pos == source_pos:
            self._selected_position = None
            self._engine.jump_request(source_pos)
            return

        # לחיצה על כלי חבר → החלפת סלקציה
        if (source_piece is not None and clicked_piece is not None
                and source_piece.color == clicked_piece.color):
            self._selected_position = clicked_pos
            return

        # הזזה
        self._selected_position = None
        self._engine.move_request(source_pos, clicked_pos)

    @property
    def selected_position(self) -> Position:
        return self._selected_position
