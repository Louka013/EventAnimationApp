#!/usr/bin/env python3
"""
Example Usage Script for Synchronized Animation System
=====================================================

This script demonstrates how to use the synchronized animation system
to create and deploy animations for different scenarios.
"""

import os
import subprocess
import json
from datetime import datetime, timedelta

def run_command(command, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    print(f"🔧 Command: {command}")
    print()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ SUCCESS:")
            print(result.stdout)
        else:
            print("❌ ERROR:")
            print(result.stderr)
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")

def get_future_time(minutes_ahead=5):
    """Get a future time string."""
    future_time = datetime.now() + timedelta(minutes=minutes_ahead)
    return future_time.strftime("%Y-%m-%dT%H:%M:%S")

def main():
    """Main example usage demonstrations."""
    print("🎬 SYNCHRONIZED ANIMATION SYSTEM - USAGE EXAMPLES")
    print("="*60)
    print()
    
    # Example 1: Basic Animation Generation
    print("📝 Example 1: Basic Animation Generation")
    print("Generate a wave animation for a medium stadium (10x10 grid)")
    command1 = "python split_animation_grid.py --animation wave --rows 10 --cols 10 --fps 15"
    run_command(command1, "Basic Wave Animation Generation")
    
    # Example 2: Animation with Firebase Upload
    print("\n📝 Example 2: Animation with Firebase Upload")
    print("Generate rainbow animation and upload to Firebase")
    future_time = get_future_time(10)  # 10 minutes from now
    command2 = f"python split_animation_grid.py --animation rainbow --upload-firebase --start-time '{future_time}' --event-type football_stadium"
    run_command(command2, "Rainbow Animation with Firebase Upload")
    
    # Example 3: Real-Time Event Animation
    print("\n📝 Example 3: Real-Time Event Animation")
    print("Deploy fireworks animation during live event (5 minutes warning)")
    future_time = get_future_time(5)  # 5 minutes from now
    command3 = f"python split_animation_grid.py --animation fireworks --upload-firebase --start-time '{future_time}' --event-type concert_hall --rows 10 --cols 10"
    run_command(command3, "Real-Time Fireworks Animation")
    
    # Example 4: Large Stadium Configuration
    print("\n📝 Example 4: Large Stadium Configuration")
    print("Generate pulse animation for large stadium (10x10 grid)")
    future_time = get_future_time(15)  # 15 minutes from now
    command4 = f"python split_animation_grid.py --animation pulse --rows 10 --cols 10 --upload-firebase --start-time '{future_time}' --event-type arena"
    run_command(command4, "Large Stadium Pulse Animation")
    
    # Example 5: Custom Configuration
    print("\n📝 Example 5: Custom Configuration")
    print("Generate wave animation with custom frame rate")
    command5 = "python split_animation_grid.py --animation wave --fps 20 --rows 10 --cols 10 --verbose"
    run_command(command5, "Custom Frame Rate Wave Animation")
    
    # Example 6: Testing Different Event Types
    print("\n📝 Example 6: Testing Different Event Types")
    print("Generate animations for different event types")
    
    event_types = ["football_stadium", "theater", "concert_hall", "arena"]
    animations = ["wave", "rainbow", "pulse", "fireworks"]
    
    for i, (event_type, animation) in enumerate(zip(event_types, animations)):
        future_time = get_future_time(20 + i * 5)  # Staggered times
        command = f"python split_animation_grid.py --animation {animation} --event-type {event_type} --rows 15 --cols 20 --start-time '{future_time}'"
        run_command(command, f"{animation.title()} Animation for {event_type}")
    
    print("\n🎉 All example scenarios completed!")
    print("📱 Now test the Android app to see synchronized animations in action!")

if __name__ == "__main__":
    main()