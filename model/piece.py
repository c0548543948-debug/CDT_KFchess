from model.position import Position

class Piece:
    def __init__(self, piece_id: str, color: str, kind: str, cell: Position, state: str = "idle"):
        # שדות (Attributes)
        self._id = piece_id
        self._color = color      # "white" / "black"
        self._kind = kind        # "king" / "queen" / "rook" / "bishop" / "knight" / "pawn"
        self.cell = cell         # אובייקט מסוג Position (משתנה במהלך המשחק)
        self.state = state       # "idle" / "moving" / "captured" (משתנה במהלך המשחק)

    # --- מאפיינים לקריאה בלבד (שדות יציבים שלא משתנים אחרי היצירה) ---
    @property
    def id(self) -> str:
        return self._id

    @property
    def color(self) -> str:
        return self._color

    @property
    def kind(self) -> str:
        return self._kind

    # --- EQUATION (מנגנון השוואה לפי מזהה ייחודי) ---
    def __eq__(self, other) -> bool:
        """שני כלים נחשבים לזהים אך ורק אם יש להם את אותו ID ייחודי"""
        if not isinstance(other, Piece):
            return False
        return self._id == other._id

    # --- READABLE PRESENTATION (ייצוג קריא עבור טסטים) ---
    def __repr__(self) -> str:
        return f"Piece(id={self._id!r}, color={self._color!r}, kind={self._kind!r}, cell={self.cell}, state={self.state!r})"

    def __str__(self) -> str:
        """הצגה פשוטה כטקסט"""
        return f"{self._color} {self._kind} [{self._id}] at {self.cell} ({self.state})"