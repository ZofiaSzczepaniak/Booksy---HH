import sqlite3
from datetime import datetime
from difflib import get_close_matches


class HardwareManager:
    """
    Manages hardware items in a SQLite database.
    Handles CRUD operations with input normalization.
    """

    def __init__(self, db_path="hardware.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS hardware (
            id INTEGER PRIMARY KEY,
            name TEXT,
            brand TEXT,
            purchase_date TEXT,
            status TEXT,
            notes TEXT,
            assigned_to TEXT
        )
        """)
        try:
            self.cursor.execute("ALTER TABLE hardware ADD COLUMN assigned_to TEXT")
        except Exception:
            pass
        self.conn.commit()

    # ─── Normalization helpers ───────────────────────────────


    def _normalize_date(self, raw_date):
        """Convert multiple date formats to ISO 8601 (YYYY-MM-DD)."""
        if not raw_date:
            return None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y", "%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        print(f"[WARN] Invalid date format: {raw_date} — stored as None")
        return None

    def _normalize_status(self, status):
        """Accept only known statuses; fall back to 'Unknown'."""
        valid = ["Available", "In Use", "Repair"]
        return status if status in valid else "Unknown"

    KNOWN_BRANDS = [
        "Apple", "Samsung", "Dell", "Lenovo", "Logitech",
        "Razer", "Sony", "HP", "Asus", "Acer", "Microsoft",
        "Google", "Huawei", "LG", "Toshiba",    "Intel", "AMD", "Nvidia", "Qualcomm", "IBM",
        "Cisco", "Oracle", "Siemens", "Panasonic", "Philips",
        "Xiaomi", "OnePlus", "Realme", "Oppo", "Vivo",
        "Motorola", "Nokia", "ZTE",
        "Gigabyte", "MSI", "ASRock",
        "Corsair", "Kingston", "Seagate", "Western Digital",
        "Crucial", "Sandisk",
        "Alienware", "HyperX", "SteelSeries",
        "Beats", "Bose", "JBL", "Sennheiser",
        "Epson", "Canon", "Brother",
        "Fitbit", "Garmin",
        "DJI", "GoPro",
        "Bang & Olufsen",
        "Roku", "Amazon",
    ]

    def _normalize_brand(self, brand):
        """Return 'Unknown' for empty/None brands. Fuzzy-match known brands (case-insensitive)."""
        if not brand or not brand.strip():
            return "Unknown"
        cleaned = brand.strip()
        lower_map = {b.lower(): b for b in self.KNOWN_BRANDS}
        matches = get_close_matches(cleaned.lower(), lower_map.keys(), n=1, cutoff=0.6)
        return lower_map[matches[0]] if matches else cleaned

    # ─── CREATE ─────────────────────────────────────────────

    def _get_first_free_id(self):
        """Find the lowest unused integer ID."""
        self.cursor.execute("SELECT id FROM hardware ORDER BY id")
        ids = [row[0] for row in self.cursor.fetchall()]
        expected = 1
        for current in ids:
            if current != expected:
                return expected
            expected += 1
        return expected

    def add(self, item: dict):
        """
        Insert a hardware item.
        - Skips exact duplicates.
        - Re-assigns a new ID if the given ID is already taken by a different item.
        """
        purchase_date = self._normalize_date(item.get("purchaseDate"))
        brand = self._normalize_brand(item.get("brand"))
        status = self._normalize_status(item.get("status"))
        new_data = (item.get("name"), brand, purchase_date, status, item.get("notes"))

        self.cursor.execute(
            "SELECT name, brand, purchase_date, status, notes FROM hardware WHERE id = ?",
            (item["id"],)
        )
        existing = self.cursor.fetchone()

        if existing:
            if existing == new_data:
                print(f"[SKIP] Full duplicate for ID {item['id']}")
                return
            new_id = self._get_first_free_id()
            print(f"[INFO] ID {item['id']} conflict → assigned new ID {new_id}")
        else:
            new_id = item["id"]

        self.cursor.execute(
            "INSERT INTO hardware (id, name, brand, purchase_date, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (new_id, *new_data)
        )
        self.conn.commit()

    # ─── DELETE ─────────────────────────────────────────────

    def delete(self, item_id: int):
        self.cursor.execute("SELECT 1 FROM hardware WHERE id = ?", (item_id,))
        if not self.cursor.fetchone():
            print(f"[WARN] No item with ID {item_id}")
            return
        self.cursor.execute("DELETE FROM hardware WHERE id = ?", (item_id,))
        self.conn.commit()
        print(f"[OK] Deleted item {item_id}")

    # ─── UPDATE ─────────────────────────────────────────────

    def update(self, item_id: int, updated_item: dict):
        self.cursor.execute("SELECT 1 FROM hardware WHERE id = ?", (item_id,))
        if not self.cursor.fetchone():
            print(f"[WARN] No item with ID {item_id}")
            return
        self.cursor.execute(
            """UPDATE hardware
               SET name = ?, brand = ?, purchase_date = ?, status = ?, notes = ?, assigned_to = ?
               WHERE id = ?""",
            (
                updated_item.get("name"),
                self._normalize_brand(updated_item.get("brand")),
                self._normalize_date(updated_item.get("purchaseDate")),
                self._normalize_status(updated_item.get("status")),
                updated_item.get("notes"),
                updated_item.get("assignedTo"),
                item_id,
            )
        )
        self.conn.commit()
        print(f"[OK] Updated item {item_id}")

    def get_by_assignee(self, username: str):
        self.cursor.execute("SELECT * FROM hardware WHERE assigned_to = ?", (username,))
        return self.cursor.fetchall()

    # ─── READ ────────────────────────────────────────────────

    def get(self, item_id: int):
        self.cursor.execute("SELECT * FROM hardware WHERE id = ?", (item_id,))
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute("SELECT * FROM hardware")
        return self.cursor.fetchall()

    # ─── Connection ──────────────────────────────────────────

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
