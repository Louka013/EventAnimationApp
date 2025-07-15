#!/usr/bin/env python3
"""
Script pour uploader une animation découpée vers Firebase Storage et Firestore
"""

import io
import os
from PIL import Image, ImageSequence
import firebase_admin
from firebase_admin import credentials, storage, firestore

# Configuration
INPUT_PATH = "blue_black_flash_10s.gif"
ROWS = 30
COLS = 40
ANIMATION_ID = "blue_black_flash"
START_TIME = "2025-07-15T20:00:00Z"
BUCKET_NAME = "data-base-test-6ef5f.appspot.com"
SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

# Initialisation Firebase
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()
bucket = storage.bucket()


def extract_frames(path):
    """
    Extrait les frames d'un GIF ou d'une vidéo
    
    Args:
        path: Chemin vers le fichier GIF ou vidéo
        
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


def get_average_color(frame):
    """
    Calcule la couleur moyenne d'une frame
    
    Args:
        frame: Image PIL
        
    Returns:
        tuple: (r, g, b) couleur moyenne
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
    
    return (avg_r, avg_g, avg_b)


def create_solid_color_image(color, width, height):
    """
    Crée une image unicolore
    
    Args:
        color: tuple (r, g, b)
        width: largeur de l'image
        height: hauteur de l'image
        
    Returns:
        Image PIL
    """
    return Image.new('RGB', (width, height), color)


def slice_and_upload(frames, rows, cols, animation_id):
    """
    Extrait la couleur moyenne de chaque frame et crée des images unicolores pour chaque utilisateur
    
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
    
    # Taille fixe pour toutes les images (par exemple 100x100)
    tile_w, tile_h = 100, 100
    user_data = {}  # Pour stocker les URLs par utilisateur
    
    print(f"Génération d'images unicolores pour {rows}x{cols} utilisateurs")
    print(f"Upload de {frame_count} frames...")
    
    for f_idx, frame in enumerate(frames):
        print(f"Processing frame {f_idx + 1}/{frame_count}")
        
        # Extraire la couleur moyenne de la frame
        avg_color = get_average_color(frame)
        print(f"  Couleur moyenne: RGB{avg_color}")
        
        # Créer une image unicolore pour tous les utilisateurs
        solid_image = create_solid_color_image(avg_color, tile_w, tile_h)
        
        # Convertir en binaire une seule fois
        img_bytes = io.BytesIO()
        solid_image.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        # Upload pour chaque utilisateur
        for r in range(rows):
            for c in range(cols):
                # Reset du buffer pour chaque upload
                img_bytes = io.BytesIO(img_data)
                
                # Upload vers Firebase Storage
                path = f"animations/{animation_id}/{r+1}_{c+1}/frame_{f_idx:03d}.png"
                blob = bucket.blob(path)
                blob.upload_from_file(img_bytes, content_type="image/png")
                blob.make_public()
                
                # Enregistrer URL
                user_id = f"user_{r+1}_{c+1}"
                if user_id not in user_data:
                    user_data[user_id] = []
                user_data[user_id].append(blob.public_url)
    
    return user_data, frame_count


def upload_firestore_metadata(animation_id, user_data, frame_count, frame_duration, start_time):
    """
    Crée les documents Firestore pour l'animation
    
    Args:
        animation_id: ID de l'animation
        user_data: Dictionnaire {user_id: [urls]}
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
        "startTime": start_time
    })
    
    # Documents des utilisateurs
    users_ref = animation_ref.collection("users")
    for user_id, urls in user_data.items():
        users_ref.document(user_id).set({
            "frames": urls,
            "startTime": start_time
        })
    
    print(f"✅ {len(user_data)} utilisateurs créés dans Firestore")


def main():
    """
    Fonction principale
    """
    try:
        print(f"📁 Lecture du fichier: {INPUT_PATH}")
        frames, frame_duration = extract_frames(INPUT_PATH)
        
        print(f"🎞 {len(frames)} frames extraites (durée: {frame_duration}ms)")
        
        print("🔪 Découpage et upload vers Firebase Storage...")
        user_data, frame_count = slice_and_upload(frames, ROWS, COLS, ANIMATION_ID)
        
        print("🔥 Upload des métadonnées vers Firestore...")
        upload_firestore_metadata(ANIMATION_ID, user_data, frame_count, frame_duration, START_TIME)
        
        print("✅ Animation entièrement publiée dans Firebase.")
        print(f"📊 Statistiques:")
        print(f"   - Animation ID: {ANIMATION_ID}")
        print(f"   - Frames: {frame_count}")
        print(f"   - Utilisateurs: {len(user_data)}")
        print(f"   - Grille: {ROWS}x{COLS}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise


if __name__ == "__main__":
    main()