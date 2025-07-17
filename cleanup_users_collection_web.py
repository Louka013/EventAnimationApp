#!/usr/bin/env python3
"""
Web-based script to clean up users collection using Firebase Web SDK.
No service account required - uses same credentials as web interface.
"""

import requests
import json
import re
from datetime import datetime
from firebase_web_admin import FirebaseWebClient

def parse_user_id(user_id):
    """Parse user ID to extract row and seat numbers"""
    match = re.match(r'user_(\d+)_(\d+)', user_id)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def is_valid_user(user_id):
    """Check if user ID is in valid range (1-10 for both row and seat)"""
    row, seat = parse_user_id(user_id)
    if row is None or seat is None:
        return False
    return 1 <= row <= 10 and 1 <= seat <= 10

def cleanup_user_animation_packages(client):
    """Clean up userAnimationPackages collection"""
    print("\n🧹 Cleaning up userAnimationPackages collection...")
    
    try:
        # Get all documents
        packages = client.list_documents('userAnimationPackages')
        
        removed_count = 0
        kept_count = 0
        
        for doc in packages:
            doc_id = doc['id']
            data = doc['data']
            user_id = data.get('userId', '')
            
            if not is_valid_user(user_id):
                print(f"  ❌ Removing invalid user: {user_id}")
                client.delete_document('userAnimationPackages', doc_id)
                removed_count += 1
            else:
                print(f"  ✅ Keeping valid user: {user_id}")
                kept_count += 1
        
        print(f"  📊 Removed {removed_count} invalid users, kept {kept_count} valid users")
        return removed_count, kept_count
    
    except Exception as e:
        print(f"  ❌ Error cleaning userAnimationPackages: {e}")
        return 0, 0

def cleanup_seat_selections(client):
    """Clean up seatSelections collection"""
    print("\n🧹 Cleaning up seatSelections collection...")
    
    try:
        # Get all documents
        selections = client.list_documents('seatSelections')
        
        removed_count = 0
        kept_count = 0
        
        for doc in selections:
            doc_id = doc['id']
            data = doc['data']
            rang = data.get('rang', 0)
            numero_de_place = data.get('numeroDePlace', 0)
            
            if not (1 <= rang <= 10 and 1 <= numero_de_place <= 10):
                print(f"  ❌ Removing invalid seat selection: row={rang}, seat={numero_de_place}")
                client.delete_document('seatSelections', doc_id)
                removed_count += 1
            else:
                print(f"  ✅ Keeping valid seat selection: row={rang}, seat={numero_de_place}")
                kept_count += 1
        
        print(f"  📊 Removed {removed_count} invalid selections, kept {kept_count} valid selections")
        return removed_count, kept_count
    
    except Exception as e:
        print(f"  ❌ Error cleaning seatSelections: {e}")
        return 0, 0

def cleanup_animations_users(client):
    """Clean up users in animations collection"""
    print("\n🧹 Cleaning up users in animations collection...")
    
    try:
        # Get all animations
        animations = client.list_documents('animations')
        
        total_removed = 0
        total_kept = 0
        
        for doc in animations:
            animation_id = doc['id']
            animation_data = doc['data']
            
            print(f"  🎬 Processing animation: {animation_id}")
            
            # Check if animation has users data
            if 'users' in animation_data:
                users_data = animation_data['users']
                valid_users = {}
                removed_count = 0
                
                for user_id, user_data in users_data.items():
                    if is_valid_user(user_id):
                        valid_users[user_id] = user_data
                        total_kept += 1
                    else:
                        print(f"    ❌ Removing invalid user: {user_id}")
                        removed_count += 1
                        total_removed += 1
                
                # Update animation with cleaned users data
                if removed_count > 0:
                    animation_data['users'] = valid_users
                    client.update_document('animations', animation_id, animation_data)
                    print(f"    📝 Updated animation {animation_id}: removed {removed_count} invalid users")
        
        print(f"  📊 Total: removed {total_removed} invalid users, kept {total_kept} valid users")
        return total_removed, total_kept
    
    except Exception as e:
        print(f"  ❌ Error cleaning animations: {e}")
        return 0, 0

