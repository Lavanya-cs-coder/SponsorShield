import numpy as np
from PIL import Image
import json
import os
import datetime

def get_perceptual_hash(image_path, hash_size=8):
    try:
        img = Image.open(image_path).convert('L')
        img = img.resize((hash_size, hash_size))
        pixels = np.array(img)
        mean = pixels.mean()
        hash_str = ''.join('1' if p > mean else '0' for p in pixels.flatten())
        return hash_str
    except:
        return None

def compare_hashes(hash1, hash2):
    if hash1 is None or hash2 is None:
        return 0
    if len(hash1) != len(hash2):
        return 0
    diff = 0
    for i in range(len(hash1)):
        if hash1[i] != hash2[i]:
            diff = diff + 1
    similarity = ((len(hash1) - diff) / len(hash1)) * 100
    return round(similarity, 2)

def load_database():
    if os.path.exists("sponsorshield_database.json"):
        with open("sponsorshield_database.json", 'r') as f:
            return json.load(f)
    return {}

def save_database(db):
    with open("sponsorshield_database.json", 'w') as f:
        json.dump(db, f)

def add_to_database(image_path, image_name):
    hash_value = get_perceptual_hash(image_path)
    if not hash_value:
        return False
    db = load_database()
    db[image_name] = {"hash": hash_value, "path": image_path, "added_date": str(datetime.datetime.now())}
    save_database(db)
    return True

def generate_pdf_report(result):
    return None

def analyze_image_complete(image_path, database_images, stolen_db):
    uploaded_hash = get_perceptual_hash(image_path)
    if not uploaded_hash:
        return {"verdict": "Error", "similarity": 0, "revenue_loss": 0, "risk_score": 0}
    
    best_match = None
    best_similarity = 0
    for name, data in database_images.items():
        similarity = compare_hashes(uploaded_hash, data.get("hash", ""))
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = name
    
    return {
        'verdict': "UNAUTHORIZED REUSE" if best_similarity > 75 else "SAFE",
        'similarity': best_similarity,
        'matched_with': best_match or "None",
        'revenue_loss': int(best_similarity * 100),
        'risk_score': int(best_similarity),
        'intent': "Malicious" if best_similarity > 75 else "Normal",
        'viral_potential': "High" if best_similarity > 75 else "Low",
        'logo_status': "Unknown",
        'actions': ["Monitor usage"],
        'report': "Analysis complete"
    }

print("SponsorShield Backend Loaded")
