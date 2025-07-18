# Package Notification System

## 🎯 Visual Notifications for Animation Package Delivery

Users now receive immediate visual feedback when their personalized animation packages arrive, update, or are removed from the system.

## 🔧 Implementation Details

### 1. **Notification State Management** (MainActivity.kt:1183-1185)
```kotlin
// État pour les notifications de package
var showPackageNotification by remember { mutableStateOf(false) }
var packageNotificationMessage by remember { mutableStateOf("") }
```

### 2. **Notification Display Function** (MainActivity.kt:1200-1210)
```kotlin
fun showPackageNotification(message: String) {
    packageNotificationMessage = message
    showPackageNotification = true
    
    // Auto-hide after 3 seconds
    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.Main).launch {
        kotlinx.coroutines.delay(3000)
        showPackageNotification = false
    }
}
```

### 3. **Smart Notification Triggers** (MainActivity.kt:1223-1235)
```kotlin
// Show notification for different package events
if (previousPackage == null) {
    showPackageNotification("📦 Package d'animation reçu! ${animationPackage.frames.size} frames")
} else if (packageChanged) {
    showPackageNotification("🔄 Nouveau package d'animation! ${animationPackage.frames.size} frames")
} else if (packageRemoved) {
    showPackageNotification("📦 Package d'animation supprimé")
}
```

### 4. **Animated UI Component** (MainActivity.kt:1531-1546)
```kotlin
AnimatedVisibility(
    visible = showPackageNotification,
    enter = slideInVertically(initialOffsetY = { -it }) + fadeIn(),
    exit = slideOutVertically(targetOffsetY = { -it }) + fadeOut()
) {
    PackageNotification(message = packageNotificationMessage)
}
```

## 🎨 Visual Design

### **Notification Card** (MainActivity.kt:1593-1632)
```
┌─────────────────────────────────────────────────────┐
│  📱  Package d'animation reçu! 80 frames      ⏱️  │
└─────────────────────────────────────────────────────┘
```

**Features:**
- **Elevated Card**: Stands out with shadow and elevation
- **Icon + Message**: Clear visual communication
- **Auto-Hide Timer**: Disappears after 3 seconds
- **Slide Animation**: Smooth slide-in from top
- **Material Design**: Consistent with app theme

## 🚀 Notification Triggers

### **1. Package Received (First Time)**
```
Trigger: User enters waiting room + package available
Message: "📦 Package d'animation reçu! 80 frames"
Animation: Slide in from top
Duration: 3 seconds
```

### **2. Package Updated**
```
Trigger: New animation configured + different package
Message: "🔄 Nouveau package d'animation! 60 frames"
Animation: Slide in from top
Duration: 3 seconds
```

### **3. Package Removed**
```
Trigger: Animation expires or is deactivated
Message: "📦 Package d'animation supprimé"
Animation: Slide in from top
Duration: 3 seconds
```

## 📱 User Experience Flow

### **Scenario 1: User Enters Waiting Room**
1. **User selects seat** → Row 1, Seat 1
2. **User enters waiting room** → System fetches package
3. **Package arrives** → Notification slides in from top
4. **User sees**: "📦 Package d'animation reçu! 80 frames"
5. **Notification disappears** → After 3 seconds

### **Scenario 2: Real-Time Package Update**
1. **User in waiting room** → Watching for animations
2. **Admin configures new animation** → Via web interface
3. **New package arrives** → System detects change
4. **Notification appears** → "🔄 Nouveau package d'animation! 60 frames"
5. **Package details update** → In main UI

### **Scenario 3: Package Removal**
1. **User has active package** → Wave animation with 80 frames
2. **Animation expires** → System detects expiration
3. **Package removed** → From user's device
4. **Notification shows** → "📦 Package d'animation supprimé"
5. **UI updates** → Shows "no package available"

## 🎯 Notification Types

### **📦 Package Received**
- **When**: First time receiving a package
- **Icon**: 📦 (Package box)
- **Message**: "Package d'animation reçu! X frames"
- **Color**: Primary container (blue/green)

### **🔄 Package Updated**
- **When**: Package changes (different animation/frames)
- **Icon**: 🔄 (Refresh arrow)
- **Message**: "Nouveau package d'animation! X frames"
- **Color**: Primary container (blue/green)

### **📦 Package Removed**
- **When**: Animation expires or is deactivated
- **Icon**: 📦 (Package box)
- **Message**: "Package d'animation supprimé"
- **Color**: Primary container (blue/green)

## 🛡️ Smart Notification Logic

### **Avoids Spam:**
- Only shows notification when package actually changes
- Compares previous vs current package
- Checks userId, animationType, and frame count
- No notification for identical packages

### **Intelligent Timing:**
- Shows immediately when package arrives
- Auto-hides after 3 seconds
- Smooth animations (500ms in, 300ms out)
- Non-blocking overlay design

### **Visual Hierarchy:**
- Appears at top of screen
- Elevated above main content
- Clear typography and icons
- Consistent with Material Design

## 🎭 Animation Details

### **Slide In Animation:**
```kotlin
slideInVertically(
    initialOffsetY = { -it },  // Starts above screen
    animationSpec = tween(500)  // 500ms duration
) + fadeIn(animationSpec = tween(500))
```

### **Slide Out Animation:**
```kotlin
slideOutVertically(
    targetOffsetY = { -it },   // Moves above screen
    animationSpec = tween(300)  // 300ms duration
) + fadeOut(animationSpec = tween(300))
```

## 📊 Benefits

1. **✅ Immediate Feedback**: Users know exactly when their package arrives
2. **✅ Visual Confirmation**: Clear indication of package status changes
3. **✅ Non-Intrusive**: Auto-hides after 3 seconds
4. **✅ Smooth Animations**: Professional slide-in/out transitions
5. **✅ Smart Detection**: Only shows when packages actually change
6. **✅ Real-Time Updates**: Instant notifications for package changes

## 🧪 Testing

### **Test Package Notifications:**
1. **Start app** → Select Row 1, Seat 1
2. **Enter waiting room** → Watch for "Package reçu" notification
3. **Configure new animation** → Via web interface
4. **Observe update** → "Nouveau package" notification
5. **Wait for expiration** → "Package supprimé" notification

The notification system provides immediate, visual feedback to users about their animation package status!