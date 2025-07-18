#!/usr/bin/env python3
"""
Test script to verify frames loading without scheduled animation
Uses Firebase Web SDK - no service account needed
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta

ANIMATION_ID = "blue_black_flash"

def setup_frames_only():
    """
    Set up animation frames without scheduling
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        print(f"📦 Setting up frames-only animation for testing")
        print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
        
        # Deactivate all existing animations
        existing_configs = fb.query_documents("animation_configs", "status", "==", "active")
        
        deactivated_count = 0
        for config in existing_configs:
            fb.update_document("animation_configs", config["id"], {"status": "inactive"})
            deactivated_count += 1
        
        if deactivated_count > 0:
            print(f"🔄 Deactivated {deactivated_count} existing animations")
        
        # Update only the animations collection with frames data (no scheduling)
        animation_data = {
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": "2099-01-01T00:00:00Z",  # Far future - won't trigger
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
        
        if success:
            print(f"✅ Frames-only animation configured successfully!")
            print(f"   - Animation ID: {ANIMATION_ID}")
            print(f"   - Frame Rate: 2 fps")
            print(f"   - Frame Count: 20")
            print(f"   - User: user_1_1 (row=1, col=1)")
            print(f"   - Start Time: 2099-01-01T00:00:00Z (far future - won't trigger)")
            print(f"   - NO scheduled animations active")
            
            print(f"\n📦 Test the Android app now:")
            print(f"   - Open the app and select:")
            print(f"     - Event: Stade de foot")
            print(f"     - Tribune: Tribune Nord")
            print(f"     - Row: 1")
            print(f"     - Seat: 1")
            print(f"   - Enter the waiting room")
            print(f"   - You should see 'Package reçu: 20 frames' but NO animation playing")
            print(f"   - The animation should only load frames, not play them")
        else:
            print(f"❌ Failed to configure animation")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    setup_frames_only()