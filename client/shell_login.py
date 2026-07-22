def login() -> tuple[str, str]:
    """
    מבקש שם משתמש וסיסמה בטרמינל.
    מחזיר (username, password).
    """
    print("=== KungFu Chess ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    return username, password


def show_menu(username: str, rating: int) -> str:
    """
    מציג את הדירוג ותפריט בחירה.
    מחזיר "play" או "room".
    """
    print(f"\nWelcome, {username}! Rating: {rating}")
    print("\n1. Play (matchmaking)")
    print("2. Room")

    while True:
        choice = input("Choose (1/2): ").strip()
        if choice == "1":
            return "play"
        if choice == "2":
            return "room"
        print("Invalid choice. Please enter 1 or 2.")