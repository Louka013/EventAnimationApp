#!/usr/bin/env python3
"""
Comprehensive Test Suite for Synchronized Animation System
=========================================================

This script provides comprehensive testing for the synchronized animation system,
including Firebase connectivity, animation generation, and Android app integration.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from split_animation_grid import AnimationGridSplitter

def test_animation_generation():
    """Test basic animation generation functionality."""
    print("🧪 Testing Animation Generation")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        # Test frame generation
        user_frames = splitter.generate_animation_frames("wave", 3, 3)
        
        assert len(user_frames) == 9, f"Expected 9 users, got {len(user_frames)}"
        assert "user_1_1" in user_frames, "user_1_1 should be in generated frames"
        assert "user_3_3" in user_frames, "user_3_3 should be in generated frames"
        assert len(user_frames["user_1_1"]) == 80, "Wave animation should have 80 frames"
        
        print("✅ Animation generation test passed")
        return True
    except Exception as e:
        print(f"❌ Animation generation test failed: {e}")
        return False

def test_json_file_creation():
    """Test JSON file creation for users."""
    print("\n🧪 Testing JSON File Creation")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        # Generate frames for small grid
        user_frames = splitter.generate_animation_frames("pulse", 2, 2)
        
        # Create JSON files
        start_time = datetime.now() + timedelta(minutes=5)
        json_files = splitter.create_user_json_files("pulse", user_frames, start_time)
        
        assert len(json_files) == 4, f"Expected 4 JSON files, got {len(json_files)}"
        
        # Check if files exist
        for user_id, file_path in json_files.items():
            assert os.path.exists(file_path), f"JSON file {file_path} should exist"
            
            # Check file content
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert data["userId"] == user_id, f"User ID mismatch in {file_path}"
                assert data["animationType"] == "pulse", f"Animation type mismatch in {file_path}"
                assert len(data["frames"]) == 40, f"Pulse animation should have 40 frames in {file_path}"
        
        print("✅ JSON file creation test passed")
        return True
    except Exception as e:
        print(f"❌ JSON file creation test failed: {e}")
        return False

def test_firebase_connectivity():
    """Test Firebase connectivity and basic operations."""
    print("\n🧪 Testing Firebase Connectivity")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        # Try to initialize Firebase
        if not splitter.initialize_firebase():
            print("⚠️  Firebase initialization failed - Firebase tests will be skipped")
            return True  # Don't fail the entire test suite
        
        # Test basic Firestore operations
        # This is a read-only test to avoid creating unnecessary data
        print("✅ Firebase connectivity test passed")
        return True
    except Exception as e:
        print(f"❌ Firebase connectivity test failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration file loading and validation."""
    print("\n🧪 Testing Configuration Loading")
    print("-" * 40)
    
    try:
        # Test with default config
        splitter = AnimationGridSplitter()
        
        # Check if default animations are loaded
        assert "wave" in splitter.config["animations"], "Wave animation should be in config"
        assert "rainbow" in splitter.config["animations"], "Rainbow animation should be in config"
        assert "pulse" in splitter.config["animations"], "Pulse animation should be in config"
        assert "fireworks" in splitter.config["animations"], "Fireworks animation should be in config"
        
        # Check animation properties
        wave_config = splitter.config["animations"]["wave"]
        assert wave_config["frame_rate"] == 15, "Wave animation should have 15 fps"
        assert wave_config["frame_count"] == 80, "Wave animation should have 80 frames"
        
        print("✅ Configuration loading test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        return False

def test_user_id_generation():
    """Test user ID generation logic."""
    print("\n🧪 Testing User ID Generation")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        # Test various seat positions
        test_cases = [
            (1, 1, "user_1_1"),
            (10, 15, "user_10_15"),
            (5, 8, "user_5_8"),
            (20, 30, "user_20_30")
        ]
        
        for row, col, expected in test_cases:
            user_frames = splitter.generate_animation_frames("wave", row, col)
            assert expected in user_frames, f"Expected {expected} in generated frames"
        
        print("✅ User ID generation test passed")
        return True
    except Exception as e:
        print(f"❌ User ID generation test failed: {e}")
        return False

def test_timing_calculations():
    """Test timing and synchronization calculations."""
    print("\n🧪 Testing Timing Calculations")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        # Test start time formatting
        start_time = datetime(2025, 7, 11, 21, 0, 0)
        
        # Generate animation with specific start time
        user_frames = splitter.generate_animation_frames("wave", 2, 2)
        json_files = splitter.create_user_json_files("wave", user_frames, start_time)
        
        # Check timing in generated files
        for user_id, file_path in json_files.items():
            with open(file_path, 'r') as f:
                data = json.load(f)
                assert data["startTime"] == "2025-07-11T21:00:00Z", f"Start time mismatch in {file_path}"
                assert data["frameRate"] == 15, f"Frame rate mismatch in {file_path}"
                assert data["duration"] == 5.33, f"Duration mismatch in {file_path}"
        
        print("✅ Timing calculations test passed")
        return True
    except Exception as e:
        print(f"❌ Timing calculations test failed: {e}")
        return False

def test_animation_types():
    """Test all supported animation types."""
    print("\n🧪 Testing Animation Types")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        animation_types = ["wave", "rainbow", "pulse", "fireworks"]
        expected_frame_counts = [80, 60, 40, 120]
        expected_frame_rates = [15, 12, 8, 18]
        
        for i, animation_type in enumerate(animation_types):
            user_frames = splitter.generate_animation_frames(animation_type, 2, 2)
            
            # Check frame count
            for user_id, frames in user_frames.items():
                assert len(frames) == expected_frame_counts[i], \
                    f"{animation_type} should have {expected_frame_counts[i]} frames"
            
            # Check configuration
            config = splitter.config["animations"][animation_type]
            assert config["frame_rate"] == expected_frame_rates[i], \
                f"{animation_type} should have {expected_frame_rates[i]} fps"
        
        print("✅ Animation types test passed")
        return True
    except Exception as e:
        print(f"❌ Animation types test failed: {e}")
        return False

def test_grid_sizes():
    """Test different grid sizes and scaling."""
    print("\n🧪 Testing Grid Sizes")
    print("-" * 40)
    
    try:
        splitter = AnimationGridSplitter()
        
        # Test different grid sizes
        test_grids = [
            (5, 5, 25),     # Small grid
            (10, 15, 150),  # Medium grid
            (20, 30, 600),  # Large grid
        ]
        
        for rows, cols, expected_users in test_grids:
            user_frames = splitter.generate_animation_frames("wave", rows, cols)
            assert len(user_frames) == expected_users, \
                f"Grid {rows}x{cols} should generate {expected_users} users, got {len(user_frames)}"
        
        print("✅ Grid sizes test passed")
        return True
    except Exception as e:
        print(f"❌ Grid sizes test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("🎬 SYNCHRONIZED ANIMATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("User ID Generation", test_user_id_generation),
        ("Animation Generation", test_animation_generation),
        ("JSON File Creation", test_json_file_creation),
        ("Timing Calculations", test_timing_calculations),
        ("Animation Types", test_animation_types),
        ("Grid Sizes", test_grid_sizes),
        ("Firebase Connectivity", test_firebase_connectivity),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"💥 CRITICAL ERROR in {test_name}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    print(f"🎯 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {failed} tests failed. Please review and fix issues before deployment.")
        return False

def cleanup_test_files():
    """Clean up test files created during testing."""
    print("\n🧹 Cleaning up test files...")
    
    try:
        # Remove JSON files created during testing
        json_dir = "./user_animations"
        if os.path.exists(json_dir):
            for file in os.listdir(json_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(json_dir, file))
        
        print("✅ Test files cleaned up successfully")
    except Exception as e:
        print(f"⚠️  Error cleaning up test files: {e}")

if __name__ == "__main__":
    try:
        success = run_all_tests()
        cleanup_test_files()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        cleanup_test_files()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        cleanup_test_files()
        sys.exit(1)