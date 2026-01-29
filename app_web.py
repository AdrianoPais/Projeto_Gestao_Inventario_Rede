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
    """Regista ações num ficheiro local para auditoria (Sistema de Honra)."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def gerar_pdf(lista_dispositivos):
    """Gera um relatório formal em PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Inventario de Rede - Relatorio Oficial", 0, 1, "C")
    pdf.ln(10)
    
    for d in lista_dispositivos:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{d.name} ({d.device_type})", "T", 1)
        pdf.set_font("Arial", "", 10)
        
        # Uso de getattr para compatibilidade com dados antigos
        rack = getattr(d, 'rack', 1)
        cond = getattr(d, 'condition', 'Funcional')
        mod = getattr(d, 'model', 'N/A')
        
        pdf.cell(0, 7, f"Localizacao: Bastidor {rack} | Saude: {cond}", 0, 1)
        pdf.cell(0, 7, f"Modelo: {mod} | Estado Logico: {d.status}", 0, 1)
        
        def_desc = getattr(d, 'defect_description', '')
        if def_desc:
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 7, f"NOTA DE DEFEITO: {def_desc}", 0, 1)
            pdf.set_text_color(0, 0, 0)
            
        pdf.cell(0, 7, f"Obs: {d.observations if d.observations else 'Sem notas.'}", 0, 1)
        pdf.ln(5)
    return pdf.output(dest="S").encode("latin-1", errors="replace")

# ==================================================
# FUNÇÕES DE FORMULÁRIO
# ==================================================

def limpar_form():
    keys = [
        "add_tipo_select", "add_nome_input", "add_modelo_input", 
        "add_serial_select", "add_obs_input", "add_saude_select", 
        "add_defeito_input", "add_rack_select",
        "add_ip_router", "add_mac_router",
        "add_ports_sw", "add_giga_sw", "add_fast_sw", "add_mac_sw",
        "add_ssid_ap", "add_uid_ep", "add_ip_ep", "add_mac_ep"
    ]
    for k in keys:
        if k in st.session_state: del st.session_state[k]

