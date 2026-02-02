import httpx
import asyncio

URL = "http://localhost:8003/test-error"

async def test_errors():
    async with httpx.AsyncClient() as client:
        print("Testing Error Handling...")

        # 1. ChurnException
        resp = await client.get(f"{URL}?type=churn")
        print(f"ChurnException (Expected 418): {resp.status_code}")
        print(f"Body: {resp.json()}")
        if resp.status_code == 418 and resp.json().get("error") == "ChurnException":
             print("✅ ChurnException handled correctly")
        else:
             print("❌ ChurnException handling failed")

        # 2. PredictionError
        resp = await client.get(f"{URL}?type=prediction")
        print(f"PredictionError (Expected 400): {resp.status_code}")
        print(f"Body: {resp.json()}")
        if resp.status_code == 400 and resp.json().get("error") == "PredictionError":
             print("✅ PredictionError handled correctly")
        else:
             print("❌ PredictionError handling failed")

        # 3. Generic Error
        resp = await client.get(f"{URL}?type=generic")
        print(f"Generic Error (Expected 500): {resp.status_code}")
        print(f"Body: {resp.json()}")
        if resp.status_code == 500 and resp.json().get("error") == "InternalServerError":
             print("✅ Generic Error handled correctly")
        else:
             print("❌ Generic Error handling failed")

if __name__ == "__main__":
    asyncio.run(test_errors())
