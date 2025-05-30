
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

codice_pv = st.text_input("Codice Punto Vendita (PV)", max_chars=6)

num_extensions = st.number_input("Numero di estensioni aggiuntive da generare", min_value=0, max_value=100, value=5)

# Prompt per MAC address per Box e Interfono
mac_box = st.text_input("MAC address per Box (interno 00)")
mac_interfono = st.text_input("MAC address per Interfono (interno 80)")

# Valori booleani e fissi presi dal file di esempio
campi_booleani = {
    "VMEnable": "0",
    "VMNoPin": "1",
    "VMPlayCallerID": "0",
    "RecordCalls": "0",
    "RecordExternal": "0",
    "RecordCanSee": "0",
    "RecordCanDelete": "0",
    "RecordStartStop": "1",
    "RecordNotify": "0",
    "Disabled": "0",
    "HideFWrules": "0",
    "DisableExternalCalls": "0",
    "HideInPhonebook": "0",
    "CallScreening": "0",
    "PinProtected": "0",
    "AllowLanOnly": "1",
    "HotDesk": "0",
    "EmailMissedCalls": "1"
}

# Carichiamo le colonne da un file di esempio statico (dal sample PV587)
colonne = [
    'Number', 'FirstName', 'LastName', 'EmailAddress', 'MobileNumber', 'OutboundCallerID', 'DID', 'Role', 'Department',
    'ClickToCallAuth', 'WMApprove', 'WebMeetingFriendlyName', 'MAC', 'Template', 'Model', 'Router', 'Language',
    'Ringtone', 'QRingtone', 'VMEnable', 'VMLanguage', 'VMPlayMsgDateTime', 'VMPIN', 'VMEmailOptions', 'VMNoPin',
    'VMPlayCallerID', 'RecordCalls', 'RecordExternal', 'RecordCanSee', 'RecordCanDelete', 'RecordStartStop',
    'RecordNotify', 'Disabled', 'HideFWrules', 'DisableExternalCalls', 'HideInPhonebook', 'CallScreening',
    'PinProtected', 'PinTimeout', 'Transcription', 'AllowLanOnly', 'SIPID', 'DeliverAudio', 'HotDesk', 'SRTPMode',
    'EmailMissedCalls', 'MS365SignInDisabled', 'MS365CalendarDisabled', 'MS365ContactsDisabled', 'MS365TeamsDisabled',
    'GoogleSignInDisabled', 'GoogleContactsDisabled', 'GoogleCalendarDisabled', 'BLF'
]

def generate_extensions(pv_code: str, count: int):
    base = int(pv_code) * 100
    rows = []

    def make_row(number, first_name, mac="", template="Yealink T42S", model="T42", role="", department="PV", blf=""):
        row = {col: "" for col in colonne}
        row["Number"] = number
        row["FirstName"] = first_name
        row["EmailAddress"] = f"user{number}@example.com"
        row["MAC"] = mac
        row["Router"] = mac
        row["Template"] = template
        row["Model"] = model
        row["Language"] = "it"
        row["Role"] = role
        row["Department"] = department
        row["WebMeetingFriendlyName"] = first_name
        row["Ringtone"] = "Europe"
        row["QRingtone"] = "Europe"
        row["BLF"] = blf
        row.update(campi_booleani)
        return row

    # Estensioni fisse
    rows.append(make_row(base + 0, "Box", mac=mac_box, role="Box", blf=""))
    rows.append(make_row(base + 80, "Interfono", mac=mac_interfono, role="Interfono", template="Fanvil PA3", model="PA3", blf=""))
    rows.append(make_row(base + 99, "Direttore", role="Direttore"))
    rows.append(make_row(base + 98, "Vicedirettore", role="Vicedirettore"))
    rows.append(make_row(base + 97, "Capo Cassiera", role="Capo Cassiera"))
    rows.append(make_row(base + 96, "Ricevimento Merci", role="Ricevimento Merci"))

    # Estensioni aggiuntive
    for i in range(count):
        ext = base + i
        if ext in [base + s for s in [0, 80, 99, 98, 97, 96]]:
            continue
        rows.append(make_row(ext, f"User{ext}"))

    return pd.DataFrame(rows)

if codice_pv and codice_pv.isdigit():
    df = generate_extensions(codice_pv, num_extensions)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Scarica CSV per 3CX",
        data=csv,
        file_name='3cx_import_ready.csv',
        mime='text/csv'
    )
else:
    st.info("Inserisci un codice punto vendita numerico per generare le estensioni.")
