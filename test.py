import requests

# Base URL for PumpFun v3 API
BASE_URL = "https://frontend-api-v3.pump.fun/coins"

# Enter your PumpFun JWT token here
JWT_TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkRmYnlOelZjdkZrX0ltUVBGTFNTb1NMTTR5eUVBenVqdGVNa01GeEpRWWcifQ.eyJzaWQiOiJjbWZvbG1jcm4wMDA3anIwYnNydmUwMGc5IiwiaXNzIjoicHJpdnkuaW8iLCJpYXQiOjE3NTgxNTA4NDgsImF1ZCI6ImNtMXAyZ3pvdDAzZnpxdHk1eHpnamd0aHEiLCJzdWIiOiJkaWQ6cHJpdnk6Y21mb2t6OTNkMDA2MGw4MGIzY2duM2l1dSIsImV4cCI6MTc1ODE1NDQ0OH0.rARcbkTAFj4IFlGTlr20Px0pA8IQJG-13MUPKunj1u9rnp_0m_SEnGozRE6eW27CQq1AccL_tMv66OrMUWDNeg#"

def get_coin_data(mint_address: str, sync: bool = True):
    """
    Fetch real-time data for a single PumpFun coin by mint address.
    
    Args:
        mint_address (str): The coin mint address.
        sync (bool): Whether to force fresh real-time data. Default: True.
    
    Returns:
        dict: Coin data if successful, or error message.
    """
    url = f"{BASE_URL}/{mint_address}"
    params = {"sync": str(sync).lower()}  # sync must be boolean (true/false)
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # raise error for bad status
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Example usage
    coin_mint = input("Enter the PumpFun coin mint address: ").strip()
    data = get_coin_data(coin_mint)
    print("\n=== PumpFun Coin Data ===")
    print(data)
