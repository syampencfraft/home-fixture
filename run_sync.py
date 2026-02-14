import os
import django
import sqlite3

# Active root DB path
ROOT_DB = "db.sqlite3"
# Source nested DB path
SOURCE_DB = "home/db.sqlite3"

def sync():
    print(f"Syncing from {SOURCE_DB} to {ROOT_DB}...")
    
    # Connect to source
    conn_src = sqlite3.connect(SOURCE_DB)
    cursor_src = conn_src.cursor()
    
    # Connect to root
    conn_root = sqlite3.connect(ROOT_DB)
    cursor_root = conn_root.cursor()
    
    try:
        # 1. Sync Categories
        cursor_src.execute("SELECT id, name, icon, description FROM fixture_category")
        categories = cursor_src.fetchall()
        
        for cat in categories:
            cat_id, name, icon, desc = cat
            print(f"Processing Category: {name} (ID: {cat_id})")
            
            # Use REPLACE to update or insert
            cursor_root.execute("""
                INSERT OR REPLACE INTO fixture_category (id, name, icon, description)
                VALUES (?, ?, ?, ?)
            """, (cat_id, name, icon, desc))
            
        # 2. Sync Services
        cursor_src.execute("SELECT id, name, base_price, duration, category_id, description, is_active FROM fixture_service")
        services = cursor_src.fetchall()
        
        for svc in services:
            svc_id, name, price, duration, cat_id, desc, active = svc
            print(f"Processing Service: {name} (ID: {svc_id}, Category ID: {cat_id})")
            
            cursor_root.execute("""
                INSERT OR REPLACE INTO fixture_service (id, name, base_price, duration, category_id, description, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (svc_id, name, price, duration, cat_id, desc, active))
            
        conn_root.commit()
        print("\nSync completed successfully!")
        
    except Exception as e:
        print(f"Error during sync: {e}")
        conn_root.rollback()
    finally:
        conn_src.close()
        conn_root.close()

if __name__ == "__main__":
    sync()
