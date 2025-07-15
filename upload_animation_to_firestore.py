#!/usr/bin/env python3
"""
Script pour uploader une animation vers Firestore uniquement (sans Storage)
Stocke les couleurs directement dans la base de données
"""

import os
from PIL import Image, ImageSequence
import firebase_admin
from firebase_admin import credentials, firestore

# Configuration
INPUT_PATH = "blue_black_flash_10s.gif"
ROWS = 30
COLS = 40
ANIMATION_ID = "blue_black_flash"
START_TIME = "2025-07-15T20:00:00Z"
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

# Initialisation Firebase
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()


def get_average_color(frame):
    """
    Calcule la couleur moyenne d'une frame
    
    Args:
        frame: Image PIL
        
    Returns:
        dict: {"r": int, "g": int, "b": int}
    """
    # Convertir en mode RGB si nécessaire
    if frame.mode != 'RGB':
        frame = frame.convert('RGB')
    
    # Obtenir toutes les couleurs des pixels
    pixels = list(frame.getdata())
    
    # Calculer la moyenne pour chaque canal
    r_sum = sum(pixel[0] for pixel in pixels)
    g_sum = sum(pixel[1] for pixel in pixels)
    b_sum = sum(pixel[2] for pixel in pixels)
    
    pixel_count = len(pixels)
    
    avg_r = r_sum // pixel_count
    avg_g = g_sum // pixel_count
    avg_b = b_sum // pixel_count
    
    return {"r": avg_r, "g": avg_g, "b": avg_b}


def extract_frames(path):
    """
    Extrait les frames d'un GIF
    
    Args:
        path: Chemin vers le fichier GIF
        
    Returns:
        tuple: (frames, frame_duration_ms)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier {path} n'existe pas")
    
    ext = path.lower().split('.')[-1]
    
    if ext == "gif":
        gif = Image.open(path)
        frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(gif)]
        duration = gif.info.get("duration", 100)  # durée en ms
        return frames, duration
    else:
        # Pour les autres formats, on peut essayer de les ouvrir comme une image
        # et supposer qu'il s'agit d'une seule frame
        try:
            img = Image.open(path)
            frames = [img.convert('RGB')]
            duration = 1000  # 1 seconde par défaut
            return frames, duration
        except Exception:
            raise ValueError(f"Format de fichier non supporté: {ext}")


def process_and_upload(frames, rows, cols, animation_id):
    """
    Traite les frames et stocke les couleurs dans Firestore
    
    Args:
        frames: Liste des frames PIL
        rows: Nombre de lignes
        cols: Nombre de colonnes
        animation_id: ID de l'animation
        
    Returns:
        tuple: (user_data, frame_count)
    """
    frame_count = len(frames)
    if frame_count == 0:
        raise ValueError("Aucune frame trouvée")
    
    user_data = {}  # Pour stocker les couleurs par utilisateur
    
    print(f"Traitement de {frame_count} frames pour {rows}x{cols} utilisateurs")
    
    for f_idx, frame in enumerate(frames):
        print(f"Processing frame {f_idx + 1}/{frame_count}")
        
        # Extraire la couleur moyenne de la frame
        avg_color = get_average_color(frame)
        print(f"  Couleur moyenne: RGB({avg_color['r']}, {avg_color['g']}, {avg_color['b']})")
        
        # Stocker la couleur pour tous les utilisateurs
        for r in range(rows):
            for c in range(cols):
                user_id = f"user_{r+1}_{c+1}"
                if user_id not in user_data:
                    user_data[user_id] = []
                user_data[user_id].append(avg_color)
    
    return user_data, frame_count


def upload_firestore_data(animation_id, user_data, frame_count, frame_duration, start_time):
    """
    Crée les documents Firestore pour l'animation
    
    Args:
        animation_id: ID de l'animation
        user_data: Dictionnaire {user_id: [colors]}
        frame_count: Nombre total de frames
        frame_duration: Durée d'une frame en ms
        start_time: Heure de début de l'animation
    """
    print("Création des documents Firestore...")
    
    # Document principal de l'animation
    animation_ref = db.collection("animations").document(animation_id)
    animation_ref.set({
        "animationId": animation_id,
        "frameRate": int(1000 / frame_duration),
        "frameCount": frame_count,
        "startTime": start_time,
        "type": "color_animation"  # Nouveau type pour les animations couleur
    })
    
    print(f"✅ Document animation créé: {animation_id}")
    
    # Documents des utilisateurs avec couleurs
    users_ref = animation_ref.collection("users")
    
    # Traitement par batch pour optimiser les écritures
    batch_size = 500
    batch = db.batch()
    batch_count = 0
    
    for user_id, colors in user_data.items():
        user_doc_ref = users_ref.document(user_id)
        
        # Créer le document utilisateur
        user_doc_data = {
            "userId": user_id,
            "colors": colors,  # Liste des couleurs pour chaque frame
            "startTime": start_time,
            "frameCount": len(colors)
        }
        
        batch.set(user_doc_ref, user_doc_data)
        batch_count += 1
        
        # Commit du batch s'il est plein
        if batch_count >= batch_size:
            batch.commit()
            print(f"📦 Batch committé: {batch_count} utilisateurs")
            batch = db.batch()
            batch_count = 0
    
    # Commit du dernier batch
    if batch_count > 0:
        batch.commit()
        print(f"📦 Dernier batch committé: {batch_count} utilisateurs")
    
    print(f"✅ {len(user_data)} utilisateurs créés dans Firestore")


def main():
    """
    Fonction principale
    """
    try:
        print(f"📁 Lecture du fichier: {INPUT_PATH}")
        frames, frame_duration = extract_frames(INPUT_PATH)
        
        print(f"🎞 {len(frames)} frames extraites (durée: {frame_duration}ms)")
        
        print("🎨 Traitement des couleurs...")
        user_data, frame_count = process_and_upload(frames, ROWS, COLS, ANIMATION_ID)
        
        print("🔥 Upload vers Firestore...")
        upload_firestore_data(ANIMATION_ID, user_data, frame_count, frame_duration, START_TIME)
        
        print("✅ Animation entièrement publiée dans Firestore.")
        print(f"📊 Statistiques:")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Frames: {frame_count}")
        print(f"   - Utilisateurs: {len(user_data)}")
        print(f"   - Grille: {ROWS}x{COLS}")
        print(f"   - Couleurs stockées: {frame_count * len(user_data)}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    main()