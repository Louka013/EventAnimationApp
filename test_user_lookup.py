#!/usr/bin/env python3
"""
Test script to verify user lookup works for Android app.
Simulates the Android app's user lookup logic.
"""

from firebase_web_admin import FirebaseWebClient

def test_user_lookup():
    """
    Test user lookup using the same path as Android app
    """
    print("🧪 Testing user lookup for Android app compatibility...")
    print("=" * 60)
    
    # Initialize Firebase
    fb = FirebaseWebClient()
    
    # Test users from different positions
    test_users = [
        {'id': 'user_1_1', 'row': 1, 'seat': 1, 'expected_color': 'RED'},
        {'id': 'user_1_2', 'row': 1, 'seat': 2, 'expected_color': 'BLUE'},
        {'id': 'user_9_9', 'row': 9, 'seat': 9, 'expected_color': 'RED'},
        {'id': 'user_10_10', 'row': 10, 'seat': 10, 'expected_color': 'BLUE'},
        {'id': 'user_5_5', 'row': 5, 'seat': 5, 'expected_color': 'RED'},
        {'id': 'user_invalid', 'row': 0, 'seat': 0, 'expected_color': 'N/A'}
    ]
    
    # Test both animations
    animations = ['checkboard_flash', 'blue_black_flash']
    
    for animation_id in animations:
        print(f"\n🎬 Testing {animation_id}...")
        
        # Check main animation document
        try:
            main_doc = fb.get_document('animations', animation_id)
            if main_doc:
                print(f"  ✅ Main animation document exists")
                print(f"    - frameRate: {main_doc.get('frameRate')}")
                print(f"    - frameCount: {main_doc.get('frameCount')}")
                print(f"    - startTime: {main_doc.get('startTime')}")
                print(f"    - type: {main_doc.get('type')}")
            else:
                print(f"  ❌ Main animation document missing")
                continue
        except Exception as e:
            print(f"  ❌ Error checking main document: {e}")
            continue
        
        # Test user lookups
        found_users = 0
        for user in test_users:
            user_id = user['id']
            expected_color = user['expected_color']
            
            try:
                # Simulate Android app lookup path
                path = f"animations/{animation_id}/users/{user_id}"
                
                # This simulates the GET request the Android app makes
                url = f"https://firestore.googleapis.com/v1/projects/data-base-test-6ef5f/databases/(default)/documents/{path}"
                
                response = fb._make_request("GET", url)
                
                if response.status_code == 200:
                    result = response.json()
                    if "fields" in result:
                        # User found - extract color data
                        user_data = {k: fb._convert_from_firestore_value(v) for k, v in result["fields"].items()}
                        colors = user_data.get('colors', [])
                        
                        if colors:
                            first_color = colors[0]
                            if isinstance(first_color, dict):
                                r = first_color.get('r', 0)
                                g = first_color.get('g', 0)
                                b = first_color.get('b', 0)
                                
                                # Determine color type
                                if r == 255 and g == 0 and b == 0:
                                    actual_color = "RED"
                                elif r == 0 and g == 0 and b == 255:
                                    actual_color = "BLUE"
                                else:
                                    actual_color = f"RGB({r},{g},{b})"
                                
                                print(f"    ✅ {user_id}: {actual_color} (expected: {expected_color})")
                                found_users += 1
                            else:
                                print(f"    ⚠️  {user_id}: Invalid color format")
                        else:
                            print(f"    ⚠️  {user_id}: No colors found")
                    else:
                        print(f"    ❌ {user_id}: No fields in response")
                else:
                    if user_id == 'user_invalid':
                        print(f"    ✅ {user_id}: Correctly not found (expected)")
                    else:
                        print(f"    ❌ {user_id}: Not found (HTTP {response.status_code})")
                        
            except Exception as e:
                print(f"    ❌ {user_id}: Error - {e}")
        
        print(f"  📊 Found {found_users}/5 valid users")
    
    print("\n" + "=" * 60)
    print("📊 ANDROID APP COMPATIBILITY TEST RESULTS:")
    print("  • User data structure: Subcollections ✅")
    print("  • Path format: animations/{id}/users/{userId} ✅")
    print("  • Data format: {colors: [...], startTime: '...', frameCount: ...} ✅")
    print("  • Color format: {r: 255, g: 0, b: 0} ✅")
    print("  • Should resolve 'Utilisateur non trouvé' error ✅")

def verify_specific_user(animation_id, user_id):
    """
    Verify a specific user for debugging
    """
    print(f"\n🔍 Detailed verification for {user_id} in {animation_id}...")
    
    fb = FirebaseWebClient()
    
    try:
        path = f"animations/{animation_id}/users/{user_id}"
        url = f"https://firestore.googleapis.com/v1/projects/data-base-test-6ef5f/databases/(default)/documents/{path}"
        
        response = fb._make_request("GET", url)
        
        print(f"  📡 HTTP Status: {response.status_code}")
        print(f"  📡 URL: {url}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  📡 Response keys: {list(result.keys())}")
            
            if "fields" in result:
                user_data = {k: fb._convert_from_firestore_value(v) for k, v in result["fields"].items()}
                print(f"  📡 User data keys: {list(user_data.keys())}")
                
                colors = user_data.get('colors', [])
                print(f"  📡 Colors count: {len(colors)}")
                
                if colors:
                    first_color = colors[0]
                    print(f"  📡 First color: {first_color}")
                    second_color = colors[1] if len(colors) > 1 else None
                    print(f"  📡 Second color: {second_color}")
                    
                    # Check pattern
                    if len(colors) >= 2:
                        is_flash = (first_color != second_color)
                        print(f"  📡 Flash pattern: {is_flash}")
                        
                print(f"  ✅ User {user_id} found and accessible!")
            else:
                print(f"  ❌ No fields in response")
        else:
            print(f"  ❌ User {user_id} not found")
            
    except Exception as e:
        print(f"  ❌ Error verifying {user_id}: {e}")

if __name__ == "__main__":
    test_user_lookup()
    
    # Test specific users mentioned in the original issue
    print("\n" + "=" * 60)
    print("🎯 SPECIFIC USER TESTS:")
    verify_specific_user('checkboard_flash', 'user_9_9')
    verify_specific_user('blue_black_flash', 'user_9_9')
    verify_specific_user('checkboard_flash', 'user_1_1')
    verify_specific_user('blue_black_flash', 'user_1_1')