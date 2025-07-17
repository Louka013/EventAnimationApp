#!/usr/bin/env python3
"""
Check all checkboard_flash related data in Firebase
"""

from firebase_web_admin import FirebaseWebClient

def check_checkboard_animations():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Checking all checkboard_flash related data...")
        
        # Check animations collection
        print("\n📊 Checking animations collection...")
        animations = fb.list_documents("animations")
        checkboard_found = False
        
        for animation in animations:
            animation_id = animation["id"]
            data = animation["data"]
            
            if "checkboard" in animation_id.lower():
                checkboard_found = True
                print(f"✅ Found animation: {animation_id}")
                users = data.get("users", {})
                print(f"   - Users: {len(users)}")
                print(f"   - Frame rate: {data.get('frameRate', 'N/A')}")
                print(f"   - Frame count: {data.get('frameCount', 'N/A')}")
                print(f"   - Start time: {data.get('startTime', 'N/A')}")
                
                # Check if user_9_9 is in this animation
                if "user_9_9" in users:
                    print(f"   - user_9_9: ✅ FOUND")
                    user_data = users["user_9_9"]
                    colors = user_data.get("colors", [])
                    print(f"     - Colors: {len(colors)} frames")
                    if colors:
                        print(f"     - First color: {colors[0]}")
                else:
                    print(f"   - user_9_9: ❌ NOT FOUND")
                
                # Show sample users
                sample_users = list(users.keys())[:5]
                print(f"   - Sample users: {sample_users}")
        
        if not checkboard_found:
            print("❌ No checkboard animations found in animations collection")
        
        # Check animation_configs collection
        print("\n⚙️ Checking animation_configs collection...")
        configs = fb.list_documents("animation_configs")
        checkboard_configs = []
        
        for config in configs:
            config_id = config["id"]
            data = config["data"]
            
            animation_type = data.get("animationType", "")
            if "checkboard" in animation_type.lower():
                checkboard_configs.append({
                    "id": config_id,
                    "data": data
                })
        
        if checkboard_configs:
            print(f"✅ Found {len(checkboard_configs)} checkboard animation configs:")
            for config in checkboard_configs:
                config_id = config["id"]
                data = config["data"]
                print(f"   - Config ID: {config_id}")
                print(f"   - Type: {data.get('animationType', 'N/A')}")
                print(f"   - Status: {data.get('status', 'N/A')}")
                print(f"   - Start time: {data.get('animationStartTime', 'N/A')}")
                print(f"   - Created: {data.get('createdAt', 'N/A')}")
        else:
            print("❌ No checkboard animation configs found")
        
        # Check userAnimationPackages for any checkboard data
        print("\n📦 Checking userAnimationPackages for checkboard data...")
        packages = fb.list_documents("userAnimationPackages")
        checkboard_packages = []
        
        for package in packages:
            package_id = package["id"]
            data = package["data"]
            
            animation_type = data.get("animationType", "")
            if "checkboard" in animation_type.lower():
                checkboard_packages.append({
                    "id": package_id,
                    "data": data
                })
        
        if checkboard_packages:
            print(f"✅ Found {len(checkboard_packages)} checkboard user packages:")
            user_9_9_found = False
            
            for package in checkboard_packages:
                package_id = package["id"]
                data = package["data"]
                
                if package_id == "user_9_9":
                    user_9_9_found = True
                    print(f"   - user_9_9: ✅ FOUND")
                    print(f"     - Animation type: {data.get('animationType', 'N/A')}")
                    print(f"     - Active: {data.get('isActive', 'N/A')}")
                    print(f"     - Start time: {data.get('startTime', 'N/A')}")
                    print(f"     - Frames: {len(data.get('frames', []))}")
                
                print(f"   - {package_id}: {data.get('animationType', 'N/A')}")
            
            if not user_9_9_found:
                print(f"   - user_9_9: ❌ NOT FOUND in checkboard packages")
        else:
            print("❌ No checkboard user packages found")
        
        return checkboard_found, len(checkboard_configs), len(checkboard_packages)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, 0, 0

if __name__ == "__main__":
    check_checkboard_animations()