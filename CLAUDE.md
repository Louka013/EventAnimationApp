# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Android application called "EventAnimationApp" that provides a synchronized animation system for stadium events. The app integrates with Firebase for real-time data synchronization and user management.

## Project Structure

### Two Main Versions

#### 📱 **VersionAndroid** (Clean Distribution)
- **Path**: `EventAnimationApp/VersionAndroid/`
- **Purpose**: Production-ready version for distribution
- **Features**: Clean UI, minimal debug info, optimized for end users
- **Usage**: For deployment to end users and production environments

#### 🧪 **VersionTestAndroid** (Development)
- **Path**: `EventAnimationApp/VersionTestAndroid/`
- **Purpose**: Development version with testing tools
- **Features**: Debug tools, Python scripts, detailed logging
- **Usage**: For development, testing, and debugging

## Key Architecture Components

### Android App Structure
- **MainActivity.kt**: Main entry point with seat selection UI and animation playback
- **AnimationPlayer.kt**: Handles color-based animations synchronized across devices
- **Firebase Integration**: Uses Firestore for real-time data sync and Firebase Auth for user management
- **Jetpack Compose**: Modern UI framework used throughout the app

### Animation System
- **Color Animation Framework**: Displays synchronized color animations based on seat positions
- **Real-time Synchronization**: Animations are triggered simultaneously across all connected devices
- **Frame-based Animation**: Uses color frames (RGB values) stored in Firestore
- **Seat-based Targeting**: Different animations can be sent to specific seats/sections

### Firebase Backend
- **Cloud Functions**: Located in `/functions/` directory with Node.js backend
- **Firestore Collections**: 
  - `seatSelections`: User seat assignments
  - `animationConfigs`: Animation metadata and timing
  - `userAnimationPackages`: Individual user animation data
- **Real-time Listeners**: App listens for animation triggers and updates

## Development Commands

### Android Build Commands (Both Versions)
```bash
# Navigate to desired version
cd EventAnimationApp/VersionAndroid          # Production version
cd EventAnimationApp/VersionTestAndroid      # Development version

# Build the Android app
./gradlew build

# Build and install debug APK
./gradlew installDebug

# Build without lint checks (faster)
./gradlew assembleDebug -x lint

# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest

# Clean build
./gradlew clean
```

### Firebase Commands
```bash
# Deploy Firebase Functions (from either version)
cd functions && npm run deploy

# Start Firebase emulators
cd functions && npm run serve

# View Firebase logs
cd functions && npm run logs
```

### Python Testing Scripts (VersionTestAndroid Only)
Multiple Python scripts are available for testing various components:
- `test_animation_config.py`: Tests animation configuration
- `test_firebase_auth.py`: Tests Firebase authentication
- `test_scheduled_animation.py`: Tests scheduled animations
- `test_synchronized_system.py`: Tests the synchronization system

## Key Data Models

### Animation Data Structure
```kotlin
data class ColorFrame(val r: Int, val g: Int, val b: Int)
data class ColorAnimationUser(
    val colors: List<ColorFrame>,
    val startTime: String,
    val frameCount: Int
)
```

### Seat Selection
```kotlin
data class SeatSelection(
    val evenement: String,
    val tribune: String,
    val rang: Int,
    val numeroDePlace: Int,
    val timestamp: Timestamp,
    val userId: String
)
```

## Firebase Configuration

The app requires proper Firebase configuration:
- `google-services.json` must be present in `/app/` directory
- Firebase project must have Firestore and Authentication enabled
- Service account key may be needed for admin operations (excluded from git)

## Animation Workflow

1. User selects seat position in the app
2. Admin triggers animation via web interface or Python scripts
3. Animation data is written to Firestore with precise timing
4. All devices receive real-time updates and start animation simultaneously
5. Each device displays colors based on their seat position

## App Features

### Mobile App Enhancements
- **Portrait-only mode**: `android:screenOrientation="portrait"` prevents landscape rotation
- **Sleep prevention**: Wake lock system keeps screen on during animations
- **Immersive fullscreen**: System UI (status bar) hidden during animations
- **Leading zero formatting**: Seat numbers display as "01, 02" instead of "1, 2"
- **QR code scanning**: Automatic seat assignment via QR codes
- **Manual seat selection**: Venue/section/row/seat picker interface

### UI Differences Between Versions
- **VersionAndroid**: Simplified "Animation Couleur" window with minimal information
- **VersionTestAndroid**: Detailed debug information and development tools

## Security Notes

- Service account keys are gitignored for security
- Firebase rules control access to collections
- User authentication required for seat selection

## Development Guidelines

1. **Use VersionTestAndroid** for development and testing
2. **Test thoroughly** with Python scripts and debug tools
3. **Port clean changes** to VersionAndroid for production
4. **Follow existing patterns** for consistency across versions
5. **Document significant changes** in both versions

## Version-Specific Commands

### Working with VersionAndroid
```bash
cd EventAnimationApp/VersionAndroid
./gradlew assembleDebug -x lint
```

### Working with VersionTestAndroid
```bash
cd EventAnimationApp/VersionTestAndroid
./gradlew assembleDebug -x lint
python test_synchronized_system.py  # Run tests
```

## Important Notes

- **Always test changes in VersionTestAndroid first**
- **VersionAndroid should remain clean and minimal**
- **Both versions share the same core functionality**
- **Firebase configuration is identical between versions**
- **QR codes are shared between both versions**