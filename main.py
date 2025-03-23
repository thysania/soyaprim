import streamlit as st

# Sidebar for app selection
st.sidebar.title("Navigation")
app_choice = st.sidebar.radio(
    "Choisissez une application :",
    ("bq_ref", "bq", "achats")
)

# Import and run the selected app
if app_choice == "bq_ref":
    from bq_ref import app as bq_ref_app
    bq_ref_app()
elif app_choice == "bq":
    from bq import app as bq_app
    bq_app()
elif app_choice == "achats":
    from achats import app as achats_app
    achats_app()
