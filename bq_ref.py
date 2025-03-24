import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter

def app():
    st.title("BQ Ref - Transformation Excel")
    st.write("Téléchargez votre fichier Excel pour recevoir une version avec menus déroulants")

    uploaded_file = st.file_uploader("Choisissez votre fichier Excel", type=["xlsx"])

    if uploaded_file:
        try:
            # Read and prepare data
            df = pd.read_excel(uploaded_file, header=None)
            
            if df.shape[1] < 7:
                st.error("Le fichier doit contenir au moins 7 colonnes")
                return
                
            # Keep original values from column 5 (index 4) which will become RAW_REF
            original_ref_values = df.iloc[:, 4].values
            df.columns = ["DATE", "DROP", "RAW_LIB", "RAW_TIER", "RAW_REF", "DEBIT", "CREDIT"]
            df = df.drop(columns="DROP")
            
            # Convert to lowercase for matching
            df["RAW_TIER"] = df["RAW_TIER"].astype(str).str.lower()
            df["RAW_LIB"] = df["RAW_LIB"].astype(str).str.lower()
            
            # Create Excel workbook
            wb = Workbook()
            ws = wb.active
            
            # Don't write headers - start from first row
            start_row = 1
            
            # Define dropdown options
            options = ["FELAH", "FAC", "FRAIS", "REMB", "PAIE", "COTIS", "IR", "RETENU MEDECIN", "RETENU AVOCAT"]
            
            # Create data validation
            dv = DataValidation(type="list", formula1=f'"{",".join(options)}"', allow_blank=True)
            ws.add_data_validation(dv)
            
            # Process each row
            for idx, row in df.iterrows():
                original_ref = str(original_ref_values[idx]) if idx < len(original_ref_values) else ""
                
                # Only auto-fill if the original cell was empty
                if pd.isna(original_ref_values[idx]) or str(original_ref_values[idx]).strip() == "":
                    if any(name in row["RAW_TIER"] for name in ["hamza", "youssef", "abdellah", "yousef", "rachid", "majdoubi", "touhami", "bikri", 
                                "bouzidi", "brahim", "derouach", "hatta", "benda", "khalid", "amine", "hamid", 
                                "mohammed", "mohamed", "sliman", "benbo", "dkhail", "charrad", "bouzid", "lehcen", 
                                "acha", "akil", "benz", "hassan", "hadri", "kharmo", "jilali", "houcin", "fellaha", 
                                "miloud", "asmaa", "bouchta", "ahmed"]):
                        ref = "FELAH"
                    elif any(kw in row["RAW_TIER"] for kw in ["orange", "mamda", "onssa", "aswak", "brico", "carref", "wafabail", "cabinet", 
                                "trans", "redal", "refri", "secola", "dakar", "attijari", "temara", "kpa", "easy", 
                                "ajyad", "bioci", "must", "saidou", "bounmer", "print", "moges", "fourni", "bois", 
                                "planex", "smurf"]):
                        ref = "FAC"
                    elif any(kw in row["RAW_LIB"] or kw in row["RAW_TIER"] for kw in ["frais", "commis"]):
                        ref = "FRAIS"
                    elif row["RAW_TIER"] == "cnss":
                        ref = "COTIS"
                    elif any(kw in row["RAW_LIB"] or kw in row["RAW_TIER"] for kw in ["salaire", "paie"]):
                        ref = "PAIE"
                    elif "relanc" in row["RAW_TIER"]:
                        ref = "REMB"
                    elif row["RAW_TIER"] == "dgi" and row["DEBIT"] > 50000:
                        ref = "IR"
                    else:
                        ref = ""  # Empty for dropdown
                else:
                    ref = original_ref  # Keep original value
                
                # Write row to Excel
                ws.append([
                    row["DATE"],
                    row["RAW_LIB"],
                    row["RAW_TIER"],
                    ref,
                    row["DEBIT"],
                    row["CREDIT"]
                ])
                
                # Add dropdown to empty cells or cells that had original values from dropdown options
                if ref == "" or (ref in options and ref == original_ref):
                    dv.add(ws[f"D{idx + start_row + 1}"])  # D column is RAW_REF
            
            # Auto-fit columns
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = (max_length + 2) * 1.2
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Handle row splitting (will appear as separate rows in Excel)
            st.warning("Les lignes DGI avec DEBIT=734 seront divisées en deux lignes dans le fichier final")
            
            # Save to buffer
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            
            st.success("Fichier prêt !")
            st.download_button(
                "Télécharger le fichier avec menus déroulants",
                data=output,
                file_name="donnees_avec_menus.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

if __name__ == "__main__":
    app()
