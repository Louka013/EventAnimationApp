# Dépendances Android à ajouter

Pour que le système QR code fonctionne, vous devez ajouter ces dépendances dans votre `app/build.gradle`:

## Dans le bloc `dependencies`:

```gradle
// CameraX
implementation "androidx.camera:camera-camera2:1.3.0"
implementation "androidx.camera:camera-lifecycle:1.3.0"
implementation "androidx.camera:camera-view:1.3.0"

// ML Kit pour scan QR codes
implementation 'com.google.mlkit:barcode-scanning:17.2.0'
```

## Dans le bloc `android` (si pas déjà présent):

```gradle
compileOptions {
    sourceCompatibility JavaVersion.VERSION_1_8
    targetCompatibility JavaVersion.VERSION_1_8
}

kotlinOptions {
    jvmTarget = '1.8'
}
```

## Permissions dans AndroidManifest.xml:

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="true" />
```

## Instructions d'utilisation des scripts Python:

1. **Générer les QR codes:**
   ```bash
   pip install qrcode[pil] opencv-python
   python generate_qr_codes.py
   ```

2. **Uploader vers Firebase:**
   ```bash
   python upload_qr_to_firebase.py
   ```

3. **Tester l'app:**
   - Construire l'app avec les nouvelles dépendances
   - Utiliser le bouton "📷 Scanner QR Code"
   - Scanner un QR code généré
   - Vérifier que les champs sont pré-remplis

## Fonctionnement:

1. **QR codes générés** contiennent: `user_<rang>_<siège>` (ex: `user_5_3`)
2. **Scan QR** → extraction du rang et siège → pré-remplissage automatique
3. **Transition** → va directement à l'étape 3 (validation)
4. **Validation** → fonctionne normalement comme avant

Les QR codes sont stockés dans Firebase Storage et les URLs dans Firestore collection `users`.