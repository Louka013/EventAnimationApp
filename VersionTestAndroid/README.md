# EventAnimationApp - VersionTestAndroid

## 🧪 Development Version

This is the **development version** of EventAnimationApp with comprehensive testing tools and debug information.

### Purpose
- Development and testing of new features
- Debug information and detailed logging
- Testing scripts for animation system validation
- Development tools for Firebase integration

### Features

#### 📱 **Mobile App Features**
- **QR Code scanning** for automatic seat assignment
- **Manual seat selection** with venue/section/row/seat chooser
- **Portrait-only mode** with landscape prevention
- **Sleep prevention** using Android wake locks
- **Immersive fullscreen** with hidden system UI
- **Leading zero formatting** for seat numbers (01, 02, etc.)
- **Real-time animation synchronization**
- **Detailed debug information** in waiting room

#### 🔧 **Development Tools**
- **Python testing scripts** for animation validation
- **Debug logging** throughout the application
- **Animation testing utilities**
- **Firebase integration testing**
- **Performance monitoring tools**

#### 🎨 **Animation System**
- **Color-based animations** synchronized across devices
- **Frame-based timing** with precise millisecond control
- **Seat-specific targeting** for different venue sections
- **Multiple animation types** (flash, checkboard, custom)
- **Real-time Firebase synchronization**

## Quick Start

### Prerequisites
- Android Studio Arctic Fox or later
- Android SDK API 21+ (Android 5.0)
- Firebase project with Firestore and Authentication
- Python 3.7+ for testing scripts

### Build Commands
```bash
# Build debug APK
./gradlew assembleDebug

# Build without lint checks (faster)
./gradlew assembleDebug -x lint

# Install on device
./gradlew installDebug

# Run tests
./gradlew test

# Clean build
./gradlew clean
```

### Python Testing Scripts
```bash
# Test animation configuration
python test_animation_config.py

# Test Firebase authentication
python test_firebase_auth.py

# Test scheduled animations
python test_scheduled_animation.py

# Test synchronized system
python test_synchronized_system.py

# Test all functions
python test_all_functions.py
```

## Project Structure

```
VersionTestAndroid/
├── app/                          # Android app source code
│   ├── src/main/java/           # Kotlin source files
│   │   └── com/example/menuevent/
│   │       ├── MainActivity.kt   # Main app entry point
│   │       ├── SynchronizedAnimationScheduler.kt
│   │       └── TimeSynchronizationManager.kt
│   └── src/main/res/            # Android resources
├── functions/                   # Firebase Cloud Functions
│   ├── index.js                # Cloud Functions code
│   └── package.json            # Node.js dependencies
├── config-user-web/            # Web admin interface
│   └── index.html              # Animation control interface
├── qr_codes/                   # QR code images for seat assignment
├── test_*.py                   # Python testing scripts
├── *_flash_*.py               # Animation testing utilities
├── debug_*.py                 # Debug and analysis tools
├── firebase.json              # Firebase configuration
├── firestore.rules           # Database security rules
└── README.md                  # This file
```

## Venue Support

### Supported Venues
- **🏟️ Stade de foot** (Football Stadium)
  - Tribune Nord, Sud, Est, Ouest
- **🎭 Salle de concert** (Concert Hall)
  - Orchestre, Mezzanine, Balcon
- **🎪 Théâtre** (Theater)
  - Parterre, Corbeille

### Seating Configuration
- **10 rows × 10 seats** per section
- **QR codes** for each seat position
- **Automatic seat assignment** via QR scanning
- **Manual selection** with dropdown interface

## Firebase Configuration

### Required Setup
1. Create Firebase project at https://console.firebase.google.com
2. Enable Firestore Database and Authentication
3. Download `google-services.json` → place in `app/` directory
4. Deploy Cloud Functions: `cd functions && npm run deploy`

### Firestore Collections
- `seatSelections`: User seat assignments
- `animationConfigs`: Animation metadata and timing
- `userAnimationPackages`: Individual user animation data

## Development Guidelines

### Testing Workflow
1. **Test locally** with Python scripts
2. **Validate animations** with debug tools
3. **Check Firebase integration** with test utilities
4. **Verify synchronization** across multiple devices
5. **Document any issues** in debug reports

### Debug Information
- **Detailed logging** in Android logcat
- **Animation frame information** displayed in UI
- **Real-time update timestamps** shown
- **Firebase connection status** visible
- **Performance metrics** available

### Production Deployment
- **Clean changes** should be ported to VersionAndroid
- **Remove debug information** before production
- **Test thoroughly** in development environment first
- **Document breaking changes** for production version

## Testing Scripts

### Animation Testing
- `test_animation_config.py`: Validates animation configuration
- `test_scheduled_animation.py`: Tests animation scheduling
- `checkboard_flash_*.py`: Various checkerboard animation tests
- `blue_black_flash_*.py`: Flash animation testing

### Firebase Testing
- `test_firebase_auth.py`: Authentication testing
- `test_synchronized_system.py`: Full system synchronization
- `cleanup_firestore.py`: Database cleanup utilities

### Debug Tools
- `debug_animation_status.py`: Animation status monitoring
- `debug_user_coverage.py`: User coverage analysis
- `debug_package_issue.py`: Package delivery debugging

## Architecture

### Android App
- **Jetpack Compose** for modern UI
- **Kotlin** as primary language
- **Firebase SDK** for backend integration
- **CameraX** for QR code scanning
- **PowerManager** for wake lock management

### Backend
- **Node.js** Cloud Functions
- **Firestore** NoSQL database
- **Real-time listeners** for synchronization
- **Firebase Authentication** for user management

## Troubleshooting

### Common Issues
1. **Build failures**: Run `./gradlew clean` then rebuild
2. **Firebase connection**: Check `google-services.json` placement
3. **Animation timing**: Use debug tools to verify synchronization
4. **QR scanning**: Ensure camera permissions are granted

### Debug Resources
- Check `debug_*.py` scripts for specific issues
- Review Android logcat for detailed error messages
- Use web interface for manual animation testing
- Verify Firebase console for backend issues

## Contributing

1. **Always test in VersionTestAndroid first**
2. **Use Python scripts** for validation
3. **Document changes** thoroughly
4. **Test across multiple devices** when possible
5. **Follow existing code patterns** for consistency