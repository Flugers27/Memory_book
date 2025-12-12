# test_simple.py
import requests
import json

def test_simple():
    print("=== Simple Test ===\n")
    
    # 1. Сначала получим токен
    print("1. Getting token...")
    login_response = requests.post(
        "http://localhost:8080/auth/login",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print(f"   Login failed: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        
        # Попробуем зарегистрировать пользователя
        print("\n   Trying to register...")
        register_response = requests.post(
            "http://localhost:8080/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        print(f"   Register: {register_response.status_code}")
        
        # Снова попробуем войти
        login_response = requests.post(
            "http://localhost:8080/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
    
    if login_response.status_code != 200:
        print("   Cannot get token, stopping test")
        return
    
    token = login_response.json()["access_token"]
    print(f"   Token received: {token[:50]}...\n")
    
    # 2. Протестируем Memory сервис
    print("2. Testing Memory service...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Прямой запрос к Memory
    print("   a) Direct to Memory service (port 8001):")
    response1 = requests.get("http://localhost:8001/agents/", headers=headers)
    print(f"      Status: {response1.status_code}")
    print(f"      Response: {response1.text[:200]}")
    
    # Через Gateway
    print("\n   b) Through Gateway (port 8080):")
    response2 = requests.get("http://localhost:8080/agents/", headers=headers)
    print(f"      Status: {response2.status_code}")
    print(f"      Response: {response2.text[:200]}")
    
    # Без токена
    print("\n   c) Without token:")
    response3 = requests.get("http://localhost:8001/agents/")
    print(f"      Status: {response3.status_code}")
    print(f"      Response: {response3.text}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_simple()