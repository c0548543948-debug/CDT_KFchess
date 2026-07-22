from engine.model.position import Position


class Piece:
    def __init__(self, piece_id: str, color: str, kind: str, cell: Position, state: str = "idle"):
        # שדות (Attributes)
        self._id = piece_id
        self._color = color  # "white" / "black"
        self._kind = kind  # "king" / "queen" / "rook" / "bishop" / "knight" / "pawn"
        self.cell = cell  # אובייקט מסוג Position (משתנה במהלך המשחק)
        self.state = state  # "idle" / "moving" / "captured" (משתנה במהלך המשחק)
        self.cooldown_remaining = 0  # ⏳ זמן הצינון שנותר במילישניות

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

    # --- מנגנון שכפול עמוק (Cloning) ---
    def clone(self) -> 'Piece':
        """
        מייצר עותק חדש ועצמאי לחלוטין של הכלי הנוכחי.
        מעתיק במדויק את המיקום, המצב וזמן הצינון שנותר.
        """
        # יוצרים מיקום חדש כדי למנוע הצבעה לאותו אובייקט בזיכרון (Deep Copy של ה-Position)
        cloned_cell = Position(row=self.cell.row, col=self.cell.col)

        cloned_piece = Piece(
            piece_id=self._id,
            color=self._color,
            kind=self._kind,
            cell=cloned_cell,
            state=self.state
        )
        # מעתיקים ידנית את זמן הצינון שנותר
        cloned_piece.cooldown_remaining = self.cooldown_remaining
        return cloned_piece

    # --- EQUATION (מנגנון השוואה לפי מזהה ייחודי) ---
    def __eq__(self, other) -> bool:
        """שני כלים נחשבים לזהים אך ורק אם יש להם את אותו ID ייחודי"""
        if not isinstance(other, Piece):
            return False
        return self._id == other._id

    # --- READABLE PRESENTATION (ייצוג קריא עבור טסטים) ---
    def __repr__(self) -> str:
        return f"Piece(id={self._id!r}, color={self._color!r}, kind={self._kind!r}, cell={self.cell}, state={self.state!r}, cooldown={self.cooldown_remaining})"

    def __str__(self) -> str:
        """הצגה פשוטה כטקסט"""
        return f"{self._color} {self._kind} [{self._id}] at {self.cell} ({self.state}) - Cooldown: {self.cooldown_remaining}ms"