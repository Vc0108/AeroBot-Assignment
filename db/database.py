import sqlite3

# This file handles saving data to a local file called "aviation.db"

def init_db():
    """Creates the database tables if they don't exist."""
    conn = sqlite3.connect('aviation.db')
    c = conn.cursor()
    
    # Create Table 1: Customers (Satisfies requirement 2.3)
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    
    # Create Table 2: Bookings (Satisfies requirement 2.3)
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            service_type TEXT,
            date TEXT,
            time TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_booking(name, email, phone, service_type, date, time):
    """Saves a new booking and returns the Booking ID."""
    conn = sqlite3.connect('aviation.db')
    c = conn.cursor()
    
    # 1. Check if customer exists, if not, add them
    c.execute("SELECT id FROM customers WHERE email=?", (email,))
    data = c.fetchone()
    
    if data:
        customer_id = data[0]
    else:
        c.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)", 
                  (name, email, phone))
        customer_id = c.lastrowid
    
    # 2. Add the booking
    c.execute('''
        INSERT INTO bookings (customer_id, service_type, date, time, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_id, service_type, date, time, "CONFIRMED"))
    
    booking_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return booking_id

def get_all_bookings():
    """Fetches all bookings for the Admin Dashboard."""
    conn = sqlite3.connect('aviation.db')
    c = conn.cursor()
    # Join tables to get customer name with booking details
    c.execute('''
        SELECT b.id, c.name, c.email, b.service_type, b.date, b.time 
        FROM bookings b
        JOIN customers c ON b.customer_id = c.id
    ''')
    data = c.fetchall()
    conn.close()
    return data