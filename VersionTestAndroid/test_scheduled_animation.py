#!/usr/bin/env python3
"""
Script to test scheduled animation after frames are loaded
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
ANIMATION_ID = "blue_black_flash"

def setup_scheduled_animation():
    """
    Set up a scheduled animation that will run after frames are loaded
    """
    try:
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Set animation time to 1 minute from now
        now = datetime.now()
        start_time = now + timedelta(minutes=1)
        animation_start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        print(f"🎨 Setting up scheduled animation for: {animation_start_time}")
        print(f"🕐 Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
        
        # First, update the animations collection with the scheduled time
        db.collection('animations').document(ANIMATION_ID).update({
            "startTime": animation_start_time + "Z"  # Add Z for UTC
        })
        
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
            "createdAt": firestore.SERVER_TIMESTAMP,
            "status": "active"
        }
        
        # Add the animation configuration
        doc_ref = db.collection('animation_configs').add(animation_config)
        config_id = doc_ref[1].id
        
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
        print(f"   1. First run: python3 test_frames_only.py")
        print(f"   2. Open Android app and enter waiting room")
        print(f"   3. You should see 'Package reçu: 20 frames' (no animation)")
        print(f"   4. Then run: python3 test_scheduled_animation.py")
        print(f"   5. The animation should start in 1 minute!")
        print(f"   6. Full screen animation should play for 10 seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    setup_scheduled_animation()