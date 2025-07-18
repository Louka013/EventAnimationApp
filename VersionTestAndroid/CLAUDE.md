# CLAUDE.md - VersionTestAndroid

This file provides guidance to Claude Code (claude.ai/code) when working with the **development version** of EventAnimationApp.

## Project Overview

This is the **development version** of EventAnimationApp called "VersionTestAndroid" that provides a synchronized animation system for stadium events. The app integrates with Firebase for real-time data synchronization and user management.

## Version Information

### 🧪 VersionTestAndroid (This Version)
- **Purpose**: Development, testing, and debugging
- **Features**: Full debug information, testing tools, Python scripts
- **Use Case**: Development environment, testing new features
- **Location**: `EventAnimationApp/VersionTestAndroid/`

### 📱 VersionAndroid (Production Version)
- **Purpose**: Clean production deployment
- **Features**: Minimal UI, no debug information
- **Use Case**: End-user deployment
- **Location**: `EventAnimationApp/VersionAndroid/`

## Key Architecture Components

### Android App Structure
- **MainActivity.kt**: Main entry point with seat selection UI and animation playback
- **SynchronizedAnimationScheduler.kt**: Handles animation timing and synchronization
- **TimeSynchronizationManager.kt**: Manages time synchronization across devices
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

### Android Build Commands
```bash
# Build the Android app
./gradlew build

# Build debug APK (faster, skips lint)
./gradlew assembleDebug -x lint

# Build and install debug APK
./gradlew installDebug

# Run unit tests
./gradlew test

# Run instrumented tests
./gradlew connectedAndroidTest

# Clean build
./gradlew clean
```

### Firebase Commands
```bash
# Deploy Firebase Functions
cd functions && npm run deploy

# Start Firebase emulators
cd functions && npm run serve

# View Firebase logs
cd functions && npm run logs
```

### Python Testing Scripts (Development Tools)
```bash
# Animation Testing
python test_animation_config.py          # Tests animation configuration
python test_scheduled_animation.py       # Tests scheduled animations
python test_synchronized_system.py       # Tests the synchronization system

# Firebase Testing
python test_firebase_auth.py            # Tests Firebase authentication
python test_all_functions.py            # Comprehensive testing suite

# Animation Creation & Testing
python checkboard_flash_animation.py    # Creates checkboard animations
python blue_black_flash_working.py      # Creates flash animations
python test_checkboard_flash.py         # Tests checkboard animations

# Debug & Analysis Tools
python debug_animation_status.py        # Monitors animation status
python debug_user_coverage.py           # Analyzes user coverage
python debug_user_packages.py           # Debugs user animation packages

# Database Management
python cleanup_firestore.py             # Cleans up test data
python cleanup_users_collection.py      # Cleans up user data
```

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

## App Features (Development Version)

### Mobile App Enhancements
- **Portrait-only mode**: `android:screenOrientation="portrait"` prevents landscape rotation
- **Sleep prevention**: Wake lock system keeps screen on during animations
- **Immersive fullscreen**: System UI (status bar) hidden during animations
- **Leading zero formatting**: Seat numbers display as "01, 02" instead of "1, 2"
- **QR code scanning**: Automatic seat assignment via QR codes
- **Manual seat selection**: Venue/section/row/seat picker interface

### Development-Specific Features
- **Detailed debug information**: Animation frame counts, timing details, real-time updates
- **Animation status monitoring**: Live updates on animation loading and execution
- **Firebase connection status**: Visual indicators for backend connectivity
- **Performance metrics**: Timing and synchronization data
- **Error reporting**: Detailed error messages and stack traces

## Testing & Development Tools

### Animation Testing Scripts
- `test_animation_config.py`: Validates animation configuration and timing
- `test_scheduled_animation.py`: Tests scheduled animation functionality
- `checkboard_flash_*.py`: Various checkerboard animation patterns
- `blue_black_flash_*.py`: Flash animation testing utilities

### Firebase Integration Testing
- `test_firebase_auth.py`: Authentication testing
- `test_synchronized_system.py`: Full system synchronization testing
- `cleanup_firestore.py`: Database cleanup utilities

### Debug & Analysis Tools
- `debug_animation_status.py`: Real-time animation monitoring
- `debug_user_coverage.py`: User coverage analysis
- `debug_package_issue.py`: Package delivery debugging
- `verify_*.py`: Data verification utilities

## Development Guidelines

### Testing Workflow
1. **Use Python scripts** for initial testing and validation
2. **Test animations** with debug tools before deployment
3. **Verify Firebase integration** with testing utilities
4. **Check synchronization** across multiple devices
5. **Document issues** using debug reports

### Code Development
1. **Always test in VersionTestAndroid first**
2. **Use detailed logging** for debugging
3. **Test with Python scripts** before Android testing
4. **Verify changes** with multiple devices when possible
5. **Port clean changes** to VersionAndroid for production

### Debug Information Available
- **Animation frame information**: Real-time frame counts and timing
- **Firebase connection status**: Live connection monitoring
- **Real-time update timestamps**: When data was last updated
- **Performance metrics**: Animation loading and execution times
- **Error details**: Comprehensive error reporting and stack traces

## Security Notes

- Service account keys are gitignored for security
- Firebase rules control access to collections
- User authentication required for seat selection
- Debug information should not be exposed in production

## Production Deployment

### Porting to VersionAndroid
1. **Test thoroughly** in VersionTestAndroid
2. **Remove debug information** and testing code
3. **Simplify UI elements** for production
4. **Verify functionality** remains intact
5. **Document any differences** between versions

### Clean-up Process
- Remove Python testing scripts
- Simplify debug information displays
- Clean up logging statements
- Remove development-specific features
- Optimize for production performance

## Important Notes

- **This is the development version** - use for testing and development only
- **VersionAndroid is the production version** - deploy that for end users
- **Always test changes here first** before porting to production
- **Use Python scripts extensively** for validation and testing
- **Document all changes** for future reference and troubleshooting