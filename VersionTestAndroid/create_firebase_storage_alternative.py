#!/usr/bin/env python3
"""
Alternative pour stocker les QR codes directement dans Firestore comme base64
au lieu de Firebase Storage, pour contourner les problèmes d'authentification.
"""

import os
import glob
import base64
from firebase_web_admin import FirebaseWebClient

def encode_qr_to_base64(file_path):
    """
    Encode un fichier QR en base64
    """
    with open(file_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def upload_qr_codes_to_firestore():
    """
    Upload tous les QR codes vers Firestore comme base64
    """
    print("🚀 Upload des QR codes vers Firestore (base64)...")
    
    # Vérifier que le dossier qr_codes existe
    qr_codes_dir = "qr_codes"
    if not os.path.exists(qr_codes_dir):
        print(f"❌ Le dossier '{qr_codes_dir}' n'existe pas. Exécutez d'abord generate_qr_codes.py")
        return
    
    # Initialiser Firebase
    fb = FirebaseWebClient()
    
    # Obtenir tous les fichiers QR
    qr_files = glob.glob(f"{qr_codes_dir}/user_*.png")
    
    if not qr_files:
        print(f"❌ Aucun fichier QR trouvé dans '{qr_codes_dir}'")
        return
    
    print(f"📦 {len(qr_files)} QR codes à uploader...")
    
    uploaded_count = 0
    
    for qr_file in qr_files:
        # Extraire le user_id du nom de fichier
        filename = os.path.basename(qr_file)
        user_id = filename.replace('.png', '')
        
        try:
            # Encoder le QR en base64
            base64_data = encode_qr_to_base64(qr_file)
            
            # Extraire rang et siège du user_id
            parts = user_id.split('_')
            if len(parts) != 3:
                print(f"   ⚠️ {user_id}: Format invalide")
                continue
                
            row = int(parts[1])
            seat = int(parts[2])
            
            # Données utilisateur
            user_data = {
                "userId": user_id,
                "row": row,
                "seat": seat,
                "qrCodeBase64": base64_data,
                "updatedAt": fb.get_current_timestamp()
            }
            
            # Enregistrer dans Firestore
            success = fb.set_document('users', user_id, user_data)
            
            if success:
                uploaded_count += 1
                print(f"   ✅ {user_id}: Upload terminé")
                
                if uploaded_count % 10 == 0:
                    print(f"   📊 Progression: {uploaded_count}/{len(qr_files)} uploadés")
            else:
                print(f"   ❌ {user_id}: Échec Firestore")
                
        except Exception as e:
            print(f"   ❌ {user_id}: Erreur - {e}")
    
    print(f"\n✅ Upload terminé!")
    print(f"   📤 QR codes uploadés: {uploaded_count}/{len(qr_files)}")
    print(f"   📝 Données stockées dans Firestore collection 'users'")
    print(f"   🔗 QR codes stockés comme base64 dans le champ 'qrCodeBase64'")

def verify_qr_uploads():
    """
    Vérifie quelques uploads pour s'assurer qu'ils fonctionnent
    """
    print("\n🔍 Vérification des uploads...")
    
    fb = FirebaseWebClient()
    
    test_users = ['user_1_1', 'user_5_5', 'user_10_10']
    
    for user_id in test_users:
        try:
            user_data = fb.get_document('users', user_id)
            
            if user_data and 'qrCodeBase64' in user_data:
                qr_data = user_data['qrCodeBase64']
                
                # Vérifier que les données base64 sont valides
                if qr_data.startswith('data:image/png;base64,'):
                    print(f"   ✅ {user_id}: QR base64 disponible ({len(qr_data)} caractères)")
                else:
                    print(f"   ❌ {user_id}: Format base64 invalide")
            else:
                print(f"   ❌ {user_id}: Pas de QR base64 dans Firestore")
                
        except Exception as e:
            print(f"   ❌ {user_id}: Erreur vérification - {e}")

def create_test_html():
    """
    Crée un fichier HTML de test pour afficher les QR codes
    """
    print("\n🌐 Création d'un fichier de test HTML...")
    
    fb = FirebaseWebClient()
    
    # Récupérer quelques QR codes pour test
    test_users = ['user_1_1', 'user_5_5', 'user_10_10']
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test QR Codes</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .qr-container { margin: 20px; padding: 20px; border: 1px solid #ccc; }
        .qr-code { max-width: 200px; border: 1px solid #000; }
    </style>
</head>
<body>
    <h1>Test QR Codes</h1>
"""
    
    for user_id in test_users:
        try:
            user_data = fb.get_document('users', user_id)
            
            if user_data and 'qrCodeBase64' in user_data:
                qr_data = user_data['qrCodeBase64']
                row = user_data.get('row', 'N/A')
                seat = user_data.get('seat', 'N/A')
                
                html_content += f"""
    <div class="qr-container">
        <h3>{user_id}</h3>
        <p>Rang: {row}, Siège: {seat}</p>
        <img src="{qr_data}" alt="QR Code {user_id}" class="qr-code">
    </div>
"""
            else:
                html_content += f"""
    <div class="qr-container">
        <h3>{user_id}</h3>
        <p>❌ QR code non trouvé</p>
    </div>
"""
                
        except Exception as e:
            html_content += f"""
    <div class="qr-container">
        <h3>{user_id}</h3>
        <p>❌ Erreur: {e}</p>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open('test_qr_codes.html', 'w') as f:
        f.write(html_content)
    
    print("   ✅ Fichier 'test_qr_codes.html' créé")
    print("   📖 Ouvrez ce fichier dans un navigateur pour voir les QR codes")

if __name__ == "__main__":
    upload_qr_codes_to_firestore()
    verify_qr_uploads()
    create_test_html()
    
    print("\n💡 Solution alternative:")
    print("   - Les QR codes sont stockés comme base64 dans Firestore")
    print("   - Pas besoin de Firebase Storage")
    print("   - L'app Android peut afficher les QR codes directement")
    print("   - Testez avec 'test_qr_codes.html'")