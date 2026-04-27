import numpy as np
from PIL import Image
import json
import os
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

DB_FILE = "sponsorshield_database.json"

# ---------------- HASH FUNCTION ----------------
def get_perceptual_hash(image_path, hash_size=8):
    try:
        img = Image.open(image_path).convert('L')
        img = img.resize((hash_size, hash_size))
        pixels = np.array(img)

        mean = pixels.mean()
        hash_str = ''.join('1' if p > mean else '0' for p in pixels.flatten())

        return hash_str

    except Exception as e:
        print("Error in hashing:", e)
        return None


# ---------------- HASH COMPARISON ----------------
def compare_hashes(hash1, hash2):
    if not hash1 or not hash2:
        return 0

    if len(hash1) != len(hash2):
        return 0

    diff = sum(1 for i in range(len(hash1)) if hash1[i] != hash2[i])
    similarity = ((len(hash1) - diff) / len(hash1)) * 100

    return round(similarity, 2)


# ---------------- DATABASE ----------------
def load_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_database(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)


# ---------------- ADD IMAGE ----------------
def add_to_database(image_path, image_name):
    hash_value = get_perceptual_hash(image_path)

    if not hash_value:
        return False

    db = load_database()

    db[image_name] = {
        "hash": hash_value,
        "path": image_path,
        "added_date": str(datetime.datetime.now())
    }

    save_database(db)
    return True


# ---------------- PDF REPORT ----------------
def generate_pdf_report(result):
    try:
        file_path = "sponsorshield_report.pdf"

        doc = SimpleDocTemplate(file_path)
        styles = getSampleStyleSheet()

        content = []

        content.append(Paragraph("SponsorShield Report", styles['Title']))
        content.append(Paragraph(f"Verdict: {result['verdict']}", styles['Normal']))
        content.append(Paragraph(f"Similarity: {result['similarity']}%", styles['Normal']))
        content.append(Paragraph(f"Revenue Loss: Rs.{result['revenue_loss']}", styles['Normal']))
        content.append(Paragraph(f"Risk Score: {result['risk_score']}", styles['Normal']))
        content.append(Paragraph(f"Intent: {result['intent']}", styles['Normal']))
        content.append(Paragraph(f"Viral Potential: {result['viral_potential']}", styles['Normal']))
        content.append(Paragraph(f"Logo Status: {result['logo_status']}", styles['Normal']))
        content.append(Paragraph(f"Matched With: {result['matched_with']}", styles['Normal']))

        doc.build(content)

        return file_path

    except Exception as e:
        print("PDF Error:", e)
        return None


# ---------------- ANALYSIS ----------------
def analyze_image_complete(image_path, database_images, stolen_db):
    uploaded_hash = get_perceptual_hash(image_path)

    if not uploaded_hash:
        return None

    best_match = None
    best_similarity = 0

    for name, data in database_images.items():
        similarity = compare_hashes(uploaded_hash, data.get("hash", ""))

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = name

    # ---------------- VERDICT LOGIC ----------------
    if best_similarity > 80:
        verdict = "UNAUTHORIZED REUSE"
        intent = "Malicious"
        viral = "High"
        actions = ["Take down content", "Send legal notice"]
    elif best_similarity > 60:
        verdict = "POSSIBLE MISUSE"
        intent = "Suspicious"
        viral = "Medium"
        actions = ["Monitor closely", "Issue warning"]
    elif best_similarity > 40:
        verdict = "SUSPICIOUS"
        intent = "Unclear"
        viral = "Low"
        actions = ["Track usage"]
    else:
        verdict = "SAFE"
        intent = "Normal"
        viral = "Low"
        actions = ["No action needed"]

    result = {
        "verdict": verdict,
        "similarity": best_similarity,
        "matched_with": best_match if best_match else "None",
        "revenue_loss": int(best_similarity * 50),
        "risk_score": int(best_similarity),
        "intent": intent,
        "viral_potential": viral,
        "logo_status": "Unknown",
        "actions": actions
    }

    return result