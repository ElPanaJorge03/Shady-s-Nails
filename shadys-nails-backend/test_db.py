import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Force stdout/stderr to utf-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Try to force libpq to use UTF-8 for error messages
os.environ["PGCLIENTENCODING"] = "utf-8"

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/shadys_nails_db")
print(f"Connecting to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Connected!")
        result = conn.execute(text("SELECT 1"))
        print(f"Result: {result.scalar()}")
except Exception as e:
    print("Connection failed!")
    try:
        print(f"Error: {e}")
    except:
        print(repr(e))
