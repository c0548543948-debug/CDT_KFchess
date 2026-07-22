from __future__ import annotations
from engine.model.position import Position
from engine.model.piece import Piece
from engine.config import STEP_DURATION_MS

class Motion:
    def __init__(self, piece: Piece, target: Position, is_jump: bool = False):
        self.piece: Piece = piece
        self.source: Position = piece.cell
        self.target: Position = target
        self.is_jump: bool = is_jump

        self.steps: list[Position] = self._calculate_steps_path()
        self.total_steps: int = len(self.steps) - 1
        self.step_duration_ms: int = STEP_DURATION_MS

        # קפיצה במקום (source == target): משך של צעד אחד באוויר
        if is_jump and self.total_steps == 0:
            self.total_duration_ms = self.step_duration_ms
        else:
            self.total_duration_ms = self.total_steps * self.step_duration_ms

        self.elapsed_time: int = 0
        self.is_blocked: bool = False
        self.blocked_at_step: int = -1

    def _calculate_steps_path(self) -> list[Position]:
        steps = [self.source]
        if self.source == self.target:
            return steps  # קפיצה במקום
        if self.piece.kind == "knight":
            steps.append(self.target)
            return steps
        row_diff = self.target.row - self.source.row
        col_diff = self.target.col - self.source.col
        step_row = (row_diff // abs(row_diff)) if row_diff != 0 else 0
        step_col = (col_diff // abs(col_diff)) if col_diff != 0 else 0
        cur_row = self.source.row + step_row
        cur_col = self.source.col + step_col
        while (cur_row, cur_col) != (self.target.row, self.target.col):
            steps.append(Position(row=cur_row, col=cur_col))
            cur_row += step_row
            cur_col += step_col
        steps.append(self.target)
        return steps

    def advance_time(self, ms: int) -> None:
        if self.is_blocked:
            return
        self.elapsed_time = min(self.total_duration_ms, self.elapsed_time + ms)

    def get_current_physical_step_idx(self) -> int:
        if self.is_blocked:
            return self.blocked_at_step
        return min(self.elapsed_time // self.step_duration_ms, self.total_steps)

    def get_current_physical_position(self) -> Position:
        return self.steps[self.get_current_physical_step_idx()]

    def get_next_physical_position(self) -> Position | None:
        if self.is_blocked:
            return None
        idx = self.get_current_physical_step_idx()
        if idx >= self.total_steps:
            return None
        return self.steps[idx + 1]

    def get_interpolated_position(self) -> tuple[float, float]:
        if self.is_blocked:
            pos = self.steps[self.blocked_at_step]
            return float(pos.row), float(pos.col)
        idx = self.get_current_physical_step_idx()
        if idx >= self.total_steps:
            p = self.steps[self.total_steps]
            return float(p.row), float(p.col)
        fraction = (self.elapsed_time % self.step_duration_ms) / float(self.step_duration_ms)
        p1, p2 = self.steps[idx], self.steps[idx + 1]
        return p1.row + (p2.row - p1.row) * fraction, p1.col + (p2.col - p1.col) * fraction

    def force_stop_at_step(self, step_idx: int) -> None:
        self.is_blocked = True
        self.blocked_at_step = step_idx
        self.elapsed_time = step_idx * self.step_duration_ms
        self.target = self.steps[step_idx]

    @property
    def is_finished(self) -> bool:
        if self.is_blocked:
            return True
        return self.elapsed_time >= self.total_duration_ms
