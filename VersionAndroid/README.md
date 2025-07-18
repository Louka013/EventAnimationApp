# EventAnimationApp - VersionAndroid

## 📱 Production Version

This is the **production version** of EventAnimationApp, optimized for deployment to end users with a clean, minimal interface.

### Purpose
- Production deployment to end users
- Clean, simplified user interface
- Optimized performance for events
- Minimal debug information

### Features

#### 📱 **Mobile App Features**
- **QR Code scanning** for automatic seat assignment
- **Manual seat selection** with venue/section/row/seat chooser
- **Portrait-only mode** with landscape prevention
- **Sleep prevention** using Android wake locks
- **Immersive fullscreen** with hidden system UI
- **Leading zero formatting** for seat numbers (01, 02, etc.)
- **Real-time animation synchronization**
- **Simplified interface** with minimal information

#### 🎨 **Animation System**
- **Color-based animations** synchronized across devices
- **Frame-based timing** with precise millisecond control
- **Seat-specific targeting** for different venue sections
- **Multiple animation types** (flash, checkboard, custom)
- **Real-time Firebase synchronization**
- **Fullscreen animation display**

#### 🏟️ **Venue Support**
- **Stade de foot** (Football Stadium)
- **Salle de concert** (Concert Hall)
- **Théâtre** (Theater)
- **10x10 seating grid** per section

## Quick Start

### Prerequisites
- Android Studio Arctic Fox or later
- Android SDK API 21+ (Android 5.0)
- Firebase project with Firestore and Authentication

### Build Commands
```bash
# Build production APK
./gradlew assembleDebug

# Build without lint checks (faster)
./gradlew assembleDebug -x lint

# Build release APK
./gradlew assembleRelease

# Install on device
./gradlew installDebug

# Clean build
./gradlew clean
```

## Project Structure

```
VersionAndroid/
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
├── firebase.json              # Firebase configuration
├── firestore.rules           # Database security rules
└── README.md                  # This file
```

## App Interface

### Clean User Experience
- **Simplified waiting room** with minimal information
- **"Animation Couleur"** section shows only "Prêt pour l'animation"
- **Essential information only**: Seat details and basic status
- **No debug information** or technical details
- **Streamlined navigation** for easy use

### Animation Display
- **Fullscreen color animations** when triggered
- **Automatic return** to waiting room after animation
- **Immersive experience** with hidden system UI
- **Portrait-only orientation** for consistency

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

## Web Interface

### Admin Control Panel
- **Location**: `config-user-web/index.html`
- **Features**: Animation scheduling and triggering
- **Access**: Open in web browser for event management
- **Real-time control** of animations across all devices

## QR Code System

### Seat Assignment
- **Automatic scanning** via device camera
- **Venue-specific QR codes** for each seat
- **Instant seat assignment** upon successful scan
- **Backup manual selection** if QR scanning fails

### QR Code Library
- **Complete venue coverage** with QR codes for every seat
- **Standardized format** for consistent scanning
- **High-quality images** for reliable recognition

## Event Management

### Supported Events
- **🏟️ Football Stadium** (Stade de foot)
  - Tribune Nord, Sud, Est, Ouest
- **🎭 Concert Hall** (Salle de concert)
  - Orchestre, Mezzanine, Balcon
- **🎪 Theater** (Théâtre)
  - Parterre, Corbeille

### Seating System
- **10 rows × 10 seats** per section
- **Leading zero formatting** (01, 02, 03...)
- **Clear seat identification** in app interface
- **Real-time seat validation** with Firebase

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

## Performance Optimizations

### Mobile App
- **Portrait-only mode** prevents orientation changes
- **Wake lock management** keeps screen active during events
- **Immersive fullscreen** for distraction-free animations
- **Optimized Firebase queries** for fast data loading
- **Minimal UI elements** for better performance

### Animation System
- **Frame-based synchronization** for precise timing
- **Efficient color updates** with minimal CPU usage
- **Real-time listener optimization** for instant updates
- **Automatic cleanup** of resources after animations

## Deployment

### Production Checklist
1. ✅ **Build APK** with release configuration
2. ✅ **Firebase configuration** properly set up
3. ✅ **QR codes** deployed and accessible
4. ✅ **Web interface** configured for event management
5. ✅ **Testing** completed on target devices

### Event Setup
1. **Configure Firebase** with event-specific data
2. **Deploy QR codes** to physical venue locations
3. **Set up web interface** for event administrators
4. **Test animation system** with multiple devices
5. **Distribute app** to event participants

## Troubleshooting

### Common Issues
1. **QR scanning fails**: Ensure good lighting and camera permissions
2. **Animation not showing**: Check Firebase connection and seat assignment
3. **App crashes**: Verify Firebase configuration and permissions
4. **Screen goes to sleep**: Wake lock should prevent this automatically

### Support
- **Check Firebase Console** for backend issues
- **Verify QR code format** if scanning problems occur
- **Test with web interface** for manual animation triggering
- **Review app permissions** for camera and wake lock access

## Version Differences

### VersionAndroid (This Version)
- **Clean production interface**
- **Minimal debug information**
- **Optimized for end users**
- **Simplified UI elements**

### VersionTestAndroid (Development Version)
- **Full debug information**
- **Python testing scripts**
- **Development tools**
- **Detailed logging**

For development and testing, use **VersionTestAndroid**. For production deployment, use **VersionAndroid**.

## Security

- **Firebase Authentication** required for seat selection
- **Firestore security rules** control data access
- **No sensitive information** stored locally
- **Secure QR code validation** prevents unauthorized access