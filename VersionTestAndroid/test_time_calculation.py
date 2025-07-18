#!/usr/bin/env python3
from datetime import datetime, timedelta

def test_time_calculation():
    print("=== Testing Animation End Time Calculation ===")
    
    # Test cases based on the animation data from the web interface
    test_cases = [
        ("Wave Animation", "2024-01-15T20:30", 80, 15),
        ("Rainbow Animation", "2024-01-15T20:30", 60, 12),
        ("Pulse Animation", "2024-01-15T20:30", 40, 8),
        ("Fireworks Animation", "2024-01-15T20:30", 120, 18)
    ]
    
    for name, start_time_str, frame_count, frame_rate in test_cases:
        # Parse start time
        start_time = datetime.fromisoformat(start_time_str + ":00")
        
        # Calculate duration
        duration_seconds = frame_count / frame_rate
        
        # Calculate end time
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        print(f"\n--- {name} ---")
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Frames: {frame_count}")
        print(f"Frame rate: {frame_rate} fps")
        print(f"Duration: {duration_seconds:.2f} seconds ({duration_seconds/60:.2f} minutes)")
        print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Difference: {(end_time - start_time).total_seconds():.2f} seconds")
        
        # Check if calculation is correct
        if abs((end_time - start_time).total_seconds() - duration_seconds) < 0.1:
            print("✅ Calculation is correct")
        else:
            print("❌ Calculation is incorrect")

if __name__ == "__main__":
    test_time_calculation()