import numpy as np
from PIL import Image
import json
import os
from datetime import datetime

# ============================================================
# PERCEPTUAL HASHING (using PIL instead of cv2)
# ============================================================

def get_perceptual_hash(image_path, hash_size=8):
    try:
        img = Image.open(image_path).convert('L')
        img = img.resize((hash_size, hash_size))
        pixels = np.array(img)
        mean = pixels.mean()
        hash_str = ''.join('1' if p > mean else '0' for row in pixels for p in row)
        return hash_str
    except:
        return None

def compare_hashes(hash1, hash2):
    if not hash1 or not hash2:
        return 0.0
    if len(hash1) != len(hash2):
        return 0.0
    differences = sum(1 for i in range(len(hash1)) if hash1[i] != hash2[i])
    similarity = ((len(hash1) - differences) / len(hash1)) * 100
    return round(similarity, 2)

# ============================================================
# HISTOGRAM SIMILARITY (using PIL instead of cv2)
# ============================================================

def histogram_similarity(image_path1, image_path2):
    try:
        img1 = Image.open(image_path1).convert('RGB')
        img2 = Image.open(image_path2).convert('RGB')
        
        img1 = img1.resize((256, 256))
        img2 = img2.resize((256, 256))
        
        hist1 = np.array(img1.histogram())
        hist2 = np.array(img2.histogram())
        
        hist1 = hist1 / hist1.sum()
        hist2 = hist2 / hist2.sum()
        
        score = np.sum(np.minimum(hist1, hist2)) * 100
        return round(score, 2)
    except:
        return 0.0

# ============================================================
# DATABASE MANAGEMENT
# ============================================================

DATABASE_FILE = "sponsorshield_database.json"

def load_database():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_database(database):
    with open(DATABASE_FILE, 'w') as file:
        json.dump(database, file, indent=2)

def add_to_database(image_path, image_name):
    hash_value = get_perceptual_hash(image_path)
    if hash_value is None:
        return False
    database = load_database()
    database[image_name] = {
        "hash": hash_value,
        "path": image_path,
        "added_date": str(datetime.now())
    }
    save_database(database)
    return True

# ============================================================
# LOGO TAMPERING DETECTION (using PIL)
# ============================================================

def detect_logo_tampering(image_path):
    try:
        img = Image.open(image_path).convert('L')
        width, height = img.size
        
        # Crop logo region (top 30-50%, center 30-70%)
        left = int(width * 0.3)
        top = int(height * 0.3)
        right = int(width * 0.7)
        bottom = int(height * 0.5)
        
        logo_region = img.crop((left, top, right, bottom))
        pixels = np.array(logo_region)
        variance = np.var(pixels)
        
        if variance < 500:
            return "Logo Tampered", 40
        else:
            return "Logo Intact", 85
    except:
        return "Unknown", 50

# ============================================================
# REVENUE CALCULATION
# ============================================================

def calculate_revenue_loss(similarity_percent, visibility_percent=50, estimated_reach=50000):
    cost_per_mille = 200
    visibility_loss = (100 - visibility_percent) / 100
    revenue_loss = (estimated_reach / 1000) * cost_per_mille * visibility_loss
    if similarity_percent > 85:
        revenue_loss += (estimated_reach / 1000) * cost_per_mille * 0.5
    return round(revenue_loss)

# ============================================================
# RISK SCORE CALCULATION
# ============================================================

def calculate_risk_score(similarity_percent, visibility_percent=50):
    risk = 0
    if similarity_percent > 90:
        risk += 60
    elif similarity_percent > 75:
        risk += 40
    elif similarity_percent > 50:
        risk += 20
    if visibility_percent < 30:
        risk += 40
    elif visibility_percent < 60:
        risk += 25
    elif visibility_percent < 80:
        risk += 10
    return min(risk, 100)

# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(similarity_percent, logo_status):
    if similarity_percent > 90 and logo_status == "Logo Tampered":
        return "Malicious Theft - Logo Hidden"
    elif similarity_percent > 90:
        return "Malicious Theft"
    elif similarity_percent > 70:
        return "Unauthorized Reuse"
    elif similarity_percent > 50:
        return "Possible Misuse"
    return "Safe"

# ============================================================
# VIRAL REACH PREDICTION
# ============================================================

def predict_reach(similarity_percent, platform_count):
    base_reach = 10000
    if similarity_percent > 80:
        base_reach *= 5
    elif similarity_percent > 60:
        base_reach *= 3
    if platform_count > 2:
        base_reach *= 3
    elif platform_count > 0:
        base_reach *= 2
    if base_reach > 150000:
        return "Critical Viral", base_reach
    elif base_reach > 50000:
        return "High Viral", base_reach
    elif base_reach > 20000:
        return "Medium Viral", base_reach
    return "Low Viral", base_reach

# ============================================================
# TREND ANALYSIS
# ============================================================

def analyze_trend(similarity_percent, days_delayed=1):
    daily_loss = 5000 * days_delayed
    if similarity_percent > 80:
        daily_loss *= 2
    if days_delayed <= 1:
        return "Critical - Act Now", daily_loss
    elif days_delayed <= 3:
        return "Urgent - Loss Increasing", daily_loss
    return "Delayed - Maximum Damage", daily_loss

