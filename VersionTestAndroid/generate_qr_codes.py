#!/usr/bin/env python3
"""
Script de génération des QR codes pour chaque place du stade.
Génère des QR codes pour les places 1-10 en rang et 1-10 en siège.
"""

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

def generate_qr_codes():
    """
    Génère les QR codes pour toutes les places du stade
    """
    print("🎯 Génération des QR codes pour le stade...")
    
    # Créer le dossier de sortie
    output_dir = "qr_codes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    total_codes = 0
    
    # Générer QR codes pour chaque place
    for row in range(1, 11):  # Rangs 1-10
        for seat in range(1, 11):  # Sièges 1-10
            user_id = f"user_{row}_{seat}"
            
            # Configuration du QR code
            qr = qrcode.QRCode(
                version=1,  # Taille du QR code
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Ajouter les données (seulement le user_id)
            qr.add_data(user_id)
            qr.make(fit=True)
            
            # Créer l'image du QR code
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Créer une image plus grande avec du texte
            img_size = 400
            final_img = Image.new('RGB', (img_size, img_size + 60), 'white')
            
            # Redimensionner le QR code
            qr_img = qr_img.resize((img_size - 40, img_size - 40))
            
            # Coller le QR code au centre
            final_img.paste(qr_img, (20, 20))
            
            # Ajouter le texte en bas
            draw = ImageDraw.Draw(final_img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except OSError:
                font = ImageFont.load_default()
            
            text = f"Rang {row} - Siège {seat}"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (img_size - text_width) // 2
            
            draw.text((text_x, img_size - 30), text, fill="black", font=font)
            
            # Sauvegarder
            filename = f"{output_dir}/user_{row}_{seat}.png"
            final_img.save(filename)
            
            total_codes += 1
            
            if total_codes % 10 == 0:
                print(f"   Généré {total_codes} QR codes...")
    
    print(f"✅ {total_codes} QR codes générés dans le dossier '{output_dir}'")
    print(f"   Format: user_<rang>_<siège>.png")
    print(f"   Contenu QR: 'user_<rang>_<siège>'")
    print(f"   Couverture: 10 rangs × 10 sièges = 100 places")

def verify_qr_codes():
    """
    Vérifie quelques QR codes générés
    """
    print("\n🔍 Vérification des QR codes...")
    
    import cv2
    
    test_files = [
        "qr_codes/user_1_1.png",
        "qr_codes/user_5_5.png",
        "qr_codes/user_10_10.png"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            # Lire l'image
            img = cv2.imread(file_path)
            detector = cv2.QRCodeDetector()
            
            # Décoder le QR code
            data, vertices_array, binary_qrcode = detector.detectAndDecode(img)
            
            if data:
                print(f"   {file_path}: '{data}' ✅")
            else:
                print(f"   {file_path}: Erreur de lecture ❌")
        else:
            print(f"   {file_path}: Fichier introuvable ❌")

if __name__ == "__main__":
    generate_qr_codes()
    
    # Vérifier si opencv est disponible pour la vérification
    try:
        import cv2
        verify_qr_codes()
    except ImportError:
        print("\n💡 Pour vérifier les QR codes, installez opencv-python:")
        print("   pip install opencv-python")