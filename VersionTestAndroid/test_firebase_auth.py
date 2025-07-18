#!/usr/bin/env python3
"""
Script pour tester l'authentification Firebase
"""

import firebase_admin
from firebase_admin import credentials, storage

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

def test_firebase_auth():
    """
    Teste l'authentification Firebase
    """
    try:
        # Initialisation Firebase
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
        
        # Obtenir le bucket par défaut
        bucket = storage.bucket()
        print(f"✅ Bucket par défaut: {bucket.name}")
        
        # Lister quelques fichiers pour tester
        try:
            blobs = list(bucket.list_blobs(max_results=5))
            print(f"📂 Fichiers dans le bucket: {len(blobs)}")
            for blob in blobs:
                print(f"  - {blob.name}")
        except Exception as e:
            print(f"⚠️  Impossible de lister les fichiers: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'authentification: {e}")
        return False

if __name__ == "__main__":
    success = test_firebase_auth()
    if success:
        print("🎉 Authentification Firebase réussie!")
    else:
        print("💥 Échec de l'authentification")