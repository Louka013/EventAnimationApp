#!/usr/bin/env python3
"""
Test script for checkboard_flash animation - frames only (no scheduling)
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
ANIMATION_ID = "checkboard_flash"

def test_checkboard_flash():
    """
    Test the checkboard_flash animation frames without scheduling
    """
    try:
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        print(f"📦 Testing checkboard_flash animation frames")
        print(f"🕐 Current time: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
        
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
        
        # Generate animation for a few test seats
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
        
        # Deactivate all existing animations
        existing_query = db.collection('animation_configs').where('status', '==', 'active')
        existing_docs = existing_query.stream()
        
        deactivated_count = 0
        for doc in existing_docs:
            doc.reference.update({"status": "inactive"})
            deactivated_count += 1
        
        if deactivated_count > 0:
            print(f"🔄 Deactivated {deactivated_count} existing animations")
        
        # Update only the animations collection with frames data (no scheduling)
        db.collection('animations').document(ANIMATION_ID).set({
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": "2099-01-01T00:00:00Z",  # Far future - won't trigger
            "users": users
        })
        
        print(f"✅ Checkboard flash test frames configured successfully!")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Frame Rate: 2 fps")
        print(f"   - Frame Count: 20")
        print(f"   - Test Users: {len(users)}")
        print(f"   - Start Time: 2099-01-01T00:00:00Z (far future - won't trigger)")
        print(f"   - NO scheduled animations active")
        
        print(f"\n🎨 Checkboard Pattern:")
        print(f"   - ODD seats (1, 3, 5, etc.): RED flash alternating with BLACK")
        print(f"   - EVEN seats (2, 4, 6, etc.): BLUE flash alternating with BLACK")
        
        # Print test users
        print(f"\n📍 Test users:")
        for row in range(1, 3):
            for seat in range(1, 5):
                user_id = f"user_{row}_{seat}"
                color = "RED" if seat % 2 == 1 else "BLUE"
                print(f"   - {user_id}: {color} flash")
        
        print(f"\n📦 Test the Android app now:")
        print(f"   - Open the app and select:")
        print(f"     - Event: Stade de foot")
        print(f"     - Tribune: Tribune Nord")
        print(f"     - Row: 1 or 2")
        print(f"     - Seat: 1, 2, 3, or 4")
        print(f"   - Enter the waiting room")
        print(f"   - You should see 'Package reçu: 20 frames' but NO animation playing")
        print(f"   - The animation should only load frames, not play them")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    test_checkboard_flash()