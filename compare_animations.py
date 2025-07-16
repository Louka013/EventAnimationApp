#!/usr/bin/env python3
"""
Compare blue_black_flash vs checkboard_flash data structures
"""

from firebase_web_admin import FirebaseWebClient
import json

def compare_animations():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Comparing animation data structures...")
        
        # Get blue_black_flash animation
        blue_black = fb.get_document("animations", "blue_black_flash")
        checkboard = fb.get_document("animations", "checkboard_flash")
        
        print("\n📊 BLUE_BLACK_FLASH structure:")
        if blue_black:
            print(f"   - animationId: {blue_black.get('animationId')}")
            print(f"   - frameRate: {blue_black.get('frameRate')}")
            print(f"   - frameCount: {blue_black.get('frameCount')}")
            print(f"   - type: {blue_black.get('type')}")
            print(f"   - startTime: {blue_black.get('startTime')}")
            
            users = blue_black.get('users', {})
            print(f"   - users count: {len(users)}")
            
            # Show first user structure
            if users:
                first_user_id = list(users.keys())[0]
                first_user_data = users[first_user_id]
                print(f"   - first user: {first_user_id}")
                print(f"   - first user data keys: {list(first_user_data.keys())}")
                
                if 'colors' in first_user_data:
                    colors = first_user_data['colors']
                    print(f"   - colors count: {len(colors)}")
                    if colors:
                        print(f"   - first color: {colors[0]}")
                        print(f"   - second color: {colors[1] if len(colors) > 1 else 'none'}")
                
                if 'frames' in first_user_data:
                    frames = first_user_data['frames']
                    print(f"   - frames count: {len(frames)}")
                    if frames:
                        print(f"   - first frame: {frames[0]}")
        else:
            print("   - NOT FOUND")
        
        print("\n📊 CHECKBOARD_FLASH structure:")
        if checkboard:
            print(f"   - animationId: {checkboard.get('animationId')}")
            print(f"   - frameRate: {checkboard.get('frameRate')}")
            print(f"   - frameCount: {checkboard.get('frameCount')}")
            print(f"   - type: {checkboard.get('type')}")
            print(f"   - startTime: {checkboard.get('startTime')}")
            
            users = checkboard.get('users', {})
            print(f"   - users count: {len(users)}")
            
            # Show first user structure
            if users:
                first_user_id = list(users.keys())[0]
                first_user_data = users[first_user_id]
                print(f"   - first user: {first_user_id}")
                print(f"   - first user data keys: {list(first_user_data.keys())}")
                
                if 'colors' in first_user_data:
                    colors = first_user_data['colors']
                    print(f"   - colors count: {len(colors)}")
                    if colors:
                        print(f"   - first color: {colors[0]}")
                        print(f"   - second color: {colors[1] if len(colors) > 1 else 'none'}")
                
                if 'frames' in first_user_data:
                    frames = first_user_data['frames']
                    print(f"   - frames count: {len(frames)}")
                    if frames:
                        print(f"   - first frame: {frames[0]}")
            
            # Check for user_2_4
            if 'user_2_4' in users:
                user_2_4_data = users['user_2_4']
                print(f"\n   ✅ user_2_4 found:")
                print(f"   - data keys: {list(user_2_4_data.keys())}")
                if 'colors' in user_2_4_data:
                    colors = user_2_4_data['colors']
                    print(f"   - colors count: {len(colors)}")
                    print(f"   - first 3 colors: {colors[:3]}")
            else:
                print(f"\n   ❌ user_2_4 NOT found")
        else:
            print("   - NOT FOUND")
            
        # Check the difference
        print("\n🔍 KEY DIFFERENCES:")
        if blue_black and checkboard:
            blue_users = blue_black.get('users', {})
            checkboard_users = checkboard.get('users', {})
            
            if blue_users and checkboard_users:
                blue_first_user = list(blue_users.values())[0]
                checkboard_first_user = list(checkboard_users.values())[0]
                
                blue_keys = set(blue_first_user.keys())
                checkboard_keys = set(checkboard_first_user.keys())
                
                print(f"   - Blue user keys: {blue_keys}")
                print(f"   - Checkboard user keys: {checkboard_keys}")
                print(f"   - Missing in checkboard: {blue_keys - checkboard_keys}")
                print(f"   - Extra in checkboard: {checkboard_keys - blue_keys}")
                
                # Compare data structures
                if 'colors' in blue_first_user and 'colors' in checkboard_first_user:
                    blue_color = blue_first_user['colors'][0]
                    checkboard_color = checkboard_first_user['colors'][0]
                    
                    print(f"   - Blue color type: {type(blue_color)}")
                    print(f"   - Checkboard color type: {type(checkboard_color)}")
                    
                    if isinstance(blue_color, dict) and isinstance(checkboard_color, dict):
                        blue_color_keys = set(blue_color.keys())
                        checkboard_color_keys = set(checkboard_color.keys())
                        print(f"   - Blue color keys: {blue_color_keys}")
                        print(f"   - Checkboard color keys: {checkboard_color_keys}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_animations()