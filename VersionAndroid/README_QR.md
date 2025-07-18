# 📷 Système QR Code - Guide d'Installation

## 🔧 Solution pour l'erreur `externally-managed-environment`

Votre système Ubuntu/Debian protège l'environnement Python global. Voici comment procéder :

### 📋 **Méthode 1 : Environnement Virtuel (Recommandée)**

```bash
# 1. Exécuter le script de configuration
./setup_qr_env.sh

# 2. Activer l'environnement
source qr_env/bin/activate

# 3. Générer les QR codes
python generate_qr_codes.py

# 4. Uploader vers Firebase
python upload_qr_to_firebase.py

# 5. Désactiver l'environnement
deactivate
```

### 📋 **Méthode 2 : Installation Système**

```bash
# Installer les paquets système
sudo apt update
sudo apt install python3-qrcode python3-opencv python3-requests python3-pil

# Utiliser directement
python3 generate_qr_codes.py
python3 upload_qr_to_firebase.py
```

### 📋 **Méthode 3 : Avec pipx (Applications)**

```bash
# Installer pipx si pas déjà fait
sudo apt install pipx

# Créer un environnement isolé
pipx install qrcode[pil]
pipx install opencv-python
pipx install requests
```

## 🎯 **Étapes Complètes**

### 1. **Préparer l'environnement**
```bash
./setup_qr_env.sh
source qr_env/bin/activate
```

### 2. **Générer les QR codes**
```bash
python generate_qr_codes.py
```
- Crée 100 QR codes dans `qr_codes/`
- Format: `user_<rang>_<siège>.png`
- Contenu: `user_5_3` (par exemple)

### 3. **Uploader vers Firebase**
```bash
python upload_qr_to_firebase.py
```
- Upload vers Firebase Storage
- Enregistre URLs dans Firestore
- Collection `users` avec champ `qrUrl`

### 4. **Vérifier**
- Ouvrir Firebase Console
- Vérifier Storage → `qrcodes/`
- Vérifier Firestore → collection `users`

## 📱 **Application Android**

### Ajouter les dépendances dans `app/build.gradle`:
```gradle
dependencies {
    // CameraX
    implementation "androidx.camera:camera-camera2:1.3.0"
    implementation "androidx.camera:camera-lifecycle:1.3.0"
    implementation "androidx.camera:camera-view:1.3.0"
    
    // ML Kit
    implementation 'com.google.mlkit:barcode-scanning:17.2.0'
}
```

### Permissions dans `AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="true" />
```

## 🎯 **Test du Système**

1. **Générer QR codes** → vérifier dossier `qr_codes/`
2. **Uploader Firebase** → vérifier Storage et Firestore
3. **Builder app** → avec nouvelles dépendances
4. **Scanner QR** → bouton "📷 Scanner QR Code"
5. **Vérifier** → rang et siège pré-remplis

## 🔧 **Dépannage**

### Si l'environnement virtuel ne marche pas:
```bash
# Forcer l'installation (non recommandé)
pip install --break-system-packages qrcode[pil] opencv-python

# Ou utiliser conda si disponible
conda install qrcode opencv pillow requests
```

### Si Firebase ne fonctionne pas:
- Vérifier `firebase_web_admin.py` existe
- Vérifier configuration Firebase
- Tester avec un QR code manuellement

Le système est maintenant prêt à être déployé ! 🚀