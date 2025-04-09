import sqlite3
from config import DATABASE_NAME

def create_connection():
    """Створює підключення до бази даних SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Помилка підключення до БД: {e}")
    return conn

def execute_query(conn, query, params=None):
    """Виконує SQL-запит."""
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return cursor
    except sqlite3.Error as e:
        print(f"Помилка виконання запиту '{query}': {e}")
        conn.rollback()
        return None

def fetch_one(cursor):
    """Отримує один результат запиту."""
    try:
        return cursor.fetchone()
    except Exception as e:
        print(f"Помилка отримання одного результату: {e}")
        return None

def fetch_all(cursor):
    """Отримує всі результати запиту."""
    try:
        return cursor.fetchall()
    except Exception as e:
        print(f"Помилка отримання всіх результатів: {e}")
        return None

def close_connection(conn):
    """Закриває підключення до бази даних."""
    if conn:
        conn.close()

def initialize_database():
    """Ініціалізує таблиці бази даних, якщо вони не існують."""
    conn = create_connection()
    if conn is not None:
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE
            )
        """)
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                price REAL NOT NULL
            )
        """)
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending_payment',
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        close_connection(conn)

def add_product(name, description, price):
    """Додає новий продукт до бази даних."""
    conn = create_connection()
    if conn is not None:
        cursor = execute_query(conn, """
            INSERT INTO products (name, description, price) VALUES (?, ?, ?)
        """, (name, description, price))
        product_id = None
        if cursor:
            product_id = cursor.lastrowid
        close_connection(conn)
        return product_id
    return None

def get_product(product_id):
    """Отримує інформацію про продукт за його ID."""
    conn = create_connection()
    if conn is not None:
        cursor = execute_query(conn, "SELECT id, name, description, price FROM products WHERE id = ?", (product_id,))
        if cursor:
            result = fetch_one(cursor)
            close_connection(conn)
            if result:
                return {'id': result[0], 'name': result[1], 'description': result[2], 'price': result[3]}
        close_connection(conn)
    return None

def update_product(product_id, name=None, description=None, price=None):
    """Оновлює інформацію про продукт."""
    conn = create_connection()
    if conn is not None:
        query_parts = []
        params = []
        if name is not None:
            query_parts.append("name = ?")
            params.append(name)
        if description is not None:
            query_parts.append("description = ?")
            params.append(description)
        if price is not None:
            query_parts.append("price = ?")
            params.append(price)

        if not query_parts:
            close_connection(conn)
            return True  # Нічого не оновлювалося, але успіх

        query = f"UPDATE products SET {', '.join(query_parts)} WHERE id = ?"
        params.append(product_id)

        cursor = execute_query(conn, query, params)
        close_connection(conn)
        return cursor is not None

def delete_product(product_id):
    """Видаляє продукт з бази даних."""
    conn = create_connection()
    if conn is not None:
        cursor = execute_query(conn, "DELETE FROM products WHERE id = ?", (product_id,))
        close_connection(conn)
        return cursor is not None

def get_all_products():
    """Отримує інформацію про всі продукти."""
    conn = create_connection()
    if conn is not None:
        cursor = execute_query(conn, "SELECT id, name, description, price FROM products")
        if cursor:
            results = fetch_all(cursor)
            close_connection(conn)
            return [{'id': row[0], 'name': row[1], 'description': row[2], 'price': row[3]} for row in results]
        close_connection(conn)
    return None