#!/usr/bin/env python3
import json
import urllib.request
import urllib.error

def test_firebase_function():
    url = "https://us-central1-data-base-test-6ef5f.cloudfunctions.net/getActiveConfig"
    
    try:
        print(f"Testing: {url}")
        
        # Create request
        request = urllib.request.Request(url)
        request.add_header('Content-Type', 'application/json')
        
        # Make request
        with urllib.request.urlopen(request) as response:
            print(f"Status Code: {response.status}")
            print(f"Headers: {dict(response.headers)}")
            
            # Read response
            response_data = response.read().decode('utf-8')
            print(f"Response: {response_data}")
            
            # Try to parse JSON
            try:
                json_data = json.loads(response_data)
                print(f"Parsed JSON: {json.dumps(json_data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        error_data = e.read().decode('utf-8')
        print(f"Error response: {error_data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_firebase_function()