#!/usr/bin/env python3
"""
Debug script to check animation status and timing
"""

from firebase_web_admin import FirebaseWebClient
from datetime import datetime, timezone
import json

def debug_animation_status():
    try:
        fb = FirebaseWebClient()
        
        print("🔍 Debugging animation status...")
        current_time = datetime.now()
        utc_time = datetime.now(timezone.utc)
        
        print(f"🕐 Current local time: {current_time.strftime('%Y-%m-%dT%H:%M:%S')}")
        print(f"🌍 Current UTC time: {utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')}")
        
        # Check animation_configs
        print("\n📋 Animation Configs:")
        configs = fb.list_documents("animation_configs")
        for config in configs:
            config_id = config["id"]
            data = config["data"]
            print(f"   Config {config_id}:")
            print(f"      - Type: {data.get('animationType', 'unknown')}")
            print(f"      - Start Time: {data.get('animationStartTime', 'unknown')}")
            print(f"      - Status: {data.get('status', 'unknown')}")
            print(f"      - Event Type: {data.get('eventType', 'unknown')}")
        
        # Check animations collection
        print("\n🎬 Animations Collection:")
        animations = fb.list_documents("animations")
        for animation in animations:
            anim_id = animation["id"]
            data = animation["data"]
            print(f"   Animation {anim_id}:")
            print(f"      - Start Time: {data.get('startTime', 'unknown')}")
            print(f"      - Frame Rate: {data.get('frameRate', 'unknown')}")
            print(f"      - Frame Count: {data.get('frameCount', 'unknown')}")
            print(f"      - Users: {len(data.get('users', {}))}")
            
            # Check if start time has passed
            start_time_str = data.get('startTime', '')
            if start_time_str:
                try:
                    # Parse the start time
                    if start_time_str.endswith('Z'):
                        start_time = datetime.fromisoformat(start_time_str[:-1]).replace(tzinfo=timezone.utc)
                    else:
                        start_time = datetime.fromisoformat(start_time_str)
                    
                    time_diff = (utc_time - start_time).total_seconds()
                    if time_diff > 0:
                        print(f"      - ⏰ Should have started {time_diff:.0f} seconds ago")
                    else:
                        print(f"      - ⏳ Will start in {-time_diff:.0f} seconds")
                except Exception as e:
                    print(f"      - ❌ Error parsing time: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_animation_status()