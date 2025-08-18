import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()
async def reverse_geocode(lat: float, lon: float):
    """Get city, district (if available), state using OpenCage API."""
    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        params = {"q": f"{lat},{lon}", "key": os.getenv("OPENCAGE_KEY")}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, params=params)
            data = res.json()

            if "results" in data and len(data["results"]) > 0:
                comp = data["results"][0]["components"]

                city = comp.get("city") or comp.get("town") or comp.get("village")
                state = comp.get("state")
                # District may come under different keys
                district = comp.get("state_district") or comp.get("county") or comp.get("suburb")

                print(f"City: {city}, District: {district}, State: {state}")
                return {"city": city, "district": district, "state": state}
    except Exception as e:
        print(f"Error in reverse geocode: {e}")
    return {"city": None, "district": None, "state": None}


# Example usage
if __name__ == "__main__":
    lat, lon = 28.6139, 77.2090  # New Delhi
    asyncio.run(reverse_geocode(lat, lon))
