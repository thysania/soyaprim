import streamlit as st
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="SOYAPRIM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling - modern, clean look
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        color: #1E3A8A;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        padding: 0.5rem 0;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* Subtitle styling */
    .subtitle {
        color: #1F2937;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 300;
    }
    
    /* Card styling */
    .card {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
    }
    
    /* App card styling */
    .app-card {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1.2rem;
        margin: 0.7rem 0;
        border-left: 4px solid #2563EB;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .app-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        cursor: pointer;
    }
    
    .app-card.selected {
        background-color: #EFF6FF;
        border-left: 4px solid #1E40AF;
    }
    
    /* App title styling */
    .app-title {
        color: #1E3A8A;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* App description styling */
    .app-description {
        color: #4B5563;
        font-size: 0.9rem;
    }
    
    /* Footer styling */
    .footer {
        color: #6B7280;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
    
    /* Streamlit components styling */
    div.stButton button {
        background-color: #2563EB;
        color: white;
        border-radius: 0.375rem;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: background-color 0.2s;
    }
    
    div.stButton button:hover {
        background-color: #1D4ED8;
    }
    
    /* For file uploader */
    .uploadedFile {
        background-color: #F9FAFB !important;
        border: 1px dashed #D1D5DB !important;
        border-radius: 0.375rem !important;
        padding: 0.75rem !important;
    }
    
    /* For sidebar */
    .css-1d391kg, .css-163ttbj, .css-1fcdlhc {
        background-color: #F8FAFC;
    }
    
    /* For dataframes */
    .dataframe {
        font-size: 0.9rem !important;
    }
    
    /* Header alignment */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar header with logo (using emoji as placeholder)
st.sidebar.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 1rem;">
    <div style="font-size: 2rem; margin-right: 0.8rem;">📊</div>
    <div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #1E3A8A;">SOYAPRIM</div>
        <div style="font-size: 0.8rem; color: #6B7280;">{datetime.now().strftime('%d %b %Y')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# App descriptions for better context
app_descriptions = {
    "REFERENCE": "Préparer et classifier les données bancaires avec des références personnalisées.",
    "BANQUE": "Transformer et analyser les transactions bancaires pour l'importation.",
    "ACHATS": "Gérer et suivre vos achats et approvisionnements."
}

# Create interactive app selection cards in sidebar
st.sidebar.markdown("<div style='margin-bottom: 1.5rem;'><strong>Applications</strong></div>", unsafe_allow_html=True)

# Initialize session state for selected app if not exists
if 'selected_app' not in st.session_state:
    st.session_state.selected_app = "REFERENCE"

# Create app selection cards
for app_name in ["REFERENCE", "BANQUE", "ACHATS"]:
    selected_class = "selected" if st.session_state.selected_app == app_name else ""
    app_card = st.sidebar.markdown(f"""
    <div class="app-card {selected_class}" id="{app_name.lower()}-card">
        <div class="app-title">{app_name}</div>
        <div class="app-description">{app_descriptions[app_name]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle clicks
    if st.sidebar.button(f"Select {app_name}", key=f"btn_{app_name}"):
        st.session_state.selected_app = app_name
        st.experimental_rerun()

# Sidebar footer
st.sidebar.markdown("""
<div class="footer">
    © 2025 SOYAPRIM<br>
    Version 2.1.0
</div>
""", unsafe_allow_html=True)

# Main content
st.markdown(f"<h1 class='main-title'>SOYAPRIM</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='subtitle'>Système de gestion financière et comptable</p>", unsafe_allow_html=True)

# Display current app info
st.markdown(f"""
<div class="card">
    <h2 style="color: #1E3A8A; margin-bottom: 0.8rem;">Application: {st.session_state.selected_app}</h2>
    <p style="color: #4B5563;">{app_descriptions[st.session_state.selected_app]}</p>
</div>
""", unsafe_allow_html=True)

# Show loading animation
with st.spinner(f"Chargement de l'application {st.session_state.selected_app}..."):
    time.sleep(0.3)  # Small delay for visual feedback

# Container for the app
app_container = st.container()

with app_container:
    # Import and run the selected app
    if st.session_state.selected_app == "REFERENCE":
        from bq_ref import app as bq_ref_app
        bq_ref_app()
    elif st.session_state.selected_app == "BANQUE":
        from bq import app as bq_app
        bq_app()
    elif st.session_state.selected_app == "ACHATS":
        try:
            from achats import app as achats_app
            achats_app()
        except ImportError:
            st.info("Module 'achats' n'est pas encore disponible. L'application est en cours de développement.")
            
            # Placeholder content for ACHATS module
            st.markdown("""
            ### Fonctionnalités à venir:
            
            - Gestion des bons de commande
            - Suivi des factures fournisseurs
            - Analyse des coûts d'approvisionnement
            - Rapports de performance fournisseurs
            """)
