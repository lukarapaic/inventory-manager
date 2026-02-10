import sqlite3
from datetime import datetime
from functools import wraps
from enum import Enum

class MovementType(Enum):
    IN = 0
    OUT = 1
    TRANSFER = 2
    ADJUST = 3

class MovementInReason(Enum):
    RESTOCK = 0
    RETURN = 1

class MovementOutReason(Enum):
    SALE = 0
    DAMAGE = 1
    DISPOSAL = 2

class MovementTransferReason(Enum):
    INTERNAL = 0

class MovementAdjustReason(Enum):
    CORRECTION = 0

class MovementStatus(Enum):
    PENDING = 0
    COMPLETED = 1
    CANCELLED = 2
    IN_TRANSIT = 3


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
                    current_price INTEGER DEFAULT 0,
                    
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
                    physical_amount INTEGER DEFAULT 0,
                       
                    FOREIGN KEY (variant_id) REFERENCES variants(id),
                    FOREIGN KEY (location_id) REFERENCES locations(id)
                    )
                    ''')
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_movements (
                    variant_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    source_location_id INTEGER
                    change_amount INTEGER DEFAULT 0,
                    type VARCHAR(50),
                    status VARCHAR(50),
                    reason VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       
                    FOREIGN KEY (variant_id) REFERENCES variants(id),
                    FOREIGN KEY (location_id) REFERENCES locations(id),
                    FOREIGN KEY (source_location_id) REFERENCES locations(id)
                    )
                    ''')
        cursor.execute('''
                CREATE VIEW IF NOT EXISTS v_inventory_summary AS
                SELECT
                    v.id AS variant_id,
                    p.name AS product_name,
                    v.description AS description,
                    v.current_price as current_price,
                    l.id AS location_id,
                    l.location_name AS location_name,
                    h.physical_amount AS physical_amount,
                    
                    h.physical_amount - IFNULL((
                        SELECT SUM(m.change_amount)
                        FROM stock_movements m
                        WHERE m.variant_id = h.variant_id
                        AND m.location_id = h.location_id
                        AND m.type = 'OUT'
                        AND m.status = 'Pending'

                       ), 0) AS available_amount

                FROM variants v
                JOIN products p ON v.product_id = p.id
                JOIN has_variants h ON v.id = h.variant_id
                JOIN locations l ON h.location_id = l.id;

                    ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_variant_product_id ON variants(product_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON products(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_review_variant ON reviews(variant_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_has_products_logic ON has_variants(variant_id, location_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movement_logic ON stock_movements(variant_id, location_id, type, status);")
        
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
def addLocation(conn, location_name, is_storage, address=''):
    _addLocationLogic(conn, location_name, is_storage, address)

@wrap_transaction
def addProduct(conn, name, category):
    return _addProductLogic(conn, name, category)

@wrap_transaction
def findProductByName(conn, name):
    return _findProductByNameLogic(conn, name)
    
@wrap_transaction
def addPrice(conn, variant, price, date_time = None):
    _addPriceLogic(conn, variant, price, date_time = None)

@wrap_transaction
def addVariant(conn, product, description, current_price=None):
    return _addVariantLogic(conn, product, description, current_price=None)
    
@wrap_transaction    
def addReview(conn, variant, text_body, user_name, rating):
    _addReviewLogic(conn, variant, text_body, user_name, rating)

@wrap_transaction
def fetchReviews(conn, variant):
    return _fetchReviewsLogic(conn, variant)

@wrap_transaction
def getVariantRating(conn, variant):
    return _getVariantRatingLogic(conn, variant)

@wrap_transaction
def addMovementIn(conn, variant, location, amount, reason, status):
    return _addMovementInLogic(conn, variant, location, amount, reason, status)

@wrap_transaction
def addMovementOut(conn, variant, location, amount, reason, status):
    return _addMovementOutLogic(conn, variant, location, amount, reason, status)

@wrap_transaction
def addMovementTransfer(conn, variant, location, source_location, amount, reason, status):
    return _addMovementTransferLogic(conn, variant, location, source_location, amount, reason, status)

@wrap_transaction
def addMovementAdjust(conn, variant, location, amount, reason, status):
    return _addMovementAdjustLogic(conn, variant, location, amount, reason, status)

@wrap_transaction
def updatedMovementIn(conn, movement_id, status):
    return _updateMovementInLogic(conn, movement_id, status)

@wrap_transaction
def updatedMovementOut(conn, movement_id, status):
    return _updateMovementOutLogic(conn, movement_id, status)

@wrap_transaction
def updatedMovementTransfer(conn, movement_id, status):
    return _updateMovementTransferLogic(conn, movement_id, status)

@wrap_transaction
def updatedMovementAdjust(conn, movement_id, status):
    return _updateMovementAdjustLogic(conn, movement_id, status)

#-----------LOGIC FUNCTIONS------------#

#### Location--------------------------------------------------------------------
def _addLocationLogic(conn, location_name, is_storage, address=''):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO locations (location_name, is_storage, address) VALUES (?, ?, ?)", (location_name, is_storage, address))

#### Product---------------------------------------------------------------------
def _addProductLogic(conn, name, category):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, category) VALUES (?, ?) RETURNING id", (name, category))
    product_id = cursor.fetchone()[0]
    return product_id
def _findProductByNameLogic(conn, name):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
    return cursor.fetchone()[0]

#### Price history---------------------------------------------------------------
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

#### Variants--------------------------------------------------------------------
def _addVariantLogic(conn, product, description, current_price=None):
    cursor = conn.cursor()
    try:
        if isinstance(product, str):
            product = findProductByName(conn, product)
        cursor.execute("INSERT INTO variants (product_id, description) VALUES (?, ?) RETURNING id", (product, description))
        variant_id = cursor.fetchone()[0]
        if current_price:
            _addPriceLogic(conn, variant_id, current_price)
        return variant_id
    except sqlite3.Error as e:
        print("Error adding a product variant: ")
        raise e

#### Reviews---------------------------------------------------------------------
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

#### Functions for adding to and updating stock_movements table------------------
def _addMovementLogic(conn, variant, location, source_location, amount, type, reason, status = MovementStatus.PENDING):
    cursor = conn.cursor()

    cursor.execute("INSERT INTO stock_movements (variant_id, location_id, source_location_id, change_amount, type, reason, status) VALUES (?, ?, ?, ?, ?, ?) RETURNING id", (variant, location, source_location, amount, type, reason, status))
    return cursor.fetchone()[0]

def _updateMovementLogic(conn, movement_id, status):
    cursor = conn.cursor()
    
    cursor.execute("UPDATE stock_movement SET status = ? WHERE id = ?", (status, movement_id))

# Logic functions for IN type stock_movements------------------------------------
def _addMovementInLogic(conn, variant, location, amount, reason, status = MovementStatus.PENDING):
    _addMovementLogic(conn, variant, location, None, amount, MovementType.IN, reason, status)

    if status == MovementStatus.COMPLETED:
        _completedMovementLogic(conn, variant, location, amount, False)

def _updateMovementInLogic(conn, movement_id, status):
    _updateMovementLogic(conn,movement_id, status)
    #TODO Edge case when the status is already completed
    if status == MovementStatus.COMPLETED:
        results = _fetchMovementInfo(conn, movement_id)
        _completedMovementLogic(conn, results["variant"], results["location"], results["amount"], False)

# Logic functions for OUT type stock_movements-----------------------------------
def _addMovementOutLogic(conn, variant, location, amount, reason, status = MovementStatus.COMPLETED):
    _addMovementLogic(conn, variant, location, None, amount, MovementType.OUT, reason, status)

    if status == MovementStatus.COMPLETED:
        _completedMovementLogic(conn, variant, location, - amount, False)

def _updateMovementOutLogic(conn, movement_id, status):
    _updateMovementLogic(conn, movement_id, status)
    #TODO Edge case when the status is already completed
    if status == MovementStatus.COMPLETED:
        results = _fetchMovementInfo(conn, movement_id)
        _completedMovementLogic(conn, results["variant"], results["location"], results["amount"], False)

# Logic functions for TRANSFER type stock_movements------------------------------
def _addMovementTransferLogic(conn, variant, location, source_location, amount, reason, status = MovementStatus.IN_TRANSIT):
    _addMovementLogic(conn, variant, location, source_location, amount, MovementType.TRANSFER, reason, status)

    if status == MovementStatus.COMPLETED:
        _completedMovementLogic(conn, variant, location, amount, False)
        _completedMovementLogic(conn, variant, source_location, - amount, False)

def _updateMovementTransferLogic(conn, movement_id, status):
    _updateMovementLogic(conn, movement_id, status)
    #TODO Edge case when the status is already completed
    if status == MovementStatus.COMPLETED:
        results = _fetchMovementInfo(conn, movement_id)
        _completedMovementLogic(conn, results["variant"], results["location"], results["amount"], False)
        _completedMovementLogic(conn, results["variant"], results["source_location"], - results["amount"], False)

# Logic functions for ADJUST type stock_movements--------------------------------
def _addMovementAdjustLogic(conn, variant, location, amount, reason, status = MovementStatus.COMPLETED):
    _addMovementLogic(conn, variant, location, None, amount, MovementType.ADJUST, reason, status)

    if status == MovementStatus.COMPLETED:
        _completedMovementLogic(conn, variant, location, amount, True)

def _updateMovementAdjustLogic(conn, movement_id, status):
    _updateMovementLogic(conn, movement_id, status)
    #TODO Edge case when the status is already completed
    if status == MovementStatus.COMPLETED:
        results = _fetchMovementInfo(conn, movement_id)
        _completedMovementLogic(conn, results["variant"], results["location"], results["amount"], True)

#### Function for updating the has_variants whenever a movement is marked as completed.
def _completedMovementLogic(conn, variant, location, amount, replace = False):
    cursor = conn.cursor()

    if not replace:
        cursor.execute("SELECT h.physical_amount FROM has_products AS h WHERE variant_id = ? AND location_id = ?", (variant, location))
        amount += int(cursor.fetchone()[0])

    cursor.execute("UPDATE has_products SET physical_amount = ? WHERE variant_id = ? AND location_id = ?", (amount, variant, location))

#### Function for fetching the data from stock_movements for a given id----------
def _fetchMovementInfo(conn, movement_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stock_movements WHERE id = ?", (movement_id,))
    return {"id" : cursor.fetchone()[0], "variant" : cursor.fetchone()[1], "location" : cursor.fetchone()[2], "source_location" : cursor.fetchone()[3], "amount" : cursor.fetchone()[4], "type" : cursor.fetchone()[5], "reason" : cursor.fetchone()[6], "status" : cursor.fetchone()[7], "created_at" : cursor.fetchone()[8]}
