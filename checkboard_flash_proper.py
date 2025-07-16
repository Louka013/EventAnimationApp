#!/usr/bin/env python3
"""
Deploy checkboard_flash animation using proper userAnimationPackages approach
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta, timezone
import time

ANIMATION_ID = "checkboard_flash"

def deploy_proper_checkboard_flash():
    """
    Deploy checkboard_flash animation using individual userAnimationPackages
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        # Set animation time to 2 minutes from now in UTC
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc + timedelta(minutes=2)
        animation_start_time = start_time_utc.strftime('%Y-%m-%dT%H:%M:%S')
        
        print(f"🎨 Deploying checkboard_flash animation (PROPER METHOD)")
        print(f"🌍 Current UTC time: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        print(f"⏰ Animation start time: {animation_start_time}Z")
        
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
        
        print("🔄 Deactivating existing animations...")
        
        # Deactivate existing animation configs
        configs = fb.list_documents("animation_configs")
        if configs:
            for config in configs:
                config_id = config["id"]
                config_data = config["data"]
                if config_data.get("status") == "active":
                    fb.update_document("animation_configs", config_id, {"status": "inactive"})
                    print(f"   - Deactivated config: {config_id}")
        
        # Clear existing userAnimationPackages for checkboard_flash
        print("🗑️ Clearing existing userAnimationPackages...")
        packages = fb.list_documents("userAnimationPackages")
        cleared_count = 0
        for package in packages:
            package_id = package["id"]
            data = package["data"]
            if data.get("animationType") == "checkboard_flash":
                fb.delete_document("userAnimationPackages", package_id)
                cleared_count += 1
        
        if cleared_count > 0:
            print(f"   - Cleared {cleared_count} existing checkboard_flash packages")
        
        # Create main animation document (lightweight)
        animation_data = {
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": animation_start_time + "Z",
            "users": {
                "user_1_1": {"colors": red_pattern[:2]},  # Just sample data
                "user_1_2": {"colors": blue_pattern[:2]}  # Just sample data
            }
        }
        
        success = fb.set_document("animations", ANIMATION_ID, animation_data)
        if not success:
            print("❌ Failed to set main animation document")
            return
        
        print("📦 Creating individual userAnimationPackages...")
        
        # Create individual userAnimationPackages for each seat
        created_count = 0
        total_seats = 30 * 40  # 30 rows × 40 seats
        
        for row in range(1, 31):  # Rows 1-30
            for seat in range(1, 41):  # Seats 1-40
                user_id = f"user_{row}_{seat}"
                
                # Choose pattern based on odd/even seat
                if seat % 2 == 1:  # Odd seat -> red flash
                    colors = red_pattern
                    color_name = "RED"
                else:  # Even seat -> blue flash
                    colors = blue_pattern
                    color_name = "BLUE"
                
                # Create userAnimationPackage document
                package_data = {
                    "userId": user_id,
                    "animationType": "checkboard_flash",
                    "eventType": "football_stadium",
                    "startTime": animation_start_time,
                    "endTime": (start_time_utc + timedelta(seconds=10)).strftime('%Y-%m-%dT%H:%M:%S'),
                    "frames": [f"color_{color['r']}_{color['g']}_{color['b']}" for color in colors],
                    "frameRate": 2,
                    "frameCount": 20,
                    "isActive": True,
                    "isExpired": False,
                    "animationId": ANIMATION_ID,
                    "duration": 10.0,
                    "pattern": "checkboard_flash",
                    "createdAt": datetime.now(timezone.utc).isoformat()
                }
                
                # Use user_id as document ID for easy lookup
                success = fb.set_document("userAnimationPackages", user_id, package_data)
                if success:
                    created_count += 1
                    
                    # Progress indicator
                    if created_count % 100 == 0:
                        print(f"   - Created {created_count}/{total_seats} packages...")
                
                # Small delay to avoid rate limiting
                if created_count % 50 == 0:
                    time.sleep(0.1)
        
        # Create animation config
        animation_config = {
            "animationStartTime": animation_start_time,
            "eventType": "football_stadium",
            "animationType": "checkboard_flash",
            "animationData": {
                "animationId": "checkboard_flash",
                "frameRate": 2,
                "frameCount": 20,
                "type": "color_animation",
                "users": {}  # Users are in userAnimationPackages
            },
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        config_id = fb.add_document("animation_configs", animation_config)
        if not config_id:
            print("❌ Failed to add animation config")
            return
        
        print(f"✅ Checkboard flash animation deployed successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Event Type: football_stadium")
        print(f"   - Start Time: {animation_start_time}Z")
        print(f"   - UserAnimationPackages created: {created_count}")
        print(f"   - Coverage: 30 rows × 40 seats = {total_seats} seats")
        
        print(f"\n🎨 Checkboard Pattern:")
        print(f"   - ODD seats (1, 3, 5, etc.): RED flash alternating with BLACK")
        print(f"   - EVEN seats (2, 4, 6, etc.): BLUE flash alternating with BLACK")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print(f"   Test with any seat from row 1-30, seat 1-40")
        
        # Verify specific test users
        test_users = ["user_2_4", "user_4_1", "user_1_1", "user_30_40"]
        print(f"\n✅ Test users verification:")
        for user_id in test_users:
            package = fb.get_document("userAnimationPackages", user_id)
            if package:
                row, seat = user_id.split("_")[1], user_id.split("_")[2]
                color = "RED" if int(seat) % 2 == 1 else "BLUE"
                print(f"   - {user_id}: {color} (✅ package exists)")
            else:
                print(f"   - {user_id}: ❌ package missing")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    deploy_proper_checkboard_flash()