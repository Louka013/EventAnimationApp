#!/usr/bin/env python3
"""
Debug script to check blue_black_flash user coverage
"""

from firebase_web_admin import FirebaseWebClient

def debug_blue_black_coverage():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Checking blue_black_flash animation user coverage...")
        
        # Get blue_black_flash animation
        animation_doc = fb.get_document("animations", "blue_black_flash")
        
        if not animation_doc:
            print("❌ No blue_black_flash animation found!")
            return
        
        users = animation_doc.get("users", {})
        print(f"📊 Found {len(users)} users in blue_black_flash animation:")
        
        # Parse and sort users
        user_positions = []
        for user_id in users.keys():
            if user_id.startswith("user_"):
                parts = user_id.split("_")
                if len(parts) == 3:
                    row = int(parts[1])
                    seat = int(parts[2])
                    user_positions.append((row, seat, user_id))
        
        user_positions.sort()
        
        # Display coverage
        print("\n📍 User coverage:")
        for row, seat, user_id in user_positions:
            print(f"   - {user_id}: BLUE/BLACK pattern")
        
        # Check if user_2_4 exists
        if "user_2_4" in users:
            print(f"\n✅ user_2_4 EXISTS in blue_black_flash")
        else:
            print(f"\n❌ user_2_4 NOT FOUND in blue_black_flash")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_blue_black_coverage()