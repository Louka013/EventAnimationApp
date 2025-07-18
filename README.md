<<<<<<< HEAD
# EventAnimationApp

A synchronized animation system for stadium events that provides real-time color-based animations across multiple Android devices using Firebase for backend synchronization.

## Project Structure

This project contains two main versions:

### 📱 **VersionAndroid** (Clean Distribution)
- **Path**: `EventAnimationApp/VersionAndroid/`
- **Purpose**: Clean, production-ready version for distribution
- **Features**: 
  - Simplified UI with minimal debug information
  - Portrait-only orientation lock
  - Sleep mode prevention
  - Wake lock management
  - Immersive fullscreen mode
  - QR code seat selection
  - Real-time animation synchronization

### 🧪 **VersionTestAndroid** (Development)
- **Path**: `EventAnimationApp/VersionTestAndroid/`
- **Purpose**: Development version with testing tools and debug information
- **Features**:
  - All features from VersionAndroid
  - Debug Python scripts for testing
  - Animation testing tools
  - Detailed logging and information display
  - Development documentation

## Key Features

### 🎨 **Animation System**
- **Real-time synchronization** across all connected devices
- **Color-based animations** using RGB frame data
- **Seat-specific targeting** for different venue sections
- **Frame-based timing** with precise millisecond control
- **Multiple animation types** (flash, checkboard, custom patterns)

### 🏟️ **Venue Support**
- **Stade de foot** (Football Stadium)
- **Salle de concert** (Concert Hall)
- **Théâtre** (Theater)
- **10x10 seat grid** per section for scalable coverage

### 📱 **Mobile App Features**
- **QR Code scanning** for automatic seat assignment
- **Manual seat selection** with venue/section/row/seat chooser
- **Portrait-only mode** with landscape prevention
- **Sleep prevention** using Android wake locks
- **Immersive fullscreen** with hidden system UI
- **Leading zero formatting** for seat numbers (01, 02, etc.)

### 🔥 **Firebase Backend**
- **Firestore database** for real-time data synchronization
- **Firebase Authentication** for user management
- **Cloud Functions** for server-side animation processing
- **Real-time listeners** for instant animation triggers
- **Scalable infrastructure** for large events

## Quick Start

### For VersionAndroid (Production)
```bash
cd EventAnimationApp/VersionAndroid
./gradlew assembleDebug
```

### For VersionTestAndroid (Development)
```bash
cd EventAnimationApp/VersionTestAndroid
./gradlew assembleDebug
```

## 🚀 Setup Guide for New Computer

### Prerequisites
Before running any version, ensure you have:
- **Java Development Kit (JDK)** 11 or higher
- **Android Studio** Arctic Fox or later
- **Git** for version control
- **Firebase account** with project access

### Step-by-Step Installation

#### 1. Install Android Studio
```bash
# Download Android Studio from:
# https://developer.android.com/studio

# Install Android SDK and required packages
# Accept Android SDK licenses when prompted
```

#### 2. Clone the Repository
```bash
# Clone the project repository
git clone <repository-url>
cd EventAnimationApp
```

#### 3. Firebase Configuration
```bash
# 1. Go to Firebase Console: https://console.firebase.google.com
# 2. Create or select your project
# 3. Enable Firestore Database and Authentication
# 4. Download google-services.json from Project Settings
# 5. Place the file in the appropriate app/ directory:

# For VersionAndroid:
cp google-services.json VersionAndroid/app/

# For VersionTestAndroid:
cp google-services.json VersionTestAndroid/app/
```

#### 4. Choose Your Version and Build

##### For Production (VersionAndroid):
```bash
# Navigate to production version
cd VersionAndroid

# Make gradlew executable (Linux/Mac)
chmod +x gradlew

# Build the project
./gradlew assembleDebug

# OR build without lint checks (faster)
./gradlew assembleDebug -x lint

# Install on connected device
./gradlew installDebug
```

##### For Development (VersionTestAndroid):
```bash
# Navigate to development version
cd VersionTestAndroid

# Make gradlew executable (Linux/Mac)
chmod +x gradlew

# Build the project
./gradlew assembleDebug

# OR build without lint checks (faster)
./gradlew assembleDebug -x lint

# Install on connected device
./gradlew installDebug
```

#### 5. Set Up Firebase Functions (Optional)
```bash
# Navigate to functions directory (from either version)
cd functions

# Install Node.js dependencies
npm install

# Deploy to Firebase (requires authentication)
npm run deploy

# OR start local emulator for testing
npm run serve
```

