import httpx
import time
import asyncio

URL = "http://localhost:8003/api"

async def test_rate_limit():
    async with httpx.AsyncClient() as client:
        print("Testing Rate Limit on /api/token (Limit: 5/minute)")
        
        # 1. Successful requests
        for i in range(5):
            response = await client.post(
                f"{URL}/token", 
                data={"username": "admin", "password": "wrong_password_is_fine_for_rate_limit_check"}
            )
            print(f"Request {i+1}: {response.status_code}")
            # Even 401 Unauthorized counts towards rate limit usually, depending on configuration.
            # But the limit is on the endpoint execution.
            # If 401 is returned, it means the endpoint was hit.
            
        # 2. Exceeding request
        print("Sending 6th request (Warning: Should be 429)")
        response = await client.post(
            f"{URL}/token", 
            data={"username": "admin", "password": "admin123"}
        )
        print(f"Request 6: {response.status_code}")
        
        if response.status_code == 429:
            print("✅ Rate Limiting PASSED")
        else:
            print(f"❌ Rate Limiting FAILED (Status: {response.status_code})")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
