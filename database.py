import sqlite3
import bcrypt
from datetime import datetime
import json

DB_PATH = 'piggypoint.db'

def get_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _get_user_id(username):
    """Utility helper to fetch the numeric user id for a username."""
    try:
        with get_connection() as conn:
            row = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        return row['id'] if row else None
    except Exception as e:
        print(f"Error fetching user id: {e}")
        return None

# Initialize database tables
def init_db():
    """Create tables if they don't exist"""
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                targets_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

init_db()

def hash_password(password):
    """Hash password for security using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def create_user(username, password):
    """Create a new user in SQLite"""
    try:
        with get_connection() as conn:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                        (username, hash_password(password)))
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def verify_user(username, password):
    """Check if username and password are correct"""
    try:
        with get_connection() as conn:
            result = conn.execute('SELECT password FROM users WHERE username = ?', (username,)).fetchone()
        return result and bcrypt.checkpw(password.encode(), result['password'])
    except Exception as e:
        print(f"Error verifying user: {e}")
        return False

def user_exists(username):
    """Check if username already exists"""
    try:
        with get_connection() as conn:
            result = conn.execute('SELECT EXISTS(SELECT 1 FROM users WHERE username = ?)', (username,)).fetchone()
        return bool(result[0])
    except Exception as e:
        print(f"Error checking user: {e}")
        return False
    
def save_user_targets(username, targets):
    try:
        with get_connection() as conn:
            conn.execute('UPDATE users SET targets_json = ? WHERE username = ?', (json.dumps(targets), username))

        return True
    except:
        return False

def get_user_targets(username):
    try:
        print(username)
        with get_connection() as conn:
            row = conn.execute('SELECT targets_json FROM users WHERE username = ?', (username,)).fetchone()

            return json.loads(dict(row)["targets_json"])

        return True
    except Exception as e:
        print(f"Error getting targets: {e}")
        return {}

def save_user_transactions(username, data):
    """Save user's financial transaction data"""
    try:
        user_id = _get_user_id(username)
        if user_id is None:
            return False
        with get_connection() as conn:
            conn.execute('''
                INSERT INTO transactions (user_id, transaction_type, category, amount, date)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, data['transaction_type'], data['category'], data['amount'],
                  data.get('date', datetime.now())))
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def get_user_transactions(username):
    """Get user's financial transaction data"""
    try:
        with get_connection() as conn:
            rows = conn.execute('''
                SELECT t.id, t.transaction_type, t.category, t.amount, t.date, t.created_at
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE u.username = ?
                ORDER BY t.date DESC
            ''', (username,)).fetchall()

        return {'transactions': [dict(row) for row in rows]}
    except Exception as e:
        print(f"Error getting data: {e}")
        return {}

def reset_transactions(username, transaction_type=None):
    """
    Delete transactions for a given user.
    If transaction_type is provided, limit the reset to that type.
    """
    user_id = _get_user_id(username)
    if user_id is None:
        return False

    query = 'DELETE FROM transactions WHERE user_id = ?'
    params = [user_id]

    if transaction_type:
        query += ' AND transaction_type = ?'
        params.append(transaction_type)

    try:
        with get_connection() as conn:
            conn.execute(query, params)
        return True
    except Exception as e:
        print(f"Error resetting transactions: {e}")
        return False

def reset_total_income(username):
    """Remove all income transactions for the user."""
    return reset_transactions(username, 'Income')

def reset_total_expenses(username):
    """Remove all expense transactions for the user."""
    return reset_transactions(username, 'Expense')

def reset_all_transactions(username):
    """Remove every transaction for the user."""
    return reset_transactions(username)

def delete_transaction_by_id(transaction_id):
    """Delete a specific transaction by its ID"""
    try:
        with get_connection() as conn:
            conn.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        return True
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        return False