import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
from io import BytesIO
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill, Font

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
                # Assign column names to raw data (7 columns)
                raw_df.columns = [
                    "DATE", "RAW_LIB", "RAW_TIER", "RAW_REF", 
                    "DEBIT", "CREDIT", "CA"
                ]
                
                # Create a copy of rows to split - specifically for DGI with DEBIT=734
                rows_to_split = raw_df[(raw_df["RAW_TIER"].astype(str).str.contains("dgi", case=False)) & 
                                      (raw_df["DEBIT"] == 734)].copy()

                if not rows_to_split.empty:
                    # Create two new rows for each row to split
                    split_rows = []
                    indices_to_drop = []
                    
                    for idx, row in rows_to_split.iterrows():
                        indices_to_drop.append(idx)
                        
                        # First row - RETENU MEDECIN
                        medecin_row = row.copy()
                        medecin_row["RAW_REF"] = "RETENU MEDECIN"
                        medecin_row["DEBIT"] = 400
                        
                        # Second row - RETENU AVOCAT
                        avocat_row = row.copy()
                        avocat_row["RAW_REF"] = "RETENU AVOCAT"
                        avocat_row["DEBIT"] = 334
                        
                        split_rows.append(medecin_row)
                        split_rows.append(avocat_row)
                    
                    # Remove the original rows and add the new rows
                    raw_df = raw_df.drop(indices_to_drop)
                    
                    # Add the new rows
                    if split_rows:
                        split_df = pd.DataFrame(split_rows)
                        raw_df = pd.concat([raw_df, split_df], ignore_index=True)
    
                # Process TIERS (lookup RAW_TIER as wildcard in mappings sheet)
                def lookup_tiers(raw_tier):
                    if pd.isna(raw_tier):
                        return np.nan
                    
                    # Special case for "abdelatif saidou(medecin)"
                    if isinstance(raw_tier, str) and "saidou" in str(raw_tier).lower() and "medecin" in str(raw_tier).lower():
                        return "SAIDOU ABDELLATIPH"
                    
                    # Find rows in mappings_df where the pattern matches RAW_TIER (wildcard)
                    matches = mappings_df[mappings_df[0].astype(str).str.contains(str(raw_tier), case=False, na=False)]
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
                    # Rule 2: RAW_FILTER starts with "SALAIRE" or NAT == "PAIE"
                    (raw_df["RAW_REF"].astype(str).str.upper().str.startswith("SALAIRE", na=False)) | (raw_df["RAW_REF"] == "PAIE"),
                    # Rule 3: RAW_TIER == "CNSS" or NAT == "COTIS"
                    (raw_df["RAW_TIER"].astype(str).str.upper() == "CNSS") | (raw_df["RAW_REF"] == "COTIS"),
                    # Rule 4: RAW_REF == FRAIS
                    (raw_df["RAW_REF"] == "FRAIS") | raw_df["RAW_LIB"].astype(str).str.upper().str.startswith("FRAIS", na=False),
                    # Rule 5: RAW_REF equals PERTE
                    (raw_df["RAW_REF"] == "PERTE"),
                    # Rule 5.1: RAW_REF equals GAIN
                    (raw_df["RAW_REF"] == "GAIN"),
                    # Rule 6: NAT == "FELAH" or TIERS contains specified strings
                    (raw_df["RAW_REF"] == "FELAH") | 
                    raw_df["TIERS"].astype(str).str.contains("|".join([
                        "AJYAD", "ASWAK", "ATTIJARI", "AUTOROUTE", "BIOCI", "BOIS", "BOUNMER", 
                        "BRICO", "CABINET", "CARREF", "consilia", "conseil", "da graph", "deco new", 
                        "durofloor", "electroplanet", "environnement", "FOURNI", "BAZAS", 
                        "globus", "hamri tissus", "ideal", "inwi", "incendie", "khadamat", "kitea", 
                        "KPA", "lab", "lvs", "MAMDA", "MARAHIL", "marjan", "ministre", "MOGES", "MUST", "ORANGE", 
                        "PLANEX", "pneumatique", "PRINT", "REDAL", "relanc", "REFRI", "SANITAIRE", 
                        "secola", "SMURF", "smpce", "SOLUTIONS", "STARDEC", "TEMARA", "trois", "WAFABAIL", 
                        "intra", "abcr", "boulon", "bmj", "Khadamat", "TRANS", "AFROUKH", "onssa", "ZIMBA", 
                        "STORES", "GOLD", "COMPLEX", "LEGNO", "TISSUS", "DAKAR", "PROJET", "D.A"
                    ]), case=False, na=False),
                    # Rule 7: RAW_REF == "IR"
                    (raw_df["RAW_REF"] == "IR"),
                    # Rule 8: RAW_REF == "RETENU MEDECIN"
                    (raw_df["RAW_REF"] == "RETENU MEDECIN"),
                    # Rule 9: RAW_REF == "RETENU AVOCAT"
                    (raw_df["RAW_REF"] == "RETENU AVOCAT"),
                    # Rule 10: RAW_TIER contains "SAIDOU"
                    (raw_df["RAW_TIER"].astype(str).str.upper().str.contains("SAIDOU", na=False))
                ]
    
                choices = [
                    3497000000,  # Rule 0
                    3421000000,  # Rule 1
                    4432000000,  # Rule 2
                    4441000000,  # Rule 3
                    6147300000,  # Rule 4
                    6331000000,  # Rule 5
                    7331000000,  # Rule 5.1
                    4411000000,  # Rule 6
                    4452500000,  # Rule 7
                    4458110100,  # Rule 8
                    4458110200,  # Rule 9
                    4411000000   # Rule 10
                ]
    
                # Use float type for CPT to support NaN values
                raw_df["CPT"] = np.select(conditions, choices, default=np.nan).astype(float)
    
                # Process LIB (concatenate RAW_LIB/NAT/RAW_TIER) - ignoring empty cells
                raw_df["LIB"] = raw_df.apply(
                    lambda row: " / ".join(
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
                
                # Sort the dataframe by DATE from old to new
                # First convert back to datetime for proper sorting
                result_df["DATE_SORT"] = pd.to_datetime(result_df["DATE"], format="%d/%m/%Y")
                result_df = result_df.sort_values(by="DATE_SORT", ascending=True)
                result_df = result_df.drop(columns=["DATE_SORT"])  # Remove the sorting column
    
                # Show preview of the result
                st.write("### Aperçu des Données Transformées")
                st.dataframe(result_df.head())
    
                # Download button for the result
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    result_df.to_excel(writer, index=False, sheet_name="Données Transformées", na_rep="")
                    
                    # Get the worksheet to apply formatting
                    workbook = writer.book
                    worksheet = writer.sheets["Données Transformées"]
                    
                    # Auto-fit columns
                    for col_num, column in enumerate(result_df.columns, 1):
                        column_width = max(
                            result_df[column].astype(str).map(len).max(),  # Width of the data
                            len(str(column))  # Width of the header
                        ) + 2  # Add a little extra space
                        worksheet.column_dimensions[get_column_letter(col_num)].width = column_width
                    
                    # Format headers with color #2596be
                    for cell in worksheet[1]:
                        cell.fill = PatternFill(start_color="2596BE", end_color="2596BE", fill_type="solid")
                        cell.font = Font(bold=True, color="FFFFFF")  # White text for better contrast
                    # If date_value is already a datetime object:
                    date_value = raw_df.iloc[0, 0]
                    def get_mmyy_from_a1(date_value):
                        # Handle different potential date formats
                        if isinstance(date_value, dt.datetime):
                            mmyy = date_value.strftime("%m%y")
                        elif isinstance(date_value, str):
                            # Try to parse the string into a datetime
                            try:
                                date_obj = pd.to_datetime(date_value)
                                mmyy = date_obj.strftime("%m%y")
                            except:
                                # If parsing fails, return a default value or handle accordingly
                                mmyy = "0000"
                        else:
                            mmyy = "0000"
                        
                        return mmyy
                    
                    # Now get the MMYY string from A1
                    mmyy = get_mmyy_from_a1(date_value)
                
                output.seek(0)
                st.success("Votre fichier est prêt !")
                st.download_button(
                    label="Télécharger le fichier",
                    data=output,
                    file_name="import_awb_{mmyy}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
            # For debugging
            st.error(f"Détails: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            
if __name__ == "__main__":
    app()
