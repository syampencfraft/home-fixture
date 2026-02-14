import os
import django
import sqlite3

def check_db(db_path):
    print(f"\nChecking database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables if 'fixture' in t[0]]}")
        
        cursor.execute("SELECT COUNT(*) FROM fixture_category")
        print(f"Categories count: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM fixture_service")
        print(f"Services count: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT * FROM fixture_service")
        svcs = cursor.fetchall()
        for s in svcs:
            print(f" - Service: {s}")
            
    except Exception as e:
        print(f"Error checking {db_path}: {e}")
    finally:
        conn.close()

check_db("db.sqlite3")
check_db("home/db.sqlite3")
