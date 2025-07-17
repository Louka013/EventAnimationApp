#!/usr/bin/env python3
"""
Fix user data structure to match Android app expectations.
Convert nested user data to subcollections.
"""

from firebase_web_admin import FirebaseWebClient

def fix_user_data_structure():
    """
    Fix user data structure for both animations
    """
    print("🔧 Fixing user data structure for Android app compatibility...")
    print("=" * 60)
    
    # Initialize Firebase
    fb = FirebaseWebClient()
    
    # Animation IDs to fix
    animation_ids = ['checkboard_flash', 'blue_black_flash']
    
    for animation_id in animation_ids:
        print(f"\n🎨 Processing {animation_id}...")
        
        try:
            # Get current animation data
            animation_data = fb.get_document('animations', animation_id)
            if not animation_data:
                print(f"  ❌ Animation {animation_id} not found")
                continue
            
            # Extract users data
            users_data = animation_data.get('users', {})
            if not users_data:
                print(f"  ❌ No users data found in {animation_id}")
                continue
            
            print(f"  📊 Found {len(users_data)} users in nested structure")
            
            # Create subcollections for each user
            created_count = 0
            for user_id, user_data in users_data.items():
                try:
                    # Create subcollection document
                    subcollection_path = f"animations/{animation_id}/users/{user_id}"
                    
                    # Set the user data in subcollection
                    success = fb.set_document_at_path(subcollection_path, user_data)
                    if success:
                        created_count += 1
                        print(f"    ✅ Created subcollection for {user_id}")
                    else:
                        print(f"    ❌ Failed to create subcollection for {user_id}")
                        
                except Exception as e:
                    print(f"    ❌ Error creating subcollection for {user_id}: {e}")
            
            print(f"  📊 Created {created_count} user subcollections")
            
            # Update main animation document (remove nested users, keep metadata)
            updated_animation_data = {
                'animationId': animation_data.get('animationId'),
                'frameRate': animation_data.get('frameRate'),
                'frameCount': animation_data.get('frameCount'),
                'type': animation_data.get('type'),
                'startTime': animation_data.get('startTime'),
                'duration': animation_data.get('duration', 10.0)
            }
            
            # Update the main animation document
            fb.set_document('animations', animation_id, updated_animation_data)
            print(f"  ✅ Updated main animation document (removed nested users)")
            
        except Exception as e:
            print(f"  ❌ Error processing {animation_id}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("  • Converted nested user data to subcollections")
    print("  • Android app now expects: animations/{id}/users/{userId}")
    print("  • Main animation documents cleaned up")
    print("  ✅ Ready for Android app testing!")

def verify_subcollection_structure():
    """
    Verify that the subcollection structure is correct
    """
    print("\n🔍 Verifying subcollection structure...")
    
    fb = FirebaseWebClient()
    animation_ids = ['checkboard_flash', 'blue_black_flash']
    
    for animation_id in animation_ids:
        print(f"\n📋 Checking {animation_id}...")
        
        try:
            # Check main animation document
            animation_data = fb.get_document('animations', animation_id)
            if animation_data:
                print(f"  ✅ Main document exists")
                print(f"    - animationId: {animation_data.get('animationId')}")
                print(f"    - frameRate: {animation_data.get('frameRate')}")
                print(f"    - frameCount: {animation_data.get('frameCount')}")
                print(f"    - type: {animation_data.get('type')}")
                print(f"    - startTime: {animation_data.get('startTime')}")
                
                # Check if nested users still exist (should be removed)
                if 'users' in animation_data:
                    print(f"    ⚠️  Still has nested users: {len(animation_data['users'])}")
                else:
                    print(f"    ✅ No nested users (correctly moved to subcollections)")
            else:
                print(f"  ❌ Main document missing")
            
            # Try to check subcollections (Note: subcollection listing is limited with REST API)
            print(f"  ℹ️  Subcollections created at: animations/{animation_id}/users/{{userId}}")
            
        except Exception as e:
            print(f"  ❌ Error checking {animation_id}: {e}")

if __name__ == "__main__":
    fix_user_data_structure()
    verify_subcollection_structure()