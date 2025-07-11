#!/usr/bin/env python3
from datetime import datetime, timedelta

def format_datetime(dt):
    """Simulate the Android app's formatDateTime function"""
    return dt.strftime("%d/%m/%Y à %H:%M:%S")

def test_display_format():
    print("=== Testing Display Format with Seconds ===")
    
    # Test with a typical animation scenario
    start_time = datetime(2024, 1, 15, 20, 30, 0)  # 20:30:00
    
    # Wave animation: 80 frames at 15 fps = 5.33 seconds
    wave_duration = 80 / 15
    wave_end = start_time + timedelta(seconds=wave_duration)
    
    print(f"Wave Animation:")
    print(f"  Start: {format_datetime(start_time)}")
    print(f"  End:   {format_datetime(wave_end)}")
    print(f"  Duration: {wave_duration:.2f} seconds")
    print(f"  Same time? {format_datetime(start_time) == format_datetime(wave_end)}")
    print()
    
    # Fireworks animation: 120 frames at 18 fps = 6.67 seconds
    fireworks_duration = 120 / 18
    fireworks_end = start_time + timedelta(seconds=fireworks_duration)
    
    print(f"Fireworks Animation:")
    print(f"  Start: {format_datetime(start_time)}")
    print(f"  End:   {format_datetime(fireworks_end)}")
    print(f"  Duration: {fireworks_duration:.2f} seconds")
    print(f"  Same time? {format_datetime(start_time) == format_datetime(fireworks_end)}")
    print()
    
    # Test edge case - animation less than 1 second
    quick_duration = 0.5
    quick_end = start_time + timedelta(seconds=quick_duration)
    
    print(f"Quick Animation (0.5 seconds):")
    print(f"  Start: {format_datetime(start_time)}")
    print(f"  End:   {format_datetime(quick_end)}")
    print(f"  Duration: {quick_duration} seconds")
    print(f"  Same time? {format_datetime(start_time) == format_datetime(quick_end)}")

if __name__ == "__main__":
    test_display_format()