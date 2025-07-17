#!/usr/bin/env python3
"""
Script to verify that all users from 1-10 for both rows and seats exist in the system.
"""

from firebase_web_admin import FirebaseWebClient
import re

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

def get_all_required_users():
    """Get set of all required users (1-10 for both rows and seats)"""
    required_users = set()
    for row in range(1, 11):
        for seat in range(1, 11):
            required_users.add(f"user_{row}_{seat}")
    return required_users

def verify_users_grid():
    """Verify that all users from 1-10 exist in the system"""
    print("🔍 Verifying users grid (1-10 for both rows and seats)...")
    print("=" * 60)
    
    # Initialize Firebase Web Client
    client = FirebaseWebClient()
    
    # Get all required users
    required_users = get_all_required_users()
    print(f"📊 Total users required: {len(required_users)}")
    
    # Check userAnimationPackages collection
    print("\n📋 Checking userAnimationPackages collection...")
    packages_users = set()
    try:
        packages = client.list_documents('userAnimationPackages')
        for doc in packages:
            data = doc['data']
            user_id = data.get('userId', '')
            if is_valid_user(user_id):
                packages_users.add(user_id)
        print(f"  ✅ Found {len(packages_users)} valid users in userAnimationPackages")
    except Exception as e:
        print(f"  ❌ Error checking userAnimationPackages: {e}")
    
    # Check animations collection
    print("\n📋 Checking animations collection...")
    animations_users = set()
    try:
        animations = client.list_documents('animations')
        for doc in animations:
            animation_data = doc['data']
            if 'users' in animation_data:
                for user_id in animation_data['users'].keys():
                    if is_valid_user(user_id):
                        animations_users.add(user_id)
        print(f"  ✅ Found {len(animations_users)} valid users in animations")
    except Exception as e:
        print(f"  ❌ Error checking animations: {e}")
    
    # Check seatSelections collection
    print("\n📋 Checking seatSelections collection...")
    seats_users = set()
    try:
        selections = client.list_documents('seatSelections')
        for doc in selections:
            data = doc['data']
            rang = data.get('rang', 0)
            numero_de_place = data.get('numeroDePlace', 0)
            if 1 <= rang <= 10 and 1 <= numero_de_place <= 10:
                user_id = f"user_{rang}_{numero_de_place}"
                seats_users.add(user_id)
        print(f"  ✅ Found {len(seats_users)} valid users in seatSelections")
    except Exception as e:
        print(f"  ❌ Error checking seatSelections: {e}")
    
    # Combine all users
    all_existing_users = packages_users | animations_users | seats_users
    
    # Check coverage
    print("\n📊 COVERAGE ANALYSIS:")
    print(f"  • Required users: {len(required_users)}")
    print(f"  • UserAnimationPackages: {len(packages_users)}")
    print(f"  • Animations: {len(animations_users)}")
    print(f"  • SeatSelections: {len(seats_users)}")
    print(f"  • Total unique users: {len(all_existing_users)}")
    
    # Find missing users
    missing_users = required_users - all_existing_users
    print(f"  • Missing users: {len(missing_users)}")
    
    if missing_users:
        print(f"\n❌ MISSING USERS:")
        missing_sorted = sorted(missing_users, key=lambda x: (int(x.split('_')[1]), int(x.split('_')[2])))
        for i, user in enumerate(missing_sorted):
            if i % 10 == 0:
                print(f"  Row {i//10 + 1}: ", end="")
            print(f"{user} ", end="")
            if (i + 1) % 10 == 0:
                print()
    else:
        print("\n✅ ALL USERS PRESENT!")
    
    # Create a visual grid
    print("\n📊 VISUAL GRID (userAnimationPackages):")
    print("    ", end="")
    for seat in range(1, 11):
        print(f"S{seat:2d} ", end="")
    print()
    
    for row in range(1, 11):
        print(f"R{row:2d} ", end="")
        for seat in range(1, 11):
            user_id = f"user_{row}_{seat}"
            if user_id in packages_users:
                print(" ✅ ", end="")
            else:
                print(" ❌ ", end="")
        print()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY:")
    
    if len(packages_users) == 100:
        print("  🎉 PERFECT! All 100 users exist in userAnimationPackages!")
    else:
        print(f"  ⚠️  Only {len(packages_users)}/100 users in userAnimationPackages")
    
    if len(animations_users) > 0:
        print(f"  ℹ️  {len(animations_users)} users have animation data")
    
    if len(seats_users) > 0:
        print(f"  ℹ️  {len(seats_users)} users have seat selections")
    
    if not missing_users:
        print("  ✅ Users collection is complete and ready for use!")
    else:
        print("  ❌ Some users are still missing - manual review needed")

if __name__ == "__main__":
    verify_users_grid()