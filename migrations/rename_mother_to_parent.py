from flask import current_app
from flask_migrate import Migrate
from sqlalchemy import text
from app import db

def upgrade():
    # Rename the column in SQLite
    with current_app.app_context():
        # Create new table with desired schema
        db.session.execute(text('''
            CREATE TABLE children_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_phone VARCHAR(16) REFERENCES registration(phone_number),
                first_name TEXT NOT NULL,
                father_name TEXT NOT NULL,
                grandfather_name TEXT NOT NULL,
                family_name TEXT NOT NULL,
                gender VARCHAR(15) NOT NULL,
                age INTEGER NOT NULL,
                emergency_phone VARCHAR(16) NOT NULL,
                registration_number VARCHAR(4)
            )
        '''))
        
        # Copy data from old table to new table
        db.session.execute(text('''
            INSERT INTO children_new 
            SELECT id, mother_phone, first_name, father_name, grandfather_name, 
                   family_name, gender, age, emergency_phone, registration_number 
            FROM children
        '''))
        
        # Drop old table
        db.session.execute(text('DROP TABLE children'))
        
        # Rename new table to original name
        db.session.execute(text('ALTER TABLE children_new RENAME TO children'))
        
        db.session.commit()

def downgrade():
    # Revert the changes if needed
    with current_app.app_context():
        # Create new table with old schema
        db.session.execute(text('''
            CREATE TABLE children_old (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mother_phone VARCHAR(16) REFERENCES registration(phone_number),
                first_name TEXT NOT NULL,
                father_name TEXT NOT NULL,
                grandfather_name TEXT NOT NULL,
                family_name TEXT NOT NULL,
                gender VARCHAR(15) NOT NULL,
                age INTEGER NOT NULL,
                emergency_phone VARCHAR(16) NOT NULL,
                registration_number VARCHAR(4)
            )
        '''))
        
        # Copy data back
        db.session.execute(text('''
            INSERT INTO children_old 
            SELECT id, parent_phone, first_name, father_name, grandfather_name, 
                   family_name, gender, age, emergency_phone, registration_number 
            FROM children
        '''))
        
        # Drop new table
        db.session.execute(text('DROP TABLE children'))
        
        # Rename old table to original name
        db.session.execute(text('ALTER TABLE children_old RENAME TO children'))
        
        db.session.commit()
