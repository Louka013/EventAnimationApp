#!/usr/bin/env python3
"""
Test script to verify web interface date format compatibility
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
ANIMATION_ID = "blue_black_flash"

def test_web_format():
    """
    Test animation with web interface compatible format
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
        
        # Simulate web interface format (datetime-local without seconds)
        web_format_time = start_time.strftime('%Y-%m-%dT%H:%M')
        
        # Format with seconds as the web interface should now do
        formatted_time = web_format_time + ':00Z'
        
        print(f"🌐 Web interface format: {web_format_time}")
        print(f"🔧 Formatted for Firebase: {formatted_time}")
        print(f"🕐 Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
        
        # Deactivate existing animations
        existing_query = db.collection('animation_configs').where('eventType', '==', 'football_stadium').where('status', '==', 'active')
        existing_docs = existing_query.stream()
        
        deactivated_count = 0
        for doc in existing_docs:
            doc.reference.update({"status": "inactive"})
            deactivated_count += 1
        
        if deactivated_count > 0:
            print(f"🔄 Deactivated {deactivated_count} existing animations")
        
        # Animation configuration
        animation_config = {
            "animationStartTime": web_format_time,  # Original web format
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
        
        # Update the main animations collection with properly formatted time
        db.collection('animations').document(ANIMATION_ID).set({
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": formatted_time,  # Formatted with seconds and Z
            "users": animation_config["animationData"]["users"]
        })
        
        print(f"✅ Test animation configured successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Web Format Time: {web_format_time}")
        print(f"   - Firebase Format Time: {formatted_time}")
        print(f"   - Event Type: football_stadium")
        print(f"   - User: user_1_1 (row=1, col=1)")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print(f"   Test the Android app to verify date format compatibility!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    test_web_format()