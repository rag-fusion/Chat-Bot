import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
EMAIL = "test@example.com"
PASSWORD = "password123"

def get_token():
    try:
        # Try login first
        response = requests.post(f"{BASE_URL}/api/auth/login", data={"username": EMAIL, "password": PASSWORD})
        if response.status_code == 200:
            return response.json()["access_token"]
        
        # If login fails, try register
        print("Login failed, trying registration...")
        response = requests.post(f"{BASE_URL}/api/auth/register", json={"email": EMAIL, "password": PASSWORD, "name": "Test User"})
        if response.status_code == 200:
            # Login again
            response = requests.post(f"{BASE_URL}/api/auth/login", data={"username": EMAIL, "password": PASSWORD})
            return response.json()["access_token"]
        else:
            print(f"Registration failed: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Auth failed: {e}")
        sys.exit(1)

def test_content_retrieval():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Ingest a file
    print("Ingesting test file...", flush=True)
    files = {'files': ('test_content.txt', 'This is a unique test phrase for verification: BANANA_SPLIT.', 'text/plain')}
    response = requests.post(f"{BASE_URL}/ingest", headers=headers, files=files)
    if response.status_code != 200:
        print(f"Ingest failed: {response.text}", flush=True)
        return

    print("Ingest successful.", flush=True)
    
    # 2. Query
    print("Querying...", flush=True)
    # Using a query that matches the content
    response = requests.post(f"{BASE_URL}/query", json={"query": "BANANA_SPLIT"}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        sources = data.get("sources", [])
        print(f"Found {len(sources)} sources.")
        
        found_content = False
        for s in sources:
            text = s.get("text", "")
            if "BANANA_SPLIT" in text:
                print("SUCCESS: Found expected content in source text!")
                print(f"Source preview: {text[:50]}...")
                found_content = True
                break
            else:
                print(f"Source text (first 50 chars): {text[:50]}...")
        
        if not found_content:
            print("FAILURE: Did not find expected content in any source.")
            print("Full sources:", sources)
    else:
        print(f"Query failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    test_content_retrieval()
