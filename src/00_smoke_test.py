import requests

print("Environment ready!")
r = requests.get("https://api.github.com", timeout=30)
print("Status:", r.status_code)