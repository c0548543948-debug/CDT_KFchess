├── model/                  # שכבת הנתונים (State)
│   ├── piece.py            # כלי משחק (כולל ניהול Cooldown ו-Clone)
│   ├── board.py            # רשת הלוח 8x8 וניהול עותק עמוק
│   ├── motion.py           # אובייקט המייצג כלי בתנועה פיזית באוויר
│   └── game_state.py       # מצב המשחק (Snapshot קפוא עבור ה-UI)
│
├── rules/                  # חוקי השחמט הסטטיים
│   └── rule_engine.py      # תיקוף מהלכים קלאסיים (Source -> Target)
│
├── real_time/              # ניהול זמן אמת ופיזיקה
│   └── real_time_arbiter.py# בורר התנגשויות באוויר, תנועה וצינון
│
├── tests/                  # מערך בדיקות יחידה מקיף (Unittest)
└── config.py               # הגדרות מערכת (זמני Cooldown לפי סוג כלי)