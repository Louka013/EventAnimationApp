#!/usr/bin/env python3
"""
Script de test pour traiter l'animation sans Firebase
"""

import io
import os
from PIL import Image, ImageSequence

# Configuration
INPUT_PATH = "blue_black_flash_10s.gif"
ROWS = 10
COLS = 10

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

def process_animation(frames, rows, cols):
    """
    Traite l'animation et génère des statistiques
    
    Args:
        frames: Liste des frames PIL
        rows: Nombre de lignes
        cols: Nombre de colonnes
        
    Returns:
        dict: Statistiques du traitement
    """
    frame_count = len(frames)
    if frame_count == 0:
        raise ValueError("Aucune frame trouvée")
    
    # Taille fixe pour toutes les images
    tile_w, tile_h = 100, 100
    
    print(f"Génération d'images unicolores pour {rows}x{cols} utilisateurs")
    print(f"Traitement de {frame_count} frames...")
    
    colors = []
    
    for f_idx, frame in enumerate(frames):
        print(f"Processing frame {f_idx + 1}/{frame_count}")
        
        # Extraire la couleur moyenne de la frame
        avg_color = get_average_color(frame)
        colors.append(avg_color)
        print(f"  Couleur moyenne: RGB{avg_color}")
        
        # Créer une image unicolore (test)
        solid_image = create_solid_color_image(avg_color, tile_w, tile_h)
        
        # Sauvegarder un exemple pour vérification
        if f_idx == 0:
            solid_image.save(f"test_frame_{f_idx}_color.png")
            print(f"  Image test sauvegardée: test_frame_{f_idx}_color.png")
    
    total_users = rows * cols
    total_images = frame_count * total_users
    
    return {
        "frame_count": frame_count,
        "total_users": total_users,
        "total_images": total_images,
        "colors": colors
    }

def main():
    """
    Fonction principale
    """
    try:
        print(f"📁 Lecture du fichier: {INPUT_PATH}")
        frames, frame_duration = extract_frames(INPUT_PATH)
        
        print(f"🎞 {len(frames)} frames extraites (durée: {frame_duration}ms)")
        
        print("🔪 Traitement de l'animation...")
        stats = process_animation(frames, ROWS, COLS)
        
        print("✅ Traitement terminé.")
        print(f"📊 Statistiques:")
        print(f"   - Frames: {stats['frame_count']}")
        print(f"   - Utilisateurs: {stats['total_users']}")
        print(f"   - Images totales à générer: {stats['total_images']}")
        print(f"   - Couleurs détectées: {len(set(stats['colors']))}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        raise

if __name__ == "__main__":
    main()