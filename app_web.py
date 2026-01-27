import streamlit as st
import json
import os
from inventory import NetworkInventory
from devices import Router, Switch, AccessPoint, Endpoint
from storage import save_to_json, load_from_json

# ==================================================
# CONFIGURAÇÃO DA PÁGINA E ESTADO
# ==================================================
st.set_page_config(page_title="Network Manager Pro", layout="wide")

# Inicialização do Inventário
if 'inv' not in st.session_state:
    if os.path.exists("inventario.json"):
        try:
            st.session_state.inv = load_from_json("inventario.json")
        except:
            st.session_state.inv = NetworkInventory()
    else:
        st.session_state.inv = NetworkInventory()

inv = st.session_state.inv

# Estado de Edição
if 'editing_device' not in st.session_state:
    st.session_state.editing_device = None

# ==================================================
# SIDEBAR: GESTÃO DE DADOS
# ==================================================
with st.sidebar:
    st.title("Gestão de Dados")
    
    if st.button("Guardar no Servidor"):
        save_to_json(inv, "inventario.json")
        st.success("Dados guardados no servidor.")
    
    if st.button("Recarregar do Ficheiro"):
        st.session_state.inv = load_from_json("inventario.json")
        st.session_state.editing_device = None
        st.rerun()
    
    st.divider()
    
    # --- DOWNLOAD LOCAL ---
    st.subheader("Download Local")
    inventory_data = [d.to_dict() for d in inv.list_devices()]
    json_string = json.dumps(inventory_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="Descarregar inventario.json",
        data=json_string,
        file_name="inventario.json",
        mime="application/json"
    )

    st.divider()

    # --- UPLOAD LOCAL ---
    st.subheader("Upload Local")
    uploaded_file = st.file_uploader("Carregar backup JSON", type=["json"])

    if uploaded_file is not None:
        if st.button("Restaurar a partir do Upload", use_container_width=True):
            try:
                data = json.load(uploaded_file)
                temp_inv = NetworkInventory()
                
                for item in data:
                    t = item.get("type")
                    obs = item.get("observations", "")
                    mod = item.get("model", "")
                    ser_int = item.get("serial_interface", False) # Recupera booleano

                    if t == "ROUTER":
                        obj = Router(item["name"], item.get("ipv4", ""), "", item["mac_address"], 
                                     model=mod, serial_interface=ser_int, observations=obs)
                    elif t == "SWITCH":
                        obj = Switch(item["name"], "", item["mac_address"], int(item["ports"]), 
                                     item.get("eth_ports", 0), item.get("fast_eth_ports", 0), item.get("giga_eth_ports", 0),
                                     model=mod, serial_interface=ser_int, observations=obs)
                    elif t == "AP":
                        obj = AccessPoint(item["name"], item["ssid"], model=mod, serial_interface=ser_int, observations=obs)
                    elif t == "ENDPOINT":
                        obj = Endpoint(item["name"], item["user_id"], item.get("ipv4", ""), "", item["mac_address"], 
                                       model=mod, serial_interface=ser_int, observations=obs)
                        obj.traffic_up_mb = float(item.get("traffic_up_mb", 0.0))
                        obj.traffic_down_mb = float(item.get("traffic_down_mb", 0.0))
                    else:
                        continue
                    
                    obj.status = item.get("status", obj.status)
                    temp_inv.add_device(obj)

                st.session_state.inv = temp_inv
                st.session_state.editing_device = None
                st.success("Backup restaurado!")
                st.rerun()
            except Exception as e:
                st.error(f"Falha no processamento: {e}")

st.title("Sistema de Gestão de Rede")

# ==================================================
# DEFINIÇÃO DOS SEPARADORES (TABS)
# ==================================================
tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs([
    "Gestão", 
    "Consultas", 
    "Trafego e Politicas",
    "Ligacoes"
])

# --- 1. TAB GESTÃO ---
with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device

    with col_add:
        st.subheader("Editar Dispositivo" if is_editing else "Novo Dispositivo")
        
        lista_tipos = ["ROUTER", "SWITCH", "AP", "ENDPOINT"]
        tipo_idx = lista_tipos.index(dev_edit.device_type) if is_editing else 0
        tipo = st.selectbox("Tipo", lista_tipos, index=tipo_idx, disabled=is_editing)
        
        nome = st.text_input("Nome Unico", value=dev_edit.name if is_editing else "").strip()
        modelo =
