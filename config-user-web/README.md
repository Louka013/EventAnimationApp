# ConfigUser Web Application

## Overview
This web application allows configuration users to set up animation parameters for different events. The configurations are stored in Firebase Firestore.

## Features
- 🕐 **Time Selection**: Choose when the animation should start
- 🏟️ **Event Selection**: Select the type of event (football stadium, theater, concert hall, etc.)
- ✨ **Animation Selection**: Choose the type of animation to display
- 💾 **Firebase Integration**: All configurations are saved to Firestore
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Firebase Structure
The application creates a new collection called `animation_configs` with the following structure:

```json
{
  "animationStartTime": "2024-01-15T19:30:00",
  "eventType": "football_stadium",
  "animationType": "wave",
  "createdAt": "Firebase ServerTimestamp",
  "status": "active"
}
```

## Available Event Types
- 🏈 Football Stadium
- 🎭 Theater
- 🎵 Concert Hall
- 🏟️ Sports Arena
- 📊 Conference Center
- 🎬 Cinema

## Available Animation Types
- 🌊 Wave Effect
- ⚡ Flash Lighting
- 🌈 Rainbow
- 💓 Pulse
- ✨ Sparkle
- 🌊 Cascade
- 🌀 Spiral
- 🎆 Fireworks

## Usage
1. Open `index.html` in a web browser
2. Select the animation start time
3. Choose the event type
4. Select the animation type
5. Review the configuration preview
6. Click "Save Configuration" to store in Firebase

## Firebase Configuration
The application uses the Firebase project with ID: `data-base-test-6ef5f`

## Files
- `index.html` - Main web application file with embedded CSS and JavaScript
- `README.md` - This documentation file