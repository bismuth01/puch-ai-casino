import sqlite3
import time
import json

DAILY_AMOUNT = 1000

conn = sqlite3.connect("db/game_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS balance (
               user_id TEXT PRIMARY_KEY,
               amount INTEGER
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS username (
               user_id TEXT PRIMARY_KEY,
               user_name TEXT UNIQUE
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_cooldown (
               user_id TEXT PRIMARY KEY,
               last_time INTEGER
               )
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS hourly_cooldown (
               user_id TEXT PRIMARY KEY,
               last_time INTEGER
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS blackjack (
               user_id TEXT PRIMARY KEY,
               player_hand TEXT,
               dealer_hand TEXT,
               status TEXT
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rob_cooldown (
               user_id TEXT PRIMARY KEY,
               in_lobby BOOLEAN,
               last_time INTEGER
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rob_lobby (
               lobby_id INTEGER PRIMARY KEY,
               team TEXT
               )
""")

def add_balance(user_id: str, amount: int):
    cursor.execute("SELECT amount FROM balance WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
        UPDATE balance
        SET amount = amount + ?
        WHERE user_id = ?
        """, (amount, user_id))
    else:
        cursor.execute("""
        INSERT INTO balance (user_id, amount)
        VALUES (?, ?)
        """, (user_id, amount))
    conn.commit()

def deduct_balance(user_id: str, amount: int):
    cursor.execute("""
    UPDATE balance
    SET amount = amount - ?
    WHERE user_id = ?
    """, (amount, user_id))
    conn.commit()

def get_daily_claim_time(user_id: str):
    cursor.execute("""
    SELECT last_time
    FROM daily_cooldown
    WHERE user_id = ?
    """,
    (user_id,))

    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("""
        INSERT INTO daily_cooldown (user_id, last_time)
        VALUES (?, ?)
        """,
        (user_id, 0,))
        conn.commit()
        return 0
    
def set_daily_claim_time(user_id: str, new_time: int):
    cursor.execute("""
    UPDATE daily_cooldown
    SET last_time = ?
    WHERE user_id = ?
    """,
    (new_time, user_id,))
    conn.commit()

def get_hourly_claim_time(user_id: str):
    cursor.execute("""
    SELECT last_time
    FROM hourly_cooldown
    WHERE user_id = ?
    """,
    (user_id,))

    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("""
        INSERT INTO hourly_cooldown (user_id, last_time)
        VALUES (?, ?)
        """,
        (user_id, 0,))
        conn.commit()
        return 0
    
def set_hourly_claim_time(user_id: str, new_time: int):
    cursor.execute("""
    UPDATE hourly_cooldown
    SET last_time = ?
    WHERE user_id = ?
    """,
    (new_time, user_id,))
    conn.commit()
    
def get_balance(user_id: str):
    cursor.execute("""
    SELECT amount
    FROM balance
    WHERE user_id = ?
    """,
    (user_id,))

    row = cursor.fetchone()
    if row:
        return int(row[0])
    else:
        cursor.execute("""
        INSERT INTO balance (user_id, amount)
        VALUES (?, ?)
        """,
        (user_id, 0,))
        conn.commit()
        return 0
    
def save_blackjack_state(user_id, player_hand, dealer_hand, status):
    cursor.execute("""
    INSERT OR REPLACE INTO blackjack (user_id, player_hand, dealer_hand, status)
    VALUES (?, ?, ?, ?)
    """, (user_id, json.dumps(player_hand), json.dumps(dealer_hand), status))
    conn.commit()

def get_blackjack_state(user_id):
    cursor.execute("""
    SELECT player_hand, dealer_hand, status
    FROM blackjack
    WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    if row:
        return {
            "player_hand": json.loads(row[0]),
            "dealer_hand": json.loads(row[1]),
            "status": row[2]
        }
    return None

def delete_blackjack_state(user_id):
    cursor.execute("DELETE FROM blackjack WHERE user_id = ?", (user_id,))
    conn.commit()

def get_top_balances(limit=10):
    cursor.execute("""
    SELECT username.user_name, balance.amount
    FROM balance
    JOIN username ON balance.user_id = username.user_id
    ORDER BY balance.amount DESC
    LIMIT ?
    """, (limit,))
    return cursor.fetchall()

def get_username(user_id: str):
    cursor.execute("""
    SELECT user_name
    FROM username
    WHERE user_id = ?
    """,
    (user_id,))
    user_name = cursor.fetchone()
    if user_name:
        return user_name[0]
    else:
        return None

def set_username(user_id: str, user_name: str):
    cursor.execute("""
    SELECT user_id
    FROM username
    WHERE user_name = ?
    """,
    (user_name,))
    existing = cursor.fetchone()
    if existing:
        return False
    
    cursor.execute("""
    INSERT INTO username (user_id, user_name)
    VALUES (?, ?)
    """, (user_id, user_name))
    
    conn.commit()
    return True
