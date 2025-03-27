import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

def app():
    # Page title
    st.title("Banque")
    
    # File upload
    uploaded_file = st.file_uploader("Choisissez votre fichier Excel", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            # Read raw data (Sheet 1) and mappings (Sheet 2)
            raw_df = pd.read_excel(uploaded_file, sheet_name=0, header=None)
            mappings_df = pd.read_excel(uploaded_file, sheet_name=1, header=None)  # Assuming no headers in Sheet 2
    
            # Validate the number of columns in the raw file
            if raw_df.shape[1] != 7:
                st.error(f"8 colonnes attendues dans le fichier, mais {raw_df.shape[1]} trouvées. Veuillez vérifier la structure du fichier.")
            elif mappings_df.shape[1] < 2:
                st.error(f"Au moins 2 colonnes attendues dans la feuille de mappage, mais {mappings_df.shape[1]} trouvées. Veuillez vérifier la structure du fichier.")
            else:
                # Assign column names to raw data (9 columns)
                raw_df.columns = [
                    "DATE", "RAW_LIB", "RAW_TIER", "RAW_REF", 
                    "DEBIT", "CREDIT", "CA"
                ]
    
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
                    # Rule 0: Column CA equals 1
                    (raw_df["CA"] == 1),
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
                        "BOUNMER", "PRINT", "MOGES", "FOURNI", "BOIS", "PLANEX", "SMURF", "inwi", "deco new", "ideal", "bmj", "relanc"
                    ]), case=False, na=False),
                    # Rule 7: RAW_REF == "IR"
                    (raw_df["RAW_REF"] == "IR")
                ]
    
                choices = [
                    3497000000,  # Rule 0
                    3421000000,  # Rule 1
                    4432000000,  # Rule 2
                    4441000000,  # Rule 3
                    6147300000,  # Rule 4
                    6331000000,  # Rule 5
                    4411000000,  # Rule 6
                    4452500000   # Rule 7
                ]
    
                # Use float type for CPT to support NaN values
                raw_df["CPT"] = np.select(conditions, choices, default=np.nan).astype(float)
    
                # Process LIB (concatenate RAW_LIB/NAT/RAW_TIER)
               # Process LIB (concatenate RAW_LIB/NAT/RAW_TIER) - ignoring empty cells
                raw_df["LIB"] = raw_df.apply(
                    lambda row: "/".join(
                        filter(None, [
                            str(row["RAW_LIB"]).strip() if pd.notna(row["RAW_LIB"]) else None,
                            str(row["RAW_REF"]).strip() if pd.notna(row["RAW_REF"]) else None,
                            str(row["RAW_TIER"]).strip() if pd.notna(row["RAW_TIER"]) else None
                        ]
                    )),
                    axis=1
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
                st.write("### Aperçu des Données Transformées")
                st.dataframe(result_df.head())
    
                # Download button for the result
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    result_df.to_excel(writer, index=False, sheet_name="Données Transformées", na_rep="")
                output.seek(0)
    
                st.download_button(
                    label="Télécharger le fichier",
                    data=output,
                    file_name="import_awb.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
if __name__ == "__main__":
    app()
