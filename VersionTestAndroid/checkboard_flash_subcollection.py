#!/usr/bin/env python3
"""
Deploy checkboard_flash animation using subcollections (Android app compatible format).
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timedelta

def deploy_checkboard_flash_subcollection():
    """
    Deploy checkboard_flash animation with users in subcollections
    """
    print("🎨 Deploying checkboard_flash animation (SUBCOLLECTION METHOD)")
    
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
    red_color = {"r": 255, "g": 0, "b": 0}    # Red
    blue_color = {"r": 0, "g": 0, "b": 255}   # Blue
    black_color = {"r": 0, "g": 0, "b": 0}    # Black
    
    # Create the flashing patterns (20 frames, 2 fps = 10 seconds)
    red_pattern = []
    blue_pattern = []
    
    for i in range(20):
        if i % 2 == 0:  # Even frames -> colored
            red_pattern.append(red_color)
            blue_pattern.append(blue_color)
        else:  # Odd frames -> black
            red_pattern.append(black_color)
            blue_pattern.append(black_color)
    
    # Create main animation document (without nested users)
    animation_data = {
        "animationId": "checkboard_flash",
        "frameRate": 2,
        "frameCount": 20,
        "type": "color_animation",
        "startTime": start_time_str,
        "duration": 10.0
    }
    
    # Save main animation document
    print("💾 Saving main animation document...")
    try:
        fb.set_document('animations', 'checkboard_flash', animation_data)
        print("✅ Main animation document saved successfully!")
    except Exception as e:
        print(f"❌ Error saving main animation document: {e}")
        return
    
    # Create subcollections for users
    print("👥 Creating user subcollections...")
    created_count = 0
    
    for row in range(1, 11):  # Rows 1-10
        for seat in range(1, 11):  # Seats 1-10
            user_id = f"user_{row}_{seat}"
            
            # Determine color pattern based on seat number
            if seat % 2 == 1:  # Odd seat -> red pattern
                user_data = {
                    "colors": red_pattern,
                    "startTime": start_time_str,
                    "frameCount": 20
                }
            else:  # Even seat -> blue pattern
                user_data = {
                    "colors": blue_pattern,
                    "startTime": start_time_str,
                    "frameCount": 20
                }
            
            # Create subcollection document
            try:
                subcollection_path = f"animations/checkboard_flash/users/{user_id}"
                success = fb.set_document_at_path(subcollection_path, user_data)
                
                if success:
                    created_count += 1
                    color = "RED" if seat % 2 == 1 else "BLUE"
                    print(f"    ✅ Created {user_id}: {color}")
                else:
                    print(f"    ❌ Failed to create {user_id}")
                    
            except Exception as e:
                print(f"    ❌ Error creating {user_id}: {e}")
    
    print(f"📊 Created {created_count} user subcollections")
    
    # Create animation config
    config_data = {
        "animationStartTime": start_time_str[:-1],  # Remove Z for config
        "eventType": "football_stadium",
        "animationType": "checkboard_flash",
        "animationData": animation_data,
        "status": "active",
        "createdAt": now.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    try:
        config_id = fb.add_document('animation_configs', config_data)
        print("✅ Checkboard flash animation deployed successfully!")
        print(f"   - Config ID: {config_id}")
        print(f"   - Animation ID: checkboard_flash")
        print(f"   - Event Type: football_stadium")
        print(f"   - Start Time: {start_time_str}")
        print(f"   - User subcollections created: {created_count}")
        print(f"   - Coverage: 10 rows × 10 seats = 100 seats")
        
        print("\n🎨 Checkboard Pattern:")
        print("   - ODD seats (1, 3, 5, etc.): RED flash alternating with BLACK")
        print("   - EVEN seats (2, 4, 6, etc.): BLUE flash alternating with BLACK")
        
        print(f"\n🔥 Animation will start in 2 minutes!")
        print("   Test with seats from row 1-10, seat 1-10")
        
        print("\n📱 Android App Compatible:")
        print("   - User data stored in subcollections")
        print("   - Path: animations/checkboard_flash/users/{userId}")
        print("   - Should resolve 'Utilisateur non trouvé' error")
        
    except Exception as e:
        print(f"❌ Error creating config: {e}")

if __name__ == "__main__":
    deploy_checkboard_flash_subcollection()