import ChessPiece
class Knight(ChessPiece):
    def is_valid_move(self, target_position):
        # פייתון מאפשרת לעשות unpacking קצר וחמוד למיקומים
        current_row, current_col = self.position
        target_row, target_col = target_position
        distance_row=abs(current_row-target_row)
        distance_col=abs(current_col-target_col)
        if distance_col==1 and distance_row==2 or distance_col==2 and distance_row==1:
            return True
        return False