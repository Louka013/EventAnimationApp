#!/usr/bin/env python3
"""
Script pour uploader les QR codes basés sur l'app vers Firestore
Utilise les événements et tribunes exactes de l'app Android
"""

import os
import glob
import json
import base64
from firebase_web_admin import FirebaseWebClient

def encode_qr_to_base64(file_path):
    """
    Encode un fichier QR en base64
    """
    with open(file_path, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def upload_qr_codes_to_firestore():
    """
    Upload tous les QR codes basés sur l'app vers Firestore
    """
    print("🚀 Upload des QR codes de l'app vers Firestore...")
    
    # Vérifier que le dossier qr_codes existe
    qr_codes_dir = "qr_codes"
    if not os.path.exists(qr_codes_dir):
        print(f"❌ Le dossier '{qr_codes_dir}' n'existe pas. Exécutez d'abord generate_qr_codes_app_based.py")
        return
    
    # Charger le mapping des QR codes
    mapping_file = os.path.join(qr_codes_dir, "qr_codes_mapping.json")
    if not os.path.exists(mapping_file):
        print(f"❌ Fichier de mapping '{mapping_file}' non trouvé")
        return
    
    with open(mapping_file, 'r') as f:
        qr_codes_info = json.load(f)
    
    # Initialiser Firebase
    fb = FirebaseWebClient()
    
    print(f"📦 {len(qr_codes_info)} QR codes à uploader...")
    
    uploaded_count = 0
    
    for qr_info in qr_codes_info:
        filename = qr_info["filename"]
        qr_content = qr_info["content"]
        event = qr_info["event"]
        tribune = qr_info["tribune"]
        rang = qr_info["rang"]
        siege = qr_info["siege"]
        
        # Chemin du fichier
        file_path = os.path.join(qr_codes_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"   ❌ Fichier non trouvé: {filename}")
            continue
        
        try:
            # Encoder le QR en base64
            base64_data = encode_qr_to_base64(file_path)
            
            # ID du document: event_tribune_rang_siege (safe pour Firebase)
            safe_event = event.replace(" ", "_")
            safe_tribune = tribune.replace(" ", "_")
            document_id = f"{safe_event}_{safe_tribune}_{rang}_{siege}"
            
            # Données pour Firestore
            seat_data = {
                "documentId": document_id,
                "event": event,
                "tribune": tribune,
                "rang": rang,
                "siege": siege,
                "qrContent": qr_content,
                "qrCodeBase64": base64_data,
                "isOccupied": False,
                "userId": None,
                "updatedAt": fb.get_current_timestamp()
            }
            
            # Enregistrer dans Firestore collection 'appSeats'
            success = fb.set_document('appSeats', document_id, seat_data)
            
            if success:
                uploaded_count += 1
                if uploaded_count % 100 == 0:
                    print(f"   📊 Progression: {uploaded_count}/{len(qr_codes_info)} uploadés")
            else:
                print(f"   ❌ Échec Firestore: {document_id}")
                
        except Exception as e:
            print(f"   ❌ Erreur {filename}: {e}")
    
    print(f"\n✅ Upload terminé!")
    print(f"   📤 QR codes uploadés: {uploaded_count}/{len(qr_codes_info)}")
    print(f"   📝 Données stockées dans Firestore collection 'appSeats'")
    print(f"   🎯 Format document: event_tribune_rang_siege")

def verify_uploads():
    """
    Vérifie quelques uploads pour s'assurer qu'ils fonctionnent
    """
    print("\n🔍 Vérification des uploads...")
    
    fb = FirebaseWebClient()
    
    test_documents = [
        'Stade_de_foot_Tribune_Nord_5_5',
        'Salle_de_concert_Balcon_3_8',
        'Théâtre_Parterre_10_15'
    ]
    
    for doc_id in test_documents:
        try:
            seat_data = fb.get_document('appSeats', doc_id)
            
            if seat_data:
                qr_content = seat_data.get('qrContent', 'N/A')
                event = seat_data.get('event', 'N/A')
                tribune = seat_data.get('tribune', 'N/A')
                rang = seat_data.get('rang', 'N/A')
                siege = seat_data.get('siege', 'N/A')
                
                print(f"   ✅ {doc_id}: {event} | {tribune} | Rang {rang} | Siège {siege}")
                print(f"       QR: {qr_content}")
            else:
                print(f"   ❌ {doc_id}: Document non trouvé")
                
        except Exception as e:
            print(f"   ❌ {doc_id}: Erreur - {e}")

def create_test_html():
    """
    Crée un fichier HTML pour tester les QR codes de l'app
    """
    print("\n🌐 Création d'un fichier de test HTML...")
    
    fb = FirebaseWebClient()
    
    # Récupérer quelques QR codes pour test
    test_documents = [
        'Stade_de_foot_Tribune_Nord_5_5',
        'Salle_de_concert_Balcon_3_8',
        'Théâtre_Parterre_10_15'
    ]
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test QR Codes App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .qr-container { margin: 20px; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
        .qr-code { max-width: 200px; border: 1px solid #000; }
        .qr-info { margin: 10px 0; }
        .qr-content { font-family: monospace; background: #f0f0f0; padding: 5px; }
        .event-type { color: #0066cc; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Test QR Codes App</h1>
    <p>QR codes correspondant aux événements et tribunes de l'app Android</p>
"""
    
    for doc_id in test_documents:
        try:
            seat_data = fb.get_document('appSeats', doc_id)
            
            if seat_data:
                qr_data = seat_data.get('qrCodeBase64', '')
                qr_content = seat_data.get('qrContent', 'N/A')
                event = seat_data.get('event', 'N/A')
                tribune = seat_data.get('tribune', 'N/A')
                rang = seat_data.get('rang', 'N/A')
                siege = seat_data.get('siege', 'N/A')
                
                html_content += f"""
    <div class="qr-container">
        <h3>{doc_id}</h3>
        <div class="qr-info">
            <span class="event-type">📱 {event}</span><br>
            <strong>Tribune:</strong> {tribune}<br>
            <strong>Rang:</strong> {rang}<br>
            <strong>Siège:</strong> {siege}
        </div>
        <div class="qr-content">
            <strong>Contenu QR:</strong> {qr_content}
        </div>
        <img src="{qr_data}" alt="QR Code {doc_id}" class="qr-code">
    </div>
"""
            else:
                html_content += f"""
    <div class="qr-container">
        <h3>{doc_id}</h3>
        <p>❌ QR code non trouvé</p>
    </div>
"""
                
        except Exception as e:
            html_content += f"""
    <div class="qr-container">
        <h3>{doc_id}</h3>
        <p>❌ Erreur: {e}</p>
    </div>
"""
    
    html_content += """
</body>
</html>
"""
    
    with open('test_qr_codes_app.html', 'w') as f:
        f.write(html_content)
    
    print("   ✅ Fichier 'test_qr_codes_app.html' créé")
    print("   📖 Ouvrez ce fichier dans un navigateur pour voir les QR codes")

if __name__ == "__main__":
    upload_qr_codes_to_firestore()
    verify_uploads()
    create_test_html()
    
    print("\n💡 Système QR app-based:")
    print("   - QR codes correspondent exactement aux options de l'app")
    print("   - Événements: Stade de foot, Salle de concert, Théâtre")
    print("   - Tribunes selon configuration MainActivity.kt")
    print("   - Scan QR → salle d'attente directe avec bonnes données")