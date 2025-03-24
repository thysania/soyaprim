import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

def app():
    st.title("BQ Ref - Transformation de données")
    st.write("Téléchargez votre fichier Excel brut pour modifier la cinquième colonne et diviser les lignes.")

    uploaded_file = st.file_uploader("Téléchargez votre fichier Excel", type=["xlsx"])

    if uploaded_file is not None:
        try:
            raw_df = pd.read_excel(uploaded_file, sheet_name=0, header=None)
            
            if raw_df.shape[1] < 7:  # Check for minimum required columns
                st.error("Le fichier doit contenir au moins 7 colonnes.")
                return
                
            # Assign column names
            raw_df.columns = ["DATE", "DROP", "RAW_LIB", "RAW_TIER", "RAW_REF", "DEBIT", "CREDIT"]
            raw_df = raw_df.drop(columns="DROP")
            
            # Convert all columns to string for case-insensitive comparison
            raw_df["RAW_TIER"] = raw_df["RAW_TIER"].astype(str).str.lower()
            raw_df["RAW_LIB"] = raw_df["RAW_LIB"].astype(str).str.lower()
            
            # Process empty RAW_REF cells
            for i in range(len(raw_df)):
                if pd.isna(raw_df.at[i, "RAW_REF"]):
                    tier = raw_df.at[i, "RAW_TIER"]
                    lib = raw_df.at[i, "RAW_LIB"]
                    debit = raw_df.at[i, "DEBIT"]
                    
                    # Determine the appropriate value for RAW_REF
                    if any(name in tier for name in ["hamza", "youssef", "abdellah"]):  # Add all names
                        raw_df.at[i, "RAW_REF"] = "FELAH"
                    elif any(kw in tier for kw in ["orange", "mamda", "onssa"]):  # Add all keywords
                        raw_df.at[i, "RAW_REF"] = "FAC"
                    elif any(kw in lib or kw in tier for kw in ["frais", "commis", "com/vir"]):
                        raw_df.at[i, "RAW_REF"] = "FRAIS"
                    elif tier == "cnss":
                        raw_df.at[i, "RAW_REF"] = "COTIS"
                    elif any(kw in lib or kw in tier for kw in ["salaire", "paie", "ettoumy"]):
                        raw_df.at[i, "RAW_REF"] = "PAIE"
                    elif "relanc" in tier:
                        raw_df.at[i, "RAW_REF"] = "REMB"
                    elif tier == "dgi" and debit > 50000:
                        raw_df.at[i, "RAW_REF"] = "IR"
                    else:
                        # Show dropdown if no condition matches
                        raw_df.at[i, "RAW_REF"] = st.selectbox(
                            f"Choix pour ligne {i+1}",
                            options=["FELAH", "FAC", "FRAIS", "REMB", "PAIE", "COTIS", "IR", "RETENU MEDECIN", "RETENU AVOCAT"]
                        )

            # Row splitting logic
            new_rows = []
            drop_indices = []
            
            for idx, row in raw_df.iterrows():
                if row["RAW_TIER"] == "dgi" and row["DEBIT"] == 734:
                    # Create split rows
                    medecin_row = row.copy()
                    medecin_row["DEBIT"] = 400
                    medecin_row["RAW_REF"] = "RETENU MEDECIN"
                    
                    avocat_row = row.copy()
                    avocat_row["DEBIT"] = 334
                    avocat_row["RAW_REF"] = "RETENU AVOCAT"
                    
                    new_rows.extend([medecin_row, avocat_row])
                    drop_indices.append(idx)
            
            # Combine all data
            if new_rows:
                raw_df = pd.concat([
                    raw_df.drop(drop_indices),
                    pd.DataFrame(new_rows)
                ], ignore_index=True)

            # Display and download results
            st.write("## Résultats transformés")
            st.dataframe(raw_df)
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                raw_df.to_excel(writer, index=False)
            output.seek(0)
            
            st.download_button(
                "Télécharger les données",
                data=output,
                file_name="donnees_transformees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"Erreur: {str(e)}")

if __name__ == "__main__":
    app()
