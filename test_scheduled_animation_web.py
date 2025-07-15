#!/usr/bin/env python3
"""
Test script to set up scheduled animation after frames are loaded
Uses Firebase Web SDK - no service account needed
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta

ANIMATION_ID = "blue_black_flash"

def setup_scheduled_animation():
    """
    Set up a scheduled animation that will run after frames are loaded
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        # Set animation time to 1 minute from now
        now = datetime.now()
        start_time = now + timedelta(minutes=1)
        animation_start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        print(f"🎨 Setting up scheduled animation for: {animation_start_time}")
        print(f"🕐 Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
        
        # First, update the animations collection with the scheduled time
        animation_data = {
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": animation_start_time + "Z",  # Add Z for UTC
            "users": {
                "user_1_1": {
                    "colors": [
                        {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                        {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                        {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                        {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                        {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}
                    ]
                }
            }
        }
        
        success = fb.set_document("animations", ANIMATION_ID, animation_data)
        
        # Add the animation configuration for real-time notifications
        animation_config = {
            "animationStartTime": animation_start_time,
            "eventType": "football_stadium",
            "animationType": "blue_black_flash",
            "animationData": {
                "animationId": "blue_black_flash",
                "frameRate": 2,
                "frameCount": 20,
                "type": "color_animation",
                "users": {
                    "user_1_1": {
                        "colors": [
                            {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                            {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                            {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                            {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0},
                            {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}, {"r": 0, "g": 0, "b": 255}, {"r": 0, "g": 0, "b": 0}
                        ]
                    }
                }
            },
            "createdAt": fb.get_current_timestamp(),
            "status": "active"
        }
        
        # Add the animation configuration
        config_id = fb.add_document("animation_configs", animation_config)
        
        if success and config_id:
            print(f"✅ Scheduled animation configured successfully!")
            print(f"   - Config ID: {config_id}")
            print(f"   - Animation ID: {ANIMATION_ID}")
            print(f"   - Start Time: {animation_start_time}Z")
            print(f"   - Event Type: football_stadium")
            print(f"   - User: user_1_1 (row=1, col=1)")
            print(f"   - Frame Rate: 2 fps")
            print(f"   - Frame Count: 20")
            print(f"   - Duration: 10 seconds")
            
            print(f"\n🎬 Test sequence:")
            print(f"   1. First run: python3 test_frames_only_web.py")
            print(f"   2. Open Android app and enter waiting room")
            print(f"   3. You should see 'Package reçu: 20 frames' (no animation)")
            print(f"   4. Then run: python3 test_scheduled_animation_web.py")
            print(f"   5. The animation should start in 1 minute!")
            print(f"   6. Full screen animation should play for 10 seconds")
        else:
            print(f"❌ Failed to configure scheduled animation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    setup_scheduled_animation()