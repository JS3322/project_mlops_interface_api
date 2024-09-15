from fastapi import Depends

def get_db():
    db = "database connection"
    try:
        yield db
    finally:
        db.close()