import requests
import json

def fetch_coin_data(jwt_token, coin_mint):
    url = f"https://frontend-api-v3.pump.fun/coins/{coin_mint}?sync=true"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("\n=== PumpFun Coin Data ===\n")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error {response.status_code}: {response.text}")


if __name__ == "__main__":
    # Ask user for inputs
    jwt_token = input("Enter your PumpFun JWT token: ").strip()
    coin_mint = input("Enter the PumpFun coin mint address: ").strip()

    fetch_coin_data(jwt_token, coin_mint)
