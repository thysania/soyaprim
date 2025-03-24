import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

def app():
    st.title("BQ Ref - Transformation de données")
    
    if 'processed' not in st.session_state:
        st.session_state.processed = False
        st.session_state.raw_df = None
        st.session_state.final_df = None

    uploaded_file = st.file_uploader("Téléchargez votre fichier Excel", type=["xlsx"])

    if uploaded_file and not st.session_state.processed:
        try:
            # Read and prepare data
            raw_df = pd.read_excel(uploaded_file, sheet_name=0, header=None)
            
            if raw_df.shape[1] < 7:
                st.error("Le fichier doit contenir au moins 7 colonnes.")
                return
                
            raw_df.columns = ["DATE", "DROP", "RAW_LIB", "RAW_TIER", "RAW_REF", "DEBIT", "CREDIT"]
            raw_df = raw_df.drop(columns="DROP")
            raw_df["RAW_TIER"] = raw_df["RAW_TIER"].astype(str).str.lower()
            raw_df["RAW_LIB"] = raw_df["RAW_LIB"].astype(str).str.lower()
            
            # Store the raw data
            st.session_state.raw_df = raw_df
            st.session_state.final_df = raw_df.copy()
            
            # Find rows needing manual selection
            manual_selection_rows = []
            for i in range(len(raw_df)):
                if pd.isna(raw_df.at[i, "RAW_REF"]):
                    tier = raw_df.at[i, "RAW_TIER"]
                    lib = raw_df.at[i, "RAW_LIB"]
                    debit = raw_df.at[i, "DEBIT"]
                    
                    # Automatic assignments
                    if any(name in tier for name in ["hamza", "youssef"]):
                        st.session_state.final_df.at[i, "RAW_REF"] = "FELAH"
                    elif any(kw in tier for kw in ["orange", "mamda"]):
                        st.session_state.final_df.at[i, "RAW_REF"] = "FAC"
                    elif any(kw in lib or kw in tier for kw in ["frais", "commis"]):
                        st.session_state.final_df.at[i, "RAW_REF"] = "FRAIS"
                    elif tier == "cnss":
                        st.session_state.final_df.at[i, "RAW_REF"] = "COTIS"
                    elif any(kw in lib or kw in tier for kw in ["salaire", "paie"]):
                        st.session_state.final_df.at[i, "RAW_REF"] = "PAIE"
                    elif "relanc" in tier:
                        st.session_state.final_df.at[i, "RAW_REF"] = "REMB"
                    elif tier == "dgi" and debit > 50000:
                        st.session_state.final_df.at[i, "RAW_REF"] = "IR"
                    else:
                        manual_selection_rows.append(i)
            
            # Store rows needing manual selection
            st.session_state.manual_rows = manual_selection_rows
            st.session_state.current_row = 0 if manual_selection_rows else None
            
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
            return

    if st.session_state.raw_df is not None and not st.session_state.processed:
        if st.session_state.manual_rows:
            # Show dropdown for current row needing selection
            current_idx = st.session_state.manual_rows[st.session_state.current_row]
            row_data = st.session_state.raw_df.iloc[current_idx]
            
            st.write(f"## Ligne {current_idx + 1} nécessite une sélection manuelle")
            st.write(f"Libellé: {row_data['RAW_LIB']}")
            st.write(f"Tiers: {row_data['RAW_TIER']}")
            
            selected = st.selectbox(
                "Choisissez une option:",
                options=["FELAH", "FAC", "FRAIS", "REMB", "PAIE", "COTIS", "IR", "RETENU MEDECIN", "RETENU AVOCAT"],
                key=f"select_{current_idx}"
            )
            
            if st.button("Confirmer la sélection"):
                st.session_state.final_df.at[current_idx, "RAW_REF"] = selected
                st.session_state.current_row += 1
                
                if st.session_state.current_row >= len(st.session_state.manual_rows):
                    st.session_state.processed = True
                    st.experimental_rerun()
        else:
            st.session_state.processed = True

    if st.session_state.processed and st.session_state.final_df is not None:
        # Apply row splitting
        new_rows = []
        drop_indices = []
        
        for idx, row in st.session_state.final_df.iterrows():
            if row["RAW_TIER"] == "dgi" and row["DEBIT"] == 734:
                medecin_row = row.copy()
                medecin_row["DEBIT"] = 400
                medecin_row["RAW_REF"] = "RETENU MEDECIN"
                
                avocat_row = row.copy()
                avocat_row["DEBIT"] = 334
                avocat_row["RAW_REF"] = "RETENU AVOCAT"
                
                new_rows.extend([medecin_row, avocat_row])
                drop_indices.append(idx)
        
        if new_rows:
            final_df = pd.concat([
                st.session_state.final_df.drop(drop_indices),
                pd.DataFrame(new_rows)
            ], ignore_index=True)
        else:
            final_df = st.session_state.final_df.copy()

        # Show final results
        st.write("## Résultats finaux")
        st.dataframe(final_df)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            final_df.to_excel(writer, index=False)
        
        st.download_button(
            "Télécharger les données transformées",
            data=output,
            file_name="donnees_finales.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        if st.button("Traiter un nouveau fichier"):
            st.session_state.clear()
            st.experimental_rerun()

if __name__ == "__main__":
    app()
