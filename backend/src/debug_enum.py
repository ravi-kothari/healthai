import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, Column, String, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base
from enum import Enum

# Define Enum
class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"

Base = declarative_base()

class User(Base):
    __tablename__ = "users_debug"
    id = Column(String, primary_key=True)
    role = Column(SQLEnum(UserRole))

# Create engine
engine = create_engine("sqlite:///./debug.db")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

try:
    print(f"UserRole.DOCTOR: {UserRole.DOCTOR}")
    print(f"UserRole.DOCTOR.value: {UserRole.DOCTOR.value}")
    
    user = User(id="1", role=UserRole.DOCTOR)
    session.add(user)
    session.commit()
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
