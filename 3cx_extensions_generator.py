
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="3CX Extensions Generator", layout="centered")
st.title("📞 3CX Extensions Generator")

st.markdown("""
Questa app ti permette di generare un file `extensions.csv` per l'importazione in 3CX partendo da un codice punto vendita.

- Gli interni verranno generati automaticamente in base al codice PV.
- Alcuni ruoli chiave (Box, Interfono, Direttore, Vicedirettore, Capo Cassiera, Ricevimento Merci) vengono creati automaticamente.
- Puoi scaricare direttamente il file pronto per l'import.
""")

# Input del codice punto vendita (PV)
codice_pv = st.text_input("Codice Punto Vendita (PV)", max_chars=6)

# Numero di estensioni aggiuntive da generare (oltre ai ruoli fissi)
num_extensions = st.number_input("Numero di estensioni aggiuntive da generare", min_value=0, max_value=100, value=5)

def generate_extensions(pv_code: str, count: int):
    base = int(pv_code) * 100
    extensions = []

    # Estensioni fisse per i ruoli chiave
    ruoli_fissi = [
        (int("00"), "Box"),
        (80, "Interfono"),
        (99, "Direttore"),
        (98, "Vicedirettore"),
        (97, "Capo Cassiera"),
        (96, "Ricevimento Merci")
    ]
    for suffix, ruolo in ruoli_fissi:
        ext = base + suffix
        extensions.append({
            "Extension": ext,
            "First Name": ruolo,
            "Last Name": "",
            "Email Address": f"user{ext}@example.com",
            "Mobile Number": "",
            "Outbound Caller ID": "",
            "Authentication ID": ext,
            "Authentication Password": ""
        })

    # Estensioni aggiuntive
    for i in range(count):
        ext = base + i
        # Evita duplicati con gli interni fissi
        if ext in [base + s for s, _ in ruoli_fissi]:
            continue
        extensions.append({
            "Extension": ext,
            "First Name": f"User{ext}",
            "Last Name": "",
            "Email Address": f"user{ext}@example.com",
            "Mobile Number": "",
            "Outbound Caller ID": "",
            "Authentication ID": ext,
            "Authentication Password": ""
        })

    return pd.DataFrame(extensions)

if codice_pv and codice_pv.isdigit():
    df = generate_extensions(codice_pv, num_extensions)
    st.dataframe(df, use_container_width=True)

    # Converti in CSV e offri per il download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica CSV per 3CX",
        data=csv,
        file_name='3cx_import_ready.csv',
        mime='text/csv'
    )
else:
    st.info("Inserisci un codice punto vendita numerico per generare le estensioni.")
