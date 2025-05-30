
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="3CX Extensions Generator", layout="centered")
st.title("📞 3CX Extensions Generator")

st.markdown("""
Questa app genera un file `extensions.csv` compatibile con 3CX, rispettando il formato ufficiale.
- Inserisci il codice punto vendita (PV)
- MAC richiesti solo per Box (00) e Interfono (80)
- Estensioni fisse: Box (00), Interfono (80), Direttore (99), Vicedirettore (98), Capo Cassiera (97), Ricevimento Merci (96)
- Aggiungi un numero arbitrario di estensioni extra
""")

# Input utente
codice_pv = st.text_input("Codice Punto Vendita (PV)", max_chars=6)
num_extra = st.number_input("Numero di estensioni aggiuntive", min_value=0, max_value=100, value=5)

# Prepara colonne dal sample
colonne = {col: "" for col in [
    "Number", "FirstName", "LastName", "EmailAddress", "MobileNumber", "OutboundCallerID", "DID",
    "Role", "Department", "ClickToCallAuth", "WMApprove", "WebMeetingFriendlyName", "MAC",
    "Template", "Model", "Router", "Language", "Ringtone", "QRingtone", "VMEnable", "VMLanguage",
    "VMPlayMsgDateTime", "VMPIN", "VMEmailOptions", "VMNoPin", "VMPlayCallerID", "RecordCalls",
    "RecordExternal", "RecordCanSee", "RecordCanDelete", "RecordStartStop", "RecordNotify",
    "Disabled", "HideFWrules", "DisableExternalCalls", "HideInPhonebook", "CallScreening",
    "PinProtected", "PinTimeout", "Transcription", "AllowLanOnly", "SIPID", "DeliverAudio",
    "HotDesk", "SRTPMode", "EmailMissedCalls", "MS365SignInDisabled", "MS365CalendarDisabled",
    "MS365ContactsDisabled", "MS365TeamsDisabled", "GoogleSignInDisabled", "GoogleContactsDisabled",
    "GoogleCalendarDisabled", "BLF"
]}

# Valori fissi dal sample
valori_fissi = {
    "Role": "<role name=\"users\" />",
    "Template": "yealinkT4x.ph.xml",
    "Model": "Yealink T42U",
    "Language": "Italian",
    "Ringtone": "Ring 1",
    "QRingtone": "Ring 6",
    "VMLanguage": "307392E1-F915-4f3a-9362-5049AADC242C",
    "VMPIN": 423395,
    "PinTimeout": 60,
    "BLF": "<PhoneDevice><BLFS/></PhoneDevice>",
    "ClickToCallAuth": 0, "WMApprove": 0, "VMEnable": 0, "VMPlayMsgDateTime": 0, "VMEmailOptions": 1,
    "VMNoPin": 1, "VMPlayCallerID": 0, "RecordCalls": 0, "RecordExternal": 0, "RecordCanSee": 0,
    "RecordCanDelete": 0, "RecordStartStop": 1, "RecordNotify": 0, "Disabled": 0, "HideFWrules": 0,
    "DisableExternalCalls": 0, "HideInPhonebook": 0, "CallScreening": 0, "PinProtected": 0,
    "AllowLanOnly": 1, "DeliverAudio": 0, "HotDesk": 0, "SRTPMode": 0, "EmailMissedCalls": 1
}

ruoli_fissi = [
    (0, "Box"), (80, "Interfono"), (99, "Direttore"), (98, "Vicedirettore"),
    (97, "Capo Cassiera"), (96, "Ricevimento Merci")
]

def chiedi_mac(etichetta):
    return st.text_input(f"MAC per {etichetta}:")

if codice_pv and codice_pv.isdigit():
    base = int(codice_pv) * 100
    righe = []

    mac_dict = {}
    for suffisso, ruolo in ruoli_fissi:
        interno = base + suffisso
        key = f"{interno} - {ruolo}"
        if ruolo in ["Box", "Interfono"]:
            mac_dict[key] = chiedi_mac(key)
        else:
            mac_dict[key] = ""

    for i in range(num_extra):
        interno = base + i
        key = f"{interno} - Estensione Extra"
        if interno not in [base + s for s, _ in ruoli_fissi]:
            mac_dict[key] = ""  # No richiesta MAC per extra

    for chiave, mac in mac_dict.items():
        numero = chiave.split(" - ")[0]
        nome = chiave.split(" - ")[1]
        row = colonne.copy()
        row.update(valori_fissi)
        row["Number"] = numero
        row["FirstName"] = f"{numero} {nome}"
        row["WebMeetingFriendlyName"] = f"{numero}{nome.lower().replace(' ', '')}"
        row["Department"] = f"PV {codice_pv}"
        row["EmailAddress"] = f"user{numero}@example.com"
        row["MAC"] = mac
        row["Router"] = mac
        righe.append(row)

    df = pd.DataFrame(righe)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Scarica CSV 3CX", data=csv, file_name="3cx_extensions.csv", mime="text/csv")

else:
    st.info("Inserisci un codice punto vendita valido.")
