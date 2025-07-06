#!/usr/bin/env python3
"""
Générateur d'images de test pour l'Agent Vision
Crée 25+ images variées avec contenu sensible et normal pour tester la détection PII
"""

import cv2
import numpy as np
from pathlib import Path
import random
from datetime import datetime, timedelta

def create_test_images():
    """Génère 25+ images de test variées"""
    
    # Créer le dossier de sortie
    output_dir = Path("test_images")
    output_dir.mkdir(exist_ok=True)
    
    print(f"🖼️ Génération d'images de test dans {output_dir}")
    print("=" * 50)
    
    # === IMAGES AVEC CONTENU SENSIBLE (WARNING=TRUE) ===
    
    # 1. Carte bancaire Visa
    create_credit_card_image(output_dir / "01_carte_visa_sensible.jpg", 
                           "CARTE VISA", "4532 1234 5678 9012", "12/27", "123")
    
    # 2. Carte bancaire Mastercard  
    create_credit_card_image(output_dir / "02_carte_mastercard_sensible.jpg",
                           "MASTERCARD", "5412 7890 1234 5678", "09/26", "456")
    
    # 3. RIB/IBAN
    create_document_image(output_dir / "03_rib_iban_sensible.jpg", [
        "RELEVÉ D'IDENTITÉ BANCAIRE",
        "IBAN: FR76 1234 5678 9012 3456 7890 123",
        "BIC: BNPAFRPPXXX",
        "Titulaire: MARTIN Jean"
    ])
    
    # 4. Email et téléphone
    create_document_image(output_dir / "04_contact_email_sensible.jpg", [
        "COORDONNÉES CLIENT",
        "Email: jean.martin@gmail.com",
        "Téléphone: 06 12 34 56 78",
        "Adresse: 123 Rue de la Paix, Paris"
    ])
    
    # 5. Passeport
    create_document_image(output_dir / "05_passeport_sensible.jpg", [
        "RÉPUBLIQUE FRANÇAISE",
        "PASSEPORT",
        "N° 12AB34567",
        "NOM: MARTIN",
        "Prénom: Jean"
    ])
    
    # 6. Carte d'identité
    create_document_image(output_dir / "06_cni_sensible.jpg", [
        "CARTE NATIONALE D'IDENTITÉ",
        "N° 123456789012",
        "MARTIN Jean",
        "Né le 15/06/1985"
    ])
    
    # 7. Ordonnance médicale
    create_document_image(output_dir / "07_ordonnance_medicale_sensible.jpg", [
        "ORDONNANCE MÉDICALE",
        "Dr. DUPONT",
        "Patient: MARTIN Jean",
        "Médicament: Doliprane 1000mg"
    ])
    
    # 8. Bulletin de paie
    create_document_image(output_dir / "08_bulletin_paie_sensible.jpg", [
        "BULLETIN DE PAIE",
        "Employé: MARTIN Jean",
        "Salaire brut: 3500.00 EUR",
        "CONFIDENTIEL"
    ])
    
    # 9. Permis de conduire
    create_document_image(output_dir / "09_permis_conduire_sensible.jpg", [
        "PERMIS DE CONDUIRE",
        "N° 123456789012",
        "MARTIN Jean",
        "Catégorie B"
    ])
    
    # 10. Carte Vitale
    create_document_image(output_dir / "10_carte_vitale_sensible.jpg", [
        "CARTE VITALE",
        "N° Sécurité Sociale:",
        "1 85 06 75 123 456 78",
        "MARTIN Jean"
    ])
    
    # 11. American Express
    create_credit_card_image(output_dir / "11_amex_sensible.jpg",
                           "AMERICAN EXPRESS", "3712 345678 90123", "03/28", "7890")
    
    # 12. Document bancaire confidentiel
    create_document_image(output_dir / "12_document_confidentiel_sensible.jpg", [
        "DOCUMENT CONFIDENTIEL",
        "Compte client: 12345678901",
        "Code secret: 1234",
        "PRIVÉ - NE PAS DIFFUSER"
    ])
    
    # === IMAGES NORMALES (WARNING=FALSE) ===
    
    # 13. Facture normale
    create_document_image(output_dir / "13_facture_normale.jpg", [
        "FACTURE",
        "Entreprise ABC",
        "Produit: Livre Python",
        "Prix: 29.99 EUR",
        "Date: 15/12/2024"
    ])
    
    # 14. Menu restaurant
    create_document_image(output_dir / "14_menu_restaurant.jpg", [
        "RESTAURANT LE FRANÇAIS",
        "MENU DU JOUR",
        "Entrée: Salade verte - 8€",
        "Plat: Steak frites - 18€",
        "Dessert: Tarte aux pommes - 6€"
    ])
    
    # 15. Reçu magasin
    create_document_image(output_dir / "15_recu_magasin.jpg", [
        "SUPERMARCHÉ CHAMPION",
        "Article: Pain de mie - 2.50€",
        "Article: Lait 1L - 1.20€",
        "Total: 3.70€",
        "Merci de votre visite"
    ])
    
    # 16. Affiche événement
    create_document_image(output_dir / "16_affiche_evenement.jpg", [
        "CONCERT DE JAZZ",
        "Samedi 20 Janvier 2025",
        "Salle Pleyel - Paris",
        "Tarif: 25€",
        "Réservations: www.jazz-paris.fr"
    ])
    
    # 17. Notice produit
    create_document_image(output_dir / "17_notice_produit.jpg", [
        "NOTICE D'UTILISATION",
        "Aspirateur modèle XY-2000",
        "1. Brancher l'appareil",
        "2. Appuyer sur le bouton ON",
        "3. Passer sur les surfaces à nettoyer"
    ])
    
    # 18. Horaires magasin
    create_document_image(output_dir / "18_horaires_magasin.jpg", [
        "HORAIRES D'OUVERTURE",
        "Lundi - Vendredi: 9h - 19h",
        "Samedi: 9h - 18h",
        "Dimanche: Fermé",
        "Magasin Bio Nature"
    ])
    
    # 19. Recette cuisine
    create_document_image(output_dir / "19_recette_cuisine.jpg", [
        "RECETTE TARTE TATIN",
        "Ingrédients:",
        "- 6 pommes",
        "- 200g pâte brisée",
        "- 100g sucre",
        "Cuisson: 30min à 180°C"
    ])
    
    # 20. Livre titre
    create_document_image(output_dir / "20_livre_titre.jpg", [
        "L'ART DE LA PROGRAMMATION",
        "Guide complet Python",
        "Auteur: Jean Développeur",
        "Éditions TechBooks 2024",
        "480 pages"
    ])
    
    # 21. Panneau publicitaire
    create_document_image(output_dir / "21_panneau_pub.jpg", [
        "NOUVEAUTÉ !",
        "Smartphone UltraTech Pro",
        "Écran 6.7 pouces",
        "Appareil photo 108MP",
        "À partir de 799€"
    ])
    
    # 22. Programme TV
    create_document_image(output_dir / "22_programme_tv.jpg", [
        "PROGRAMME TV - TF1",
        "20h00: Journal",
        "20h30: Météo",
        "20h45: Film: Bienvenue chez les Ch'tis",
        "22h30: Débat société"
    ])
    
    # 23. Calendrier
    create_document_image(output_dir / "23_calendrier.jpg", [
        "JANVIER 2025",
        "Lun Mar Mer Jeu Ven Sam Dim",
        "    1   2   3   4   5",
        "6   7   8   9  10  11  12",
        "13 14  15  16  17  18  19"
    ])
    
    # 24. Citations motivation
    create_document_image(output_dir / "24_citations.jpg", [
        "CITATION DU JOUR",
        '"Le succès, c\'est d\'aller d\'échec',
        'en échec sans perdre son',
        'enthousiasme."',
        "- Winston Churchill"
    ])
    
    # 25. Image presque vide (test edge case)
    create_document_image(output_dir / "25_presque_vide.jpg", [
        "ABC"
    ])
    
    # 26. Image complètement vide (test edge case)
    create_empty_image(output_dir / "26_image_vide.jpg")
    
    # === IMAGES NSFW TEST (WARNING=TRUE par détection visuelle) ===
    
    # 27. Test NSFW - beaucoup de tons chair
    create_nsfw_test_image(output_dir / "27_nsfw_tons_chair.jpg", skin_percentage=0.85)
    
    # 28. Test NSFW - tons chair modérés
    create_nsfw_test_image(output_dir / "28_nsfw_tons_moderés.jpg", skin_percentage=0.70)
    
    # 29. Test Safe - peu de tons chair 
    create_nsfw_test_image(output_dir / "29_safe_peu_chair.jpg", skin_percentage=0.40)
    
    # 30. Test Safe - pas de tons chair
    create_nsfw_test_image(output_dir / "30_safe_pas_chair.jpg", skin_percentage=0.10)
    
    print(f"\n✅ {len(list(output_dir.glob('*.jpg')))} images générées avec succès !")
    print(f"📁 Dossier: {output_dir.absolute()}")
    print("\n🧪 Prêt pour les tests avec Streamlit !")

