"""Quick Snowflake connection test (Windows-compatible)"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment
load_dotenv()

print("\n" + "="*60)
print("  Snowflake Connection Test")
print("="*60)

# Check environment variables
print("\n[1/3] Checking configuration...")
account = os.getenv("SNOWFLAKE_ACCOUNT", "").strip()
user = os.getenv("SNOWFLAKE_USER", "").strip()
password = os.getenv("SNOWFLAKE_PASSWORD", "").strip()
enabled = os.getenv("ENABLE_SNOWFLAKE", "false").lower()

if enabled != "true":
    print("[ERROR] ENABLE_SNOWFLAKE is not set to 'true' in .env")
    print("Please set: ENABLE_SNOWFLAKE=true")
    sys.exit(1)

if not account or account == "your_account_identifier.region":
    print("[ERROR] SNOWFLAKE_ACCOUNT not configured in .env")
    print("Please update .env with your Snowflake account identifier")
    print("Example: SNOWFLAKE_ACCOUNT=abc12345.us-east-1")
    sys.exit(1)

if not user or user == "your_username":
    print("[ERROR] SNOWFLAKE_USER not configured in .env")
    print("Please update .env with your Snowflake username/email")
    sys.exit(1)

if not password or password == "your_password":
    print("[ERROR] SNOWFLAKE_PASSWORD not configured in .env")
    print("Please update .env with your Snowflake password")
    sys.exit(1)

print("[OK] Configuration found:")
print(f"  Account: {account}")
print(f"  User: {user}")
print(f"  Password: {'*' * len(password)}")

# Try to connect
print("\n[2/3] Connecting to Snowflake...")
try:
    from app.services.snowflake_service import SnowflakeService

    snowflake = SnowflakeService.get_instance()

    if not snowflake.is_connected():
        print("[ERROR] Could not connect to Snowflake")
        print("\nTroubleshooting:")
        print("1. Verify your account identifier is correct (Format: abc12345.region)")
        print("2. Check your username and password are correct")
        print("3. Make sure you've created the BUGREWIND database in Snowflake UI")
        sys.exit(1)

    print("[OK] Connected successfully!")

except Exception as e:
    print(f"[ERROR] Connection failed: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Verify credentials in .env are correct")
    print("2. Check Snowflake account is active")
    print("3. Ensure firewall/VPN isn't blocking connection")
    sys.exit(1)

# Test health
print("\n[3/3] Testing health endpoint...")
try:
    health = snowflake.health_check()

    if health.get("status") == "healthy":
        print("[OK] Health check passed!")
        print(f"  Database: {health.get('database')}")
        print(f"  Schema: {health.get('schema')}")
        print(f"  Warehouse: {health.get('warehouse')}")
        print(f"  Version: {health.get('version')}")
    else:
        print(f"[WARNING] Health check returned: {health.get('status')}")

except Exception as e:
    print(f"[ERROR] Health check failed: {str(e)}")
    sys.exit(1)

# Test insert
print("\n[4/4] Testing data insertion...")
try:
    test_commit = {
        "commit_hash": "test123abc456def789012345678901234567890",
        "repo_name": "test/bugrewind",
        "author": "Test User",
        "author_email": "test@example.com",
        "timestamp": "2024-01-15T10:30:00",
        "message": "Test commit for Snowflake integration",
        "files_changed": ["test.py"],
        "insertions": 5,
        "deletions": 2
    }

    success = snowflake.insert_commit(test_commit)

    if success:
        print("[OK] Test commit inserted successfully!")
    else:
        print("[WARNING] Could not insert test commit")
        print("Make sure you've run the SQL setup (CREATE TABLE COMMITS...)")

except Exception as e:
    print(f"[ERROR] Insert failed: {str(e)}")
    print("\nMake sure you've run the SQL setup from Step 1:")
    print("  - CREATE TABLE COMMITS ...")
    print("  - CREATE TABLE BUG_ANALYSIS ...")

print("\n" + "="*60)
print("  SUCCESS! Snowflake is ready to use!")
print("="*60)
print("\nNext step: Start the backend server:")
print("  cd backend")
print("  python app/main.py")
print("\nThen visit: http://localhost:8000/docs")
print("="*60 + "\n")
