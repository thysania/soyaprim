import streamlit as st

# Custom CSS to center the buttons and remove the sidebar
st.markdown("""
<style>
/* Center the buttons */
.stButton button {
    display: block;
    margin: 0 auto;
    background-color: #4F8BF9;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
}

/* Hide the sidebar on the first screen */
section[data-testid="stSidebar"] {
    display: none;
}

/* Change the color of the selected radio button */
div[role="radiogroup"] > label > div:first-child {
    background-color: #4F8BF9 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("SOYAPRIM Data Transformation Suite")
st.write("""
Bienvenue dans l'application de transformation de données SOYAPRIM. 
Sélectionnez une application ci-dessous pour commencer.
""")

# Create three centered buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("BQ Ref"):
        st.session_state.app_choice = "BQ Ref"

with col2:
    if st.button("BQ"):
        st.session_state.app_choice = "BQ"

with col3:
    if st.button("Achats"):
        st.session_state.app_choice = "Achats"

# Initialize session state for app choice
if "app_choice" not in st.session_state:
    st.session_state.app_choice = None

# If an app is selected, display it with a sidebar
if st.session_state.app_choice:
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_choice = st.sidebar.radio(
        "Choisissez une application :",
        ("BQ Ref", "BQ", "Achats"),
        index=["BQ Ref", "BQ", "Achats"].index(st.session_state.app_choice)
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