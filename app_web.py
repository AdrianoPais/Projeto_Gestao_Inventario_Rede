import streamlit as st
import json
import os
import pandas as pd 
from io import BytesIO 
from datetime import datetime
from fpdf import FPDF # Certifica-te que tens 'fpdf' no requirements.txt
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
    """Regista ações no ficheiro local logs.txt."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

def gerar_pdf(lista_dispositivos):
    """Gera um relatório PDF oficial com os dados do inventário."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "Inventario de Rede - Relatorio Oficial", 0, 1, "C")
    pdf.ln(10)
    for d in lista_dispositivos:
        rk = getattr(d, 'rack', 1)
        cond = getattr(d, 'condition', 'Funcional')
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{d.name} ({d.device_type}) - Bastidor {rk}", "T", 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"Modelo: {d.model} | Saude: {cond}", 0, 1)
        pdf.cell(0, 7, f"Dados Tecnicos: {str(d)}", 0, 1)
        pdf.ln(4)
    return pdf.output(dest="S").encode("latin-1", errors="replace")

# ==================================================
# FUNÇÕES DE FORMULÁRIO
# ==================================================

def limpar_form():
    keys = [
        "add_tipo_select", "add_nome_input", "add_modelo_input", 
        "add_serial_select", "add_obs_input", "add_saude_select", 
        "add_defeito_input", "add_rack_select", "add_ip_router", 
        "add_mac_router", "add_ports_sw", "add_giga_sw", "add_fast_sw", 
        "add_mac_sw", "add_ssid_ap", "add_uid_ep", "add_ip_ep", "add_mac_ep"
    ]
    for k in keys:
        if k in st.session_state: del st.session_state[k]

