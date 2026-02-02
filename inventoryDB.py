import sqlite3

def init_database():
    conn = sqlite3.connect('inventory.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN;")
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255),
                    category VARCHAR(50))
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS variants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    description TEXT,
                    current_price INTEGER,
                    
                    FOREIGN KEY (product_id) REFERENCES products (id) )
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    variant_id INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                    FOREIGN KEY (variant_id) REFERENCES variants (id))
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    variant_id INTEGER NOT NULL,
                    body TEXT,
                    user_name VARCHAR(50),
                    rating INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       
                    FOREIGN KEY (variant_id) REFERENCES variants (id))
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_name VARCHAR(50) NOT NULL,
                    is_storage BOOLEAN NOT NULL,
                    address VARCHAR(255)
                    )
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS has_variants (
                    variant_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    physical_amount INTEGER,
                    available_amount INTEGER,
                       
                    FOREIGN KEY (variant_id) REFERENCES variants(id),
                    FOREIGN KEY (location_id) REFERENCES locations(id)
                    )
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_movements (
                    variant_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    change_amount INTEGER,
                    type VARCHAR(50),
                    status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       
                    FOREIGN KEY (variant_id) REFERENCES variants(id),
                    FOREIGN KEY (location_id) REFERENCES locations(id)
                    )
                    ''')
        conn.commit()
        return conn
    except sqlite3.Error as e:
        conn.rollback()
        raise e

def add_locations(conn, location_name, is_storage, address=''):
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO locations (location_name, is_storage, address) VALUES (?, ?, ?)", (location_name, is_storage, address))
    