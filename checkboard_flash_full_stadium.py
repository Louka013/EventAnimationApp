#!/usr/bin/env python3
"""
Deploy checkboard_flash animation with 10x10 COVERAGE using subcollections
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta, timezone
import time

ANIMATION_ID = "checkboard_flash"

def deploy_full_stadium_checkboard_flash():
    """
    Deploy checkboard_flash with 10x10 coverage using subcollections
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        # Set animation time to 3 minutes from now in UTC
        now_utc = datetime.now(timezone.utc)
        start_time_utc = now_utc + timedelta(minutes=3)
        animation_start_time = start_time_utc.strftime('%Y-%m-%dT%H:%M:%S')
        
        print(f"🎨 Deploying checkboard_flash animation (10x10 COVERAGE)")
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
        
        # Create main animation document (lightweight - no user data)
        animation_data = {
            "animationId": ANIMATION_ID,
            "frameRate": 2,
            "frameCount": 20,
            "type": "color_animation",
            "startTime": animation_start_time + "Z",
            "users": {}  # Empty - users will be in subcollection
        }
        
        print("💾 Saving main animation document...")
        success = fb.set_document("animations", ANIMATION_ID, animation_data)
        if not success:
            print("❌ Failed to set main animation document")
            return
        
        print("📦 Creating user subcollection documents...")
        
        # Create individual user documents in subcollection
        created_count = 0
        total_seats = 10 * 10  # 10 rows × 10 seats
        
        # Process in batches to avoid timeout
        batch_size = 50
        current_batch = 0
        
        for row in range(1, 11):  # Rows 1-10
            for seat in range(1, 11):  # Seats 1-10
                user_id = f"user_{row}_{seat}"
                
                # Choose pattern based on odd/even seat
                if seat % 2 == 1:  # Odd seat -> red flash
                    colors = red_pattern
                    color_name = "RED"
                else:  # Even seat -> blue flash
                    colors = blue_pattern
                    color_name = "BLUE"
                
                # Create user document in subcollection
                user_data = {
                    "colors": colors,
                    "startTime": animation_start_time,
                    "userId": user_id,
                    "pattern": color_name
                }
                
                # Create path: animations/checkboard_flash/users/user_X_Y
                collection_path = f"animations/{ANIMATION_ID}/users"
                
                # Try to create the document
                try:
                    # Use a direct request to create subcollection document
                    url = f"https://firestore.googleapis.com/v1/projects/{fb.project_id}/databases/(default)/documents/{collection_path}/{user_id}"
                    
                    # Convert to Firestore format
                    firestore_data = {
                        "fields": {
                            "colors": {
                                "arrayValue": {
                                    "values": [
                                        {
                                            "mapValue": {
                                                "fields": {
                                                    "r": {"integerValue": str(color["r"])},
                                                    "g": {"integerValue": str(color["g"])},
                                                    "b": {"integerValue": str(color["b"])}
                                                }
                                            }
                                        } for color in colors
                                    ]
                                }
                            },
                            "startTime": {"stringValue": animation_start_time},
                            "userId": {"stringValue": user_id},
                            "pattern": {"stringValue": color_name}
                        }
                    }
                    
                    import requests
                    response = requests.patch(
                        url,
                        params={"key": fb.api_key},
                        json=firestore_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        created_count += 1
                        
                        # Progress indicator
                        if created_count % batch_size == 0:
                            print(f"   - Created {created_count}/{total_seats} users...")
                            current_batch += 1
                    else:
                        print(f"   - Failed to create {user_id}: {response.status_code}")
                        if created_count < 10:  # Show first few errors
                            print(f"     Response: {response.text}")
                
                except Exception as e:
                    print(f"   - Error creating {user_id}: {e}")
                
                # Rate limiting
                if created_count % 10 == 0:
                    time.sleep(0.1)
                
                # Continue for all 100 users (10x10 grid)
        
        print(f"📊 Created {created_count} user documents in subcollection")
        
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
                "users": {}  # Users are in subcollection
            },
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }
        
        config_id = fb.add_document("animation_configs", animation_config)
        if not config_id:
            print("❌ Failed to add animation config")
            return
        
        print(f"✅ Checkboard flash animation (10x10 GRID) deployed successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Event Type: football_stadium")
        print(f"   - Start Time: {animation_start_time}Z")
        print(f"   - User documents created: {created_count}")
        print(f"   - Storage method: Subcollections")
        
        print(f"\n🎨 Checkboard Pattern:")
        print(f"   - ODD seats (1, 3, 5, etc.): RED flash alternating with BLACK")
        print(f"   - EVEN seats (2, 4, 6, etc.): BLUE flash alternating with BLACK")
        print(f"   - Coverage: {created_count} seats")
        
        print(f"\n🔥 Animation will start in 3 minutes!")
        print(f"   Test with any seat that was created")
        
        # Test specific users
        test_users = ["user_1_1", "user_2_4", "user_5_10", "user_10_10"]
        print(f"\n✅ Testing subcollection access:")
        for user_id in test_users:
            try:
                url = f"https://firestore.googleapis.com/v1/projects/{fb.project_id}/databases/(default)/documents/animations/{ANIMATION_ID}/users/{user_id}"
                response = requests.get(url, params={"key": fb.api_key})
                
                if response.status_code == 200:
                    row, seat = user_id.split("_")[1], user_id.split("_")[2]
                    color = "RED" if int(seat) % 2 == 1 else "BLUE"
                    print(f"   - {user_id}: {color} (✅ found in subcollection)")
                else:
                    print(f"   - {user_id}: ❌ not found in subcollection")
            except Exception as e:
                print(f"   - {user_id}: ❌ error checking: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    deploy_full_stadium_checkboard_flash()