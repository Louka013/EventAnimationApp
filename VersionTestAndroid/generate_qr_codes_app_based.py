#!/usr/bin/env python3
"""
Script pour générer des QR codes basés sur les événements et tribunes de l'app
Configuration exacte selon MainActivity.kt :
- Stade de foot : Tribune Nord, Tribune Sud, Tribune Est, Tribune Ouest
- Salle de concert : Balcon, Orchestre, Mezzanine
- Théâtre : Parterre, Corbeille, Poulailler
"""

import qrcode
import os
import cv2
import json

def generate_qr_codes():
    """
    Génère des QR codes pour tous les événements et tribunes disponibles dans l'app
    """
    print("🚀 Génération des QR codes basés sur l'app...")
    
    # Configuration 10x10 maximum par tribune
    events_config = {
        "Stade de foot": {
            "Tribune Nord": {"rangs": 10, "sieges": 10},
            "Tribune Sud": {"rangs": 10, "sieges": 10},
            "Tribune Est": {"rangs": 10, "sieges": 10},
            "Tribune Ouest": {"rangs": 10, "sieges": 10}
        },
        "Salle de concert": {
            "Balcon": {"rangs": 10, "sieges": 10},
            "Orchestre": {"rangs": 10, "sieges": 10},
            "Mezzanine": {"rangs": 10, "sieges": 10}
        },
        "Théâtre": {
            "Parterre": {"rangs": 10, "sieges": 10},
            "Corbeille": {"rangs": 10, "sieges": 10},
            "Poulailler": {"rangs": 10, "sieges": 10}
        }
    }
    
    # Créer le dossier de sortie
    output_dir = "qr_codes"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Dossier '{output_dir}' créé")
    
    generated_count = 0
    qr_codes_info = []
    
    # Générer pour chaque événement/tribune/rang/siège
    for event, tribunes in events_config.items():
        for tribune, config in tribunes.items():
            max_rangs = config["rangs"]
            max_sieges = config["sieges"]
            
            for rang in range(1, max_rangs + 1):
                for siege in range(1, max_sieges + 1):
                    # Contenu du QR code: événement|tribune|rang|siège
                    qr_content = f"{event}|{tribune}|{rang}|{siege}"
                    
                    # Créer le QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_content)
                    qr.make(fit=True)
                    
                    # Créer l'image
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Nom du fichier (safe pour filesystem)
                    safe_event = event.replace(" ", "_")
                    safe_tribune = tribune.replace(" ", "_")
                    filename = f"{safe_event}_{safe_tribune}_{rang}_{siege}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Sauvegarder
                    img.save(filepath)
                    
                    # Stocker les informations
                    qr_info = {
                        "filename": filename,
                        "content": qr_content,
                        "event": event,
                        "tribune": tribune,
                        "rang": rang,
                        "siege": siege
                    }
                    qr_codes_info.append(qr_info)
                    
                    generated_count += 1
                    
                    if generated_count % 100 == 0:
                        print(f"   📊 Progression: {generated_count} QR codes générés")
    
    # Sauvegarder le mapping des QR codes
    with open(os.path.join(output_dir, "qr_codes_mapping.json"), "w") as f:
        json.dump(qr_codes_info, f, indent=2)
    
    print(f"\n✅ Génération terminée!")
    print(f"   📤 {generated_count} QR codes générés dans '{output_dir}/'")
    print(f"   🎯 Format: événement|tribune|rang|siège")
    print(f"   📋 Mapping sauvegardé dans 'qr_codes_mapping.json'")
    
    # Afficher un résumé
    print(f"\n📊 Résumé par événement:")
    for event, tribunes in events_config.items():
        event_total = 0
        print(f"   🎪 {event}:")
        for tribune, config in tribunes.items():
            tribune_total = config["rangs"] * config["sieges"]
            event_total += tribune_total
            print(f"     🏛️ {tribune}: {tribune_total} places ({config['rangs']} rangs × {config['sieges']} sièges)")
        print(f"     Total {event}: {event_total} places")
    
    return generated_count

def verify_qr_codes():
    """
    Vérifie quelques QR codes générés pour s'assurer qu'ils sont lisibles
    """
    print("\n🔍 Vérification des QR codes...")
    
    test_files = [
        "qr_codes/Stade_de_foot_Tribune_Nord_5_5.png",
        "qr_codes/Salle_de_concert_Balcon_3_8.png",
        "qr_codes/Théâtre_Parterre_10_15.png"
    ]
    
    detector = cv2.QRCodeDetector()
    
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                # Lire l'image
                img = cv2.imread(test_file)
                
                # Décoder le QR code
                data, bbox, _ = detector.detectAndDecode(img)
                
                if data:
                    print(f"   ✅ {os.path.basename(test_file)}: '{data}'")
                else:
                    print(f"   ❌ {os.path.basename(test_file)}: Non lisible")
                    
            except Exception as e:
                print(f"   ❌ {os.path.basename(test_file)}: Erreur - {e}")
        else:
            print(f"   ❌ {os.path.basename(test_file)}: Fichier non trouvé")

if __name__ == "__main__":
    count = generate_qr_codes()
    verify_qr_codes()
    
    print(f"\n💡 Prochaines étapes:")
    print(f"   1. Vérifiez les QR codes dans le dossier 'qr_codes/'")
    print(f"   2. Utilisez 'upload_qr_app_based_to_firebase.py' pour les uploader")
    print(f"   3. Testez avec l'app Android - scan QR → salle d'attente directe")
    print(f"   4. Les QR codes correspondent exactement aux options de l'app")