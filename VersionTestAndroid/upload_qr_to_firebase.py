#!/usr/bin/env python3
"""
Script pour uploader les QR codes vers Firebase Storage et enregistrer les URLs dans Firestore.
"""

import os
import glob
from firebase_web_admin import FirebaseWebClient
import requests
import json
import mimetypes

def upload_qr_codes_to_firebase():
    """
    Upload tous les QR codes vers Firebase Storage et enregistre les URLs dans Firestore
    """
    print("🚀 Upload des QR codes vers Firebase Storage...")
    
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
    updated_users = 0
    
    for qr_file in qr_files:
        # Extraire le user_id du nom de fichier
        filename = os.path.basename(qr_file)
        user_id = filename.replace('.png', '')
        
        try:
            # Upload vers Firebase Storage
            storage_path = f"qrcodes/{filename}"
            download_url = upload_to_firebase_storage(qr_file, storage_path)
            
            if download_url:
                uploaded_count += 1
                print(f"   ✅ {user_id}: Upload terminé")
                
                # Enregistrer l'URL dans Firestore
                success = update_user_qr_url(fb, user_id, download_url)
                if success:
                    updated_users += 1
                    
                if uploaded_count % 10 == 0:
                    print(f"   📊 Progression: {uploaded_count}/{len(qr_files)} uploadés")
                    
            else:
                print(f"   ❌ {user_id}: Échec upload")
                
        except Exception as e:
            print(f"   ❌ {user_id}: Erreur - {e}")
    
    print(f"\n✅ Upload terminé!")
    print(f"   📤 QR codes uploadés: {uploaded_count}/{len(qr_files)}")
    print(f"   📝 Utilisateurs mis à jour: {updated_users}")
    print(f"   🔗 URLs stockées dans Firestore collection 'users'")

def upload_to_firebase_storage(file_path, storage_path):
    """
    Upload un fichier vers Firebase Storage et retourne l'URL de téléchargement
    """
    try:
        # Configuration Firebase
        project_id = "data-base-test-6ef5f"
        api_key = "AIzaSyAWGEHQK8f61d4OCgreDRu0fXUjt_sG14w"
        
        # Lire le fichier
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Déterminer le type MIME
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'image/png'
        
        # URL d'upload Firebase Storage avec authentification
        upload_url = f"https://firebasestorage.googleapis.com/v0/b/{project_id}.appspot.com/o"
        
        # Paramètres d'upload avec clé API
        params = {
            'name': storage_path,
            'uploadType': 'media',
            'key': api_key
        }
        
        headers = {
            'Content-Type': mime_type
        }
        
        # Effectuer l'upload
        response = requests.post(upload_url, params=params, headers=headers, data=file_data)
        
        if response.status_code == 200:
            # Générer l'URL de téléchargement public
            encoded_path = requests.utils.quote(storage_path, safe='')
            download_url = f"https://firebasestorage.googleapis.com/v0/b/{project_id}.appspot.com/o/{encoded_path}?alt=media"
            return download_url
        else:
            print(f"   ❌ Erreur upload: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Erreur upload: {e}")
        return None

def update_user_qr_url(fb, user_id, qr_url):
    """
    Met à jour ou crée un document utilisateur avec l'URL du QR code
    """
    try:
        # Extraire rang et siège du user_id
        parts = user_id.split('_')
        if len(parts) != 3:
            print(f"   ⚠️ {user_id}: Format invalide")
            return False
            
        row = int(parts[1])
        seat = int(parts[2])
        
        # Données utilisateur
        user_data = {
            "userId": user_id,
            "row": row,
            "seat": seat,
            "qrUrl": qr_url,
            "updatedAt": fb._get_current_timestamp()
        }
        
        # Enregistrer dans Firestore
        success = fb.set_document('users', user_id, user_data)
        
        if success:
            return True
        else:
            print(f"   ❌ {user_id}: Échec Firestore")
            return False
            
    except Exception as e:
        print(f"   ❌ {user_id}: Erreur Firestore - {e}")
        return False

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
            
            if user_data and 'qrUrl' in user_data:
                qr_url = user_data['qrUrl']
                
                # Tester l'accès à l'URL
                response = requests.head(qr_url, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ {user_id}: QR accessible")
                else:
                    print(f"   ❌ {user_id}: QR non accessible ({response.status_code})")
            else:
                print(f"   ❌ {user_id}: Pas de QR URL dans Firestore")
                
        except Exception as e:
            print(f"   ❌ {user_id}: Erreur vérification - {e}")

if __name__ == "__main__":
    upload_qr_codes_to_firebase()
    verify_qr_uploads()
    
    print("\n💡 Pour tester les QR codes:")
    print("   1. Ouvrez Firestore Console")
    print("   2. Allez dans la collection 'users'")
    print("   3. Vérifiez que les documents ont un champ 'qrUrl'")
    print("   4. Testez l'URL dans un navigateur")