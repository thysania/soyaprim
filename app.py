import pandas as pd
import streamlit as st
from io import BytesIO

# Function to transform the data
def transform_data(file):
    # Load raw data from Excel
    df = pd.read_excel(file, header=None)

    # Step 1: Delete unwanted columns (2, 3, 6, 7, 8 -> index 1, 2, 5, 6, 7)
    df.drop(columns=[1, 2, 5, 6, 7], inplace=True)

    # Step 2: Rename the remaining columns
    df.columns = ["Date", "PRODUIT", "TIERS", "TTC"]

    # Step 3: Add empty columns
    empty_columns = ["N FAC", "IF", "ICE", "MODE REGL", "TAUX TVA", "JOURNAL TRESORIE"]
    for col in empty_columns:
        df[col] = ""

    # Step 4: Add columns with default 0 value
    zero_columns = ["TVA", "CPT TVA"]
    for col in zero_columns:
        df[col] = 0

    # Step 5: Add "CPT HT" column with value 6111000000
    df["CPT HT"] = 6111000000

    # Step 6: Duplicate "TTC" column as "HT"
    df["HT"] = df["TTC"]

    # Step 7: Add "DESIGNATION" column as concatenation of "PRODUIT / TIERS" and delete "PRODUIT"
    df["DESIGNATION"] = df["PRODUIT"] + " / " + df["TIERS"]
    df.drop(columns=["PRODUIT"], inplace=True)

    # Step 8: Rearrange columns in the desired order and set data types
    columns_order = [
        "Date", "N FAC", "TIERS", "IF", "ICE", "DESIGNATION",
        "TTC", "HT", "TVA", "MODE REGL", "DATE REGL", "CPT HT",
        "CPT TVA", "TAUX TVA", "JOURNAL TRESORIE"
    ]
    df = df[columns_order]

    # Convert data types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # Set invalid dates as NaT
    df["TIERS"] = df["TIERS"].astype(str)
    df["DESIGNATION"] = df["DESIGNATION"].astype(str)
    df["TTC"] = df["TTC"].astype(float)
    df["HT"] = df["HT"].astype(float)
    df["CPT HT"] = df["CPT HT"].astype(int)

    return df

# Streamlit app
st.title("Excel Data Transformation App")

# File upload
uploaded_file = st.file_uploader("Upload your raw data file (Excel format)", type=["xlsx", "xls"])

if uploaded_file:
    # Transform the uploaded file
    transformed_data = transform_data(uploaded_file)

    # Save the transformed data to a BytesIO object
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        transformed_data.to_excel(writer, index=False, sheet_name="Transformed Data")
        workbook = writer.book
        worksheet = writer.sheets["Transformed Data"]

        # Format headers with blue fill and white font
        from openpyxl.styles import PatternFill, Font
        header_fill = PatternFill(start_color="0000FF", end_color="0000FF", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in worksheet[1]:  # First row (headers)
            cell.fill = header_fill
            cell.font = header_font

    # Convert BytesIO to downloadable file
    output.seek(0)
    st.success("File transformed successfully!")
    st.download_button(
        label="Download Transformed File",
        data=output,
        file_name="transformed_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )