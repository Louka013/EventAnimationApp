#!/usr/bin/env python3
"""
Debug script to check which users are covered by checkboard_flash animation
"""

from firebase_web_admin import FirebaseWebClient

def debug_user_coverage():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Checking checkboard_flash animation user coverage...")
        
        # Get checkboard_flash animation
        animation_doc = fb.get_document("animations", "checkboard_flash")
        
        if not animation_doc:
            print("❌ No checkboard_flash animation found!")
            return
        
        users = animation_doc.get("users", {})
        print(f"📊 Found {len(users)} users in checkboard_flash animation:")
        
        # Parse and sort users
        user_positions = []
        for user_id in users.keys():
            if user_id.startswith("user_"):
                parts = user_id.split("_")
                if len(parts) == 3:
                    row = int(parts[1])
                    seat = int(parts[2])
                    user_positions.append((row, seat, user_id))
        
        user_positions.sort()
        
        # Display coverage
        print("\n📍 User coverage:")
        current_row = 0
        for row, seat, user_id in user_positions:
            if row != current_row:
                if current_row > 0:
                    print()
                print(f"Row {row}:", end=" ")
                current_row = row
            
            # Check if odd or even seat
            color = "RED" if seat % 2 == 1 else "BLUE"
            print(f"{user_id}({color})", end=" ")
        
        print("\n")
        
        # Check ranges
        rows = [pos[0] for pos in user_positions]
        seats = [pos[1] for pos in user_positions]
        
        print(f"📊 Coverage summary:")
        print(f"   - Rows: {min(rows)} to {max(rows)}")
        print(f"   - Seats: {min(seats)} to {max(seats)}")
        print(f"   - Total users: {len(user_positions)}")
        
        # Check if user_4_1 exists
        if "user_4_1" in users:
            print(f"✅ user_4_1 EXISTS in animation data")
        else:
            print(f"❌ user_4_1 NOT FOUND in animation data")
            print(f"   Missing users in row 4:")
            for seat in range(1, 11):
                user_id = f"user_4_{seat}"
                if user_id not in users:
                    print(f"   - {user_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_user_coverage()