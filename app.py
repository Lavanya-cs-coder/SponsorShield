# Redeploy
import streamlit as st
import tempfile
import os
from PIL import Image
from backend_code import analyze_image_complete, get_perceptual_hash, add_to_database, load_database, generate_pdf_report

st.set_page_config(page_title="SponsorShield", layout="wide")

# ========== LIGHT THEME CSS ==========
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
}
.main-title {
    text-align: center;
    padding: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.main-title h1 {
    color: white;
    margin: 0;
    font-size: 2.5rem;
}
.main-title p {
    color: #e0e0e0;
    margin: 0;
    font-size: 1rem;
}
div[data-testid="stExpander"] {
    background: white;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
}
div[data-testid="stExpander"] summary {
    font-weight: bold;
    color: #333;
}
.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: bold;
}
.stButton button:hover {
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown('<div class="main-title"><h1>SponsorShield</h1><p>AI-Powered Sports Media Protection with Revenue Impact Analysis</p></div>', unsafe_allow_html=True)

# ========== INITIALIZE SESSION STATE ==========
if 'database' not in st.session_state:
    st.session_state.database = load_database()

if 'stolen_db' not in st.session_state:
    st.session_state.stolen_db = {
        "Instagram": [],
        "Twitter": [],
        "Facebook": []
    }

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("Official Image Database")
    st.markdown("---")
    
    official_image = st.file_uploader("Upload official image", type=["jpg", "png", "jpeg"], key="official")
    image_name = st.text_input("Image name (e.g., Kohli_IPL_2024)")
    
    if official_image and image_name:
        temp_path = os.path.join(tempfile.gettempdir(), official_image.name)
        with open(temp_path, "wb") as f:
            f.write(official_image.getbuffer())
        
        if add_to_database(temp_path, image_name):
            st.success(f"Added {image_name} to database")
            st.session_state.database = load_database()
        else:
            st.error("Failed to add image")
    
    st.markdown("---")
    st.write(f"Protected Images: **{len(st.session_state.database)}**")
    
    if st.session_state.database:
        with st.expander("View Protected Images"):
            for name in st.session_state.database.keys():
                st.write(f"- {name}")

# ========== MAIN CONTENT - MULTIPLE UPLOAD ==========
st.subheader("Upload Images for Analysis")

uploaded_files = st.file_uploader(
    "Select one or more images to analyze (Ctrl+click for multiple)", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Selected {len(uploaded_files)} image(s)")
    
    for idx, uploaded_file in enumerate(uploaded_files):
        with st.expander(f"Image {idx + 1}: {uploaded_file.name}", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(uploaded_file, width=250)
            
            with col2:
                if st.button(f"Analyze This Image", key=f"analyze_btn_{idx}"):
                    if len(st.session_state.database) == 0:
                        st.warning("Please add official images to database first")
                    else:
                        temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        with st.spinner("Analyzing..."):
                            result = analyze_image_complete(temp_path, st.session_state.database, st.session_state.stolen_db)
                        
                        if result:
                            # Verdict color coding
                            if result['verdict'] == "UNAUTHORIZED REUSE":
                                st.error(f"VERDICT: {result['verdict']}")
                            elif result['verdict'] == "POSSIBLE MISUSE":
                                st.warning(f"VERDICT: {result['verdict']}")
                            elif result['verdict'] == "SUSPICIOUS":
                                st.info(f"VERDICT: {result['verdict']}")
                            else:
                                st.success(f"VERDICT: {result['verdict']}")
                            
                            # Metrics
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Similarity", f"{result['similarity']}%")
                            m2.metric("Revenue Loss", f"Rs.{result['revenue_loss']:,}")
                            m3.metric("Risk Score", f"{result['risk_score']}/100")
                            
                            # Details
                            st.write(f"**Intent:** {result['intent']}")
                            st.write(f"**Viral Potential:** {result['viral_potential']}")
                            st.write(f"**Logo Status:** {result['logo_status']}")
                            st.write(f"**Matched With:** {result['matched_with']}")
                            
                            # Actions
                            st.write("**Recommended Actions:**")
                            for action in result['actions']:
                                st.write(f"- {action}")
                            
                            # PDF Download
                            if st.button(f"Download PDF Report", key=f"pdf_btn_{idx}"):
                                pdf_path = generate_pdf_report(result)
                                if pdf_path and os.path.exists(pdf_path):
                                    with open(pdf_path, "rb") as f:
                                        st.download_button("Click to Download PDF", f, file_name=f"sponsorshield_report_{idx}.pdf")
                                else:
                                    st.error("PDF generation failed")
                        else:
                            st.error("Analysis failed. Please try again.")

# ========== SINGLE IMAGE QUICK UPLOAD ==========
with st.expander("Quick Upload - Single Image"):
    single_file = st.file_uploader("Or upload a single image here", type=["jpg", "png", "jpeg"], key="single")
    
    if single_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(single_file, width=200)
        
        with col2:
            if st.button("Analyze Single Image"):
                if len(st.session_state.database) == 0:
                    st.warning("Please add official images to database first")
                else:
                    temp_path = os.path.join(tempfile.gettempdir(), single_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(single_file.getbuffer())
                    
                    with st.spinner("Analyzing..."):
                        result = analyze_image_complete(temp_path, st.session_state.database, st.session_state.stolen_db)
                    
                    if result:
                        if result['verdict'] == "UNAUTHORIZED REUSE":
                            st.error(f"Verdict: {result['verdict']}")
                        elif result['verdict'] == "POSSIBLE MISUSE":
                            st.warning(f"Verdict: {result['verdict']}")
                        elif result['verdict'] == "SUSPICIOUS":
                            st.info(f"Verdict: {result['verdict']}")
                        else:
                            st.success(f"Verdict: {result['verdict']}")
                        
                        colA, colB, colC = st.columns(3)
                        colA.metric("Similarity", f"{result['similarity']}%")
                        colB.metric("Revenue Loss", f"Rs.{result['revenue_loss']:,}")
                        colC.metric("Risk Score", f"{result['risk_score']}/100")
                        
                        st.write(f"**Intent:** {result['intent']}")
                        st.write(f"**Logo Status:** {result['logo_status']}")

# ========== FOOTER ==========
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>SponsorShield - Protecting Sports Sponsors | Team: Lavanya, Ramya, Divya</p>", 
    unsafe_allow_html=True
)