# ============================================================
# PLATFORM TRACKING
# ============================================================

def track_platforms(image_hash):
    return ["Twitter", "Telegram", "Facebook"]

def get_stolen_database():
    return {
        "Instagram": [],
        "Twitter": [],
        "Facebook": [],
        "Telegram": []
    }

# ============================================================
# LEGAL ACTIONS GENERATOR
# ============================================================

def generate_legal_actions(risk_score, revenue_loss, platforms):
    actions = []
    if risk_score > 70:
        actions.append("Send DMCA takedown notice to platforms")
        actions.append("File legal complaint for copyright violation")
    if revenue_loss > 50000:
        actions.append(f"Claim compensation of Rs.{revenue_loss * 2}")
    if len(platforms) > 2:
        actions.append("Escalate to cyber crime cell")
    if not actions:
        actions.append("Monitor and document evidence")
    return actions

# ============================================================
# SPONSOR REPORT GENERATION
# ============================================================

def generate_sponsor_report(sponsor_name, revenue_loss, platforms, risk_score, similarity):
    report = f"""
SPONSORSHIELD PROTECTION REPORT
================================

Sponsor: {sponsor_name}
Date: {datetime.now().strftime('%Y-%m-%d')}

VIOLATION SUMMARY
--------------------------------
Similarity with official: {similarity}%
Revenue Loss Estimated: Rs.{revenue_loss:,}
Risk Score: {risk_score}/100
Platforms Violating: {', '.join(platforms) if platforms else 'None'}

RECOMMENDED ACTIONS
--------------------------------
Priority: {'URGENT' if risk_score > 70 else 'NORMAL'}

This report is generated automatically by SponsorShield AI System.
"""
    return report

# ============================================================
# PDF REPORT GENERATION (without fpdf)
# ============================================================

def generate_pdf_report(result):
    # Return None - PDF generation not available in cloud
    return None

# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_image_complete(image_path, database_images, stolen_db, sponsor_name="Dream11", days_delayed=1):
    uploaded_hash = get_perceptual_hash(image_path)
    if uploaded_hash is None:
        return None
    
    if not database_images:
        return {
            "verdict": "Add official images to database",
            "similarity": 0,
            "matched_with": "None",
            "revenue_loss": 0,
            "risk_score": 0,
            "logo_status": "N/A",
            "visibility": 50,
            "intent": "N/A",
            "viral_potential": "N/A",
            "estimated_reach": 0,
            "trend_status": "N/A",
            "trend_loss": 0,
            "platforms": [],
            "actions": ["Please add official images to database first"],
            "report": "Database is empty. Add official images to start protection."
        }
    
    best_similarity = 0
    best_match = "None"
    
    for name, data in database_images.items():
        hash_similarity = compare_hashes(uploaded_hash, data.get("hash", ""))
        color_similarity = histogram_similarity(image_path, data.get("path", ""))
        total_similarity = (hash_similarity * 0.6) + (color_similarity * 0.4)
        
        if total_similarity > best_similarity:
            best_similarity = total_similarity
            best_match = name
    
    if best_similarity < 40:
        return {
            "verdict": "SAFE",
            "similarity": round(best_similarity, 2),
            "matched_with": "No strong match",
            "revenue_loss": 0,
            "risk_score": 10,
            "logo_status": "Not relevant",
            "visibility": 50,
            "intent": "Normal Use",
            "viral_potential": "Low Viral",
            "estimated_reach": 0,
            "trend_status": "Stable",
            "trend_loss": 0,
            "platforms": [],
            "actions": ["No action needed - Image appears safe"],
            "report": "No violation detected. Image is safe."
        }
    
    logo_status, visibility = detect_logo_tampering(image_path)
    revenue_loss = calculate_revenue_loss(best_similarity, visibility)
    risk_score = calculate_risk_score(best_similarity, visibility)
    intent = detect_intent(best_similarity, logo_status)
    
    platforms = list(stolen_db.keys()) if best_similarity > 70 else []
    
    viral_status, estimated_reach = predict_reach(best_similarity, len(platforms))
    trend_status, trend_loss = analyze_trend(best_similarity, days_delayed)
    actions = generate_legal_actions(risk_score, revenue_loss, platforms)
    report = generate_sponsor_report(sponsor_name, revenue_loss, platforms, risk_score, best_similarity)
    
    if best_similarity > 85:
        verdict = "UNAUTHORIZED REUSE"
    elif best_similarity > 65:
        verdict = "POSSIBLE MISUSE"
    else:
        verdict = "SUSPICIOUS"
    
    return {
        "verdict": verdict,
        "similarity": round(best_similarity, 2),
        "matched_with": best_match,
        "revenue_loss": revenue_loss,
        "risk_score": risk_score,
        "logo_status": logo_status,
        "visibility": visibility,
        "intent": intent,
        "viral_potential": viral_status,
        "estimated_reach": estimated_reach,
        "trend_status": trend_status,
        "trend_loss": trend_loss,
        "platforms": platforms,
        "actions": actions,
        "report": report
    }

print("SponsorShield Backend Loaded Successfully")