#!/usr/bin/env python3
"""
Script pour étendre un GIF à 10 secondes en répétant l'animation
"""

from PIL import Image, ImageSequence
import sys

def extend_gif_to_10_seconds(input_path, output_path):
    """
    Étend un GIF à 10 secondes en répétant l'animation
    
    Args:
        input_path: Chemin vers le GIF d'entrée
        output_path: Chemin vers le GIF de sortie
    """
    
    # Ouvrir le GIF original
    original_gif = Image.open(input_path)
    
    # Extraire toutes les frames et leurs durées
    frames = []
    durations = []
    
    for frame in ImageSequence.Iterator(original_gif):
        frames.append(frame.copy())
        durations.append(frame.info.get('duration', 100))  # 100ms par défaut
    
    # Calculer la durée totale de l'animation originale
    total_duration = sum(durations)
    print(f"Animation originale: {len(frames)} frames, durée totale: {total_duration}ms")
    
    # Durée cible: 10 secondes = 10000ms
    target_duration = 10000
    
    # Calculer le nombre de répétitions nécessaires
    repetitions = target_duration // total_duration
    if target_duration % total_duration > 0:
        repetitions += 1
    
    print(f"Nombre de répétitions nécessaires: {repetitions}")
    
    # Créer la nouvelle séquence de frames
    extended_frames = []
    extended_durations = []
    
    current_duration = 0
    for rep in range(repetitions):
        for i, (frame, duration) in enumerate(zip(frames, durations)):
            if current_duration + duration <= target_duration:
                extended_frames.append(frame)
                extended_durations.append(duration)
                current_duration += duration
            else:
                # Ajuster la durée de la dernière frame si nécessaire
                remaining_duration = target_duration - current_duration
                if remaining_duration > 0:
                    extended_frames.append(frame)
                    extended_durations.append(remaining_duration)
                break
        
        if current_duration >= target_duration:
            break
    
    print(f"Animation étendue: {len(extended_frames)} frames, durée totale: {sum(extended_durations)}ms")
    
    # Sauvegarder le nouveau GIF
    extended_frames[0].save(
        output_path,
        save_all=True,
        append_images=extended_frames[1:],
        duration=extended_durations,
        loop=0  # Loop infini
    )
    
    print(f"✅ GIF étendu sauvegardé: {output_path}")

def main():
    input_file = "blue_black_flash.gif"
    output_file = "blue_black_flash_10s.gif"
    
    try:
        extend_gif_to_10_seconds(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ Fichier {input_file} non trouvé")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()