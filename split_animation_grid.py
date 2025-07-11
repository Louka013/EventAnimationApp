#!/usr/bin/env python3
"""
Advanced Animation Grid Splitter for Synchronized Stadium Animations
====================================================================

This script generates user-specific animation frames and JSON files for 
synchronized stadium animations. It supports multiple animation types 
and can automatically upload to Firebase Firestore.

Features:
- Generates individual animation frames for each seat position
- Creates user-specific JSON files with frame URLs and timing
- Supports multiple animation types (wave, rainbow, pulse, fireworks)
- Optional Firebase Firestore integration
- Configurable grid sizes and frame rates
- Automatic timestamp generation for synchronization

Usage:
    python split_animation_grid.py --animation wave --rows 20 --cols 30 --fps 15
    python split_animation_grid.py --animation rainbow --upload-firebase
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Optional Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Firebase Admin SDK not available. Install with: pip install firebase-admin")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnimationGridSplitter:
    """Advanced animation grid splitter with Firebase integration."""
    
    def __init__(self, config_file: str = "animation_config.json"):
        """Initialize the animation splitter."""
        self.config = self._load_config(config_file)
        self.firebase_app = None
        self.firestore_db = None
        self.storage_bucket = None
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "firebase": {
                "project_id": "data-base-test-6ef5f",
                "storage_bucket": "data-base-test-6ef5f.firebasestorage.app",
                "service_account_key": None
            },
            "animations": {
                "wave": {
                    "frame_rate": 15,
                    "frame_count": 80,
                    "duration_seconds": 5.33,
                    "pattern": "wave_horizontal"
                },
                "rainbow": {
                    "frame_rate": 12,
                    "frame_count": 60,
                    "duration_seconds": 5.0,
                    "pattern": "rainbow_cascade"
                },
                "pulse": {
                    "frame_rate": 8,
                    "frame_count": 40,
                    "duration_seconds": 5.0,
                    "pattern": "pulse_radial"
                },
                "fireworks": {
                    "frame_rate": 18,
                    "frame_count": 120,
                    "duration_seconds": 6.67,
                    "pattern": "fireworks_burst"
                }
            },
            "grid": {
                "default_rows": 20,
                "default_cols": 30,
                "max_rows": 50,
                "max_cols": 100
            },
            "output": {
                "base_path": "./animations",
                "json_path": "./user_animations",
                "url_template": "https://firebasestorage.googleapis.com/v0/b/{bucket}/o/animations/{animation}/{row}_{col}/frame_{frame:03d}.png"
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                # Merge with default config
                self._deep_merge(default_config, user_config)
        
        return default_config
    
    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def initialize_firebase(self, service_account_key: Optional[str] = None) -> bool:
        """Initialize Firebase connection."""
        if not FIREBASE_AVAILABLE:
            logger.error("Firebase Admin SDK not available")
            return False
        
        try:
            # Use service account key if provided
            if service_account_key and os.path.exists(service_account_key):
                cred = credentials.Certificate(service_account_key)
                self.firebase_app = firebase_admin.initialize_app(cred)
            else:
                # Use default credentials
                self.firebase_app = firebase_admin.initialize_app()
            
            self.firestore_db = firestore.client()
            self.storage_bucket = storage.bucket(self.config["firebase"]["storage_bucket"])
            
            logger.info("Firebase initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False
    
    def generate_animation_frames(self, animation_type: str, rows: int, cols: int) -> Dict[str, List[str]]:
        """Generate frame URLs for each user position."""
        if animation_type not in self.config["animations"]:
            raise ValueError(f"Unknown animation type: {animation_type}")
        
        animation_config = self.config["animations"][animation_type]
        frame_count = animation_config["frame_count"]
        bucket = self.config["firebase"]["storage_bucket"]
        url_template = self.config["output"]["url_template"]
        
        user_frames = {}
        
        logger.info(f"Generating {animation_type} animation frames for {rows}x{cols} grid")
        
        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                user_id = f"user_{row}_{col}"
                frames = []
                
                for frame_idx in range(frame_count):
                    frame_url = url_template.format(
                        bucket=bucket,
                        animation=f"{animation_type}_animation",
                        row=row,
                        col=col,
                        frame=frame_idx
                    )
                    frames.append(frame_url)
                
                user_frames[user_id] = frames
        
        logger.info(f"Generated frames for {len(user_frames)} users")
        return user_frames
    
    def create_user_json_files(self, animation_type: str, user_frames: Dict[str, List[str]], 
                              start_time: Optional[datetime] = None) -> Dict[str, str]:
        """Create individual JSON files for each user."""
        if start_time is None:
            start_time = datetime.now() + timedelta(minutes=5)  # Default: 5 minutes from now
        
        animation_config = self.config["animations"][animation_type]
        json_path = self.config["output"]["json_path"]
        
        # Create output directory
        os.makedirs(json_path, exist_ok=True)
        
        user_json_files = {}
        start_time_iso = start_time.isoformat() + "Z"
        
        logger.info(f"Creating user JSON files for {len(user_frames)} users")
        
        for user_id, frames in user_frames.items():
            user_data = {
                "userId": user_id,
                "animationType": animation_type,
                "animationId": f"{animation_type}_animation",
                "startTime": start_time_iso,
                "frameRate": animation_config["frame_rate"],
                "frameCount": animation_config["frame_count"],
                "duration": animation_config["duration_seconds"],
                "frames": frames,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "pattern": animation_config["pattern"],
                    "total_frames": len(frames)
                }
            }
            
            json_filename = f"{user_id}_{animation_type}.json"
            json_filepath = os.path.join(json_path, json_filename)
            
            with open(json_filepath, 'w') as f:
                json.dump(user_data, f, indent=2)
            
            user_json_files[user_id] = json_filepath
        
        logger.info(f"Created {len(user_json_files)} JSON files in {json_path}")
        return user_json_files
    
    def upload_to_firestore(self, animation_type: str, user_frames: Dict[str, List[str]], 
                           start_time: Optional[datetime] = None, event_type: str = "football_stadium") -> str:
        """Upload animation data to Firestore."""
        if not self.firestore_db:
            raise RuntimeError("Firebase not initialized. Call initialize_firebase() first.")
        
        if start_time is None:
            start_time = datetime.now() + timedelta(minutes=5)
        
        animation_config = self.config["animations"][animation_type]
        animation_id = f"{animation_type}_animation_{int(start_time.timestamp())}"
        
        # Create main animation document
        main_doc = {
            "animationId": animation_id,
            "animationType": animation_type,
            "eventType": event_type,
            "frameRate": animation_config["frame_rate"],
            "frameCount": animation_config["frame_count"],
            "startTime": start_time.isoformat() + "Z",
            "duration": animation_config["duration_seconds"],
            "active": True,
            "createdAt": datetime.now().isoformat() + "Z",
            "updatedAt": datetime.now().isoformat() + "Z",
            "totalUsers": len(user_frames),
            "pattern": animation_config["pattern"]
        }
        
        logger.info(f"Uploading animation {animation_id} to Firestore")
        
        # Upload main animation document
        animation_ref = self.firestore_db.collection("animations").document(animation_id)
        animation_ref.set(main_doc)
        
        # Upload user-specific documents
        batch = self.firestore_db.batch()
        batch_count = 0
        
        for user_id, frames in user_frames.items():
            user_doc = {
                "userId": user_id,
                "animationId": animation_id,
                "animationType": animation_type,
                "frames": frames,
                "startTime": start_time.isoformat() + "Z",
                "frameRate": animation_config["frame_rate"],
                "frameCount": len(frames),
                "createdAt": datetime.now().isoformat() + "Z"
            }
            
            user_ref = animation_ref.collection("users").document(user_id)
            batch.set(user_ref, user_doc)
            
            batch_count += 1
            
            # Firestore batch limit is 500 operations
            if batch_count >= 500:
                batch.commit()
                batch = self.firestore_db.batch()
                batch_count = 0
        
        # Commit remaining operations
        if batch_count > 0:
            batch.commit()
        
        logger.info(f"Successfully uploaded {len(user_frames)} user documents to Firestore")
        return animation_id
    
    def create_animation_config_document(self, animation_type: str, animation_id: str, 
                                       start_time: datetime, event_type: str = "football_stadium") -> str:
        """Create a configuration document for the web interface."""
        if not self.firestore_db:
            raise RuntimeError("Firebase not initialized. Call initialize_firebase() first.")
        
        animation_config = self.config["animations"][animation_type]
        
        # First, deactivate any existing active animations for this event type
        existing_query = self.firestore_db.collection("animation_configs").where(
            "eventType", "==", event_type
        ).where("status", "==", "active")
        
        for doc in existing_query.stream():
            doc.reference.update({"status": "inactive"})
        
        # Create new configuration document
        config_doc = {
            "animationStartTime": start_time.strftime("%Y-%m-%dT%H:%M"),
            "eventType": event_type,
            "animationType": animation_type,
            "animationData": {
                "animationId": animation_id,
                "frameRate": animation_config["frame_rate"],
                "frameCount": animation_config["frame_count"],
                "users": {}  # Will be populated by the animation data
            },
            "createdAt": datetime.now().isoformat() + "Z",
            "status": "active"
        }
        
        # Add the configuration document
        config_ref = self.firestore_db.collection("animation_configs").add(config_doc)
        config_id = config_ref[1].id
        
        logger.info(f"Created animation config document: {config_id}")
        return config_id
    
    def generate_complete_animation(self, animation_type: str, rows: int, cols: int, 
                                  start_time: Optional[datetime] = None, 
                                  event_type: str = "football_stadium",
                                  upload_firebase: bool = False) -> Dict:
        """Generate complete animation with all components."""
        logger.info(f"Starting complete animation generation for {animation_type}")
        
        if start_time is None:
            start_time = datetime.now() + timedelta(minutes=5)
        
        # Step 1: Generate frame URLs
        user_frames = self.generate_animation_frames(animation_type, rows, cols)
        
        # Step 2: Create JSON files
        user_json_files = self.create_user_json_files(animation_type, user_frames, start_time)
        
        result = {
            "animation_type": animation_type,
            "start_time": start_time.isoformat() + "Z",
            "total_users": len(user_frames),
            "json_files_created": len(user_json_files),
            "grid_size": f"{rows}x{cols}",
            "local_files": user_json_files
        }
        
        # Step 3: Upload to Firebase (optional)
        if upload_firebase:
            if not self.firestore_db:
                if not self.initialize_firebase():
                    logger.error("Failed to initialize Firebase. Skipping upload.")
                    return result
            
            animation_id = self.upload_to_firestore(animation_type, user_frames, start_time, event_type)
            config_id = self.create_animation_config_document(animation_type, animation_id, start_time, event_type)
            
            result.update({
                "firebase_uploaded": True,
                "animation_id": animation_id,
                "config_id": config_id
            })
        
        logger.info("Complete animation generation finished")
        return result

def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(description="Advanced Animation Grid Splitter")
    parser.add_argument("--animation", "-a", required=True, 
                       choices=["wave", "rainbow", "pulse", "fireworks"],
                       help="Animation type to generate")
    parser.add_argument("--rows", "-r", type=int, default=20,
                       help="Number of rows in the grid (default: 20)")
    parser.add_argument("--cols", "-c", type=int, default=30,
                       help="Number of columns in the grid (default: 30)")
    parser.add_argument("--fps", type=int, help="Override frame rate")
    parser.add_argument("--start-time", "-t", help="Start time (ISO format: 2025-07-11T21:00:00)")
    parser.add_argument("--event-type", "-e", default="football_stadium",
                       choices=["football_stadium", "theater", "concert_hall", "arena"],
                       help="Event type (default: football_stadium)")
    parser.add_argument("--upload-firebase", "-u", action="store_true",
                       help="Upload to Firebase Firestore")
    parser.add_argument("--config", default="animation_config.json",
                       help="Configuration file (default: animation_config.json)")
    parser.add_argument("--service-account", help="Firebase service account key file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse start time
    start_time = None
    if args.start_time:
        try:
            start_time = datetime.fromisoformat(args.start_time.replace('Z', ''))
        except ValueError:
            logger.error(f"Invalid start time format: {args.start_time}")
            sys.exit(1)
    
    # Initialize splitter
    splitter = AnimationGridSplitter(args.config)
    
    # Override frame rate if specified
    if args.fps:
        splitter.config["animations"][args.animation]["frame_rate"] = args.fps
    
    # Initialize Firebase if needed
    if args.upload_firebase:
        if not splitter.initialize_firebase(args.service_account):
            logger.error("Failed to initialize Firebase")
            sys.exit(1)
    
    # Generate animation
    try:
        result = splitter.generate_complete_animation(
            animation_type=args.animation,
            rows=args.rows,
            cols=args.cols,
            start_time=start_time,
            event_type=args.event_type,
            upload_firebase=args.upload_firebase
        )
        
        # Print results
        print("\n" + "="*60)
        print("ANIMATION GENERATION COMPLETE")
        print("="*60)
        print(f"Animation Type: {result['animation_type']}")
        print(f"Grid Size: {result['grid_size']}")
        print(f"Total Users: {result['total_users']}")
        print(f"Start Time: {result['start_time']}")
        print(f"JSON Files Created: {result['json_files_created']}")
        
        if result.get('firebase_uploaded'):
            print(f"Firebase Animation ID: {result['animation_id']}")
            print(f"Firebase Config ID: {result['config_id']}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Animation generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()