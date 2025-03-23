import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Page title
st.title("Excel Data Transformation App")
st.write("Upload your raw Excel file and download the transformed data.")

# File upload
uploaded_file = st.file_uploader("Upload your raw Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read raw data (Sheet 1) and mappings (Sheet 2)
        raw_df = pd.read_excel(uploaded_file, sheet_name=0, header=None)
        mappings_df = pd.read_excel(uploaded_file, sheet_name=1, header=None)  # Assuming no headers in Sheet 2

        # Validate the number of columns in the raw file
        if raw_df.shape[1] != 8:
            st.error(f"Expected 8 columns in the raw file, but found {raw_df.shape[1]}. Please check the file structure.")
        elif mappings_df.shape[1] < 2:
            st.error(f"Expected at least 2 columns in the mappings sheet, but found {mappings_df.shape[1]}. Please check the file structure.")
        else:
            # Assign column names to raw data (9 columns)
            raw_df.columns = [
                "DATE", "DROP", "RAW_LIB", "RAW_TIER", "RAW_REF", 
                "DEBIT", "CREDIT", "CA"
            ]
            raw_df = raw_df.drop(columns="DROP")  # Remove second column

            # Process TIERS (lookup RAW_TIER as wildcard in mappings sheet)
            def lookup_tiers(raw_tier):
                if pd.isna(raw_tier):
                    return np.nan
                # Find rows in mappings_df where the pattern matches RAW_TIER (wildcard)
                matches = mappings_df[mappings_df[0].astype(str).str.contains(raw_tier, case=False, na=False)]
                if not matches.empty:
                    return matches.iloc[0, 1]  # Return the first matching value from column 1
                return np.nan

            raw_df["TIERS"] = raw_df["RAW_TIER"].apply(lookup_tiers)

            # Process CPT (apply conditions)
            # Ensure all conditions are boolean arrays
            conditions = [
                # Rule 7: Column CA equals 1
                (raw_df["CA"] == 1)
                # Rule 1: RAW_TIER starts with "FRUL" (case-insensitive)
                raw_df["RAW_TIER"].astype(str).str.upper().str.startswith("FRUL", na=False),
                # Rule 2: RAW_FILTER starts with "SALAIRE" or NAT == "PAIE" (assuming RAW_FILTER is a typo for another column)
                (raw_df["RAW_REF"].astype(str).str.upper().str.startswith("SALAIRE", na=False)) | (raw_df["RAW_REF"] == "PAIE"),
                # Rule 3: RAW_TIER == "CNSS" or NAT == "COTIS"
                (raw_df["RAW_TIER"].astype(str).str.upper() == "CNSS") | (raw_df["RAW_REF"] == "COTIS"),
                # Rule 4: RAW_LIB starts with "Commis" or "Frais"
                raw_df["RAW_LIB"].astype(str).str.upper().str.startswith(("COMMIS", "FRAIS"), na=False),
                # Rule 5: RAW_LIB starts with "diff" or contains "change"
                raw_df["RAW_LIB"].astype(str).str.upper().str.contains("DIFF", na=False) | 
                raw_df["RAW_LIB"].astype(str).str.upper().str.contains("CHANGE", na=False),
                # Rule 6: NAT == "FELAH" or TIERS contains specified strings
                (raw_df["RAW_REF"] == "FELAH") | 
                raw_df["TIERS"].astype(str).str.contains("|".join([
                    "ORANGE", "MAMDA", "ONSSA", "ASWAK", "BRICO", "CARREF", "WAFABAIL", 
                    "CABINET", "TRANS", "REDAL", "REFRI", "SECOLA", "DAKAR", "ATTIJARI", 
                    "TEMARA", "KPA", "EASY", "AJYAD", "BIOCI", "MUST", "SAIDOU", 
                    "BOUNMER", "PRINT", "MOGES", "FOURNI", "BOIS", "PLANEX", "SMURF"  # Added "SMURF"
                ]), case=False, na=False),
                # Rule 7: Column CA equals 1
                (raw_df["CA"] == 1)
            ]

            choices = [
                3497000000   # Rule 7
                3421000000,  # Rule 1
                4432000000,  # Rule 2
                4441000000,  # Rule 3
                6147300000,  # Rule 4
                6331000000,  # Rule 5
                4411000000,  # Rule 6
            ]

            # Use float type for CPT to support NaN values
            raw_df["CPT"] = np.select(conditions, choices, default=np.nan).astype(float)

            # Process LIB (concatenate RAW_LIB/NAT/RAW_TIER)
            raw_df["LIB"] = (
                raw_df["RAW_LIB"].astype(str) + "/" + 
                raw_df["RAW_REF"].astype(str) + "/" + 
                raw_df["RAW_TIER"].astype(str)
            )

            # Create final DataFrame with specified columns and formatting
            result_df = pd.DataFrame({
                "DATE": pd.to_datetime(raw_df["DATE"]).dt.strftime("%d/%m/%Y"),
                "N PIECE": np.nan,
                "CPT": raw_df["CPT"],
                "TIERS": raw_df["TIERS"],
                "LIB": raw_df["LIB"].astype(str),
                "REF": np.nan,
                "DEBIT": raw_df["DEBIT"].round(2),
                "CREDIT": raw_df["CREDIT"].round(2)
            })

            # Replace "nan" strings with truly empty cells
            result_df["CPT"] = result_df["CPT"].replace("nan", np.nan)
            result_df["TIERS"] = result_df["TIERS"].replace("nan", np.nan)

            # Show preview of the result
            st.write("### Transformed Data Preview")
            st.dataframe(result_df.head())

            # Download button for the result
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                result_df.to_excel(writer, index=False, sheet_name="Transformed Data", na_rep="")
            output.seek(0)

            st.download_button(
                label="Download Transformed Data",
                data=output,
                file_name="transformed_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")
