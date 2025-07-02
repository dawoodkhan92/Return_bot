import threading
import time
import requests
import uvicorn
from app import app

def start_server():
    uvicorn.run(app, host='127.0.0.1', port=8099, log_level="error")

if __name__ == "__main__":
    print("🧪 Testing FastAPI app locally...")
    
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(4)
    
    try:
        # Test health endpoint
        print("Testing /health endpoint...")
        health_response = requests.get('http://127.0.0.1:8099/health', timeout=5)
        print(f"✅ Health Status: {health_response.status_code}")
        print(f"✅ Health Response: {health_response.json()}")
        
        # Test homepage
        print("\nTesting / homepage...")
        home_response = requests.get('http://127.0.0.1:8099/', timeout=5)
        print(f"✅ Homepage Status: {home_response.status_code}")
        
        if home_response.status_code == 200:
            content = home_response.text
            has_title = "<title>" in content
            has_chat = "chat" in content.lower()
            print(f"✅ Has HTML title: {has_title}")
            print(f"✅ Contains 'chat': {has_chat}")
            print(f"✅ Content Length: {len(content)} characters")
            
            if has_title and has_chat and len(content) > 1000:
                print("\n🎉 SUCCESS: App works perfectly!")
            else:
                print("\n❌ WARNING: Homepage may not be serving correctly")
        else:
            print(f"\n❌ ERROR: Homepage returned {home_response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n🏁 Test completed!") 