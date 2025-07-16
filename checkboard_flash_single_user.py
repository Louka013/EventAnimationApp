#!/usr/bin/env python3
"""
Deploy checkboard_flash animation with single user (same as blue_black_flash)
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta, timezone

ANIMATION_ID = "checkboard_flash"

def deploy_single_user_checkboard_flash():
    """
    Deploy checkboard_flash with same user coverage as blue_black_flash
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        # Set animation time to 2 minutes from now in UTC
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc + timedelta(minutes=2)
        animation_start_time = start_time_utc.strftime('%Y-%m-%dT%H:%M:%S')
        
        print(f"🎨 Deploying checkboard_flash animation (SINGLE USER)")
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
        
        # Create users dictionary with only user_1_1 (same as blue_black_flash)
        # user_1_1 is seat 1 (odd), so it gets red pattern
        users = {
            "user_1_1": {
                "colors": red_pattern  # Red pattern for odd seat
            }
        }
        
        print(f"📊 Created {len(users)} users (same as blue_black_flash)")
        
        # Create main animation document
        animation_data = {
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": animation_start_time + "Z",
            "users": users
        }
        
        print("💾 Saving animation data...")
        success = fb.set_document("animations", ANIMATION_ID, animation_data)
        if not success:
            print("❌ Failed to set animation document")
            return
        
        print("✅ Animation data saved successfully!")
        
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
                "users": users
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
        print(f"   - Users created: {len(users)}")
        print(f"   - Coverage: SAME AS BLUE_BLACK_FLASH")
        
        print(f"\n🎨 Pattern:")
        print(f"   - user_1_1 (odd seat): RED flash alternating with BLACK")
        print(f"   - (Same user coverage as blue_black_flash)")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print(f"   Test with: row 1, seat 1 (same as blue_black_flash)")
        
        # Verify the data was saved correctly
        print(f"\n🔍 Verifying animation data...")
        saved_animation = fb.get_document("animations", ANIMATION_ID)
        if saved_animation:
            saved_users = saved_animation.get("users", {})
            print(f"✅ Verified: {len(saved_users)} users saved")
            
            # Check user_1_1
            if "user_1_1" in saved_users:
                user_data = saved_users["user_1_1"]
                colors = user_data.get("colors", [])
                print(f"   - user_1_1: {len(colors)} colors")
                if colors:
                    print(f"   - first color: {colors[0]} (should be RED)")
                    print(f"   - second color: {colors[1]} (should be BLACK)")
            else:
                print(f"   - user_1_1: ❌ not found")
        else:
            print("❌ Animation data not found!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_single_user_checkboard_flash()