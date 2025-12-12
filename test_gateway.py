# test_gateway.py
import requests
import json

def test_gateway_headers():
    # 1. Сначала получим токен через gateway
    login_response = requests.post(
        "http://localhost:8080/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"Token received: {token[:50]}...")
    
    # 2. Отправим запрос к agents через gateway с токеном
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    agents_response = requests.get(
        "http://localhost:8080/agents/",
        headers=headers
    )
    
    print(f"\nGateway response status: {agents_response.status_code}")
    print(f"Gateway response headers: {dict(agents_response.headers)}")
    
    if agents_response.status_code == 401:
        print("\nERROR: Memory service returns 401 Unauthorized")
        print("This means the token is not being validated correctly in Memory service")
        
        # Проверим напрямую Memory сервис
        print("\n--- Testing Memory service directly ---")
        direct_response = requests.get(
            "http://localhost:8001/agents/",
            headers=headers
        )
        print(f"Direct Memory response: {direct_response.status_code}")
        print(direct_response.text)
    
    return agents_response.json()

if __name__ == "__main__":
    test_gateway_headers()