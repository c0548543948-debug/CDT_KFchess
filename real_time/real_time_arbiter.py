from __future__ import annotations
from model.position import Position
from model.board import Board
from model.motion import Motion
from config import COOLDOWN_BY_KIND, DEFAULT_COOLDOWN

class RealTimeArbiter:
    def __init__(self):
        self._active_motions: list[Motion] = []

    def is_piece_moving(self, piece) -> bool:
        return any(m.piece == piece and not m.is_finished for m in self._active_motions)

    def is_route_active(self, board: Board, source: Position, target: Position) -> bool:
        piece = board.get_piece_at(source)
        if not piece:
            return False
        return self.is_piece_moving(piece)

    def start_motion(self, board: Board, source: Position, target: Position) -> None:
        piece = board.get_piece_at(source)
        if not piece:
            return
        self._active_motions.append(Motion(piece, target, is_jump=False))

    def start_jump_motion(self, board: Board, source: Position) -> None:
        """הכלי קופץ למעלה מעל הריבוע שלו — source == target, משך STEP_DURATION_MS."""
        piece = board.get_piece_at(source)
        if not piece:
            return
        board.remove_piece_at(source)
        self._active_motions.append(Motion(piece, source, is_jump=True))

    def advance_time(self, ms: int, board: Board) -> list[str]:
        """מחזירה רשימת צבעי מלכים שנאכלו."""
        captured_kings: list[str] = []
        remaining_ms = ms

        for pos in list(board._grid.keys()):
            piece = board.get_piece_at(pos)
            if piece and piece.cooldown_remaining > 0:
                piece.cooldown_remaining = max(0, piece.cooldown_remaining - ms)

        tick_size = 100
        while remaining_ms > 0:
            current_tick = min(tick_size, remaining_ms)
            remaining_ms -= current_tick

            for motion in self._active_motions:
                if not motion.is_finished:
                    motion.advance_time(current_tick)

            self._resolve_collisions(board, captured_kings)

            for motion in list(self._active_motions):
                if motion.is_finished:
                    self._handle_arrival(motion, board, captured_kings)
                    if motion in self._active_motions:
                        self._active_motions.remove(motion)

        return captured_kings

    def _resolve_collisions(self, board: Board, captured_kings: list[str]) -> None:
        motions_to_remove = set()
        motions_to_arrive_instantly = set()

        for motion in self._active_motions:
            if motion in motions_to_remove or motion in motions_to_arrive_instantly or motion.is_finished:
                continue

            next_pos = motion.get_next_physical_position()
            if not next_pos:
                continue  # כלים קופצים (is_jump, 0 צעדים) — רק מגיבים, לא יוזמים

            jump_captor = None
            air_enemy = None
            air_friend = None

            for other in self._active_motions:
                if (other == motion or other.is_finished
                        or other in motions_to_remove or other in motions_to_arrive_instantly):
                    continue

                hits = (other.get_current_physical_position() == next_pos or
                        other.get_next_physical_position() == next_pos)
                if not hits:
                    continue

                idx_self = self._active_motions.index(motion)
                idx_other = self._active_motions.index(other)

                if other.piece.color == motion.piece.color:
                    if idx_self > idx_other:
                        air_friend = other
                    break
                else:
                    if other.is_jump:
                        jump_captor = other  # כלי קופץ תופס את motion
                        break
                    elif idx_self < idx_other:
                        air_enemy = other  # motion מנצח, other מפסיד
                        break

            if jump_captor:
                board.remove_piece_at(motion.source)
                if motion.piece.kind == "king":
                    captured_kings.append(motion.piece.color)
                motions_to_remove.add(motion)
                motions_to_arrive_instantly.add(jump_captor)
                continue

            if air_friend:
                motion.force_stop_at_step(motion.get_current_physical_step_idx())
                motions_to_arrive_instantly.add(motion)
                continue

            if air_enemy:
                board.remove_piece_at(air_enemy.source)
                if air_enemy.piece.kind == "king":
                    captured_kings.append(air_enemy.piece.color)
                motions_to_remove.add(air_enemy)
                continue

            static = board.get_piece_at(next_pos)
            if not static:
                continue

            idx = motion.get_current_physical_step_idx()
            if static.color == motion.piece.color:
                motion.force_stop_at_step(idx)
            else:
                board.remove_piece_at(next_pos)
                if static.kind == "king":
                    captured_kings.append(static.color)
                motion.force_stop_at_step(idx + 1)
            motions_to_arrive_instantly.add(motion)

        for m in motions_to_arrive_instantly:
            self._handle_arrival(m, board, captured_kings)
            if m in self._active_motions:
                self._active_motions.remove(m)

        for m in motions_to_remove:
            if m in self._active_motions:
                self._active_motions.remove(m)

    def _handle_arrival(self, motion: Motion, board: Board, captured_kings: list[str]) -> None:
        if motion.source != motion.target:
            board.remove_piece_at(motion.source)

        target_piece = board.get_piece_at(motion.target)
        if target_piece and target_piece.color != motion.piece.color:
            board.remove_piece_at(motion.target)
            if target_piece.kind == "king":
                captured_kings.append(target_piece.color)

        motion.piece.cell = motion.target
        if board.get_piece_at(motion.target) is None:
            board.add_piece(motion.piece)

        if motion.piece.kind in ("pawn", "p"):
            if (motion.piece.color == "white" and motion.target.row == 0) or \
               (motion.piece.color == "black" and motion.target.row == board.height - 1):
                motion.piece._kind = "queen"

        motion.piece.cooldown_remaining = COOLDOWN_BY_KIND.get(motion.piece.kind, DEFAULT_COOLDOWN)
