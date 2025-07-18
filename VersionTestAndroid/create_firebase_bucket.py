#!/usr/bin/env python3
"""
Script pour créer le bucket Firebase Storage
"""

import firebase_admin
from firebase_admin import credentials, storage
from google.cloud import storage as gcs

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
BUCKET_NAME = "data-base-test-6ef5f.firebasestorage.app"

def create_bucket():
    """
    Crée le bucket Firebase Storage
    """
    try:
        # Initialisation Firebase
        cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': BUCKET_NAME
        })
        
        # Créer le client Google Cloud Storage
        client = gcs.Client()
        
        # Tenter de créer le bucket
        try:
            bucket = client.create_bucket(BUCKET_NAME)
            print(f"✅ Bucket créé: {bucket.name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"ℹ️  Bucket existe déjà: {BUCKET_NAME}")
            else:
                print(f"❌ Erreur lors de la création du bucket: {e}")
                return False
        
        # Vérifier que le bucket existe
        try:
            bucket = client.bucket(BUCKET_NAME)
            bucket.reload()
            print(f"✅ Bucket accessible: {bucket.name}")
            return True
        except Exception as e:
            print(f"❌ Bucket non accessible: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return False

if __name__ == "__main__":
    success = create_bucket()
    if success:
        print("🎉 Bucket Firebase Storage prêt!")
    else:
        print("💥 Échec de la création du bucket")