#### 6. Web Interface Setup
```bash
# The web interface is ready to use
# Open in browser: config-user-web/index.html
# No additional setup required
```

### 🔧 Development Environment Setup (VersionTestAndroid)

#### Python Testing Scripts
```bash
# Ensure Python 3.7+ is installed
python --version

# Install required Python packages (if any)
pip install firebase-admin google-cloud-firestore

# Run test scripts
python test_animation_config.py
python test_firebase_auth.py
python test_synchronized_system.py
```

### 📱 Device Setup

#### Android Device Requirements
```bash
# Enable Developer Options on your Android device:
# 1. Go to Settings > About Phone
# 2. Tap "Build Number" 7 times
# 3. Go to Settings > Developer Options
# 4. Enable "USB Debugging"
# 5. Connect device via USB
```

#### Verify Device Connection
```bash
# Check if device is recognized
adb devices

# Should show your device listed
```

### 🔥 Firebase Setup Verification

#### Test Firebase Connection
```bash
# From VersionTestAndroid, run:
python test_firebase_auth.py

# Should show successful connection
```

#### Configure Firestore Rules
```bash
# Deploy security rules
firebase deploy --only firestore:rules

# Rules file location: firestore.rules
```

### 🎯 Common Issues and Solutions

#### Build Errors
```bash
# If build fails with lint errors:
./gradlew assembleDebug -x lint

# If permission denied on gradlew:
chmod +x gradlew

# Clean and rebuild:
./gradlew clean
./gradlew assembleDebug
```

#### Firebase Issues
```bash
# If google-services.json is missing:
# Re-download from Firebase Console > Project Settings
# Ensure file is in app/ directory of your chosen version

# If Firebase functions fail to deploy:
# Check Firebase CLI installation: npm install -g firebase-tools
# Login to Firebase: firebase login
# Select project: firebase use <project-id>
```

#### Device Connection Issues
```bash
# If device not recognized:
# Check USB debugging is enabled
# Try different USB cable/port
# Install device drivers if needed

# List connected devices:
adb devices
```

### 🚀 First Run Checklist

- [ ] Android Studio installed and configured
- [ ] Repository cloned successfully
- [ ] Firebase project created and configured
- [ ] `google-services.json` file placed in correct app/ directory
- [ ] Android device connected and recognized
- [ ] Project builds successfully (`./gradlew assembleDebug`)
- [ ] App installs on device (`./gradlew installDebug`)
- [ ] Firebase connection verified (for VersionTestAndroid)
- [ ] Web interface accessible (config-user-web/index.html)

### 📝 Next Steps

1. **Test the app** on your device
2. **Configure seat layout** in Firebase
3. **Set up QR codes** for your venue
4. **Test animations** using the web interface
5. **Deploy to production** using VersionAndroid

## Requirements

- **Android Studio** Arctic Fox or later
- **Android SDK** API 21+ (Android 5.0)
- **Firebase project** with Firestore and Authentication
- **Google Services** configuration file (`google-services.json`)

## Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firestore Database and Authentication
3. Download `google-services.json` and place in `app/` directory
4. Deploy Firebase Functions from `functions/` directory

## Web Interface

The project includes a web-based configuration interface:
- **Location**: `config-user-web/index.html`
- **Purpose**: Admin interface for triggering animations
- **Features**: Animation scheduling, real-time monitoring

## Documentation

- **CLAUDE.md** - Development guide and project instructions
- **README_SYNCHRONIZED_ANIMATIONS.md** - Animation system documentation
- **README_QR.md** - QR code system guide

## Architecture

### Android App
- **Jetpack Compose** UI framework
- **Kotlin** programming language
- **Firebase SDK** for backend integration
- **CameraX** for QR code scanning
- **PowerManager** for wake lock management

### Firebase Backend
- **Node.js** Cloud Functions
- **Firestore** NoSQL database
- **Real-time listeners** for instant synchronization
- **Authentication** for user management

## Contributing

1. Use **VersionTestAndroid** for development
2. Test thoroughly with Python scripts
3. Clean changes can be ported to **VersionAndroid**
4. Follow existing code patterns and conventions

## License

This project is developed for stadium event animation systems.
=======
# menuEvent
>>>>>>> db2a808dd793f92ddb06d15ca80ea1d3cc679507
