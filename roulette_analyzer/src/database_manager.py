import sqlite3
import datetime

DATABASE_NAME = 'roulette_data.db' # This will be created in the root roulette_analyzer directory

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number_spun INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_spin_result(number: int): # Not directly used by app.py currently, but good utility
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO spins (number_spun, timestamp) VALUES (?, ?)",
                       (number, datetime.datetime.now()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error adding single spin: {e}")
    finally:
        conn.close()

def add_multiple_spin_results(numbers: list[int]):
    if not numbers:
        return # Don't bother connecting if list is empty

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    spins_to_insert = []
    for number in numbers:
        spins_to_insert.append((number, datetime.datetime.now()))

    try:
        cursor.executemany("INSERT INTO spins (number_spun, timestamp) VALUES (?, ?)",
                           spins_to_insert)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error on multiple insert: {e}")
    finally:
        conn.close()

def get_total_spins_count() -> int:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM spins")
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Database error getting count: {e}")
        return 0
    finally:
        conn.close()

def get_all_spins_for_training() -> list[tuple[int, str]]:
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        # Order by timestamp ASC to get data in chronological order
        cursor.execute("SELECT number_spun, timestamp FROM spins ORDER BY timestamp ASC")
        spins = cursor.fetchall()
        return spins
    except sqlite3.Error as e:
        print(f"Database error getting all spins: {e}")
        return []
    finally:
        conn.close()

def clear_all_spins_from_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM spins")
        conn.commit()
        print("All spins cleared from the database.") # For server log
        return True
    except sqlite3.Error as e:
        print(f"Database error clearing spins: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    # Basic test and initialization when run directly
    print("Initializing database...")
    init_db()
    print(f"Database initialized. Total spins: {get_total_spins_count()}")

    print("\nAdding some sample spins...")
    add_multiple_spin_results([10, 20, 0, 5, 10])
    print(f"Total spins after adding: {get_total_spins_count()}")

    print("\nRetrieving all spins:")
    all_spins = get_all_spins_for_training()
    for spin in all_spins:
        print(spin)

    # print("\nClearing all spins...")
    # clear_all_spins_from_db()
    # print(f"Total spins after clearing: {get_total_spins_count()}")
