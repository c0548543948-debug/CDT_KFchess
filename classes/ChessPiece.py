from abc import ABC, abstractmethod


# שם קלאס ב-PascalCase
class ChessPiece(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position  # משתנה (פרופרטי) ב-snake_case

    def can_move(self, target_position):
        # אם מיקום היעד זהה למיקום הנוכחי - המהלך מיידית לא חוקי
        if self.position == target_position:
            return False

        # אם הוא באמת זז למשבצת אחרת, נבדוק את החוקים הספציפיים של הכלי
        return self.is_valid_move(target_position)
    @abstractmethod
    def is_valid_move(self, target_position):  # שם מתודה ב-snake_case
        pass


