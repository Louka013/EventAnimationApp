#!/usr/bin/env python3
"""
Script to verify both checkboard_flash and blue_black_flash animations have complete user coverage.
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

def check_animation_coverage(fb, animation_id):
    """Check user coverage for a specific animation"""
    try:
        animation = fb.get_document('animations', animation_id)
        if not animation:
            return set(), f"Animation {animation_id} not found"
        
        users = animation.get('users', {})
        valid_users = set()
        
        for user_id in users.keys():
            if is_valid_user(user_id):
                valid_users.add(user_id)
        
        return valid_users, None
    except Exception as e:
        return set(), f"Error checking {animation_id}: {e}"

def verify_both_animations():
    """Verify both animations have complete user coverage"""
    print("🔍 Verifying both animations user coverage...")
    print("=" * 70)
    
    # Initialize Firebase Web Client
    fb = FirebaseWebClient()
    
    # Get all required users
    required_users = get_all_required_users()
    print(f"📊 Total users required: {len(required_users)}")
    
    # Check checkboard_flash
    print("\n📋 Checking checkboard_flash animation...")
    checkboard_users, checkboard_error = check_animation_coverage(fb, 'checkboard_flash')
    if checkboard_error:
        print(f"  ❌ {checkboard_error}")
    else:
        print(f"  ✅ Found {len(checkboard_users)} valid users")
        missing_checkboard = required_users - checkboard_users
        if missing_checkboard:
            print(f"  ⚠️  Missing {len(missing_checkboard)} users")
        else:
            print("  🎉 Complete coverage!")
    
    # Check blue_black_flash
    print("\n📋 Checking blue_black_flash animation...")
    blue_black_users, blue_black_error = check_animation_coverage(fb, 'blue_black_flash')
    if blue_black_error:
        print(f"  ❌ {blue_black_error}")
    else:
        print(f"  ✅ Found {len(blue_black_users)} valid users")
        missing_blue_black = required_users - blue_black_users
        if missing_blue_black:
            print(f"  ⚠️  Missing {len(missing_blue_black)} users")
        else:
            print("  🎉 Complete coverage!")
    
    # Compare coverage
    print("\n📊 COVERAGE COMPARISON:")
    print(f"  • Required users: {len(required_users)}")
    print(f"  • Checkboard Flash: {len(checkboard_users)}")
    print(f"  • Blue Black Flash: {len(blue_black_users)}")
    
    # Check for differences
    if checkboard_users and blue_black_users:
        common_users = checkboard_users & blue_black_users
        checkboard_only = checkboard_users - blue_black_users
        blue_black_only = blue_black_users - checkboard_users
        
        print(f"  • Common users: {len(common_users)}")
        print(f"  • Checkboard only: {len(checkboard_only)}")
        print(f"  • Blue-Black only: {len(blue_black_only)}")
        
        if checkboard_only:
            print(f"    - Checkboard exclusive: {sorted(list(checkboard_only))[:5]}...")
        if blue_black_only:
            print(f"    - Blue-Black exclusive: {sorted(list(blue_black_only))[:5]}...")
    
    # Test specific users
    print("\n🧪 Testing specific users:")
    test_users = ['user_1_1', 'user_9_9', 'user_5_5', 'user_10_10']
    
    for user_id in test_users:
        row, seat = parse_user_id(user_id)
        checkboard_present = user_id in checkboard_users
        blue_black_present = user_id in blue_black_users
        
        print(f"  {user_id} (row {row}, seat {seat}):")
        
        if checkboard_present:
            # Determine expected color for checkboard
            if seat % 2 == 1:  # Odd seat
                expected_color = "RED"
            else:  # Even seat
                expected_color = "BLUE"
            print(f"    - Checkboard: ✅ {expected_color}")
        else:
            print(f"    - Checkboard: ❌ missing")
        
        if blue_black_present:
            print(f"    - Blue-Black: ✅ BLUE")
        else:
            print(f"    - Blue-Black: ❌ missing")
    
    # Overall status
    print("\n" + "=" * 70)
    print("📊 OVERALL STATUS:")
    
    checkboard_complete = len(checkboard_users) == 100
    blue_black_complete = len(blue_black_users) == 100
    
    if checkboard_complete and blue_black_complete:
        print("  🎉 SUCCESS: Both animations have complete user coverage!")
        print("  ✅ All 100 users (1-10 rows × 1-10 seats) are available")
        print("  ✅ System is ready for synchronized stadium animations")
    else:
        print("  ⚠️  INCOMPLETE: Some users are missing")
        if not checkboard_complete:
            print(f"    - Checkboard Flash: {len(checkboard_users)}/100 users")
        if not blue_black_complete:
            print(f"    - Blue Black Flash: {len(blue_black_users)}/100 users")
    
    return checkboard_complete and blue_black_complete

if __name__ == "__main__":
    verify_both_animations()