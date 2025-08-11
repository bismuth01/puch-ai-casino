import sqlite3
import time

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
CREATE TABLE IF NOT EXISTS daily_cooldown (
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


def daily_claim(user_id: str):
    cursor.execute("""
    SELECT last_time
    FROM daily_cooldown
    WHERE user_id = ?
    """,
    (user_id,))

    row = cursor.fetchone()
    if row:
        now = int(time.time())
        day_later = now + 24 * 60 * 60
        if row[0] <= now + day_later:
            cursor.execute("""
            UPDATE daily_cooldown
            SET last_time = ?
            WHERE user_id = ?
            """,
            (day_later, user_id,))

            add_balance(user_id, DAILY_AMOUNT)
            conn.commit()
            return True
        
        else:
            return False
        
    else:
        new_time = int(time.time())
        cursor.execute("""
        INSERT INTO daily_cooldown (user_id, last_time)
        VALUES (?, ?)
        """,
        (user_id, new_time,))

        add_balance(user_id, DAILY_AMOUNT)
        conn.commit()
        return True
    
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