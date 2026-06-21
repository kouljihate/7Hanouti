import sqlite3
import hashlib
import os
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "app.db")


def _get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate_schema():
    conn = _get_connection()
    for col in ["supplier_name", "supplier_whatsapp", "supplier_email"]:
        try:
            conn.execute(f"ALTER TABLE products ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    try:
        conn.execute("ALTER TABLE products ADD COLUMN buying_price REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE products ADD COLUMN barcode TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    _migrate_schema()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity REAL DEFAULT 0,
            price REAL DEFAULT 0,
            category TEXT DEFAULT '',
            packaging TEXT DEFAULT '',
            description TEXT DEFAULT '',
            low_stock_qty REAL DEFAULT 5,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('in','out')),
            quantity REAL NOT NULL,
            date TEXT DEFAULT (datetime('now')),
            note TEXT DEFAULT '',
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income','expense')),
            amount REAL NOT NULL,
            category TEXT DEFAULT '',
            date TEXT DEFAULT (datetime('now')),
            description TEXT DEFAULT '',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


def user_count() -> int:
    conn = _get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
    conn.close()
    return row["cnt"]


def create_user(name: str, email: str, password: str) -> int:
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, hash_password(password)),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def authenticate_user(email: str, password: str):
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ? AND password_hash = ?",
        (email, hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user(user_id: int):
    conn = _get_connection()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(user_id: int, name: str, quantity: float, price: float, buying_price: float,
                category: str, packaging: str, description: str, low_stock_qty: float,
                supplier_name: str = "", supplier_whatsapp: str = "", supplier_email: str = "",
                barcode: str = "") -> int:
    conn = _get_connection()
    cursor = conn.execute(
        """INSERT INTO products (user_id, name, quantity, price, buying_price, category, packaging,
           description, low_stock_qty, supplier_name, supplier_whatsapp, supplier_email, barcode)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id, name, quantity, price, buying_price, category, packaging,
         description, low_stock_qty, supplier_name, supplier_whatsapp, supplier_email, barcode),
    )
    conn.commit()
    conn.close()
    return cursor.lastrowid


def update_product(product_id: int, name: str, quantity: float, price: float, buying_price: float,
                   category: str, packaging: str, description: str, low_stock_qty: float,
                   supplier_name: str = "", supplier_whatsapp: str = "", supplier_email: str = "",
                   barcode: str = ""):
    conn = _get_connection()
    conn.execute(
        """UPDATE products SET name=?, quantity=?, price=?, buying_price=?, category=?, packaging=?,
           description=?, low_stock_qty=?, supplier_name=?, supplier_whatsapp=?, supplier_email=?,
           barcode=?, updated_at=datetime('now') WHERE id=?""",
        (name, quantity, price, buying_price, category, packaging, description,
         low_stock_qty, supplier_name, supplier_whatsapp, supplier_email, barcode, product_id),
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = _get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def get_products(user_id: int):
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE user_id = ? ORDER BY name", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product(product_id: int):
    conn = _get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_product_by_barcode(barcode: str, user_id: int):
    conn = _get_connection()
    row = conn.execute(
        "SELECT * FROM products WHERE barcode = ? AND user_id = ?", (barcode, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def add_stock_movement(product_id: int, user_id: int, mtype: str, quantity: float, note: str):
    conn = _get_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    new_qty = product["quantity"] + quantity if mtype == "in" else product["quantity"] - quantity
    conn.execute("UPDATE products SET quantity=?, updated_at=datetime('now') WHERE id=?",
                 (new_qty, product_id))
    conn.execute(
        "INSERT INTO stock_movements (product_id, user_id, type, quantity, note) VALUES (?,?,?,?,?)",
        (product_id, user_id, mtype, quantity, note),
    )
    conn.commit()
    conn.close()


def get_stock_movements(user_id: int, limit: int = 50):
    conn = _get_connection()
    rows = conn.execute(
        """SELECT sm.*, p.name as product_name FROM stock_movements sm
           JOIN products p ON sm.product_id = p.id
           WHERE sm.user_id = ? ORDER BY sm.date DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_transaction(user_id: int, ttype: str, amount: float, category: str, description: str):
    conn = _get_connection()
    conn.execute(
        "INSERT INTO transactions (user_id, type, amount, category, description) VALUES (?,?,?,?,?)",
        (user_id, ttype, amount, category, description),
    )
    conn.commit()
    conn.close()


def get_transactions(user_id: int, limit: int = 50):
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_dashboard_data(user_id: int):
    conn = _get_connection()
    stock_value = conn.execute(
        "SELECT COALESCE(SUM(quantity * price), 0) as val FROM products WHERE user_id = ?",
        (user_id,),
    ).fetchone()["val"]
    buying_cost = conn.execute(
        "SELECT COALESCE(SUM(quantity * buying_price), 0) as val FROM products WHERE user_id = ?",
        (user_id,),
    ).fetchone()["val"]
    cash_income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as tot FROM transactions WHERE user_id = ? AND type='income'",
        (user_id,),
    ).fetchone()["tot"]
    cash_expense = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as tot FROM transactions WHERE user_id = ? AND type='expense'",
        (user_id,),
    ).fetchone()["tot"]
    cash_balance = cash_income - cash_expense
    low_stock = conn.execute(
        "SELECT COUNT(*) as cnt FROM products WHERE user_id = ? AND quantity <= low_stock_qty",
        (user_id,),
    ).fetchone()["cnt"]
    product_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM products WHERE user_id = ?", (user_id,)
    ).fetchone()["cnt"]
    conn.close()
    return {
        "stock_value": stock_value,
        "buying_cost": buying_cost,
        "potential_profit": stock_value - buying_cost,
        "cash_balance": cash_balance,
        "low_stock_count": low_stock,
        "product_count": product_count,
        "cash_income": cash_income,
        "cash_expense": cash_expense,
    }