def carregar_dados_para_form(device):
    st.session_state['add_tipo_select'] = device.device_type
    st.session_state['add_nome_input'] = device.name
    st.session_state['add_modelo_input'] = device.model
    st.session_state['add_serial_select'] = "Sim" if getattr(device, 'serial_interface', False) else "Não"
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
# SIDEBAR: GESTÃO E EXPORTAÇÕES (FORMATO ESCADA)
# ==================================================
with st.sidebar:
    st.title("Gestão de Dados")
    
    if st.button("Guardar no Servidor", use_container_width=True, key="btn_save_srv"):
        save_to_json(inv, "inventario.json")
        log_event("Guardado manual no servidor.")
        st.success("Dados guardados.")
    
    if st.button("Recarregar do Ficheiro", use_container_width=True, key="btn_reload_srv"):
        st.session_state.inv = load_from_json("inventario.json")
        st.session_state.editing_device = None
        limpar_form()
        st.rerun()
    
    st.divider()
    st.subheader("Exportar Inventário")
    lista_dicts = [d.to_dict() for d in inv.list_devices()]
    
    if lista_dicts:
        df = pd.DataFrame(lista_dicts)

        # 1. JSON (Largura Total)
        st.download_button(
            label="📄 Download JSON", 
            data=json.dumps(lista_dicts, indent=2, ensure_ascii=False), 
            file_name="inventario.json", 
            mime="application/json",
            use_container_width=True,
            key="btn_json"
        )

        # 2. EXCEL e PDF (Lado a Lado - Escada)
        c_mid1, c_mid2 = st.columns(2)
        
        # Coluna Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dispositivos')
        c_mid1.download_button(
            label="📗 Excel",
            data=buffer.getvalue(),
            file_name="inventario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_excel"
        )
        
        # Coluna PDF
        try:
            pdf_data = gerar_pdf(inv.list_devices())
            c_mid2.download_button(
                label="📕 PDF Oficial",
                data=pdf_data,
                file_name="relatorio_oficial.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="btn_pdf"
            )
        except:
            c_mid2.error("Erro PDF")

        # 3. TXT (Largura Total)
        txt_lines = [f"RELATÓRIO DE INVENTÁRIO - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n", "="*50 + "\n"]
        for d in inv.list_devices():
            txt_lines.append(f"DISPOSITIVO: {d.name} [{d.device_type}] (Bastidor {getattr(d, 'rack', 1)})")
            txt_lines.append(f"Saúde: {getattr(d, 'condition', 'Funcional')} | Modelo: {d.model}")
            txt_lines.append(f"Dados: {str(d)}")
            txt_lines.append(f"Obs: {d.observations if d.observations else 'N/A'}")
            txt_lines.append("-" * 30 + "\n")
        
        st.download_button(
            label="📝 Relatório TXT",
            data="\n".join(txt_lines),
            file_name="relatorio_rede.txt",
            mime="text/plain",
            use_container_width=True,
            key="btn_txt"
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
                    t, mod, obs = item.get("type"), item.get("model", ""), item.get("observations", "")
                    ser_int, cond, def_desc, rk = item.get("serial_interface", False), item.get("condition", "Funcional"), item.get("defect_description", ""), item.get("rack", 1)
                    if t == "ROUTER": obj = Router(item["name"], item.get("ipv4", ""), "", item["mac_address"], mod, ser_int, obs, cond, def_desc, rk)
                    elif t == "SWITCH": obj = Switch(item["name"], "", item["mac_address"], int(item["ports"]), item.get("eth_ports", 0), item.get("fast_eth_ports", 0), item.get("giga_eth_ports", 0), mod, ser_int, obs, cond, def_desc, rk)
                    elif t == "AP": obj = AccessPoint(item["name"], item["ssid"], mod, ser_int, obs, cond, def_desc, rk)
                    elif t == "ENDPOINT":
                        obj = Endpoint(item["name"], item["user_id"], item.get("ipv4", ""), "", item["mac_address"], mod, ser_int, obs, cond, def_desc, rk)
                        obj.traffic_up_mb, obj.traffic_down_mb = float(item.get("traffic_up_mb", 0.0)), float(item.get("traffic_down_mb", 0.0))
                    else: continue
                    obj.status = item.get("status", "ACTIVE")
                    temp_inv.add_device(obj)
                st.session_state.inv = temp_inv
                log_event("Backup restaurado via Upload."); st.rerun()
            except Exception as e: st.error(f"Erro: {e}")

    st.divider()
    if st.checkbox("Ver Logs do Servidor"):
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r") as f: st.text_area("Histórico", f.read(), height=200)

# ==================================================
# CORPO DA PÁGINA
# ==================================================
st.title("Sistema de Gestão de Rede")

st.warning("""
**⚠️ Nota Importante (Sistema de Honra)**

Esta aplicação está alojada no servidor da Streamlit e, de momento, não possui controlo de acesso individual (UAC). Por este motivo, operamos num **Sistema de Honra**: solicitamos a todos os utilizadores que **não alterem ou eliminem** quaisquer dispositivos ou configurações sem a confirmação prévia dos **Administradores**. 

Contamos com a colaboração de todos para manter o inventário correto!
""")

tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs(["Gestão", "Consultas", "Tráfego", "Ligações"])

with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device
    acao_btn = "Atualizar" if is_editing else "Adicionar"

    with col_add:
        st.subheader("Dispositivo")
        tipo = st.selectbox("Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"], disabled=is_editing, key="add_tipo_select")
        nome = st.text_input("Nome Único", key="add_nome_input").strip()
        modelo = st.text_input("Modelo", key="add_modelo_input")
        rack = st.selectbox("Bastidor (1-6)", [1, 2, 3, 4, 5, 6], key="add_rack_select")
        ser_sel = st.selectbox("Interface Serial?", ["Não", "Sim"], key="add_serial_select")
        saude = st.selectbox("Estado de Conservação", ["Funcional", "Com Defeito", "Avariado"], key="add_saude_select")
        defeito_desc = st.text_input("Descreva o Defeito", key="add_defeito_input") if saude == "Com Defeito" else ""
        obs = st.text_area("Observações Gerais", key="add_obs_input")

        def process_update(new_obj):
            if is_editing:
                inv.remove_device(dev_edit.name)
                log_event(f"EDITADO: {dev_edit.name}")
            else:
                log_event(f"CRIADO: {nome} no Bastidor {rack}")
            inv.add_device(new_obj)
            st.session_state.editing_device = None
            limpar_form(); st.rerun()

        params = {"model": modelo, "serial_interface": (ser_sel == "Sim"), "observations": obs, "condition": saude, "defect_description": defeito_desc, "rack": rack}
        if tipo == "ROUTER":
            ipv4, mac = st.text_input("IPv4", key="add_ip_router"), st.text_input("MAC", key="add_mac_router")
            if st.button(f"{acao_btn} Router"): process_update(Router(nome, ipv4, "", mac, **params))
        elif tipo == "SWITCH":
            p = st.number_input("Portas", 1, 48, 24, key="add_ports_sw")
            g, f = st.slider("Gigabit", 0, p, key="add_giga_sw"), st.slider("Fast", 0, p, key="add_fast_sw")
            mac = st.text_input("MAC Address", key="add_mac_sw")
            if st.button(f"{acao_btn} Switch"): process_update(Switch(nome, "", mac, p, p-g-f, f, g, **params))
        elif tipo == "AP":
            ssid = st.text_input("SSID", key="add_ssid_ap")
            if st.button(f"{acao_btn} AP"): process_update(AccessPoint(nome, ssid, **params))
        elif tipo == "ENDPOINT":
            u, ip, m = st.text_input("User ID", key="add_uid_ep"), st.text_input("IPv4", key="add_ip_ep"), st.text_input("MAC", key="add_mac_ep")
            if st.button(f"{acao_btn} Endpoint"): process_update(Endpoint(nome, u, ip, "", m, **params))
        if is_editing: st.button("Cancelar", on_click=click_cancelar)

    with col_list:
        st.subheader("Lista do Inventário")
        devices = inv.list_devices()
        r, s, o = [d for d in devices if d.device_type=="ROUTER"], [d for d in devices if d.device_type=="SWITCH"], [d for d in devices if d.device_type not in ["ROUTER", "SWITCH"]]
        t_r, t_s, t_o, t_all = st.tabs([f"Routers ({len(r)})", f"Switches ({len(s)})", f"Outros ({len(o)})", f"Todos ({len(devices)})"])

        def render_lista(lista, prefix):
            if not lista: st.info("Vazio.")
            for d in lista:
                cond, rk = getattr(d, 'condition', 'Funcional'), getattr(d, 'rack', 1)
                ser_int = "Sim" if getattr(d, 'serial_interface', False) else "Não"
                mac_val = getattr(d, 'mac_address', 'N/A')
                ip_val = getattr(d, 'ipv4', 'N/A')
                
                header = f"{d.name} | Bastidor {rk}"
                if cond == "Avariado": header += " 🔴"
                elif cond == "Com Defeito": header += " 🟠"
                
                with st.expander(header):
                    st.write(f"**Saúde:** {cond} | **Bastidor:** {rk} | **Modelo:** {d.model}")
                    st.write(f"**Serial:** {ser_int} | **MAC:** {mac_val} | **IP:** {ip_val}")
                    st.info(f"**OBS.:** {d.observations if d.observations else 'Sem observações.'}")
                    c1, c2 = st.columns(2)
                    c1.button("Editar", key=f"{prefix}_ed_{d.name}", on_click=click_editar, args=(d,))
                    if c2.button("Eliminar", key=f"{prefix}_el_{d.name}"):
                        log_event(f"ELIMINADO: {d.name} do Bastidor {rk}"); inv.remove_device(d.name); st.rerun()

        with t_r: render_lista(r, "r")
        with t_s: render_lista(s, "s")
        with t_o: render_lista(o, "o")
        with t_all: render_lista(devices, "t")

