import ChessPiece
class King(ChessPiece):
    def is_valid_move(self, target_position):
        # פייתון מאפשרת לעשות unpacking קצר וחמוד למיקומים
        current_row, current_col = self.position
        target_row, target_col = target_position
        distance_row = abs(current_row - target_row)
        distance_col = abs(current_col - target_col)
        if distance_row>1 or distance_col>1:
            return False
        return True
