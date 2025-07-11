#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

def test_function(function_name):
    url = f"https://us-central1-data-base-test-6ef5f.cloudfunctions.net/{function_name}"
    
    try:
        print(f"Testing: {url}")
        
        # Create request
        request = urllib.request.Request(url)
        request.add_header('Content-Type', 'application/json')
        
        # Make request
        with urllib.request.urlopen(request) as response:
            print(f"Status Code: {response.status}")
            response_data = response.read().decode('utf-8')
            print(f"Response: {response_data}")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        if e.code == 404:
            print(f"Function {function_name} not found")
        else:
            error_data = e.read().decode('utf-8')
            print(f"Error response: {error_data}")
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def main():
    functions = [
        "getActiveConfig",
        "getAllAnimations", 
        "triggerAnimation",
        "getAnimation"
    ]
    
    print("Testing Firebase Cloud Functions...")
    print("=" * 50)
    
    for func_name in functions:
        print(f"\n--- Testing {func_name} ---")
        success = test_function(func_name)
        if success:
            print(f"✅ {func_name} is working")
        else:
            print(f"❌ {func_name} failed")
        print("-" * 30)

if __name__ == "__main__":
    main()