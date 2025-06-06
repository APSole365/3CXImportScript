import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="3CX Extensions Generator", layout="centered")
st.title("📞 3CX Extensions Generator")

st.markdown("""
Questa app genera un file `extensions.csv` compatibile con 3CX.
- Alcuni ruoli fissi vengono creati in automatico.
- Gli altri interni sono generati con template/model corretti.
""")

codice_pv = st.text_input("Codice Punto Vendita (PV)", max_chars=6)
num_extensions = st.number_input("Numero estensioni aggiuntive", min_value=0, max_value=100, value=1)

mac_box = st.text_input("MAC Address Box (interno 00)")
mac_interfono = st.text_input("MAC Address Interfono (interno 80)")

macs_extra = []
if num_extensions > 0:
    for i in range(num_extensions):
        mac = st.text_input(f"MAC Address per estensione aggiuntiva #{i+1}", key=f"mac_{i}")
        macs_extra.append(mac)

colonne_complete = {
    'Number': '', 'FirstName': '', 'LastName': '', 'EmailAddress': '', 'MobileNumber': '',
    'OutboundCallerID': '', 'DID': '', 'Role': '<role name="users" />', 'Department': 'DEFAULT', 'ClickToCallAuth': '0',
    'WMApprove': '', 'WebMeetingFriendlyName': '', 'MAC': '', 'Template': '', 'Model': '',
    'Router': '', 'Language': 'Italian', 'Ringtone': 'Ring1.wav', 'QRingtone': 'Ring6.wav', 'VMEnable': '0',
    'VMLanguage': 'it-IT', 'VMPlayMsgDateTime': '0', 'VMPIN': '', 'VMEmailOptions': '0', 'VMNoPin': '0',
    'VMPlayCallerID': '0', 'RecordCalls': '0', 'RecordExternal': '0', 'RecordCanSee': '', 'RecordCanDelete': '',
    'RecordStartStop': '', 'RecordNotify': '0', 'Disabled': '0', 'HideFWrules': '0', 'DisableExternalCalls': '0',
    'HideInPhonebook': '0', 'CallScreening': '0', 'PinProtected': '0', 'PinTimeout': '', 'Transcription': '0',
    'AllowLanOnly': '0', 'SIPID': '', 'DeliverAudio': '0', 'HotDesk': '0', 'SRTPMode': '0',
    'EmailMissedCalls': '1', 'MS365SignInDisabled': '0', 'MS365CalendarDisabled': '0',
    'MS365ContactsDisabled': '0', 'MS365TeamsDisabled': '0', 'GoogleSignInDisabled': '0',
    'GoogleContactsDisabled': '0', 'GoogleCalendarDisabled': '0', 'BLF': ''
}

def crea_blf_stringa(pv_code):
    return "<PhoneDevice><BLFS/></PhoneDevice>"

def generate_extensions(pv_code: str, count: int):
    base = int(pv_code) * 100
    extensions = []
    blf_string = crea_blf_stringa(pv_code)

    ruoli_fissi = [
        (0, "Box", mac_box, "yealinkT4x.ph.xml", "T42U"),
        (80, "Interfono", mac_interfono, "fanvil_pa3.xml", "PA3"),
        (99, "Direttore", '', '', ''),
        (98, "Vicedirettore", '', '', ''),
        (97, "Capo Cassiera", '', '', ''),
        (96, "Ricevimento Merci", '', '', '')
    ]

    used_suffixes = set()
    for suffix, ruolo, mac, template, model in ruoli_fissi:
        ext = base + suffix
        used_suffixes.add(ext)
        row = colonne_complete.copy()
        row.update({
            "Number": ext,
            "FirstName": f"{ext} {ruolo}",
            "EmailAddress": f"user{ext}@example.com",
            "MAC": mac,
            "Router": mac,
            "Template": template,
            "Model": model,
            "BLF": blf_string
        })
        extensions.append(row)

    idx_mac = 0
    for i in range(1, 100):  # Estensioni aggiuntive, evita collisione
        ext = base + i
        if ext in used_suffixes:
            continue
        if idx_mac >= count:
            break
        mac = macs_extra[idx_mac] if idx_mac < len(macs_extra) else ''
        row = colonne_complete.copy()
        row.update({
            "Number": ext,
            "FirstName": f"User{ext}",
            "EmailAddress": f"user{ext}@example.com",
            "MAC": mac,
            "Router": mac,
            "Template": "yealinkT4x.ph.xml",
            "Model": "T31G",
            "BLF": blf_string
        })
        extensions.append(row)
        idx_mac += 1

    return pd.DataFrame(extensions)

if codice_pv and codice_pv.isdigit():
    df = generate_extensions(codice_pv, num_extensions)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("🗅 Scarica CSV per 3CX", data=csv, file_name='3cx_import_ready.csv', mime='text/csv')
else:
    st.info("Inserisci un codice punto vendita numerico per generare le estensioni.")
