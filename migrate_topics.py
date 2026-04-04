"""
migrate_topics.py
-----------------
Adds the two new columns to the topics table:
    - pdf_path   (VARCHAR 300)
    - video_url  (VARCHAR 500)

Run this ONCE against your existing database:
    python migrate_topics.py

Safe to run multiple times — skips columns that already exist.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lms.db')

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())

def main():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Run seed.py first to create the database.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    added = []

    if not column_exists(cur, 'topics', 'pdf_path'):
        cur.execute("ALTER TABLE topics ADD COLUMN pdf_path VARCHAR(300)")
        added.append('topics.pdf_path')
    else:
        print("  SKIP  topics.pdf_path — already exists")

    if not column_exists(cur, 'topics', 'video_url'):
        cur.execute("ALTER TABLE topics ADD COLUMN video_url VARCHAR(500)")
        added.append('topics.video_url')
    else:
        print("  SKIP  topics.video_url — already exists")

    conn.commit()
    conn.close()

    for col in added:
        print(f"  OK    Added column: {col}")

    if added:
        print(f"\nMigration complete. {len(added)} column(s) added.")
    else:
        print("\nNothing to migrate — database is already up to date.")

if __name__ == '__main__':
    main()
