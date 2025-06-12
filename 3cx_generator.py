import streamlit as st
import pandas as pd
import uuid
from io import StringIO

def generate_random_mac():
    """Genera un MAC address casuale nel formato richiesto"""
    return ''.join(['%02X' % (uuid.uuid4().int >> i & 0xFF) for i in range(0, 48, 8)])

def create_extension_row(number, first_name, department_code, department_name, mac_address, model, template, vm_pin):
    """Crea una riga per un interno"""
    web_meeting_name = first_name.lower().replace(' ', '').replace('-', '')
    
    return {
        'Number': number,
        'FirstName': first_name,
        'LastName': '',
        'EmailAddress': '',
        'MobileNumber': '',
        'OutboundCallerID': '',
        'DID': '',
        'Role': '<role name="users" />',
        'Department': f'{department_code} | {department_name}',
        'ClickToCallAuth': 0,
        'WMApprove': 0,
        'WebMeetingFriendlyName': web_meeting_name,
        'MAC': mac_address,
        'Template': template,
        'Model': model,
        'Router': '44DBD28F21BD',
        'Language': 'Italian',
        'Ringtone': 'Ring 1' if model != 'Fanvil PA3' else '',
        'QRingtone': 'Ring 6' if model != 'Fanvil PA3' else '',
        'VMEnable': 0,
        'VMLanguage': '307392E1-F915-4f3a-9362-5049AADC242C',
        'VMPlayMsgDateTime': 0,
        'VMPIN': vm_pin,
        'VMEmailOptions': 1,
        'VMNoPin': 1,
        'VMPlayCallerID': 0,
        'RecordCalls': 0,
        'RecordExternal': 0,
        'RecordCanSee': 0,
        'RecordCanDelete': 0,
        'RecordStartStop': 1,
        'RecordNotify': 0,
        'Disabled': 0,
        'HideFWrules': 0,
        'DisableExternalCalls': 0,
        'CallScreening': 0,
        'PinProtected': 0,
        'PinTimeout': 0,
        'Transcription': 0,
        'AllowLanOnly': 60,
        'SIPID': '',
        'DeliverAudio': 1,
        'HotDesk': '',
        'SRTPMode': 0,
        'EmailMissedCalls': 0,
        'MS365SignInDisabled': 0,
        'MS365CalendarDisabled': 1,
        'MS365ContactsDisabled': '',
        'MS365TeamsDisabled': '',
        'GoogleSignInDisabled': '',
        'GoogleContactsDisabled': '',
        'GoogleCalendarDisabled': '',
        'BLF': '<PhoneDevice><BLFS/></PhoneDevice>'
    }

