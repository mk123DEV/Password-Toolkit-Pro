# src/core_logic.py

import secrets
import string
from zxcvbn import zxcvbn
import requests
import hashlib

def generer_mot_de_passe(longueur: int, inclure_majuscules: bool, inclure_nombres: bool, inclure_symboles: bool) -> str:
  
    alphabet = string.ascii_lowercase
    if inclure_majuscules:
        alphabet += string.ascii_uppercase
    if inclure_nombres:
        alphabet += string.digits
    if inclure_symboles:
        alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not alphabet:
        return "Erreur : Au moins un jeu de caractères doit être sélectionné."

    mot_de_passe = ''.join(secrets.choice(alphabet) for _ in range(longueur))
    return mot_de_passe

def analyser_force_mot_de_passe(mot_de_passe: str) -> dict:
 
    if not mot_de_passe:
        return {
            'score': -1,
            'temps_crack_affichage': 'N/A',
            'suggestions': [],
            'avertissements': []
        }

    analyse = zxcvbn(mot_de_passe)
    
    # On récupère les retours (en anglais) directement depuis la bibliothèque.
    # C'est simple et fiable.
    suggestions = analyse['feedback']['suggestions']
    avertissement = analyse['feedback']['warning']

    resultat = {
        'score': analyse['score'],
        'temps_crack_affichage': analyse['crack_times_display']['offline_fast_hashing_1e10_per_second'],
        'suggestions': suggestions,
        'avertissements': [avertissement] if avertissement else []
    }
    return resultat



def verifier_mot_de_passe_pwned(mot_de_passe: str) -> int:

    if not mot_de_passe:
        return 0

    # 1. Hacher le mot de passe en SHA-1
    sha1_hash = hashlib.sha1(mot_de_passe.encode('utf-8')).hexdigest().upper()
    prefixe, suffixe = sha1_hash[:5], sha1_hash[5:]
    
    # 2. Interroger l'API avec le préfixe
    url = f"https://api.pwnedpasswords.com/range/{prefixe}"
    try:
        reponse = requests.get(url)
        if reponse.status_code != 200:
            return -1 # Erreur de l'API
    except requests.exceptions.RequestException:
        return -1 # Erreur de connexion

    # 3. Chercher notre suffixe dans la réponse
    hashes = (line.split(':') for line in reponse.text.splitlines())
    for h, count in hashes:
        if h == suffixe:
            return int(count)
    
    return 0 # Le mot de passe n'a pas été trouvé
