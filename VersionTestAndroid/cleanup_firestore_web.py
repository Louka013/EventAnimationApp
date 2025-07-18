#!/usr/bin/env python3
"""
Script to clean up Firestore - uses Firebase Web SDK
No service account needed
"""

from firebase_web_admin import FirebaseWebClient

KEEP_ANIMATION = "blue_black_flash"  # Animation to keep

def cleanup_firestore():
    """
    Clean up Firestore keeping only the specified animation
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        print("🔍 Analyzing animations in Firestore...")
        
        # Get all animations
        animations = fb.list_documents("animations")
        
        animations_found = []
        animations_to_delete = []
        
        for anim in animations:
            animation_id = anim["id"]
            animations_found.append(animation_id)
            
            if animation_id != KEEP_ANIMATION:
                animations_to_delete.append(animation_id)
                print(f"❌ To delete: {animation_id}")
            else:
                print(f"✅ To keep: {animation_id}")
        
        if not animations_found:
            print("ℹ️  No animations found in Firestore")
            return
        
        print(f"\n📊 Summary:")
        print(f"   - Total animations found: {len(animations_found)}")
        print(f"   - Animations to delete: {len(animations_to_delete)}")
        print(f"   - Animations to keep: 1 ({KEEP_ANIMATION})")
        
        if not animations_to_delete:
            print("✅ No animations to delete - Firestore is already clean!")
            return
        
        # Confirm before deletion
        print(f"\n⚠️  Are you sure you want to delete these animations?")
        for anim_id in animations_to_delete:
            print(f"   - {anim_id}")
        
        response = input("\nType 'YES' to confirm deletion: ")
        if response.upper() != 'YES':
            print("❌ Deletion cancelled")
            return
        
        # Delete the animations
        print("\n🗑️  Deleting animations...")
        
        deleted_count = 0
        for animation_id in animations_to_delete:
            try:
                # Delete the main animation document
                success = fb.delete_document("animations", animation_id)
                
                if success:
                    print(f"✅ Deleted: {animation_id}")
                    deleted_count += 1
                else:
                    print(f"❌ Failed to delete: {animation_id}")
                
            except Exception as e:
                print(f"❌ Error deleting {animation_id}: {e}")
        
        print(f"\n🎉 Cleanup completed!")
        print(f"   - Animations deleted: {deleted_count}")
        print(f"   - Animation kept: {KEEP_ANIMATION}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def list_animations():
    """
    List all animations in Firestore
    """
    try:
        # Initialize Firebase Web client
        fb = FirebaseWebClient()
        
        print("📋 Animations in Firestore:")
        
        # Get all animations
        animations = fb.list_documents("animations")
        
        if not animations:
            print("ℹ️  No animations found in Firestore")
            return
        
        for anim in animations:
            animation_data = anim["data"]
            
            print(f"\n🎬 {anim['id']}:")
            print(f"   - Frame Rate: {animation_data.get('frameRate', 'N/A')}")
            print(f"   - Frame Count: {animation_data.get('frameCount', 'N/A')}")
            print(f"   - Type: {animation_data.get('type', 'N/A')}")
            print(f"   - Start Time: {animation_data.get('startTime', 'N/A')}")
            
            # Count users
            users = animation_data.get('users', {})
            print(f"   - Users: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_animations()
    else:
        cleanup_firestore()