def get_existing_users(client):
    """Get list of existing valid users from all collections"""
    existing_users = set()
    
    try:
        # Check userAnimationPackages
        packages = client.list_documents('userAnimationPackages')
        for doc in packages:
            data = doc['data']
            user_id = data.get('userId', '')
            if is_valid_user(user_id):
                existing_users.add(user_id)
        
        # Check animations collection
        animations = client.list_documents('animations')
        for doc in animations:
            animation_data = doc['data']
            if 'users' in animation_data:
                for user_id in animation_data['users'].keys():
                    if is_valid_user(user_id):
                        existing_users.add(user_id)
    
    except Exception as e:
        print(f"  ❌ Error getting existing users: {e}")
    
    return existing_users

def get_all_required_users():
    """Get set of all required users (1-10 for both rows and seats)"""
    required_users = set()
    for row in range(1, 11):
        for seat in range(1, 11):
            required_users.add(f"user_{row}_{seat}")
    return required_users

def create_missing_users(client, missing_users):
    """Create basic entries for missing users"""
    print(f"\n➕ Creating {len(missing_users)} missing users...")
    
    try:
        # Create basic animation package for each missing user
        for user_id in missing_users:
            row, seat = parse_user_id(user_id)
            
            # Create a basic animation package
            user_package = {
                'userId': user_id,
                'animationType': 'default',
                'eventType': 'football_stadium',
                'startTime': datetime.now().isoformat(),
                'endTime': datetime.now().isoformat(),
                'frames': ['color_0_0_0'],  # Default black frame
                'frameRate': 1,
                'frameCount': 1,
                'isActive': False,
                'isExpired': False,
                'animationId': 'default',
                'duration': 1.0,
                'pattern': 'default',
                'createdAt': datetime.now().isoformat(),
                'row': row,
                'seat': seat
            }
            
            # Add to userAnimationPackages collection
            client.add_document('userAnimationPackages', user_package)
            print(f"  ✅ Created user package for {user_id}")
        
        print(f"  📊 Created {len(missing_users)} missing user packages")
    
    except Exception as e:
        print(f"  ❌ Error creating missing users: {e}")

def main():
    """Main cleanup function"""
    print("🚀 Starting users collection cleanup (Web SDK)...")
    print("=" * 50)
    
    # Initialize Firebase Web Client
    client = FirebaseWebClient()
    
    # Step 1: Clean up existing collections
    print("\n📋 STEP 1: Cleaning up existing collections")
    packages_removed, packages_kept = cleanup_user_animation_packages(client)
    selections_removed, selections_kept = cleanup_seat_selections(client)
    animations_removed, animations_kept = cleanup_animations_users(client)
    
    # Step 2: Check for missing users
    print("\n📋 STEP 2: Checking for missing users")
    existing_users = get_existing_users(client)
    required_users = get_all_required_users()
    missing_users = required_users - existing_users
    
    print(f"  📊 Required users: {len(required_users)}")
    print(f"  📊 Existing users: {len(existing_users)}")
    print(f"  📊 Missing users: {len(missing_users)}")
    
    if missing_users:
        print(f"  ⚠️  Missing users: {sorted(list(missing_users))}")
        create_missing_users(client, missing_users)
    else:
        print("  ✅ All required users exist")
    
    # Step 3: Final verification
    print("\n📋 STEP 3: Final verification")
    final_existing = get_existing_users(client)
    final_missing = required_users - final_existing
    
    print(f"  📊 Final user count: {len(final_existing)}")
    print(f"  📊 Still missing: {len(final_missing)}")
    
    if not final_missing:
        print("  ✅ SUCCESS: All users 1-10 for rows and seats are now present!")
    else:
        print(f"  ❌ Still missing: {sorted(list(final_missing))}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CLEANUP SUMMARY:")
    print(f"  • UserAnimationPackages: removed {packages_removed}, kept {packages_kept}")
    print(f"  • SeatSelections: removed {selections_removed}, kept {selections_kept}")
    print(f"  • Animation Users: removed {animations_removed}, kept {animations_kept}")
    print(f"  • Missing users created: {len(missing_users)}")
    print(f"  • Final user count: {len(final_existing)}/100")
    
    if len(final_existing) == 100 and not final_missing:
        print("  🎉 PERFECT! Users collection is now clean and complete!")
    else:
        print("  ⚠️  Manual review may be needed.")

if __name__ == "__main__":
    main()