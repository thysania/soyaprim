import streamlit as st

# Custom CSS to style the buttons and hide the sidebar
st.markdown("""
<style>
/* Center the buttons and make them the same width */
.stButton button {
    width: 100%;
    background-color: #4F8BF9;
    color: white;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 16px;
    margin: 5px 0;
}

/* Hide the sidebar on the first screen */
section[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for app choice
if "app_choice" not in st.session_state:
    st.session_state.app_choice = None

# First Screen: Show only if no app is selected
if st.session_state.app_choice is None:
    # Title
    st.title("SOYAPRIM")

    # Create three vertically aligned buttons
    if st.button("BQ Ref"):
        st.session_state.app_choice = "BQ Ref"

    if st.button("BQ"):
        st.session_state.app_choice = "BQ"

    if st.button("Achats"):
        st.session_state.app_choice = "Achats"

# If an app is selected, display it with a sidebar
else:
    # Custom CSS to hide the first screen
    st.markdown("""
    <style>
    /* Hide the first screen */
    div[data-testid="stVerticalBlock"] > div:first-child {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_choice = st.sidebar.radio(
        "Choisissez une application :",
        ("BQ Ref", "BQ", "Achats"),
        index=["BQ Ref", "BQ", "Achats"].index(st.session_state.app_choice)
    )

    # Load the selected app
    if app_choice == "BQ Ref":
        from bq_ref import app as bq_ref_app
        bq_ref_app()
    elif app_choice == "BQ":
        from bq import app as bq_app
        bq_app()
    elif app_choice == "Achats":
        from achats import app as achats_app
        achats_app()
