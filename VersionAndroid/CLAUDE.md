# CLAUDE.md - VersionAndroid

This file provides guidance to Claude Code (claude.ai/code) when working with the **production version** of EventAnimationApp.

## Project Overview

This is the **production version** of EventAnimationApp called "VersionAndroid" that provides a synchronized animation system for stadium events. The app integrates with Firebase for real-time data synchronization and user management.

## Version Information

### 📱 VersionAndroid (This Version)
- **Purpose**: Clean production deployment for end users
- **Features**: Minimal UI, no debug information, optimized performance
- **Use Case**: Production deployment to event participants
- **Location**: `EventAnimationApp/VersionAndroid/`

### 🧪 VersionTestAndroid (Development Version)
- **Purpose**: Development, testing, and debugging
- **Features**: Full debug information, testing tools, Python scripts
- **Use Case**: Development environment, testing new features
- **Location**: `EventAnimationApp/VersionTestAndroid/`

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
# Build production APK
./gradlew assembleDebug

# Build without lint checks (faster)
./gradlew assembleDebug -x lint

# Build release APK
./gradlew assembleRelease

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

### Web Interface
- **Location**: `config-user-web/index.html`
- **Purpose**: Admin control panel for animation scheduling and triggering
- **Features**: Real-time animation control across all devices
- **Usage**: Open in web browser for event management

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

## App Features (Production Version)

### Mobile App Enhancements
- **Portrait-only mode**: `android:screenOrientation="portrait"` prevents landscape rotation
- **Sleep prevention**: Wake lock system keeps screen on during animations
- **Immersive fullscreen**: System UI (status bar) hidden during animations
- **Leading zero formatting**: Seat numbers display as "01, 02" instead of "1, 2"
- **QR code scanning**: Automatic seat assignment via QR codes
- **Manual seat selection**: Venue/section/row/seat picker interface

### Production-Specific Features
- **Simplified UI**: Clean, minimal interface without debug information
- **"Animation Couleur" window**: Shows only "Prêt pour l'animation" status
- **Streamlined navigation**: Essential information only for easy use
- **Optimized performance**: Minimal UI elements for better performance
- **No debug information**: Clean user experience without technical details

## Supported Venues

### Event Types
- **🏟️ Stade de foot** (Football Stadium)
  - Tribune Nord, Sud, Est, Ouest
- **🎭 Salle de concert** (Concert Hall)
  - Orchestre, Mezzanine, Balcon
- **🎪 Théâtre** (Theater)
  - Parterre, Corbeille

### Seating Configuration
- **10 rows × 10 seats** per section
- **Leading zero formatting** (01, 02, 03...)
- **QR code support** for automatic seat assignment
- **Manual selection** with dropdown interface

## Security Notes

- Service account keys are gitignored for security
- Firebase rules control access to collections
- User authentication required for seat selection
- No sensitive information exposed in production UI

## Production Guidelines

### Deployment Best Practices
1. **Use this version for end users** - VersionAndroid is production-ready
2. **Clean interface** - No debug information or technical details
3. **Optimized performance** - Minimal UI for better user experience
4. **Test thoroughly** - Always test in VersionTestAndroid first
5. **Document changes** - Update both versions when making changes

### Differences from VersionTestAndroid
- **No Python testing scripts** - Clean production environment
- **Simplified debug information** - Essential information only
- **No development tools** - Optimized for end-user experience
- **Clean UI elements** - Minimal interface for better usability
- **No detailed logging** - Production-level logging only

## Development Workflow

### Making Changes
1. **Always test in VersionTestAndroid first**
2. **Use development tools** in VersionTestAndroid for debugging
3. **Port clean changes** to VersionAndroid for production
4. **Remove debug information** when porting to production
5. **Test production version** thoroughly before deployment

### Version Synchronization
- **Keep core functionality identical** between versions
- **Maintain same Firebase configuration** for both versions
- **Use same QR codes** for both versions
- **Document any differences** between versions clearly