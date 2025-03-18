from sqlalchemy import create_engine

DB_URL = "mysql+pymysql://root:P%40ssword%401999@localhost/lead_delete_db"

try:
    engine = create_engine(DB_URL)
    conn = engine.connect()
    print("✅ Connected to MySQL successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
