import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

def app2():
    st.title("App 2: Dropdown for Fifth Column and Row Splitting")
    st.write("Téléchargez votre fichier Excel brut pour modifier la cinquième colonne et diviser les lignes.")

    # File upload for App 2
    uploaded_file = st.file_uploader("Téléchargez votre fichier Excel brut pour l'Application 2", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # Read raw data
            raw_df = pd.read_excel(uploaded_file, sheet_name=0, header=None)

            # Validate the number of columns
            if raw_df.shape[1] < 5:
                st.error("Le fichier doit contenir au moins 5 colonnes.")
            else:
                # Assign column names
                raw_df.columns = ["DATE", "DROP", "RAW_LIB", "RAW_TIER", "RAW_REF", "DEBIT", "CREDIT", "NAT", "CA"]

                # Determine the last row based on the DATE column
                last_row = raw_df["DATE"].last_valid_index()

                # Process the fifth column (RAW_REF)
                for i in range(last_row + 1):
                    if pd.isna(raw_df.at[i, "RAW_REF"]):  # If cell is empty
                        # Determine the dropdown choice based on conditions
                        if any(name in str(raw_df.at[i, "RAW_TIER"]).lower() for name in [
                            "hamza", "youssef", "abdellah", "yousef", "rachid", "majdoubi", "touhami", "bikri", 
                            "bouzidi", "brahim", "derouach", "hatta", "benda", "khalid", "amine", "hamid", 
                            "mohammed", "mohamed", "sliman", "benbo", "dkhail", "charrad", "bouzid", "lehcen", 
                            "acha", "akil", "benz", "hassan", "hadri", "kharmo", "jilali", "houcin", "fellaha", 
                            "miloud", "asmaa", "bouchta", "ahmed"
                        ]):
                            raw_df.at[i, "RAW_REF"] = "FELAH"
                        elif any(keyword in str(raw_df.at[i, "RAW_TIER"]).lower() for keyword in [
                            "orange", "mamda", "onssa", "aswak", "brico", "carref", "wafabail", "cabinet", 
                            "trans", "redal", "refri", "secola", "dakar", "attijari", "temara", "kpa", "easy", 
                            "ajyad", "bioci", "must", "saidou", "bounmer", "print", "moges", "fourni", "bois", 
                            "planex", "smurf"
                        ]):
                            raw_df.at[i, "RAW_REF"] = "FAC"
                        elif any(keyword in str(raw_df.at[i, "RAW_LIB"]).lower() or str(raw_df.at[i, "RAW_TIER"]).lower() for keyword in ["frais", "commis", "com/vir"]):
                            raw_df.at[i, "RAW_REF"] = "FRAIS"
                        elif str(raw_df.at[i, "RAW_TIER"]).lower() == "cnss":
                            raw_df.at[i, "RAW_REF"] = "COTIS"
                        elif any(keyword in str(raw_df.at[i, "RAW_LIB"]).lower() or str(raw_df.at[i, "RAW_TIER"]).lower() for keyword in ["salaire", "paie", "ettoumy"]):
                            raw_df.at[i, "RAW_REF"] = "PAIE"
                        elif "relanc" in str(raw_df.at[i, "RAW_TIER"]).lower():
                            raw_df.at[i, "RAW_REF"] = "REMB"
                        elif str(raw_df.at[i, "RAW_TIER"]).lower() == "dgi" and raw_df.at[i, "DEBIT"] > 50000:
                            raw_df.at[i, "RAW_REF"] = "IR"
                        else:
                            # Default dropdown options
                            raw_df.at[i, "RAW_REF"] = st.selectbox(
                                f"Choisissez une option pour la ligne {i + 1}",
                                ["FELAH", "FAC", "FRAIS", "REMB", "PAIE", "COTIS", "IR", "RETENU MEDECIN", "RETENU AVOCAT"]
                            )

                # Row-splitting logic
                rows_to_add = []
                rows_to_drop = []
                for index, row in raw_df.iterrows():
                    if str(row["RAW_TIER"]).lower() == "dgi" and row["DEBIT"] == 734:
                        # Create the first new row
                        new_row_1 = row.copy()
                        new_row_1["DEBIT"] = 400
                        new_row_1["RAW_REF"] = "RETENU MEDECIN"
                        rows_to_add.append(new_row_1)

                        # Create the second new row
                        new_row_2 = row.copy()
                        new_row_2["DEBIT"] = 334
                        new_row_2["RAW_REF"] = "RETENU AVOCAT"
                        rows_to_add.append(new_row_2)

                        # Mark the original row for deletion
                        rows_to_drop.append(index)

                # Add new rows and drop the original rows
                if rows_to_add:
                    raw_df = raw_df.append(rows_to_add, ignore_index=True)
                if rows_to_drop:
                    raw_df = raw_df.drop(rows_to_drop)

                # Show preview of the result
                st.write("### Aperçu des Données Modifiées")
                st.dataframe(raw_df.head())

                # Download button for the result
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    raw_df.to_excel(writer, index=False, sheet_name="Données Modifiées")
                output.seek(0)

                st.download_button(
                    label="Télécharger les Données Modifiées",
                    data=output,
                    file_name="donnees_modifiees.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")

# Run the app
if __name__ == "__main__":
    app2()
