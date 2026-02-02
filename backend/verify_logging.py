import httpx
import time
import asyncio
import os

URL = "http://localhost:8003/api"
LOG_FILE = "logs/app.log"

async def test_logging():
    # 1. Generate some traffic
    async with httpx.AsyncClient() as client:
        print("Generating traffic...")
        # Login success
        await client.post(
            f"{URL}/token", 
            data={"username": "admin", "password": "admin123"}
        )
        # Login failure
        await client.post(
            f"{URL}/token", 
            data={"username": "admin", "password": "wrongpassword"}
        )
        
    # 2. Check logs
    print(f"Checking {LOG_FILE}...")
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = f.read()
            print("--- Log Content Preview ---")
            print(logs[-500:]) # Print last 500 chars
            print("---------------------------")
            
            if "Successful login for user: admin" in logs:
                print("✅ Found successful login log")
            else:
                print("❌ Missing successful login log")
                
            if "Failed login attempt" in logs:
                print("✅ Found failed login log")
            else:
                print("❌ Missing failed login log")
                
            if "Method: POST Status: 200" in logs:
                 print("✅ Found middleware request log")
            else:
                 print("❌ Missing middleware request log")
    else:
        print("❌ Log file not found!")

if __name__ == "__main__":
    asyncio.run(test_logging())
