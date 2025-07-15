#!/usr/bin/env python3
"""
Script pour nettoyer Firestore - supprimer toutes les animations sauf blue_black_flash
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Configuration
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"
KEEP_ANIMATION = "blue_black_flash"  # Animation à conserver

def cleanup_firestore():
    """
    Nettoie Firestore en gardant seulement l'animation spécifiée
    """
    try:
        # Initialisation Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Obtenir toutes les animations
        animations_ref = db.collection("animations")
        animations = animations_ref.stream()
        
        animations_found = []
        animations_to_delete = []
        
        print("🔍 Analyse des animations dans Firestore...")
        
        for anim in animations:
            animation_id = anim.id
            animations_found.append(animation_id)
            
            if animation_id != KEEP_ANIMATION:
                animations_to_delete.append(animation_id)
                print(f"❌ À supprimer: {animation_id}")
            else:
                print(f"✅ À conserver: {animation_id}")
        
        if not animations_found:
            print("ℹ️  Aucune animation trouvée dans Firestore")
            return
        
        print(f"\n📊 Résumé:")
        print(f"   - Total animations trouvées: {len(animations_found)}")
        print(f"   - Animations à supprimer: {len(animations_to_delete)}")
        print(f"   - Animations à conserver: 1 ({KEEP_ANIMATION})")
        
        if not animations_to_delete:
            print("✅ Aucune animation à supprimer - Firestore est déjà propre!")
            return
        
        # Confirmer avant suppression
        print(f"\n⚠️  Êtes-vous sûr de vouloir supprimer ces animations ?")
        for anim_id in animations_to_delete:
            print(f"   - {anim_id}")
        
        response = input("\nTaper 'OUI' pour confirmer la suppression: ")
        if response.upper() != 'OUI':
            print("❌ Suppression annulée")
            return
        
        # Supprimer les animations
        print("\n🗑️  Suppression des animations...")
        
        for animation_id in animations_to_delete:
            try:
                # Supprimer d'abord tous les utilisateurs de cette animation
                users_ref = animations_ref.document(animation_id).collection("users")
                users = users_ref.stream()
                
                user_count = 0
                for user in users:
                    user.reference.delete()
                    user_count += 1
                
                # Supprimer le document principal de l'animation
                animations_ref.document(animation_id).delete()
                
                print(f"✅ Supprimé: {animation_id} ({user_count} utilisateurs)")
                
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {animation_id}: {e}")
        
        print(f"\n🎉 Nettoyage terminé!")
        print(f"   - Animations supprimées: {len(animations_to_delete)}")
        print(f"   - Animation conservée: {KEEP_ANIMATION}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

def list_animations():
    """
    Liste toutes les animations dans Firestore
    """
    try:
        # Initialisation Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Obtenir toutes les animations
        animations_ref = db.collection("animations")
        animations = animations_ref.stream()
        
        print("📋 Animations dans Firestore:")
        
        found_any = False
        for anim in animations:
            found_any = True
            animation_data = anim.to_dict()
            
            print(f"\n🎬 {anim.id}:")
            print(f"   - Frame Rate: {animation_data.get('frameRate', 'N/A')}")
            print(f"   - Frame Count: {animation_data.get('frameCount', 'N/A')}")
            print(f"   - Type: {animation_data.get('type', 'N/A')}")
            print(f"   - Start Time: {animation_data.get('startTime', 'N/A')}")
            
            # Compter les utilisateurs
            users_ref = animations_ref.document(anim.id).collection("users")
            users = users_ref.stream()
            user_count = sum(1 for _ in users)
            print(f"   - Utilisateurs: {user_count}")
        
        if not found_any:
            print("ℹ️  Aucune animation trouvée dans Firestore")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_animations()
    else:
        cleanup_firestore()