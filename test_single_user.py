#!/usr/bin/env python3
"""
Test creating a single user animation package
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta, timezone

def test_single_user():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Testing single user animation package creation...")
        
        # Test writing to userAnimationPackages
        test_data = {
            "userId": "user_2_4",
            "animationType": "checkboard_flash",
            "eventType": "football_stadium",
            "startTime": "2025-07-16T16:30:00",
            "endTime": "2025-07-16T16:30:10",
            "frames": ["color_255_0_0", "color_0_0_0", "color_255_0_0"],
            "frameRate": 2,
            "frameCount": 3,
            "isActive": True,
            "isExpired": False,
            "animationId": "checkboard_flash",
            "duration": 10.0,
            "pattern": "checkboard_flash",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        print("📝 Attempting to create userAnimationPackage...")
        success = fb.set_document("userAnimationPackages", "user_2_4", test_data)
        
        if success:
            print("✅ Write successful!")
            
            # Verify it was written
            retrieved = fb.get_document("userAnimationPackages", "user_2_4")
            if retrieved:
                print(f"✅ Verification successful: {retrieved.get('userId')}")
            else:
                print("❌ Verification failed: Document not found")
        else:
            print("❌ Write failed!")
            
        # Test writing to animations collection
        print("\n🔍 Testing animations collection write...")
        test_animation = {
            "animationId": "test_checkboard",
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": "2025-07-16T16:30:00Z",
            "users": {
                "user_2_4": {
                    "colors": [
                        {"r": 255, "g": 0, "b": 0},
                        {"r": 0, "g": 0, "b": 0}
                    ]
                }
            }
        }
        
        success2 = fb.set_document("animations", "test_checkboard", test_animation)
        if success2:
            print("✅ Animations collection write successful!")
        else:
            print("❌ Animations collection write failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_user()