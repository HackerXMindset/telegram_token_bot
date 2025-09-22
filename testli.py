import requests
import json

# ✅ Your PumpFun JWT token (from earlier)
JWT_TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkRmYnlOelZjdkZrX0ltUVBGTFNTb1NMTTR5eUVBenVqdGVNa01GeEpRWWcifQ.eyJzaWQiOiJjbWZvbG1jcm4wMDA3anIwYnNydmUwMGc5IiwiaXNzIjoicHJpdnkuaW8iLCJpYXQiOjE3NTgxNTA4NDgsImF1ZCI6ImNtMXAyZ3pvdDAzZnpxdHk1eHpnamd0aHEiLCJzdWIiOiJkaWQ6cHJpdnk6Y21mb2t6OTNkMDA2MGw4MGIzY2duM2l1dSIsImV4cCI6MTc1ODE1NDQ0OH0.rARcbkTAFj4IFlGTlr20Px0pA8IQJG-13MUPKunj1u9rnp_0m_SEnGozRE6eW27CQq1AccL_tMv66OrMUWDNeg"

BASE_URL = "https://frontend-api-v3.pump.fun/coins"

def fetch_coin_data(mint_address: str):
    url = f"{BASE_URL}/{mint_address}?sync=true"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    # Ask user for coin mint address
    coin_mint = input("Enter PumpFun coin mint address: ").strip()

    try:
        data = fetch_coin_data(coin_mint)
        # Print JSON formatted nicely
        print("\n=== PumpFun Coin Data ===")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Failed to fetch coin data:", str(e))
