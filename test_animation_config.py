#!/usr/bin/env python3
"""
Script to test blue_black_flash animation configuration
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
ANIMATION_ID = "blue_black_flash"

def setup_test_animation():
    """
    Set up a test animation configuration for blue_black_flash
    """
    try:
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Set animation time to 2 minutes from now
        now = datetime.now()
        start_time = now + timedelta(minutes=2)
        animation_start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        print(f"🎨 Setting up test animation for: {animation_start_time}")
        print(f"🕐 Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
        
        # Animation configuration
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
        
        # First, deactivate any existing active animations for this event type
        existing_query = db.collection('animation_configs').where('eventType', '==', 'football_stadium').where('status', '==', 'active')
        existing_docs = existing_query.stream()
        
        deactivated_count = 0
        for doc in existing_docs:
            doc.reference.update({"status": "inactive"})
            deactivated_count += 1
        
        if deactivated_count > 0:
            print(f"🔄 Deactivated {deactivated_count} existing animations")
        
        # Add the new animation configuration
        doc_ref = db.collection('animation_configs').add(animation_config)
        config_id = doc_ref[1].id
        
        # Also update the main animations collection
        db.collection('animations').document(ANIMATION_ID).set({
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": animation_start_time + "Z",  # Add Z for UTC
            "users": animation_config["animationData"]["users"]
        })
        
        print(f"✅ Test animation configured successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Event Type: football_stadium")
        print(f"   - Start Time: {animation_start_time}")
        print(f"   - Frame Rate: 2 fps")
        print(f"   - Frame Count: 20")
        print(f"   - Duration: 10 seconds")
        print(f"   - User: user_1_1 (row=1, col=1)")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print(f"   Open the Android app and select:")
        print(f"   - Event: Stade de foot")
        print(f"   - Tribune: Tribune Nord")
        print(f"   - Row: 1")
        print(f"   - Seat: 1")
        print(f"   Then enter the waiting room to see the animation!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    setup_test_animation()