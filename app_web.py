import streamlit as st
import json
import os
import pandas as pd 
from io import BytesIO 
from datetime import datetime
from fpdf import FPDF # Requer: pip install fpdf
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
# FUNÇÕES AUXILIARES (LOGS E PDF)
# ==================================================

def log_event(mensagem):
    """Regista ações no ficheiro local logs.txt para o Sistema de Honra."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def gerar_pdf(lista_dispositivos):
    """Gera um relatório PDF formatado."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Inventario de Rede - Relatorio Oficial", 0, 1, "C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 10)
    
    for d in lista_dispositivos:
        rk = getattr(d, 'rack', 1)
        cond = getattr(d, 'condition', 'Funcional')
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{d.name} ({d.device_type}) - Bastidor {rk}", "T", 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"Modelo: {d.model} | Saude: {cond}", 0, 1)
        pdf.cell(0, 7, f"Dados: {str(d)}", 0, 1)
        pdf.ln(4)
    return pdf.output(dest="S").encode("latin-1", errors="replace")

# ==================================================
# FUNÇÕES AUXILIARES DE FORMULÁRIO
# ==================================================

def limpar_form():
    """Limpa todos os campos do formulário da memória."""
    keys = [
        "add_tipo_select", "add_nome_input", "add_modelo_input", 
        "add_serial_select", "add_obs_input", "add_saude_select", "add_defeito_input",
        "add_rack_select", "add_ip_router", "add_mac_router",
        "add_ports_sw", "add_giga_sw", "add_fast_sw", "add_mac_sw",
        "add_ssid_ap",
        "add_uid_ep", "add_ip_ep", "add_mac_ep"
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

def carregar_dados_para_form(device):
    st.session_state['add_tipo_select'] = device.device_type
    st.session_state['add_nome_input'] = device.name
    st.session_state['add_modelo_input'] = device.model
    st.session_state['add_serial_select'] = "Sim" if device.serial_interface else "Não"
    st.session_state['add_obs_input'] = device.observations
    st.session_state['add_saude_select'] = getattr(device, 'condition', 'Funcional')
    st.session_state['add_defeito_input'] = getattr(device, 'defect_description', '')
    st.session_state['add_rack_select'] = getattr(device, 'rack', 1)

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
    st.session_state.editing_device = device
    carregar_dados_para_form(device)

def click_cancelar():
    st.session_state.editing_device = None
    limpar_form()

# ==================================================
# SIDEBAR: GESTÃO DE DADOS
# ==================================================
with st.sidebar:
    st.title("Gestão de Dados")
    
    if st.button("Guardar no Servidor", key="btn_save_srv"):
        save_to_json(inv, "inventario.json")
        log_event("Dados guardados no servidor manualmente.")
        st.success("Dados guardados.")
    
    if st.button("Recarregar do Ficheiro", key="btn_reload_srv"):
        st.session_state.inv = load_from_json("inventario.json")
        st.session_state.editing_device = None
        limpar_form()
        st.rerun()
    
    st.divider()
    st.subheader("Exportar Inventário")
    lista_dicts = [d.to_dict() for d in inv.list_devices()]
    
    if lista_dicts:
        df = pd.DataFrame(lista_dicts)
        st.download_button(label="📄 Download JSON", data=json.dumps(lista_dicts, indent=2), file_name="inventario.json", key="btn_json")
        st.download_button(label="📊 Download CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="inventario.csv", key="btn_csv")
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button(label="📗 Download Excel", data=buffer.getvalue(), file_name="inventario.xlsx", key="btn_excel")

        pdf_data = gerar_pdf(inv.list_devices())
        st.download_button(label="📕 Download PDF", data=pdf_data, file_name="relatorio_rede.pdf", key="btn_pdf")

    st.divider()
    if st.checkbox("Ver Logs de Atividade"):
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r") as f:
                st.text_area("Histórico", f.read(), height=200)

    st.divider()
    st.subheader("Upload Local")
    uploaded_file = st.file_uploader("Carregar backup JSON", type=["json"], key="uploader_json")

    if uploaded_file is not None:
        if st.button("Restaurar Backup", use_container_width=True, key="btn_restore_upload"):
            try:
                data = json.load(uploaded_file)
                temp_inv = NetworkInventory()
                for item in data:
                    t, mod, obs = item.get("type"), item.get("model", ""), item.get("observations", "")
                    ser_int = item.get("serial_interface", False)
                    cond, def_desc = item.get("condition", "Funcional"), item.get("defect_description", "")
                    rk = item.get("rack", 1)

                    if t == "ROUTER":
                        obj = Router(item["name"], item.get("ipv4", ""), "", item["mac_address"], mod, ser_int, obs, cond, def_desc, rk)
                    elif t == "SWITCH":
                        obj = Switch(item["name"], "", item["mac_address"], int(item["ports"]), 
                                     item.get("eth_ports", 0), item.get("fast_eth_ports", 0), item.get("giga_eth_ports", 0),
                                     mod, ser_int, obs, cond, def_desc, rk)
                    elif t == "AP":
                        obj = AccessPoint(item["name"], item["ssid"], mod, ser_int, obs, cond, def_desc, rk)
                    elif t == "ENDPOINT":
                        obj = Endpoint(item["name"], item["user_id"], item.get("ipv4", ""), "", item["mac_address"], mod, ser_int, obs, cond, def_desc, rk)
                        obj.traffic_up_mb, obj.traffic_down_mb = float(item.get("traffic_up_mb", 0.0)), float(item.get("traffic_down_mb", 0.0))
                    else: continue
                    
                    obj.status = item.get("status", "ACTIVE")
                    temp_inv.add_device(obj)

                st.session_state.inv = temp_inv
                st.session_state.editing_device = None
                limpar_form()
                st.success("Backup restaurado!")
                st.rerun()
            except Exception as e: st.error(f"Erro: {e}")

st.title("Sistema de Gestão de Rede")

st.warning("""
**⚠️ Nota Importante (Sistema de Honra)**

Esta aplicação está alojada no servidor da Streamlit e, de momento, não possui controlo de acesso individual (UAC). 
Por este motivo, operamos num **Sistema de Honra**: solicitamos a todos os utilizadores que **não alterem ou eliminem** quaisquer dispositivos ou configurações sem a confirmação prévia dos **Administradores**. 

Contamos com a colaboração de todos para manter o inventário correto!
""")

# ==================================================
# TABS PRINCIPAIS
# ==================================================
tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs(["Gestão", "Consultas", "Tráfego", "Ligações"])

# --- 1. TAB GESTÃO ---
with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device
    acao_btn = "Atualizar" if is_editing else "Adicionar"

    with col_add:
        st.subheader("Editar Dispositivo" if is_editing else "Novo Dispositivo")
        tipo = st.selectbox("Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"], disabled=is_editing, key="add_tipo_select")
        nome = st.text_input("Nome Único", key="add_nome_input").strip()
        modelo = st.text_input("Modelo", key="add_modelo_input")
        rk_val = st.selectbox("Bastidor (1-6)", [1, 2, 3, 4, 5, 6], key="add_rack_select")
        ser_sel = st.selectbox("Interface Serial?", ["Não", "Sim"], key="add_serial_select")
        saude = st.selectbox("Estado de Conservação", ["Funcional", "Com Defeito", "Avariado"], key="add_saude_select")
        defeito_desc = st.text_input("Descreva o Defeito", key="add_defeito_input") if saude == "Com Defeito" else ""
        obs = st.text_area("Observações Gerais", key="add_obs_input")

        def process_update(new_obj):
            if is_editing:
                if hasattr(dev_edit, "connected_devices"): new_obj.connected_devices = dev_edit.connected_devices
                inv.remove_device(dev_edit.name)
                log_event(f"EDITADO: {dev_edit.name} no Bastidor {rk_val}")
            else:
                log_event(f"ADICIONADO: {nome} no Bastidor {rk_val}")
            inv.add_device(new_obj)
            st.session_state.editing_device = None
            limpar_form()
            st.rerun()

        params = {"model": modelo, "serial_interface": (ser_sel == "Sim"), "observations": obs, "condition": saude, "defect_description": defeito_desc, "rack": rk_val}

        if tipo == "ROUTER":
            ipv4, mac = st.text_input("IPv4", key="add_ip_router"), st.text_input("MAC", key="add_mac_router")
            if st.button(f"{acao_btn} Router"): process_update(Router(nome, ipv4, "", mac, **params))
        elif tipo == "SWITCH":
            total_p = st.number_input("Portas", 1, 48, 24, key="add_ports_sw")
            g, f = st.slider("Gigabit", 0, total_p, key="add_giga_sw"), st.slider("Fast", 0, total_p, key="add_fast_sw")
            mac = st.text_input("MAC Address", key="add_mac_sw")
            if st.button(f"{acao_btn} Switch"): process_update(Switch(nome, "", mac, total_p, total_p-g-f, f, g, **params))
        elif tipo == "AP":
            ssid = st.text_input("SSID", key="add_ssid_ap")
            if st.button(f"{acao_btn} AP"): process_update(AccessPoint(nome, ssid, **params))
        elif tipo == "ENDPOINT":
            u, ip, m = st.text_input("User ID", key="add_uid_ep"), st.text_input("IPv4", key="add_ip_ep"), st.text_input("MAC", key="add_mac_ep")
            if st.button(f"{acao_btn} Endpoint"): process_update(Endpoint(nome, u, ip, "", m, **params))

        if is_editing: st.button("Cancelar", key="btn_cancel_edit", on_click=click_cancelar)

    with col_list:
        st.subheader("Lista do Inventário")
        devices = inv.list_devices()
        r, s, o = [d for d in devices if d.device_type == "ROUTER"], [d for d in devices if d.device_type == "SWITCH"], [d for d in devices if d.device_type in ["AP", "ENDPOINT"]]
        st_routers, st_switches, st_outros, st_todos = st.tabs([f"Routers ({len(r)})", f"Switches ({len(s)})", f"Outros ({len(o)})", f"Todos ({len(devices)})"])

        def render_lista(lista, prefix):
            if not lista: st.info("Vazio.")
            for d in lista:
                cond_atual = getattr(d, 'condition', 'Funcional')
                rk_atual = getattr(d, 'rack', 1)
                header = f"{d.name} | Bastidor {rk_atual}"
                if cond_atual == "Avariado": header += " 🔴"
                elif cond_atual == "Com Defeito": header += " 🟠"

                with st.expander(header):
                    st.write(f"**Saúde:** {cond_atual} | **Bastidor:** {rk_atual} | **Modelo:** {d.model}")
                    c1, c2 = st.columns(2)
                    c1.button("Editar", key=f"{prefix}_ed_{d.name}", on_click=click_editar, args=(d,))
                    if c2.button("Eliminar", key=f"{prefix}_el_{d.name}"):
                        log_event(f"ELIMINADO: {d.name} do Bastidor {rk_atual}")
                        inv.remove_device(d.name)
                        st.rerun()

        with st_routers: render_lista(r, "r")
        with st_switches: render_lista(s, "s")
        with st_outros: render_lista(o, "o")
        with st_todos: render_lista(devices, "t")

# --- 2. TAB CONSULTAS ---
with tab_consultas:
    st.subheader("Filtros de Pesquisa")
    search_n = st.text_input("Procurar por Nome", key="query_nome_search")
    if st.button("Filtrar por Nome"):
        for r in [d for d in inv.list_devices() if search_n.lower() in d.name.lower()]: st.text(str(r))
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        search_rk = st.selectbox("Bastidor", ["Todos", 1, 2, 3, 4, 5, 6], key="q_rk")
        if st.button("Filtrar Bastidor"):
            res = inv.list_devices() if search_rk=="Todos" else [d for d in inv.list_devices() if getattr(d, 'rack', 1)==search_rk]
            for r in res: st.text(str(r))
    with c2:
        search_ser = st.selectbox("Interface Serial?", ["Não", "Sim"], key="query_ser")
        if st.button("Filtrar Serial"):
            for r in [d for d in inv.list_devices() if d.serial_interface == (search_ser == "Sim")]: st.text(str(r))
    with c3:
        search_t = st.selectbox("Tipo", ["Todos", "ROUTER", "SWITCH", "AP", "ENDPOINT"], key="query_tipo")
        if st.button("Pesquisar Tipo"):
            res = inv.list_devices() if search_t == "Todos" else [d for d in inv.list_devices() if d.device_type == search_t]
            for r in res: st.text(str(r))

# --- TABS TRÁFEGO E LIGAÇÕES ---
with tab_trafego:
    eps = [d for d in inv.list_devices() if isinstance(d, Endpoint)]
    if eps:
        target = st.selectbox("Endpoint", [e.name for e in eps], key="traffic_target_select")
        ep_obj = inv.get_endpoint(target)
        up = st.number_input("Upload (MB)", value=float(ep_obj.traffic_up_mb), key="input_traffic_up")
        down = st.number_input("Download (MB)", value=float(ep_obj.traffic_down_mb), key="input_traffic_down")
        if st.button("Atualizar Consumo"):
            ep_obj.traffic_up_mb, ep_obj.traffic_down_mb = up, down
            st.rerun()
        st.bar_chart({e.name: e.traffic_up_mb + e.traffic_down_mb for e in eps})

with tab_ligacoes:
    hosts = [d for d in inv.list_devices() if hasattr(d, "connected_devices") or hasattr(d, "connected_endpoints")]
    if hosts:
        h_name = st.selectbox("Equipamento Base", [h.name for h in hosts], key="host_link_select")
        h_obj = inv.devices.get(h_name)
        c1, c2 = st.columns(2)
        with c1:
            target = st.selectbox("Ligar a:", [d.name for d in inv.list_devices() if d.name != h_name], key="target_link_select")
            if st.button("Ligar"):
                try:
                    if hasattr(h_obj, "connect_device"): h_obj.connect_device(target)
                    else: h_obj.connect_endpoint(target)
                    st.rerun()
                except Exception as e: st.error(e)
        with c2:
            cons = getattr(h_obj, "connected_devices", []) or getattr(h_obj, "connected_endpoints", [])
            for c in cons:
                if st.button(f"Desligar {c}", key=f"dis_{h_name}_{c}"):
                    if hasattr(h_obj, "disconnect_device"): h_obj.disconnect_device(c)
                    else: h_obj.disconnect_endpoint(c)
                    st.rerun()
