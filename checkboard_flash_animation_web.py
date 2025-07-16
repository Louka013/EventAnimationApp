#!/usr/bin/env python3
"""
Script to create checkboard_flash animation using Firebase Web SDK
No service account needed - uses Firebase Web SDK
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta

ANIMATION_ID = "checkboard_flash"

def create_checkboard_flash_animation():
    """
    Create checkboard animation where:
    - Odd seats (1, 3, 5, etc.) flash red and black
    - Even seats (2, 4, 6, etc.) flash blue and black
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
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
        
        for row in range(1, 6):  # Rows 1-5
            for seat in range(1, 7):  # Seats 1-6
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
        
        # First, deactivate any existing active animations
        print("🔄 Deactivating existing animations...")
        
        # Get all animation_configs
        configs = fb.list_documents("animation_configs")
        if configs:
            for config in configs:
                config_id = config["id"]
                config_data = config["data"]
                if config_data.get("status") == "active":
                    fb.update_document("animation_configs", config_id, {"status": "inactive"})
                    print(f"   - Deactivated config: {config_id}")
        
        # Animation data for main collection
        animation_data = {
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": animation_start_time + "Z",  # Add Z for UTC
            "users": users
        }
        
        # Set the main animation document
        success = fb.set_document("animations", ANIMATION_ID, animation_data)
        if not success:
            print("❌ Failed to set animation document")
            return
        
        # Animation configuration for scheduling
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
            "createdAt": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Add the animation configuration
        config_id = fb.add_document("animation_configs", animation_config)
        if not config_id:
            print("❌ Failed to add animation config")
            return
        
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