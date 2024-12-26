from app import app, db
from migrations.rename_mother_to_parent import upgrade

if __name__ == '__main__':
    with app.app_context():
        upgrade()