with tab_consultas:
    st.subheader("Pesquisa Avançada")
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1: search_n = st.text_input("Nome", key="q_n")
    with r1c2: search_t = st.selectbox("Tipo", ["Todos", "ROUTER", "SWITCH", "AP", "ENDPOINT"], key="q_t")
    with r1c3: search_rk = st.selectbox("Bastidor", ["Todos", 1, 2, 3, 4, 5, 6], key="q_rk")
    
    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1: search_cond = st.selectbox("Saúde", ["Todos", "Funcional", "Com Defeito", "Avariado"], key="q_cd")
    with r2c2: search_ser = st.selectbox("Serial?", ["Todos", "Sim", "Não"], key="q_ser")
    with r2c3: search_mac = st.text_input("MAC", key="q_mac")
    with r2c4: search_ip = st.text_input("IP", key="q_ip")

    if st.button("Executar Pesquisa", use_container_width=True):
        res = inv.list_devices()
        if search_n: res = [d for d in res if search_n.lower() in d.name.lower()]
        if search_t != "Todos": res = [d for d in res if d.device_type == search_t]
        if search_rk != "Todos": res = [d for d in res if getattr(d, 'rack', 1) == search_rk]
        if search_cond != "Todos": res = [d for d in res if getattr(d, 'condition', 'Funcional') == search_cond]
        if search_ser != "Todos": res = [d for d in res if getattr(d, 'serial_interface', False) == (search_ser == "Sim")]
        if search_mac: res = [d for d in res if search_mac.lower() in getattr(d, 'mac_address', '').lower()]
        if search_ip: res = [d for d in res if search_ip in getattr(d, 'ipv4', '')]
        
        for r_res in res:
            with st.expander(f"{r_res.name} | Bastidor {getattr(r_res, 'rack', 1)}"):
                st.write(f"**Tipo:** {r_res.device_type} | **Saúde:** {getattr(r_res, 'condition', 'Funcional')}")
                st.write(f"**MAC:** {getattr(r_res, 'mac_address', 'N/A')} | **IP:** {getattr(r_res, 'ipv4', 'N/A')}")
                st.info(f"**OBS.:** {r_res.observations if r_res.observations else 'N/A'}")

