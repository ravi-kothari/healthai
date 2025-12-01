import os
from src.api.config import Settings

# Set env var
os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"

# Instantiate Settings with override
settings = Settings(DATABASE_URL="sqlite:///:memory:")

print(f"DATABASE_URL from env: {os.environ['DATABASE_URL']}")
print(f"DATABASE_URL from settings: {settings.DATABASE_URL}")

if settings.DATABASE_URL == "sqlite:///:memory:":
    print("SUCCESS: Constructor override works")
else:
    print("FAILURE: Env var takes precedence")
