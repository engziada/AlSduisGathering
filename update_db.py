from app import db, Children
import sqlite3

def update_children_table():
    try:
        # Add emergency_phone column if it doesn't exist
        with sqlite3.connect('app.db') as conn:
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(children)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'emergency_phone' not in columns:
                print("Adding emergency_phone column...")
                cursor.execute("ALTER TABLE children ADD COLUMN emergency_phone VARCHAR(16)")
                conn.commit()
                print("Successfully added emergency_phone column")
            else:
                print("emergency_phone column already exists")

    except Exception as e:
        print(f"Error updating database: {str(e)}")
        raise e

if __name__ == "__main__":
    update_children_table()
