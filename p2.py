import requests
import json

def fetch_pumpfun_coin(mint: str, sync: bool = True):
    """
    Fetch raw JSON data for a single PumpFun coin by mint address.
    """
    base_url = "https://frontend-api-v3.pump.fun/coins"
    url = f"{base_url}/{mint}?sync={'true' if sync else 'false'}"

    jwt_token = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkRmYnlOelZjdkZrX0ltUVBGTFNTb1NMTTR5eUVBenVqdGVNa01GeEpRWWcifQ.eyJzaWQiOiJjbWZvbG1jcm4wMDA3anIwYnNydmUwMGc5IiwiaXNzIjoicHJpdnkuaW8iLCJpYXQiOjE3NTgxNTA4NDgsImF1ZCI6ImNtMXAyZ3pvdDAzZnpxdHk1eHpnamd0aHEiLCJzdWIiOiJkaWQ6cHJpdnk6Y21mb2t6OTNkMDA2MGw4MGIzY2duM2l1dSIsImV4cCI6MTc1ODE1NDQ0OH0.rARcbkTAFj4IFlGTlr20Px0pA8IQJG-13MUPKunj1u9rnp_0m_SEnGozRE6eW27CQq1AccL_tMv66OrMUWDNeg"

    headers = {
        "Authorization": f"Bearer {jwt_token}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    mint_address = input("Enter the PumpFun coin mint address: ").strip()
    try:
        data = fetch_pumpfun_coin(mint_address)
        print("=== PumpFun Coin Data ===")
        print(json.dumps(data, indent=2))  # <-- Pretty-print raw JSON
    except Exception as e:
        print(f"Error fetching coin data: {e}")