# --- TABS TRÁFEGO E LIGAÇÕES (SEM ALTERAÇÕES) ---
with tab_trafego:
    eps = [d for d in inv.list_devices() if isinstance(d, Endpoint)]
    if eps:
        target = st.selectbox("Escolher Endpoint", [e.name for e in eps], key="traffic_target_select")
        ep_obj = inv.get_endpoint(target)
        up = st.number_input("Upload (MB)", value=float(ep_obj.traffic_up_mb), key="input_traffic_up")
        down = st.number_input("Download (MB)", value=float(ep_obj.traffic_down_mb), key="input_traffic_down")
        if st.button("Atualizar Dados"): ep_obj.traffic_up_mb, ep_obj.traffic_down_mb = up, down; st.rerun()
        st.bar_chart({e.name: e.traffic_up_mb + e.traffic_down_mb for e in eps})

with tab_ligacoes:
    hosts = [d for d in inv.list_devices() if hasattr(d, "connected_devices") or hasattr(d, "connected_endpoints")]
    if hosts:
        h_name = st.selectbox("Equipamento Central", [h.name for h in hosts], key="host_link_select")
        h_obj = inv.devices.get(h_name)
        c_l, c_r = st.columns(2)
        with c_l:
            target = st.selectbox("Ligar a:", [d.name for d in inv.list_devices() if d.name != h_name], key="target_link_select")
            if st.button("Ligar"):
                try:
                    if hasattr(h_obj, "connect_device"): h_obj.connect_device(target)
                    else: h_obj.connect_endpoint(target)
                    st.rerun()
                except Exception as e: st.error(e)
        with c_r:
            cons = getattr(h_obj, "connected_devices", []) or getattr(h_obj, "connected_endpoints", [])
            for c in cons:
                if st.button(f"Desligar {c}", key=f"dis_{h_name}_{c}"):
                    if hasattr(h_obj, "disconnect_device"): h_obj.disconnect_device(c)
                    else: h_obj.disconnect_endpoint(c)
                    st.rerun()
