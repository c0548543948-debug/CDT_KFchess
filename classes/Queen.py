import ChessPiece
class Queen(ChessPiece):
    def is_valid_move(self, target_position):
        # פייתון מאפשרת לעשות unpacking קצר וחמוד למיקומים
        current_row, current_col = self.position
        target_row, target_col = target_position
        distance_row = abs(current_row - target_row)
        distance_col = abs(current_col - target_col)
        if distance_row!=0 and distance_col!=0 and distance_row != distance_col:
            return False
        return True