#!/usr/bin/env python3
"""
Deploy blue_black_flash animation using the working method (web SDK).
Creates a blue and black flash animation for all users in a 10x10 grid.
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta

def deploy_blue_black_flash():
    """
    Deploy blue_black_flash animation with all users
    """
    print("🎨 Deploying blue_black_flash animation (WORKING METHOD)")
    
    # Calculate start time (2 minutes from now)
    now = datetime.utcnow()
    start_time = now + timedelta(minutes=2)
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    print(f"🌍 Current UTC time: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"⏰ Animation start time: {start_time_str}")
    
    # Initialize Firebase
    fb = FirebaseWebClient()
    
    # Deactivate existing animations
    print("🔄 Deactivating existing animations...")
    try:
        configs = fb.list_documents('animation_configs')
        for doc in configs:
            config_id = doc['id']
            config_data = doc['data']
            if config_data.get('status') == 'active':
                config_data['status'] = 'inactive'
                fb.update_document('animation_configs', config_id, config_data)
                print(f"   - Deactivated config: {config_id}")
    except Exception as e:
        print(f"   - Error deactivating configs: {e}")
    
    # Create color patterns
    # Blue and black flash - all users get the same pattern
    blue_color = {"r": 0, "g": 0, "b": 255}  # Blue
    black_color = {"r": 0, "g": 0, "b": 0}   # Black
    
    # Create the flashing pattern (20 frames, 2 fps = 10 seconds)
    blue_black_pattern = []
    for i in range(20):
        if i % 2 == 0:  # Even frames (0, 2, 4, 6, 8, 10, 12, 14, 16, 18) -> blue
            blue_black_pattern.append(blue_color)
        else:  # Odd frames (1, 3, 5, 7, 9, 11, 13, 15, 17, 19) -> black
            blue_black_pattern.append(black_color)
    
    # Generate users for a 10x10 grid
    users = {}
    
    for row in range(1, 11):  # Rows 1-10
        for seat in range(1, 11):  # Seats 1-10
            user_id = f"user_{row}_{seat}"
            
            # All users get the same blue/black pattern
            users[user_id] = {
                "colors": blue_black_pattern,
                "startTime": start_time_str,
                "frameCount": 20
            }
    
    print(f"📊 Created {len(users)} users for 10x10 grid")
    
    # Create animation data
    animation_data = {
        "animationId": "blue_black_flash",
        "frameRate": 2,
        "frameCount": 20,
        "type": "color_animation",
        "startTime": start_time_str,
        "duration": 10.0,
        "users": users
    }
    
    # Save animation data
    print("💾 Saving animation data...")
    try:
        fb.set_document('animations', 'blue_black_flash', animation_data)
        print("✅ Animation data saved successfully!")
    except Exception as e:
        print(f"❌ Error saving animation data: {e}")
        return
    
    # Create animation config
    config_data = {
        "animationStartTime": start_time_str[:-1],  # Remove Z for config
        "eventType": "football_stadium",
        "animationType": "blue_black_flash",
        "animationData": animation_data,
        "status": "active",
        "createdAt": now.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    try:
        config_id = fb.add_document('animation_configs', config_data)
        print("✅ Blue black flash animation deployed successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: blue_black_flash")
        print(f"   - Event Type: football_stadium")
        print(f"   - Start Time: {start_time_str}")
        print(f"   - Users created: {len(users)}")
        print(f"   - Coverage: 10 rows × 10 seats = 100 seats")
        
        print("\n🎨 Blue Black Flash Pattern:")
        print("   - ALL users: BLUE flash alternating with BLACK")
        print("   - Frame sequence: BLUE → BLACK → BLUE → BLACK → ...")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print("   Test with seats from row 1-10, seat 1-10")
        
        # Verify some users
        print("\n🔍 Verifying animation data...")
        try:
            saved_animation = fb.get_document('animations', 'blue_black_flash')
            if saved_animation and 'users' in saved_animation:
                saved_users = saved_animation['users']
                print(f"✅ Verified: {len(saved_users)} users saved")
                
                # Test a few users
                test_users = ['user_2_4', 'user_4_1', 'user_1_1', 'user_10_10']
                for user_id in test_users:
                    if user_id in saved_users:
                        print(f"   - {user_id}: BLUE (✅ found)")
                    else:
                        print(f"   - {user_id}: ❌ missing")
            else:
                print("❌ Failed to verify animation data")
        except Exception as e:
            print(f"❌ Error verifying: {e}")
            
    except Exception as e:
        print(f"❌ Error creating config: {e}")

if __name__ == "__main__":
    deploy_blue_black_flash()