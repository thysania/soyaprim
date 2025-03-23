import streamlit as st
from PIL import Image

# Custom CSS for styling
st.markdown("""
<style>
/* Narrower sidebar */
[data-testid="stSidebar"] {
    width: 150px !important;
}

/* Button styling */
.stButton button {
    width: 100%;
    background-color: #4F8BF9;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 14px;
    margin: 5px 0;
}

/* Title styling */
h1 {
    color: #4F8BF9;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for app selection
if "app_choice" not in st.session_state:
    st.session_state.app_choice = "BQ Ref"

# Add a logo (with error handling)
try:
    logo = Image.open("logo.png")
    st.image(logo, width=100)
except FileNotFoundError:
    st.warning("Logo non trouvé. Veuillez ajouter un fichier 'logo.png' dans le répertoire principal.")
except Exception as e:
    st.error(f"Erreur lors du chargement du logo : {e}")

# Title and description
st.title("SOYAPRIM Data Transformation Suite")
st.write("""
Bienvenue dans l'application de transformation de données SOYAPRIM. 
Sélectionnez une application ci-dessous pour commencer.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")

# Navigation buttons
if st.sidebar.button("BQ Ref"):
    st.session_state.app_choice = "BQ Ref"

if st.sidebar.button("BQ"):
    st.session_state.app_choice = "BQ"

if st.sidebar.button("Achats"):
    st.session_state.app_choice = "Achats"

# Load the selected app
if st.session_state.app_choice == "BQ Ref":
    from bq_ref import app
    app()
elif st.session_state.app_choice == "BQ":
    from bq import app
    app()
elif st.session_state.app_choice == "Achats":
    from achats import app
    app()

# Footer
st.markdown("""
---
### À propos
Cette application a été développée par [OK](https://github.com/thysania).
""")
