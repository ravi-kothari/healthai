import sys
import os
from sqlalchemy import text
from src.api.database import engine, Base
from src.api.models.careprep import CarePrepAccessToken

def create_tables():
    print("Creating CarePrepAccessToken table...")
    CarePrepAccessToken.__table__.create(bind=engine, checkfirst=True)
    print("Table created successfully.")

if __name__ == "__main__":
    create_tables()
