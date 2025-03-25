import streamlit as st
from PIL import Image

# Custom CSS for styling
st.markdown("""
<style>
h1 {
    color: #4F8BF9;
    text-align: center;
}
.stButton button {
    background-color: #4F8BF9;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
}
.css-1d391kg {
    background-color: #F0F2F6;
}
</style>
""", unsafe_allow_html=True)

# Add a logo
logo = Image.open("logo.png")
st.image(logo, width=100)

# Title and description
st.title("SOYAPRIM Data Transformation Suite")
st.write("""
Bienvenue dans l'application de transformation de données SOYAPRIM. 
Sélectionnez une application ci-dessous pour commencer.
""")

# Add a fun animation
st.balloons()

# Sidebar for navigation
st.sidebar.title("Navigation")
app_choice = st.sidebar.radio(
    "Choisissez une application :",
    ("BQ Ref", "BQ", "Achats")
)

# Load the selected app
if app_choice == "BQ Ref":
    from bq_ref import app2 as bq_ref_app
    bq_ref_app()
elif app_choice == "BQ":
    from bq import app as bq_app
    bq_app()
elif app_choice == "Achats":
    from achats import app as achats_app
    achats_app()

# Footer
st.markdown("""
---
### À propos
Cette application a été développée par [Votre Nom](https://github.com/thysania).
""")
