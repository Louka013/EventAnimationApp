#!/usr/bin/env python3
"""
Check if user_9_9 exists in Firebase database for checkboard_flash animation
"""

from firebase_web_admin import FirebaseWebClient

def check_user_9_9():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Checking for user_9_9 in checkboard_flash animation...")
        
        # Check in main animations collection
        print("\n📊 Checking animations collection...")
        checkboard_animation = fb.get_document("animations", "checkboard_flash")
        
        if checkboard_animation:
            users = checkboard_animation.get("users", {})
            if "user_9_9" in users:
                print(f"✅ user_9_9 found in animations/checkboard_flash")
                user_data = users["user_9_9"]
                colors = user_data.get("colors", [])
                print(f"   - Colors: {len(colors)} frames")
                if colors:
                    print(f"   - First color: {colors[0]}")
                    print(f"   - Second color: {colors[1] if len(colors) > 1 else 'N/A'}")
            else:
                print(f"❌ user_9_9 NOT found in animations/checkboard_flash")
                print(f"   - Total users in animation: {len(users)}")
                sample_users = list(users.keys())[:5]
                print(f"   - Sample users: {sample_users}")
        else:
            print("❌ checkboard_flash animation not found in animations collection")
        
        # Check in userAnimationPackages collection
        print("\n📦 Checking userAnimationPackages collection...")
        user_package = fb.get_document("userAnimationPackages", "user_9_9")
        
        if user_package:
            animation_type = user_package.get("animationType", "unknown")
            print(f"✅ user_9_9 found in userAnimationPackages")
            print(f"   - Animation Type: {animation_type}")
            if animation_type == "checkboard_flash":
                frames = user_package.get("frames", [])
                print(f"   - Frames: {len(frames)}")
                print(f"   - Active: {user_package.get('isActive', False)}")
                print(f"   - Start Time: {user_package.get('startTime', 'N/A')}")
        else:
            print("❌ user_9_9 NOT found in userAnimationPackages")
        
        # Apply checkboard logic to determine what color user_9_9 should get
        print("\n🎨 Applying checkboard logic to user_9_9 (row 9, seat 9)...")
        row = 9
        seat = 9
        
        # Based on the checkboard_flash scripts, color is determined by seat number
        if seat % 2 == 1:  # Odd seat
            color_type = "RED"
            color_value = {"r": 255, "g": 0, "b": 0}
        else:  # Even seat
            color_type = "BLUE"
            color_value = {"r": 0, "g": 0, "b": 255}
        
        print(f"   - Row: {row}")
        print(f"   - Seat: {seat}")
        print(f"   - Seat % 2: {seat % 2}")
        print(f"   - Color assignment: {color_type} (because seat {seat} is {'odd' if seat % 2 == 1 else 'even'})")
        print(f"   - Color value: {color_value}")
        
        # Show the pattern that would be generated
        black_color = {"r": 0, "g": 0, "b": 0}
        pattern = []
        for i in range(20):
            if i % 2 == 0:  # Even frame indices -> colored
                pattern.append(color_value)
            else:  # Odd frame indices -> black
                pattern.append(black_color)
        
        print(f"   - Pattern (first 4 frames): {pattern[:4]}")
        print(f"   - Total frames: {len(pattern)}")
        
        return color_type, pattern
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    check_user_9_9()