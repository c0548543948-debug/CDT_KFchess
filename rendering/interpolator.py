from __future__ import annotations


def interpolate_position(
    start_row: float,
    start_col: float,
    end_row: float,
    end_col: float,
    start_time_ms: int,
    duration_ms: int,
    current_time_ms: int,
) -> tuple[float, float]:
    """
    מחשב את המיקום החזותי של כלי נע בין שתי משבצות.

    השרת שולח: start_row, start_col, end_row, end_col, start_time_ms, duration_ms
    הקליינט קורא לפונקציה הזו עם current_time_ms (שעון מקומי מסונכרן לשרת).

    מחזיר (row, col) כשברים עשרוניים — למשל (5.7, 3.0) אם הכלי עבר 70% מהדרך.
    """
    if duration_ms <= 0:
        return end_row, end_col

    elapsed = current_time_ms - start_time_ms

    # לפני תחילת התנועה — נשאר במקום ההתחלה
    if elapsed <= 0:
        return start_row, start_col

    # אחרי סיום התנועה — נעגן ביעד
    if elapsed >= duration_ms:
        return end_row, end_col

    # אינטרפולציה לינארית: t נע בין 0.0 ל-1.0
    t = elapsed / duration_ms
    row = start_row + t * (end_row - start_row)
    col = start_col + t * (end_col - start_col)

    return row, col


def interpolate_jump_fraction(
    start_time_ms: int,
    duration_ms: int,
    current_time_ms: int,
) -> float:
    """
    מחשב את שבר הקפיצה (0.0 עד 1.0) לצורך חישוב הפרבולה ב-Renderer.

    0.0 = תחילת הקפיצה
    0.5 = שיא הקפיצה (גובה מקסימלי)
    1.0 = סוף הקפיצה (נחיתה)
    """
    if duration_ms <= 0:
        return 1.0

    elapsed = current_time_ms - start_time_ms

    if elapsed <= 0:
        return 0.0
    if elapsed >= duration_ms:
        return 1.0

    return elapsed / duration_ms
