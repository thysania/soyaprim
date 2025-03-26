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

# Sidebar for navigation
st.sidebar.title("SOYAPRIM")
app_choice = st.sidebar.radio(
    "Choisissez une application :",
    ("REFERENCE", "BANQUE", "ACHATS")
)

# Load the selected app
if app_choice == "REFERENCE":
    from bq_ref import app as bq_ref_app
    bq_ref_app()
elif app_choice == "BANQUE":
    from bq import app as bq_app
    bq_app()
elif app_choice == "ACHATS":
    from achats import app as achats_app
    achats_app()

