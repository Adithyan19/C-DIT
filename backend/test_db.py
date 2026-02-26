import sys
from app.config import settings
import psycopg2
from urllib.parse import urlparse, urlunparse

def try_connect_psycopg2(url, name):
    print(f"\nTrying psycopg2 {name}: {url}")
    try:
        conn = psycopg2.connect(url, connect_timeout=5)
        print("✅ SUCCESS!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    base_url = settings.DATABASE_URL
    if base_url.startswith("postgresql+asyncpg://"):
        base_url = base_url.replace("postgresql+asyncpg://", "postgresql://")
        
    print(f"Original: {base_url}")
    
    success = False
    
    # Test 1: Port 6543 (Transaction)
    url1 = base_url.replace(":5432", ":6543")
    success = success or try_connect_psycopg2(url1, "Direct 6543 psycopg2")
    
    # Test 2: Port 5432 (Session)
    url2 = base_url
    success = success or try_connect_psycopg2(url2, "Direct 5432 psycopg2")
    

if __name__ == "__main__":
    main()
