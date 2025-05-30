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

mac_box = st.text_input("MAC Address Box (interno 00)")
mac_interfono = st.text_input("MAC Address Interfono (interno 80)")

macs_extra = []
if num_extensions > 0:
    for i in range(num_extensions):
        mac = st.text_input(f"MAC Address per estensione aggiuntiva #{i+1}", key=f"mac_{i}")
        macs_extra.append(mac)

colonne_complete = {
    'Number': '', 'FirstName': '', 'LastName': '', 'EmailAddress': '', 'MobileNumber': '',
    'OutboundCallerID': '', 'DID': '', 'Role': '', 'Department': 'DEFAULT', 'ClickToCallAuth': '',
    'WMApprove': '', 'WebMeetingFriendlyName': '', 'MAC': '', 'Template': '', 'Model': '',
    'Router': '', 'Language': 'Italian', 'Ringtone': 'Ring1.wav', 'QRingtone': 'Ring6.wav', 'VMEnable': '0',
    'VMLanguage': '', 'VMPlayMsgDateTime': '0', 'VMPIN': '', 'VMEmailOptions': '0', 'VMNoPin': '0',
    'VMPlayCallerID': '0', 'RecordCalls': '0', 'RecordExternal': '0', 'RecordCanSee': '', 'RecordCanDelete': '',
    'RecordStartStop': '', 'RecordNotify': '0', 'Disabled': '0', 'HideFWrules': '0', 'DisableExternalCalls': '0',
    'HideInPhonebook': '0', 'CallScreening': '0', 'PinProtected': '0', 'PinTimeout': '', 'Transcription': '0',
    'AllowLanOnly': '0', 'SIPID': '', 'DeliverAudio': '0', 'HotDesk': '0', 'SRTPMode': '0',
    'EmailMissedCalls': '0', 'MS365SignInDisabled': '0', 'MS365CalendarDisabled': '0',
    'MS365ContactsDisabled': '0', 'MS365TeamsDisabled': '0', 'GoogleSignInDisabled': '0',
    'GoogleContactsDisabled': '0', 'GoogleCalendarDisabled': '0', 'BLF': ''
}

def crea_blf_stringa(pv_code):
    base = int(pv_code) * 100
    blf_list = [f"<BLF>{base + ext}@ext</BLF>" for ext in [0, 80, 99, 98, 97, 96]]
    return f"<PhoneDevice><BLFS>{''.join(blf_list)}</BLFS></PhoneDevice>"

def generate_extensions(pv_code: str, count: int):
    base = int(pv_code) * 100
    extensions = []
    blf_string = crea_blf_stringa(pv_code)

    ruoli_fissi = [
        (0, "Box", mac_box, "yealink_t42u", "T42U"),
        (80, "Interfono", mac_interfono, "fanvil_pa3", "PA3"),
        (99, "Direttore", '', "yealink_t42u", "T42U"),
        (98, "Vicedirettore", '', "yealink_t42u", "T42U"),
        (97, "Capo Cassiera", '', "yealink_t42u", "T42U"),
        (96, "Ricevimento Merci", '', "yealink_t42u", "T42U")
    ]
    used_suffixes = set()

    for suffix, ruolo, mac, template, model in ruoli_fissi:
        ext = base + suffix
        used_suffixes.add(ext)
        row = colonne_complete.copy()
        row.update({
            "Number": ext,
            "FirstName": ruolo,
            "EmailAddress": f"user{ext}@example.com",
            "MAC": mac,
            "Router": mac,
            "Template": template,
            "Model": model,
            "BLF": blf_string,
            "SRTPMode": '0'
        })
        extensions.append(row)

    counter = 1
    while len([ext for ext in extensions if ext['FirstName'].startswith("User")]) < count:
        ext = base + counter
        counter += 1
        if ext in used_suffixes:
            continue
        row = colonne_complete.copy()
        idx = len([ext for ext in extensions if ext['FirstName'].startswith("User")])
        mac = macs_extra[idx] if idx < len(macs_extra) else ''
        row.update({
            "Number": ext,
            "FirstName": f"User{ext}",
            "EmailAddress": f"user{ext}@example.com",
            "MAC": mac,
            "Router": mac,
            "Template": "yealink_t42u",
            "Model": "T42U",
            "BLF": blf_string,
            "SRTPMode": '0'
        })
        extensions.append(row)

    return pd.DataFrame(extensions)

if codice_pv and codice_pv.isdigit():
    df = generate_extensions(codice_pv, num_extensions)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="🗅️ Scarica CSV per 3CX",
        data=csv,
        file_name='3cx_import_ready.csv',
        mime='text/csv'
    )
else:
    st.info("Inserisci un codice punto vendita numerico per generare le estensioni.")