def carregar_dados_para_form(device):
    st.session_state['add_tipo_select'] = device.device_type
    st.session_state['add_nome_input'] = device.name
    st.session_state['add_modelo_input'] = getattr(device, 'model', '')
    st.session_state['add_serial_select'] = "Sim" if getattr(device, 'serial_interface', False) else "Não"
    st.session_state['add_rack_select'] = getattr(device, 'rack', 1)
    st.session_state['add_saude_select'] = getattr(device, 'condition', 'Funcional')
    st.session_state['add_defeito_input'] = getattr(device, 'defect_description', '')
    st.session_state['add_obs_input'] = device.observations

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
# SIDEBAR: GESTÃO E EXPORTAÇÃO
# ==================================================
with st.sidebar:
    st.title("Gestão de Dados")
    
    if st.button("Guardar no Servidor", key="btn_save_srv"):
        save_to_json(inv, "inventario.json")
        log_event("Sincronização manual com o servidor executada.")
        st.success("Dados guardados.")
    
    if st.button("Recarregar do Ficheiro", key="btn_reload_srv"):
        st.session_state.inv = load_from_json("inventario.json")
        st.rerun()
    
    st.divider()
    st.subheader("Exportar Inventário")
    lista_dicts = [d.to_dict() for d in inv.list_devices()]
    
    if lista_dicts:
        df = pd.DataFrame(lista_dicts)
        
        # Colunas de exportação
        c_exp1, c_exp2 = st.columns(2)
        c_exp1.download_button("📄 JSON", data=json.dumps(lista_dicts, indent=2), file_name="inventario.json", key="btn_json")
        c_exp2.download_button("📊 CSV", data=df.to_csv(index=False).encode('utf-8'), file_name="inventario.csv", key="btn_csv")
        
        buffer_xls = BytesIO()
        with pd.ExcelWriter(buffer_xls, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📗 Excel (.xlsx)", data=buffer_xls.getvalue(), file_name="inventario.xlsx", key="btn_excel")
        
        # PDF e TXT
        pdf_data = gerar_pdf(inv.list_devices())
        st.download_button("📕 PDF Oficial", data=pdf_data, file_name="inventario_rede.pdf", key="btn_pdf")
        
        txt_content = "\n".join([str(d) for d in inv.list_devices()])
        st.download_button("📝 TXT Simples", data=txt_content, file_name="inventario.txt", key="btn_txt")

    st.divider()
    if st.checkbox("Ver Logs do Servidor"):
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r") as f:
                st.text_area("Histórico de Alterações", f.read(), height=200)
        else: st.info("Sem registos de log.")

st.title("Sistema de Gestão de Rede")

st.warning("""
**⚠️ Nota Importante (Sistema de Honra)**
Esta aplicação não possui controlo de acesso (UAC). Solicitamos que **não alterem ou eliminem** dispositivos sem confirmação dos **Administradores**.
""")

# ==================================================
# TABS
# ==================================================
tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs(["Gestão", "Consultas", "Tráfego", "Ligações"])

with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device
    acao_btn = "Atualizar" if is_editing else "Adicionar"

    with col_add:
        st.subheader("Formulário")
        tipo = st.selectbox("Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"], disabled=is_editing, key="add_tipo_select")
        nome = st.text_input("Nome Único", key="add_nome_input").strip()
        modelo = st.text_input("Modelo", key="add_modelo_input")
        
        # NOVO: Bastidor
        rack = st.selectbox("Bastidor (Localização)", [1, 2, 3, 4, 5, 6], key="add_rack_select")
        
        ser_sel = st.selectbox("Interface Serial?", ["Não", "Sim"], key="add_serial_select")
        saude = st.selectbox("Estado de Conservação", ["Funcional", "Com Defeito", "Avariado"], key="add_saude_select")
        defeito_desc = st.text_input("Descrição do Defeito", key="add_defeito_input") if saude == "Com Defeito" else ""
        obs = st.text_area("Observações Gerais", key="add_obs_input")

        def process_update(new_obj):
            if is_editing:
                if hasattr(dev_edit, "connected_devices"): new_obj.connected_devices = dev_edit.connected_devices
                inv.remove_device(dev_edit.name)
                log_event(f"EDITADO: {dev_edit.name} (Novo Bastidor: {rack})")
            else:
                log_event(f"CRIADO: {nome} no Bastidor {rack}")
            inv.add_device(new_obj)
            st.session_state.editing_device = None
            limpar_form()
            st.rerun()

        common = {"model": modelo, "serial_interface": (ser_sel == "Sim"), "observations": obs, "condition": saude, "defect_description": defeito_desc, "rack": rack}

        if tipo == "ROUTER":
            ipv4, mac = st.text_input("IPv4", key="add_ip_router"), st.text_input("MAC", key="add_mac_router")
            if st.button(f"{acao_btn} Router"): process_update(Router(nome, ipv4, "", mac, **common))
        elif tipo == "SWITCH":
            total_p = st.number_input("Portas", 1, 48, 24, key="add_ports_sw")
            g, f = st.slider("Gigabit", 0, total_p, key="add_giga_sw"), st.slider("Fast", 0, total_p, key="add_fast_sw")
            mac = st.text_input("MAC", key="add_mac_sw")
            if st.button(f"{acao_btn} Switch"): process_update(Switch(nome, "", mac, total_p, total_p-g-f, f, g, **common))
        elif tipo == "AP":
            ssid = st.text_input("SSID", key="add_ssid_ap")
            if st.button(f"{acao_btn} AP"): process_update(AccessPoint(nome, ssid, **common))
        elif tipo == "ENDPOINT":
            u, ip, m = st.text_input("User ID", key="add_uid_ep"), st.text_input("IPv4", key="add_ip_ep"), st.text_input("MAC", key="add_mac_ep")
            if st.button(f"{acao_btn} Endpoint"): process_update(Endpoint(nome, u, ip, "", m, **common))

        if is_editing: st.button("Cancelar", on_click=click_cancelar)

    with col_list:
        st.subheader("Inventário")
        devices = inv.list_devices()
        r, s, o = [d for d in devices if d.device_type=="ROUTER"], [d for d in devices if d.device_type=="SWITCH"], [d for d in devices if d.device_type not in ["ROUTER", "SWITCH"]]
        t_r, t_s, t_o, t_all = st.tabs([f"Routers ({len(r)})", f"Switches ({len(s)})", f"Outros ({len(o)})", f"Todos ({len(devices)})"])

        def render(lista, pref):
            for d in lista:
                cond = getattr(d, 'condition', 'Funcional')
                rk = getattr(d, 'rack', 1)
                header = f"{d.name} | Bastidor {rk}"
                if cond == "Avariado": header += " 🔴"
                elif cond == "Com Defeito": header += " 🟠"
                
                with st.expander(header):
                    st.write(f"**Modelo:** {getattr(d, 'model', 'N/A')} | **Saúde:** {cond}")
                    c1, c2 = st.columns(2)
                    c1.button("Editar", key=f"{pref}_ed_{d.name}", on_click=click_editar, args=(d,))
                    if c2.button("Eliminar", key=f"{pref}_el_{d.name}"):
                        log_event(f"ELIMINADO: {d.name} do Bastidor {rk}")
                        inv.remove_device(d.name)
                        st.rerun()

        with t_r: render(r, "r")
        with t_s: render(s, "s")
        with t_o: render(o, "o")
        with t_all: render(devices, "all")

with tab_consultas:
    st.subheader("Pesquisa Avançada")
    c_q1, c_q2, c_q3 = st.columns(3)
    with c_q1:
        search_n = st.text_input("Nome", key="q_n")
        if st.button("Filtrar Nome"):
            for r in [d for d in inv.list_devices() if search_n.lower() in d.name.lower()]: st.text(str(r))
    with c_q2:
        search_rk = st.selectbox("Bastidor", ["Todos", 1, 2, 3, 4, 5, 6], key="q_rk")
        if st.button("Filtrar Bastidor"):
            res = inv.list_devices() if search_rk=="Todos" else [d for d in inv.list_devices() if getattr(d, 'rack', 1)==search_rk]
            for r in res: st.text(str(r))
    with c_q3:
        search_cond = st.selectbox("Saúde", ["Todos", "Funcional", "Com Defeito", "Avariado"], key="q_cd")
        if st.button("Filtrar Saúde"):
            res = inv.list_devices() if search_cond=="Todos" else [d for d in inv.list_devices() if getattr(d, 'condition', 'Funcional')==search_cond]
            for r in res: st.text(str(r))

    st.divider()
    c4, c5 = st.columns(2)
    with c4:
        search_s = st.selectbox("Estado", ["Ativo", "Inativo"], key="query_status")
        if st.button("Filtrar Estado"):
            status_map = {"Ativo": "ACTIVE", "Inativo": "INACTIVE"}
            for r in [d for d in inv.list_devices() if d.status == status_map[search_s]]: st.text(str(r))
    with c5:
        search_ip = st.text_input("Endereço IP", key="query_ip")
        if st.button("Pesquisar IP"):
            for r in [d for d in inv.list_devices() if getattr(d, 'ipv4', '') == search_ip]: st.text(str(r))

# --- 3. TAB TRÁFEGO ---

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

# --- 4. TAB LIGAÇÕES ---

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
