import sqlite3 as sql
import config
from datetime import datetime

# function to establish connection to the database, enable foreign key constraint support, and create cursor
def connection():
    conn = sql.connect(config.database_name + '.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    c = conn.cursor()
    return conn, c

# function to establish connection to the database and create tables (if they don't exist yet)
def db_init():
    conn = sql.connect('database_1A.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS donor_record
                 (donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  blood_type TEXT NOT NULL,
                  ... other fields ...)''')
    
    conn.commit()
    conn.close()

# Database connection
def get_db_connection():
    conn = sql.connect('database_1A.db')
    conn.row_factory = sql.Row
    return conn

def execute_query(query, params=(), fetch=False):
    """
    Execute an SQL query and optionally fetch results
    
    Args:
        query (str): SQL query to execute
        params (tuple): Parameters for the query
        fetch (bool): Whether to fetch and return results
    
    Returns:
        list: Query results if fetch=True, None otherwise
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        
        if fetch:
            results = cur.fetchall()
        else:
            results = None
            
        conn.commit()
        return results
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def db_init():
    """Initialize the database with required tables"""
    
    # Create donors table
    execute_query("""
        CREATE TABLE IF NOT EXISTS donors (
            donor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            last_donation_date DATE
        )
    """)
    
    # Create blood_units table
    execute_query("""
        CREATE TABLE IF NOT EXISTS blood_units (
            unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id TEXT,
            blood_type TEXT NOT NULL,
            collection_date DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (donor_id) REFERENCES donors(donor_id)
        )
    """)
    
    # Create blood_banks table
    execute_query("""
        CREATE TABLE IF NOT EXISTS blood_banks (
            bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank_name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            contact_number TEXT,
            email TEXT,
            license_number TEXT UNIQUE
        )
    """)
    
    # Create blood_requests table
    execute_query("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            units_required INTEGER NOT NULL,
            urgency TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            request_date DATE NOT NULL,
            required_by DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

# Initialize database when module is imported
db_init()

# Add these helper functions if needed

def get_donor_by_id(donor_id):
    """Fetch donor details by ID"""
    return execute_query(
        "SELECT * FROM donors WHERE donor_id = ?", 
        (donor_id,), 
        fetch=True
    )

def get_blood_unit_by_id(unit_id):
    """Fetch blood unit details by ID"""
    return execute_query(
        "SELECT * FROM blood_units WHERE unit_id = ?", 
        (unit_id,), 
        fetch=True
    )

def get_available_blood_units(blood_type=None):
    """Fetch available blood units, optionally filtered by blood type"""
    if blood_type:
        return execute_query(
            "SELECT * FROM blood_units WHERE status = 'Available' AND blood_type = ?",
            (blood_type,),
            fetch=True
        )
    return execute_query(
        "SELECT * FROM blood_units WHERE status = 'Available'",
        fetch=True
    )
