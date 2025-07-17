#!/bin/bash

# Script pour configurer l'environnement virtuel et générer les QR codes

echo "🚀 Configuration de l'environnement QR codes..."

# Créer un environnement virtuel
python3 -m venv qr_env

# Activer l'environnement virtuel
source qr_env/bin/activate

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install qrcode[pil] opencv-python requests

# Vérifier l'installation
echo "✅ Vérification des dépendances..."
python -c "import qrcode, cv2, requests; print('Toutes les dépendances sont installées !')"

echo "🎯 Environnement prêt !"
echo ""
echo "Pour utiliser les scripts QR:"
echo "1. Activez l'environnement: source qr_env/bin/activate"
echo "2. Générez les QR codes: python generate_qr_codes.py"
echo "3. Uploadez vers Firebase: python upload_qr_to_firebase.py"
echo "4. Désactivez l'environnement: deactivate"