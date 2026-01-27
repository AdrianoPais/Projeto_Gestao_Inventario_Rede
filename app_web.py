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

    # --- NOVO: UPLOAD LOCAL ---
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
                    ser = item.get("serial", "")

                    if t == "ROUTER":
                        obj = Router(item["name"], item.get("ipv4", ""), "", item["mac_address"], model=mod, serial=ser, observations=obs)
                    elif t == "SWITCH":
                        obj = Switch(item["name"], "", item["mac_address"], int(item["ports"]), 
                                     item.get("eth_ports", 0), item.get("fast_eth_ports", 0), item.get("giga_eth_ports", 0),
                                     model=mod, serial=ser, observations=obs)
                    elif t == "AP":
                        obj = AccessPoint(item["name"], item["ssid"], model=mod, serial=ser, observations=obs)
                    elif t == "ENDPOINT":
                        obj = Endpoint(item["name"], item["user_id"], item.get("ipv4", ""), "", item["mac_address"], model=mod, serial=ser, observations=obs)
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
        modelo = st.text_input("Modelo", value=dev_edit.model if is_editing else "")
        serial = st.text_input("Serial Number (S/N)", value=getattr(dev_edit, 'serial', "") if is_editing else "")
        obs = st.text_area("Observacoes", value=dev_edit.observations if is_editing else "")

        if tipo == "ROUTER":
            ipv4 = st.text_input("IPv4 (Opcional)", value=getattr(dev_edit, 'ipv4', "") if is_editing else "")
            mac = st.text_input("MAC (Router)", value=getattr(dev_edit, 'mac_address', "") if is_editing else "")
            
            label_btn = "Atualizar Router" if is_editing else "Adicionar Router"
            if st.button(label_btn):
                try:
                    if is_editing: inv.remove_device(dev_edit.name)
                    inv.add_device(Router(nome, ipv4, "", mac, model=modelo, serial=serial, observations=obs))
                    st.session_state.editing_device = None
                    st.rerun()
                except ValueError as e: st.error(e)

        elif tipo == "SWITCH":
            p_total = getattr(dev_edit, 'ports', 24) if is_editing else 24
            p_giga = getattr(dev_edit, 'giga_eth_ports', 0) if is_editing else 0
            p_fast = getattr(dev_edit, 'fast_eth_ports', p_total) if is_editing else 24

            total_p = st.number_input("Portas", 1, 48, int(p_total))
            giga_p = st.slider("Gigabit", 0, total_p, int(p_giga))
            fast_p = st.slider("FastEthernet", 0, total_p - giga_p, int(min(p_fast, total_p - giga_p)))
            eth_p = total_p - giga_p - fast_p
            st.info(f"Ethernet restantes: {eth_p}")
            mac = st.text_input("MAC", value=getattr(dev_edit, 'mac_address', "") if is_editing else "")
            
            label_btn = "Atualizar Switch" if is_editing else "Adicionar Switch"
            if st.button(label_btn):
                try:
                    if is_editing: inv.remove_device(dev_edit.name)
                    inv.add_device(Switch(nome, "", mac, total_p, eth_p, fast_p, giga_p, model=modelo, serial=serial, observations=obs))
                    st.session_state.editing_device = None
                    st.rerun()
                except ValueError as e: st.error(e)

        # (...) Lógica similar para AP e ENDPOINT (...)

        if is_editing:
            if st.button("Cancelar Edicao", use_container_width=True):
                st.session_state.editing_device = None
                st.rerun()

    with col_list:
        st.subheader("Lista de Inventario")
        devices = inv.list_devices()
        if not devices:
            st.info("Inventario vazio.")
        else:
            for d in devices:
                with st.expander(f"{d.name} ({d.device_type}) - {d.status}"):
                    if hasattr(d, "model") and d.model: st.write(f"**Modelo:** {d.model}")
                    if hasattr(d, "serial") and d.serial: st.write(f"**S/N:** {d.serial}")
                    st.text(str(d))
                    if hasattr(d, "observations") and d.observations: st.warning(f"Notas: {d.observations}")
                    
                    c_ed, c_el = st.columns(2)
                    if c_ed.button("Editar", key=f"edit_b_{d.name}"):
                        st.session_state.editing_device = d
                        st.rerun()
                    if c_el.button("Eliminar", key=f"del_b_{d.name}"):
                        inv.remove_device(d.name)
                        st.rerun()

            st.divider()
            if st.button("NUKE - Eliminar Todo o Inventario", type="primary", use_container_width=True):
                for d in list(inv.list_devices()):
                    inv.remove_device(d.name)
                st.session_state.editing_device = None
                st.rerun()

# --- 2. TAB CONSULTAS ---
with tab_consultas:
    st.subheader("Ferramentas de Pesquisa")
    c1, c2, c3, c4 = st.columns(4) 
    
    with c1:
        st.markdown("**Por Modelo**")
        search_m = st.text_input("Procurar Modelo")
        if st.button("Filtrar Modelo"):
            results = [d for d in inv.list_devices() if search_m.lower() in d.model.lower()]
            for r in results: st.text(str(r))

    with c2:
        st.markdown("**Por Serial Number**")
        if st.button("Listar Apenas com S/N"):
            results = [d for d in inv.list_devices() if getattr(d, 'serial', "")]
            for r in results: st.text(str(r))

    with c3:
        st.markdown("**Por Estado**")
        search_s = st.selectbox("Estado", ["ACTIVE", "INACTIVE"])
        if st.button("Filtrar Estado"):
            results = inv.find_by_status(search_s)
            for r in results: st.text(str(r))
                
    with c4:
        st.markdown("**Conectividade**")
        if st.button("Listar Conectados"):
            results = [d for d in inv.list_devices() if len(getattr(d, "connected_devices", [])) > 0]
            for r in results: st.write(f"{r.name} ({r.device_type})")
