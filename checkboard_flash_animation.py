#!/usr/bin/env python3
"""
Script to create checkboard_flash animation where odd seats have red flashes
and even seats have blue flashes, alternating with black
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
ANIMATION_ID = "checkboard_flash"

def create_checkboard_flash_animation():
    """
    Create checkboard animation where:
    - Odd seats (1, 3, 5, etc.) flash red and black
    - Even seats (2, 4, 6, etc.) flash blue and black
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
        
        print(f"🎨 Creating checkboard_flash animation for: {animation_start_time}")
        print(f"🕐 Current time: {now.strftime('%Y-%m-%dT%H:%M:%S')}")
        
        # Define colors
        red_color = {"r": 255, "g": 0, "b": 0}      # Red for odd seats
        blue_color = {"r": 0, "g": 0, "b": 255}     # Blue for even seats
        black_color = {"r": 0, "g": 0, "b": 0}      # Black for all seats
        
        # Create color patterns (20 frames, 2 fps = 10 seconds)
        red_pattern = []
        blue_pattern = []
        
        for i in range(20):
            if i % 2 == 0:  # Even frame indices -> colored
                red_pattern.append(red_color)
                blue_pattern.append(blue_color)
            else:  # Odd frame indices -> black
                red_pattern.append(black_color)
                blue_pattern.append(black_color)
        
        # Generate animation for a grid of seats (5 rows x 6 columns = 30 seats)
        users = {}
        
        for row in range(1, 11):  # Rows 1-10
            for seat in range(1, 11):  # Seats 1-10
                user_id = f"user_{row}_{seat}"
                
                # Check if seat number is odd or even
                if seat % 2 == 1:  # Odd seat -> red flash
                    users[user_id] = {
                        "colors": red_pattern
                    }
                else:  # Even seat -> blue flash
                    users[user_id] = {
                        "colors": blue_pattern
                    }
        
        # Animation configuration
        animation_config = {
            "animationStartTime": animation_start_time,
            "eventType": "football_stadium",
            "animationType": "checkboard_flash",
            "animationData": {
                "animationId": "checkboard_flash",
                "frameRate": 2,
                "frameCount": 20,
                "type": "color_animation",
                "users": users
            },
            "createdAt": firestore.SERVER_TIMESTAMP,
            "status": "active"
        }
        
        # First, deactivate any existing active animations
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
            "users": users
        })
        
        print(f"✅ Checkboard flash animation configured successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Event Type: football_stadium")
        print(f"   - Start Time: {animation_start_time}")
        print(f"   - Frame Rate: 2 fps")
        print(f"   - Frame Count: 20")
        print(f"   - Duration: 10 seconds")
        print(f"   - Total Users: {len(users)}")
        
        print(f"\n🎨 Checkboard Pattern:")
        print(f"   - ODD seats (1, 3, 5, etc.): RED flash alternating with BLACK")
        print(f"   - EVEN seats (2, 4, 6, etc.): BLUE flash alternating with BLACK")
        print(f"   - Grid: 5 rows x 6 columns = 30 seats")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print(f"   Open the Android app and select:")
        print(f"   - Event: Stade de foot")
        print(f"   - Tribune: Tribune Nord")
        print(f"   - Row: 1-5")
        print(f"   - Seat: 1-6")
        print(f"   Then enter the waiting room to see the animation!")
        
        # Print some example users
        print(f"\n📍 Example users:")
        for row in range(1, 3):
            for seat in range(1, 4):
                user_id = f"user_{row}_{seat}"
                color = "RED" if seat % 2 == 1 else "BLUE"
                print(f"   - {user_id}: {color} flash")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    create_checkboard_flash_animation()