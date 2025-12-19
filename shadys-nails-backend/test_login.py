import requests
import json

# Probar login
url = "http://127.0.0.1:8000/auth/login"
data = {
    "email": "gina.paola@shadysnails.com",
    "password": "shadysnails2024"
}

print("🔐 Probando login...")
print(f"URL: {url}")
print(f"Data: {data}")

response = requests.post(url, json=data)

print(f"\n📊 Status Code: {response.status_code}")
print(f"📄 Response: {response.text}")

if response.status_code == 200:
    token_data = response.json()
    print(f"\n✅ LOGIN EXITOSO!")
    print(f"🎫 Token: {token_data['access_token'][:50]}...")
    
    # Probar endpoint /me
    print("\n\n🔍 Probando endpoint /me...")
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = requests.get("http://127.0.0.1:8000/auth/me", headers=headers)
    print(f"📊 Status Code: {me_response.status_code}")
    print(f"📄 User Data: {json.dumps(me_response.json(), indent=2)}")
else:
    print(f"\n❌ LOGIN FALLÓ")
    print(f"Error: {response.text}")
