import streamlit as st
import json
import os
import pandas as pd 
from io import BytesIO 
from inventory import NetworkInventory
from devices import Router, Switch, AccessPoint, Endpoint
from storage import save_to_json, load_from_json

# ==================================================
# CONFIGURAÇÃO DA PÁGINA E ESTADO
# ==================================================
st.set_page_config(page_title="Network Manager Pro", layout="wide")

if 'inv' not in st.session_state:
    if os.path.exists("inventario.json"):
        try: st.session_state.inv = load_from_json("inventario.json")
        except: st.session_state.inv = NetworkInventory()
    else:
        st.session_state.inv = NetworkInventory()

inv = st.session_state.inv

if 'editing_device' not in st.session_state:
    st.session_state.editing_device = None

# ==================================================
# FUNÇÕES AUXILIARES DE FORMULÁRIO (A MAGIA ESTÁ AQUI)
# ==================================================

def limpar_form():
    """Limpa todos os campos do formulário da memória."""
    keys = [
        "add_tipo_select", "add_nome_input", "add_modelo_input", 
        "add_serial_select", "add_obs_input",
        "add_ip_router", "add_mac_router",
        "add_ports_sw", "add_giga_sw", "add_fast_sw", "add_mac_sw",
        "add_ssid_ap",
        "add_uid_ep", "add_ip_ep", "add_mac_ep"
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

def carregar_dados_para_form(device):
    """
    Força os dados do dispositivo para dentro dos inputs do Streamlit via Session State.
    """
    # 1. Dados Comuns
    st.session_state['add_tipo_select'] = device.device_type
    st.session_state['add_nome_input'] = device.name
    st.session_state['add_modelo_input'] = device.model
    st.session_state['add_serial_select'] = "Sim" if device.serial_interface else "Não"
    st.session_state['add_obs_input'] = device.observations

    # 2. Dados Específicos por Tipo
    if device.device_type == "ROUTER":
        st.session_state['add_ip_router'] = getattr(device, 'ipv4', '')
        st.session_state['add_mac_router'] = getattr(device, 'mac_address', '')
    
    elif device.device_type == "SWITCH":
        st.session_state['add_ports_sw'] = getattr(device, 'ports', 24)
        st.session_state['add_giga_sw'] = getattr(device, 'giga_eth_ports', 0)
        st.session_state['add_fast_sw'] = getattr(device, 'fast_eth_ports', 0)
        st.session_state['add_mac_sw'] = getattr(device, 'mac_address', '')

    elif device.device_type == "AP":
        st.session_state['add_ssid_ap'] = getattr(device, 'ssid', '')

    elif device.device_type == "ENDPOINT":
        st.session_state['add_uid_ep'] = getattr(device, 'user_id', '')
        st.session_state['add_ip_ep'] = getattr(device, 'ipv4', '')
        st.session_state['add_mac_ep'] = getattr(device, 'mac_address', '')

def click_editar(device):
    """
    Callback executado ANTES do script recarregar.
    Define o dispositivo em edição e preenche o formulário.
    """
    st.session_state.editing_device = device
    carregar_dados_para_form(device)

def click_cancelar():
    """Callback para cancelar a edição."""
    st.session_state.editing_device = None
    limpar_form()

# ==================================================
# SIDEBAR: GESTÃO DE DADOS
# ==================================================
with st.sidebar:
    st.title("Gestão de Dados")
    
    if st.button("Guardar no Servidor", key="btn_save_srv"):
        save_to_json(inv, "inventario.json")
        st.success("Dados guardados.")
    
    if st.button("Recarregar do Ficheiro", key="btn_reload_srv"):
        st.session_state.inv = load_from_json("inventario.json")
        click_cancelar() # Usa a função de cancelar para limpar tudo
        st.rerun()
    
    st.divider()
    st.subheader("Download Local")
    inventory_data = [d.to_dict() for d in inv.list_devices()]
    st.download_button(
        label="Descarregar JSON", 
        data=json.dumps(inventory_data, indent=2), 
        file_name="inventario.json", 
        mime="application/json",
        key="btn_download_json"
    )

    st.divider()
    st.subheader("Upload Local")
    uploaded_file = st.file_uploader("Carregar backup JSON", type=["json"], key="uploader_json")

    if uploaded_file is not None:
        if st.button("Restaurar Backup", use_container_width=True, key="btn_restore_upload"):
            try:
                data = json.load(uploaded_file)
                temp_inv = NetworkInventory()
                for item in data:
                    t = item.get("type")
                    mod = item.get("model", "")
                    ser_int = item.get("serial_interface", False)
                    obs = item.get("observations", "")

                    if t == "ROUTER":
                        obj = Router(item["name"], item.get("ipv4", ""), "", item["mac_address"], mod, ser_int, obs)
                        obj.connected_devices = list(item.get("connected_devices", []))
                    elif t == "SWITCH":
                        obj = Switch(item["name"], "", item["mac_address"], int(item["ports"]), 
                                     item.get("eth_ports", 0), item.get("fast_eth_ports", 0), item.get("giga_eth_ports", 0),
                                     mod, ser_int, obs)
                        obj.connected_devices = list(item.get("connected_devices", []))
                    elif t == "AP":
                        obj = AccessPoint(item["name"], item["ssid"], mod, ser_int, obs)
                        obj.connected_endpoints = list(item.get("connected_endpoints", []))
                    elif t == "ENDPOINT":
                        obj = Endpoint(item["name"], item["user_id"], item.get("ipv4", ""), "", item["mac_address"], mod, ser_int, obs)
                        obj.traffic_up_mb = float(item.get("traffic_up_mb", 0.0))
                        obj.traffic_down_mb = float(item.get("traffic_down_mb", 0.0))
                    
                    obj.status = item.get("status", "ACTIVE")
                    temp_inv.add_device(obj)

                st.session_state.inv = temp_inv
                st.session_state.editing_device = None
                limpar_form()
                st.success("Backup restaurado!")
                st.rerun()
            except Exception as e: st.error(f"Erro no Upload: {e}")

st.title("Sistema de Gestão de Rede")

# ==================================================
# TABS
# ==================================================
tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs(["Gestão", "Consultas", "Tráfego", "Ligações"])

# --- 1. TAB GESTÃO ---
with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device
    
    # Texto dinâmico do botão
    acao_btn = "Atualizar" if is_editing else "Adicionar"

    with col_add:
        st.subheader("Editar Dispositivo" if is_editing else "Novo Dispositivo")
        
        # Tipo de dispositivo
        lista_tipos = ["ROUTER", "SWITCH", "AP", "ENDPOINT"]
        # Nota: O index aqui é controlado pelo session_state['add_tipo_select'] se ele existir
        tipo = st.selectbox("Tipo", lista_tipos, disabled=is_editing, key="add_tipo_select")
        
        # Campos Comuns
        nome = st.text_input("Nome Único", key="add_nome_input").strip()
        modelo = st.text_input("Modelo", key="add_modelo_input")
        ser_sel = st.selectbox("Interface Serial?", ["Não", "Sim"], key="add_serial_select")
        ser_bool = (ser_sel == "Sim")
        obs = st.text_area("Observações", key="add_obs_input")

        # Função interna de guardar/atualizar
        def process_update(new_obj):
            if is_editing:
                # Mantém conexões antigas
                if hasattr(dev_edit, "connected_devices"): new_obj.connected_devices = dev_edit.connected_devices
                if hasattr(dev_edit, "connected_endpoints"): new_obj.connected_endpoints = dev_edit.connected_endpoints
                # Mantém tráfego se for Endpoint
                if isinstance(new_obj, Endpoint):
                    new_obj.traffic_up_mb = dev_edit.traffic_up_mb
                    new_obj.traffic_down_mb = dev_edit.traffic_down_mb
                inv.remove_device(dev_edit.name)
            
            inv.add_device(new_obj)
            st.session_state.editing_device = None
            limpar_form() # Limpa o form para o próximo uso
            st.rerun()

        # Campos Específicos
        if tipo == "ROUTER":
            ipv4 = st.text_input("Endereço IPv4 (Opcional)", key="add_ip_router")
            mac = st.text_input("MAC", key="add_mac_router")
            
            if st.button(f"{acao_btn} Router", key="btn_confirm_router"):
                process_update(Router(nome, ipv4, "", mac, modelo, ser_bool, obs))

        elif tipo == "SWITCH":
            # Nota: usamos st.empty() ou lógica simples para garantir valores padrão se vazio
            ports_val = st.session_state.get('add_ports_sw', 24)
            total_p = st.number_input("Portas", 1, 48, int(ports_val), key="add_ports_sw")
            
            giga_p = st.slider("Gigabit Ethernet Ports", 0, total_p, 0, key="add_giga_sw")
            
            # O slider Fast Ethernet depende do total e giga. O valor inicial deve vir do state se existir
            fast_p = st.slider("Fast Ethernet Ports", 0, total_p, 0, key="add_fast_sw")
            
            mac = st.text_input("MAC Address", key="add_mac_sw")
            
            if st.button(f"{acao_btn} Switch", key="btn_confirm_sw"):
                process_update(Switch(nome, "", mac, total_p, total_p-giga_p-fast_p, fast_p, giga_p, modelo, ser_bool, obs))

        elif tipo == "AP":
            ssid = st.text_input("SSID", key="add_ssid_ap")
            
            if st.button(f"{acao_btn} AP", key="btn_confirm_ap"):
                process_update(AccessPoint(nome, ssid, modelo, ser_bool, obs))

        elif tipo == "ENDPOINT":
            uid = st.text_input("User ID", key="add_uid_ep")
            ipv4 = st.text_input("Endereço IPv4", key="add_ip_ep")
            mac = st.text_input("MAC Address", key="add_mac_ep")
            
            if st.button(f"{acao_btn} Endpoint", key="btn_confirm_ep"):
                process_update(Endpoint(nome, uid, ipv4, "", mac, modelo, ser_bool, obs))

        # Botão Cancelar (agora usa callback para ser mais seguro)
        if is_editing:
            st.button("Cancelar", key="btn_cancel_edit", on_click=click_cancelar)

    with col_list:
        st.subheader("Lista do Inventário")
        for d in inv.list_devices():
            with st.expander(f"{d.name} ({d.device_type})"):
                
                # Info Técnica + MAC
                mac_val = getattr(d, 'mac_address', '-')
                st.write(f"**MAC:** {mac_val} | **Modelo:** {d.model} | **Serial:** {'Sim' if d.serial_interface else 'Não'}")
                
                # Observações
                st.info(f"**Obs.:** {d.observations if d.observations else 'Sem observações.'}")
                
                # Raw info (opcional)
                st.text(str(d))
                
                c1, c2 = st.columns(2)
                
                # === BOTÃO EDITAR CORRIGIDO COM CALLBACK ===
                # O argumento 'on_click' garante que o estado é atualizado ANTES
                # de o Streamlit tentar desenhar o formulário novamente.
                c1.button("Editar Dispositivo", 
                          key=f"ed_{d.name}", 
                          on_click=click_editar, 
                          args=(d,)
                )
                # ===========================================
                
                if c2.button("Eliminar Dispositivo", key=f"el_{d.name}"):
                    inv.remove_device(d.name)
                    st.rerun()
        
        st.divider()
        if st.button("NUKE - Limpar Tudo", type="primary", use_container_width=True, key="btn_nuke_all"):
            for d in list(inv.list_devices()): inv.remove_device(d.name)
            st.session_state.editing_device = None
            limpar_form()
            st.rerun()

# --- 2. TAB CONSULTAS (Filtros Atualizados) ---
with tab_consultas:
    st.subheader("Filtros de Pesquisa")
    
    # Primeira Linha de Filtros
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1:
        search_m = st.text_input("Filtrar por Modelo", key="query_modelo")
        if st.button("Pesquisar Modelo", key="btn_filter_model"):
            results = [d for d in inv.list_devices() if search_m.lower() in d.model.lower()]
            if results:
                for r in results: st.text(str(r))
            else: st.warning("Nenhum modelo encontrado.")
                
    with r1_c2:
        search_ser = st.selectbox("Interface Serial?", ["Não", "Sim"], key="query_ser")
        if st.button("Filtrar Serial", key="btn_filter_serial"):
            results = [d for d in inv.list_devices() if d.serial_interface == (search_ser == "Sim")]
            if results:
                for r in results: st.text(str(r))
            else: st.info("Nenhum dispositivo encontrado.")

    with r1_c3:
        search_t = st.selectbox("Filtrar por Tipo", ["Todos", "ROUTER", "SWITCH", "AP", "ENDPOINT"], key="query_tipo")
        if st.button("Pesquisar Tipo", key="btn_filter_tipo"):
            if search_t == "Todos":
                results = inv.list_devices()
            else:
                results = [d for d in inv.list_devices() if d.device_type == search_t]
            for r in results: st.text(str(r))

    st.divider()
    
    # Segunda Linha de Filtros
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        search_s = st.selectbox("Estado do Dispositivo", ["Ativo", "Inativo"], key="query_status")
        if st.button("Filtrar Estado", key="btn_filter_status"):
            status_map = {"Ativo": "ACTIVE", "Inativo": "INACTIVE"}
            results = [d for d in inv.list_devices() if d.status == status_map[search_s]]
            if results:
                for r in results: st.text(str(r))
            else: st.info(f"Nenhum dispositivo {search_s.lower()} encontrado.")

    with r2_c2:
        search_ip = st.text_input("Pesquisar por IP (IPv4)", key="query_ip")
        if st.button("Pesquisar IP", key="btn_filter_ip"):
            # Procura em routers e endpoints que têm atributo ipv4
            results = [d for d in inv.list_devices() if getattr(d, 'ipv4', '') == search_ip]
            if results:
                for r in results: st.text(str(r))
            else: st.warning("IP não encontrado no inventário.")

# --- 3. TAB TRÁFEGO ---
with tab_trafego:
    eps = [d for d in inv.list_devices() if isinstance(d, Endpoint)]
    if not eps: 
        st.info("Adicione Endpoints na Gestão para monitorizar o tráfego.")
    else:
        target = st.selectbox("Selecionar Endpoint", [e.name for e in eps], key="traffic_target_select")
        ep_obj = inv.get_endpoint(target)
        up = st.number_input("Novo Upload (MB)", value=float(ep_obj.traffic_up_mb), key="input_traffic_up")
        down = st.number_input("Novo Download (MB)", value=float(ep_obj.traffic_down_mb), key="input_traffic_down")
        if st.button("Atualizar Consumo", key="btn_update_traffic"):
            ep_obj.traffic_up_mb, ep_obj.traffic_down_mb = up, down
            st.success("Dados atualizados!")
            st.rerun()
        
        st.divider()
        st.subheader("Visualização de Consumo")
        chart_data = {e.name: e.traffic_up_mb + e.traffic_down_mb for e in eps}
        st.bar_chart(chart_data)

# --- 4. TAB LIGAÇÕES ---
with tab_ligacoes:
    hosts = [d for d in inv.list_devices() if hasattr(d, "connected_devices") or hasattr(d, "connected_endpoints")]
    if not hosts: 
        st.info("Crie Routers ou Switches para estabelecer ligações.")
    else:
        h_name = st.selectbox("Escolher Equipamento Base", [h.name for h in hosts], key="host_link_select")
        h_obj = inv.devices.get(h_name)
        
        c_link, c_view = st.columns(2)
        with c_link:
            st.markdown("### Criar Nova Ligação")
            others = [d.name for d in inv.list_devices() if d.name != h_name]
            target = st.selectbox("Ligar a:", others, key="target_link_select")
            if st.button("Estabelecer Ligação", key="btn_establish_link"):
                try:
                    if hasattr(h_obj, "connect_device"): h_obj.connect_device(target)
                    else: h_obj.connect_endpoint(target)
                    st.success(f"Ligado: {h_name} <-> {target}")
                    st.rerun()
                except Exception as e: st.error(e)
        
        with c_view:
            st.markdown("### Ligações Atuais")
            cons = getattr(h_obj, "connected_devices", []) or getattr(h_obj, "connected_endpoints", [])
            if not cons:
                st.write("Sem dispositivos ligados.")
            for c in cons:
                if st.button(f"Desligar {c}", key=f"dis_{h_name}_{c}"):
                    if hasattr(h_obj, "disconnect_device"): h_obj.disconnect_device(c)
                    else: h_obj.disconnect_endpoint(c)
                    st.rerun()
