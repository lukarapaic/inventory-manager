import sqlite3
from datetime import datetime
from functools import wraps

def initDatabase():
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON products(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_variant ON reviews(variant_id);")
        conn.commit()
        return conn
    except sqlite3.Error as e:
        conn.rollback()
        raise e

# Wrapper function for committing or rolling back transactions -> Ensures easy use of nested transactional functions without any data integrity problems

def wrap_transaction(func):
    @wraps(func)
    def wrapper(conn,*args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
    return wrapper

# _functionameLogic() are the wrapperless functions containing internal logic -> To be used when nesting functions
# functionname() are the wrapped functions calling the logic functions -> To be used as public facing functions

#-----------WRAPPED FUNCTIONS------------#
@wrap_transaction
def addLocations(conn, location_name, is_storage, address=''):
    _addLocationsLogic(conn, location_name, is_storage, address)

@wrap_transaction
def addProduct(conn, name, category):
    _addProductLogic(conn, name, category)

@wrap_transaction
def findProductByName(conn, name):
    return _findProductByNameLogic(conn, name)
    
@wrap_transaction
def addPrice(conn, variant, price, date_time = None):
    _addPriceLogic(conn, variant, price, date_time = None)

@wrap_transaction
def addVariant(conn, product, description, current_price=None):
    _addVariantLogic(conn, product, description, current_price=None)
    
@wrap_transaction    
def addReview(conn, variant, text_body, user_name, rating):
    _addReviewLogic(conn, variant, text_body, user_name, rating)

@wrap_transaction
def fetchReviews(conn, variant):
    return _fetchReviewsLogic(conn, variant)

@wrap_transaction
def getVariantRating(conn, variant):
    return _getVariantRatingLogic(conn, variant)

#-----------LOGIC FUNCTIONS------------#
def _addLocationsLogic(conn, location_name, is_storage, address=''):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO locations (location_name, is_storage, address) VALUES (?, ?, ?)", (location_name, is_storage, address))

def _addProductLogic(conn, name, category):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category) VALUES (?, ?)", (name, category))

def _findProductByNameLogic(conn, name):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
    return cursor.fetchone()[0]

def _addPriceLogic(conn, variant, price, date_time = None):
    cursor = conn.cursor()
    try:
        if isinstance(variant, str):
            #TODO Maybe make search by variant name (+ product name?)
            pass
        if date_time and isinstance(date_time, datetime):
            date_time_formatted = date_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO price_history (variant_id, price, start_time) VALUES (?, ?, ?)", variant, price, date_time_formatted)
        else:
            cursor.execute("INSERT INTO price_history (variant_id, price) VALUES (?, ?)", (variant, price))
        
        cursor.execute("UPDATE variants SET current_price = ? WHERE id = ?", (price, variant))
    except sqlite3.Error as e:
        print("Error adding a price entry: ")
        raise e
     
def _addVariantLogic(conn, product, description, current_price=None):
    cursor = conn.cursor()
    try:
        if isinstance(product, str):
            product = findProductByName(conn, product)
        cursor.execute("INSERT INTO variants (product_id, description) VALUES (?, ?) RETURNING id", (product, description))
        variant_id = cursor.fetchone()[0]
        if current_price:
            _addPriceLogic(conn, variant_id, current_price)
    except sqlite3.Error as e:
        print("Error adding a product variant: ")
        raise e

def _addReviewLogic(conn, variant, text_body, user_name, rating):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO reviews (variant_id, body, user_name, rating) VALUES (?, ?, ?, ?)", (variant, text_body, user_name, rating))
    except sqlite3.Error as e:
        print("Error adding a review: ")
        raise e

def _fetchReviewsLogic(conn, variant):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reviews WHERE variant_id = ?", (variant,))
    return cursor.fetchall()

def _getVariantRatingLogic(conn, variant):
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(rating) FROM reviews WHERE variant_id = ?", (variant,))
    return cursor.fetchone()[0]
