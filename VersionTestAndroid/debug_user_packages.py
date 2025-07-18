#!/usr/bin/env python3
"""
Debug script to check userAnimationPackages collection structure
"""

from firebase_web_admin import FirebaseWebClient

def debug_user_packages():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Checking userAnimationPackages collection...")
        
        # Get all user packages
        packages = fb.list_documents("userAnimationPackages")
        
        print(f"📊 Found {len(packages)} user packages:")
        
        # Group by animation type
        animation_types = {}
        for package in packages:
            package_id = package["id"]
            data = package["data"]
            
            animation_type = data.get("animationType", "unknown")
            user_id = data.get("userId", "unknown")
            
            if animation_type not in animation_types:
                animation_types[animation_type] = []
            animation_types[animation_type].append(user_id)
        
        for animation_type, users in animation_types.items():
            print(f"\n🎬 {animation_type}:")
            print(f"   - Users: {len(users)}")
            if len(users) <= 10:
                print(f"   - User IDs: {', '.join(users)}")
            else:
                print(f"   - Sample User IDs: {', '.join(users[:5])}... (+{len(users)-5} more)")
        
        # Check if user_2_4 exists
        user_2_4_found = False
        for package in packages:
            data = package["data"]
            if data.get("userId") == "user_2_4":
                user_2_4_found = True
                print(f"\n✅ user_2_4 found in userAnimationPackages:")
                print(f"   - Animation Type: {data.get('animationType')}")
                print(f"   - Frame Count: {len(data.get('frames', []))}")
                print(f"   - Active: {data.get('isActive')}")
                break
        
        if not user_2_4_found:
            print(f"\n❌ user_2_4 NOT found in userAnimationPackages")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_user_packages()