def main():
    st.title("🏢 Generatore CSV per Centralino 3CX")
    st.markdown("---")
    
    # Informazioni punto vendita
    st.header("📍 Informazioni Punto Vendita")
    
    col1, col2 = st.columns(2)
    with col1:
        store_code = st.text_input("Codice Punto Vendita (es: 590)", value="590")
    with col2:
        store_location = st.text_input("Località (es: Benevento - Via Ievolella)", value="Benevento - Via Ievolella")
    
    if not store_code or not store_location:
        st.error("Inserisci il codice punto vendita e la località")
        return
    
    # Validazione codice punto vendita
    try:
        store_code_int = int(store_code)
        if len(store_code) != 3:
            st.error("Il codice punto vendita deve essere di 3 cifre")
            return
    except ValueError:
        st.error("Il codice punto vendita deve essere numerico")
        return
    
    department_full = f"{store_code_int}590 | {store_location}"
    
    st.markdown("---")
    
    # Telefono Master (Box)
    st.header("📞 Telefono Master (Box)")
    st.info("Il telefono master è sempre un Yealink T42U con interno '00'")
    
    master_mac = st.text_input("MAC Address telefono Master (Box)", placeholder="44DBD28F21BD")
    
    if not master_mac:
        st.error("Inserisci il MAC address del telefono master")
        return
    
    st.markdown("---")
    
    # Casse
    st.header("🛒 Casse")
    num_casse = st.number_input("Numero di casse", min_value=1, max_value=10, value=3)
    
    casse_macs = []
    for i in range(num_casse):
        mac = st.text_input(f"MAC Address Cassa {i+1:02d}", 
                           placeholder="44DBD284F872", 
                           key=f"cassa_{i}")
        if mac:
            casse_macs.append(mac)
    
    if len(casse_macs) != num_casse:
        st.error(f"Inserisci tutti i {num_casse} MAC address delle casse")
        return
    
    st.markdown("---")
    
    # Reparti
    st.header("🥩 Reparti")
    st.write("Seleziona i reparti presenti nel punto vendita:")
    
    reparti_config = {
        "Gastronomia Banco": {"code": "34", "selected": False, "mac": ""},
        "Macelleria Banco": {"code": "35", "selected": False, "mac": ""},
        "Panetteria Banco": {"code": "38", "selected": False, "mac": ""},
        "Gastronomia Lab": {"code": "44", "selected": False, "mac": ""},
        "Macelleria Lab": {"code": "45", "selected": False, "mac": ""},
        "Ortofrutta Lab": {"code": "46", "selected": False, "mac": ""},
        "Panetteria Lab": {"code": "48", "selected": False, "mac": ""}
    }
    
    for reparto, config in reparti_config.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            config["selected"] = st.checkbox(reparto)
        with col2:
            if config["selected"]:
                config["mac"] = st.text_input(f"MAC Address {reparto}", 
                                            placeholder="44DBD284FF64",
                                            key=f"reparto_{reparto}")
    
    # Verifica MAC reparti selezionati
    for reparto, config in reparti_config.items():
        if config["selected"] and not config["mac"]:
            st.error(f"Inserisci il MAC address per {reparto}")
            return
    
    st.markdown("---")
    
    # Interfono
    st.header("📢 Interfono")
    st.info("L'interfono è sempre presente con interno '80'")
    
    interfono_mac = st.text_input("MAC Address Interfono", placeholder="0C383E6D1321")
    
    if not interfono_mac:
        st.error("Inserisci il MAC address dell'interfono")
        return
    
    st.markdown("---")
    
    # Genera CSV
    if st.button("🚀 Genera CSV", type="primary", use_container_width=True):
        try:
            extensions = []
            
            # Telefono Master (Box)
            extensions.append(create_extension_row(
                number=f"{store_code}00",
                first_name=f"{store_code}00 Box",
                department_code=store_code_int,
                department_name=store_location,
                mac_address=master_mac,
                model="Yealink T42U",
                template="yealinkT4x.ph.xml",
                vm_pin="917011"
            ))
            
            # Casse
            for i in range(num_casse):
                extensions.append(create_extension_row(
                    number=f"{store_code}0{i+1}",
                    first_name=f"{store_code}0{i+1} Cassa {i+1:02d}",
                    department_code=store_code_int,
                    department_name=store_location,
                    mac_address=casse_macs[i],
                    model="Yealink T31G",
                    template="yealinkT4x.ph.xml",
                    vm_pin="307426"
                ))
            
            # Reparti
            for reparto, config in reparti_config.items():
                if config["selected"]:
                    reparto_clean = reparto.lower().replace(' ', '').replace('-', '')
                    extensions.append(create_extension_row(
                        number=f"{store_code}{config['code']}",
                        first_name=f"{store_code}{config['code']} {reparto}",
                        department_code=store_code_int,
                        department_name=store_location,
                        mac_address=config["mac"],
                        model="Yealink T31G",
                        template="yealinkT4x.ph.xml",
                        vm_pin="307426"
                    ))
            
            # Interfono
            extensions.append(create_extension_row(
                number=f"{store_code}80",
                first_name=f"{store_code}80 Interfono",
                department_code=store_code_int,
                department_name=store_location,
                mac_address=interfono_mac,
                model="Fanvil PA3",
                template="fanvil_doorphone.ph.xml",
                vm_pin="711831"
            ))
            
            # Interni fissi di default
            default_extensions = [
                {"code": "96", "name": "Ricevimento Merci", "pin": "043318"},
                {"code": "97", "name": "Capo Cassiera", "pin": "254346"},
                {"code": "98", "name": "Vice Direttore", "pin": "752990"},
                {"code": "99", "name": "Direttore", "pin": "555658"}
            ]
            
            for ext in default_extensions:
                row = create_extension_row(
                    number=f"{store_code}{ext['code']}",
                    first_name=f"{store_code}{ext['code']} {ext['name']}",
                    department_code=store_code_int,
                    department_name=store_location,
                    mac_address="",
                    model="",
                    template="",
                    vm_pin=ext["pin"]
                )
                extensions.append(row)
            
            # Crea DataFrame
            df = pd.DataFrame(extensions)
            
            # Converti in CSV
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            
            # Mostra anteprima
            st.success(f"✅ CSV generato con successo! ({len(extensions)} interni)")
            st.subheader("📋 Anteprima")
            st.dataframe(df[['Number', 'FirstName', 'Model', 'MAC']], use_container_width=True)
            
            # Download
            st.download_button(
                label="⬇️ Scarica CSV",
                data=csv_content,
                file_name=f"extensions_{store_code}_{store_location.replace(' ', '_').replace('-', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Errore nella generazione del CSV: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="3CX CSV Generator",
        page_icon="📞",
        layout="wide"
    )
    main()