def create_credit_card_image(filepath: Path, card_type: str, number: str, expiry: str, cvv: str):
    """Crée une image de carte bancaire"""
    img = np.zeros((300, 480, 3), dtype=np.uint8)
    
    # Couleur de fond selon le type
    if "VISA" in card_type:
        img[:] = (50, 50, 150)  # Bleu
    elif "MASTERCARD" in card_type:
        img[:] = (150, 50, 50)  # Rouge
    elif "AMERICAN EXPRESS" in card_type:
        img[:] = (50, 150, 50)  # Vert
    
    # Textes
    cv2.putText(img, card_type, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(img, number, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, f"EXP: {expiry}", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, f"CVV: {cvv}", (30, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, "MARTIN JEAN", (30, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imwrite(str(filepath), img)
    print(f"📄 {filepath.name} - Carte bancaire {card_type}")

def create_document_image(filepath: Path, lines: list, bg_color=(240, 240, 240)):
    """Crée une image de document avec plusieurs lignes de texte"""
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    img[:] = bg_color
    
    y_start = 50
    for i, line in enumerate(lines):
        y_pos = y_start + (i * 40)
        if y_pos > 350:  # Éviter le débordement
            break
            
        # Ajuster la taille selon la longueur
        scale = 0.7 if len(line) > 30 else 0.8
        thickness = 1 if len(line) > 30 else 2
        
        cv2.putText(img, line, (30, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                   scale, (0, 0, 0), thickness)
    
    cv2.imwrite(str(filepath), img)
    
    # Déterminer le type pour l'affichage
    first_line = lines[0] if lines else ""
    if any(word in first_line.lower() for word in ["carte", "visa", "iban", "email", "passeport", "ordonnance", "salaire", "confidentiel"]):
        doc_type = "⚠️ SENSIBLE"
    else:
        doc_type = "✅ Normal"
        
    print(f"📄 {filepath.name} - {doc_type}")

def create_empty_image(filepath: Path):
    """Crée une image presque vide (pour tester les edge cases)"""
    img = np.random.randint(200, 255, (200, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(filepath), img)
    print(f"📄 {filepath.name} - Image vide (test edge case)")

def create_nsfw_test_image(filepath: Path, skin_percentage: float):
    """Crée une image de test NSFW avec pourcentage de tons chair spécifié"""
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # Couleurs de fond (non-chair)
    bg_colors = [
        (100, 100, 100),  # Gris
        (50, 50, 200),    # Bleu
        (50, 200, 50),    # Vert
        (200, 200, 200),  # Gris clair
    ]
    
    # Couleurs tons chair (gamme HSV convertie en BGR)
    skin_colors = [
        (135, 174, 239),  # Ton chair clair
        (125, 158, 220),  # Ton chair moyen
        (112, 146, 198),  # Ton chair foncé
        (98, 132, 186),   # Ton chair très foncé
        (150, 180, 255),  # Ton chair très clair
    ]
    
    # Remplir l'image avec couleur de fond aléatoire
    bg_color = random.choice(bg_colors)
    img[:] = bg_color
    
    # Calculer combien de pixels pour le pourcentage de chair voulu
    total_pixels = img.shape[0] * img.shape[1]
    skin_pixels_needed = int(total_pixels * skin_percentage)
    
    # Générer des zones de tons chair de manière aléatoire
    pixels_added = 0
    attempts = 0
    max_attempts = 1000
    
    while pixels_added < skin_pixels_needed and attempts < max_attempts:
        # Taille aléatoire de la zone
        zone_size = random.randint(20, 100)
        
        # Position aléatoire
        x = random.randint(0, img.shape[1] - zone_size)
        y = random.randint(0, img.shape[0] - zone_size)
        
        # Couleur chair aléatoire
        skin_color = random.choice(skin_colors)
        
        # Forme aléatoire (rectangle ou ellipse)
        if random.choice([True, False]):
            # Rectangle
            cv2.rectangle(img, (x, y), (x + zone_size, y + zone_size), skin_color, -1)
        else:
            # Ellipse
            cv2.ellipse(img, (x + zone_size//2, y + zone_size//2), 
                       (zone_size//2, zone_size//3), 0, 0, 360, skin_color, -1)
        
        pixels_added += zone_size * zone_size
        attempts += 1
    
    # Ajouter du texte pour identifier le test
    percentage_text = f"Test NSFW: {skin_percentage:.0%} tons chair"
    cv2.putText(img, percentage_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Déterminer le type attendu
    if skin_percentage > 0.6:  # Seuil fallback à 75%, mais testons à partir de 60%
        test_type = "⚠️ NSFW ATTENDU"
    else:
        test_type = "✅ SAFE ATTENDU"
    
    cv2.imwrite(str(filepath), img)
    print(f"📄 {filepath.name} - {test_type} ({skin_percentage:.0%} chair)")

if __name__ == "__main__":
    create_test_images()
