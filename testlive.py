import requests
import json

# PumpFun API endpoint
URL = "https://frontend-api-v3.pump.fun/coins/currently-live"

# Replace this with your actual JWT (already provided in your message)
JWT_TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkRmYnlOelZjdkZrX0ltUVBGTFNTb1NMTTR5eUVBenVqdGVNa01GeEpRWWcifQ.eyJzaWQiOiJjbWZvbG1jcm4wMDA3anIwYnNydmUwMGc5IiwiaXNzIjoicHJpdnkuaW8iLCJpYXQiOjE3NTgxNTA4NDgsImF1ZCI6ImNtMXAyZ3pvdDAzZnpxdHk1eHpnamd0aHEiLCJzdWIiOiJkaWQ6cHJpdnk6Y21mb2t6OTNkMDA2MGw4MGIzY2duM2l1dSIsImV4cCI6MTc1ODE1NDQ0OH0.rARcbkTAFj4IFlGTlr20Px0pA8IQJG-13MUPKunj1u9rnp_0m_SEnGozRE6eW27CQq1AccL_tMv66OrMUWDNeg"

# Request headers
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Accept": "application/json"
}

# Optional query params (change as needed)
params = {
    "offset": 0,
    "limit": 10,         # max coins to fetch at once
    "includeNsfw": "false",
    "order": "DESC"
}

# Make the request
response = requests.get(URL, headers=headers, params=params)

# Print status code
print(f"Status Code: {response.status_code}")

# Pretty-print JSON if success
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
else:
    print("Error:", response.text)
