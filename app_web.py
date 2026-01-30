# Nome 1: Daniel Santos
# Nome 2: Sérgio Correia
# Nome 3: Tiago Costa
# Turma: GRSC0925
# Trabalho: Projeto Final UC00608 - Programação Alocada a Objetos (Em Python)

# ==================================================
# IMPORTAÇÕES DE BIBLIOTECAS
# ==================================================
# Importa todas as bibliotecas necessárias para o funcionamento da aplicação

import streamlit as st  # Framework para criar interfaces web interativas
import json  # Biblioteca para trabalhar com dados em formato JSON
import os  # Biblioteca para operações do sistema operativo (verificar ficheiros, etc.)
import pandas as pd  # Biblioteca para manipulação de dados em tabelas (DataFrames)
from io import BytesIO  # Permite trabalhar com dados binários em memória (útil para Excel)
from datetime import datetime  # Biblioteca para trabalhar com datas e horas
from fpdf import FPDF  # Biblioteca para gerar documentos PDF
from inventory import NetworkInventory  # Importa a classe que gere todo o inventário
from devices import Router, Switch, AccessPoint, Endpoint  # Importa as classes dos diferentes tipos de dispositivos
from storage import save_to_json, load_from_json  # Importa funções para guardar/carregar dados em JSON

# ==================================================
# CONFIGURAÇÃO DA PÁGINA E ESTADO
# ==================================================

# Configura a página web com título e layout largo

st.set_page_config(page_title="Network Manager Pro", layout="wide")

# Verifica se já existe um inventário na sessão (memória temporária do Streamlit)
# Se não existir, tenta carregar do ficheiro ou cria um novo inventário vazio

if 'inv' not in st.session_state:
    # Tenta carregar o inventário do ficheiro JSON existente
    if os.path.exists("inventario.json"):
        # Ao falhar, cria um inventário vazio
        try: st.session_state.inv = load_from_json("inventario.json")
        except: st.session_state.inv = NetworkInventory()
    else:
        # Cria um inventário vazio
        st.session_state.inv = NetworkInventory()

# Acesso rápido ao inventário na sessão

inv = st.session_state.inv

# Variável de estado para controlar se estamos a editar um dispositivo

if 'editing_device' not in st.session_state:
    st.session_state.editing_device = None

# ==================================================
# FUNÇÕES AUXILIARES (LOGS E PDF)
# ==================================================

# Função para registar eventos no ficheiro de logs

def log_event(mensagem):
    """
    Regista eventos/ações no ficheiro de logs.
    
    Esta função guarda um histórico de todas as ações realizadas na aplicação
    (criação, edição, eliminação de dispositivos) com data e hora.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

# Função para gerar um relatório PDF do inventário

def gerar_pdf(lista_dispositivos):
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
        pdf.cell(0, 7, f"Dados Técnicos: {str(d)}", 0, 1)
        pdf.ln(4)
    return pdf.output(dest="S").encode("latin-1", errors="replace")

# ==================================================
# FUNÇÕES DE FORMULÁRIO
# ==================================================

# Função para limpar o formulário de adição/edição de dispositivos

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

# Função para carregar os dados de um dispositivo existente no formulário para edição

def carregar_dados_para_form(device):
    st.session_state['add_tipo_select'] = device.device_type
    st.session_state['add_nome_input'] = device.name
    st.session_state['add_modelo_input'] = device.model
    st.session_state['add_serial_select'] = "Sim" if getattr(device, 'serial_interface', False) else "Não"
    st.session_state['add_obs_input'] = device.observations
    st.session_state['add_saude_select'] = getattr(device, 'condition', 'Funcional')
    st.session_state['add_defeito_input'] = getattr(device, 'defect_description', '')
    st.session_state['add_rack_select'] = getattr(device, 'rack', 1)

    # Carrega campos específicos conforme o tipo de dispositivo
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

# Função chamada ao clicar em "Editar" para carregar os dados no formulário

def click_editar(device):
    st.session_state.editing_device = device
    carregar_dados_para_form(device)

# Função chamada ao clicar em "Cancelar" para limpar o formulário

def click_cancelar():
    st.session_state.editing_device = None
    limpar_form()

# ==================================================
# SIDEBAR: GESTÃO E EXPORTAÇÕES (UMA POR LINHA)
# ==================================================

# Configuração da barra lateral com opções de gestão e exportação de dados

with st.sidebar:
    st.title("Gestão de Dados")
    
    # Botões para guardar e recarregar o inventário no servidor
    if st.button("Guardar no Servidor", use_container_width=True, key="btn_save_srv"):
        save_to_json(inv, "inventario.json")
        log_event("Guardado manual no servidor.")
        st.success("Dados guardados.")
    
    # Botão para recarregar o inventário do ficheiro no servidor
    if st.button("Recarregar do Ficheiro", use_container_width=True, key="btn_reload_srv"):
        st.session_state.inv = load_from_json("inventario.json")
        st.session_state.editing_device = None
        limpar_form()
        st.rerun()
    
    st.divider()
    st.subheader("Exportar Inventário")
    lista_dicts = [d.to_dict() for d in inv.list_devices()]
    
    # Verifica se o inventário está vazio antes de permitir downloads

    if not lista_dicts:
        st.warning("Inventário vazio.")
    else:
        df = pd.DataFrame(lista_dicts)

        # Botões de download para vários formatos - JSON, CSV, Excel, PDF, TXT
        st.download_button(
            label="📄 Download JSON", 
            data=json.dumps(lista_dicts, indent=2, ensure_ascii=False), 
            file_name="inventario.json", 
            mime="application/json",
            key="btn_json"
        )

        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name="inventario.csv",
            mime="text/csv",
            key="btn_csv"
        )

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dispositivos')
        
        st.download_button(
            label="📗 Download Excel",
            data=buffer.getvalue(),
            file_name="inventario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_excel"
        )
        # Geração do PDF com tratamento de erros
        try:
            pdf_data = gerar_pdf(inv.list_devices())
            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name="relatorio_oficial.pdf",
                mime="application/pdf",
                key="btn_pdf"
            )
        # Caso ocorra um erro na geração do PDF, exibe uma mensagem de erro
        except:
            st.sidebar.error("Erro ao gerar PDF")

        # Geração do TXT simples
        txt_lines = [f"RELATÓRIO DE INVENTÁRIO - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n", "="*50 + "\n"]
        for d in inv.list_devices():
            rk = getattr(d, 'rack', 1)
            cond = getattr(d, 'condition', 'Funcional')
            txt_lines.append(f"DISPOSITIVO: {d.name} [{d.device_type}] (Bastidor {rk})")
            txt_lines.append(f"Estado: {cond} | Modelo: {d.model}")
            txt_lines.append(f"Dados Técnicos: {str(d)}")
            txt_lines.append(f"Obs: {d.observations if d.observations else 'N/A'}")
            txt_lines.append("-" * 30 + "\n")
        
        st.download_button(
            label="📝 Download TXT",
            data="\n".join(txt_lines),
            file_name="relatorio_rede.txt",
            mime="text/plain",
            key="btn_txt"
        )

    # Seção para upload e restauração de backup JSON
    st.divider()
    st.subheader("Upload Local")
    uploaded_file = st.file_uploader("Carregar backup JSON", type=["json"], key="uploader_json")
    
    # Processa o ficheiro carregado para restaurar o inventário

    if uploaded_file is not None:
        # Botão para restaurar o backup a partir do ficheiro carregado
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
                st.rerun()
            except Exception as e: st.error(f"Erro: {e}")

    # Seção para visualizar logs do servidor
    st.divider()
    if st.checkbox("Ver Logs do Servidor"):
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r") as f: st.text_area("Histórico", f.read(), height=200)

# ==================================================
# TÍTULO E AVISO IMPORTANTE
# ==================================================

st.title("Sistema de Gestão de Rede")

st.warning("""
**⚠️ Nota Importante (Sistema de Honra)**
Esta aplicação está alojada no servidor da Streamlit e não possui controlo de acesso individual (UAC). Por este motivo, operamos num **Sistema de Honra**: solicitamos a todos os utilizadores que **não alterem ou eliminem** quaisquer dispositivos ou configurações sem a confirmação prévia dos **Administradores**. 

Contamos com a colaboração de todos para manter o inventário correto!
""")

# ==================================================
# TABS PRINCIPAIS
# ==================================================

# --- 1. TAB GESTÃO ---

tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs(["Gestão", "Consultas", "Tráfego", "Ligações"])

# Área principal de gestão de dispositivos

with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device
    acao_btn = "Atualizar" if is_editing else "Adicionar"

    # Formulário de Adição/Edição de Dispositivos
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

        # Função para processar a adição ou atualização do dispositivo
        def process_update(new_obj):
            if is_editing:
                inv.remove_device(dev_edit.name)
                log_event(f"EDITADO: {dev_edit.name} (Novo Bastidor: {rack})")
            else: log_event(f"CRIADO: {nome} no Bastidor {rack}")
            inv.add_device(new_obj)
            st.session_state.editing_device = None
            limpar_form(); st.rerun()

        # Campos específicos conforme o tipo de dispositivo
        common = {"model": modelo, "serial_interface": (ser_sel == "Sim"), "observations": obs, "condition": saude, "defect_description": defeito_desc, "rack": rack}
        if tipo == "ROUTER":
            ipv4, mac = st.text_input("IPv4", key="add_ip_router"), st.text_input("MAC", key="add_mac_router")
            if st.button(f"{acao_btn} Router"): process_update(Router(nome, ipv4, "", mac, **common))
        elif tipo == "SWITCH":
            p = st.number_input("Portas", 1, 48, 24, key="add_ports_sw")
            g, f = st.slider("Gigabit", 0, p, key="add_giga_sw"), st.slider("Fast", 0, p, key="add_fast_sw")
            mac = st.text_input("MAC", key="add_mac_sw")
            if st.button(f"{acao_btn} Switch"): process_update(Switch(nome, "", mac, p, p-g-f, f, g, **common))
        elif tipo == "AP":
            ssid = st.text_input("SSID", key="add_ssid_ap")
            if st.button(f"{acao_btn} AP"): process_update(AccessPoint(nome, ssid, **common))
        elif tipo == "ENDPOINT":
            u, ip, m = st.text_input("User ID", key="add_uid_ep"), st.text_input("IPv4", key="add_ip_ep"), st.text_input("MAC", key="add_mac_ep")
            if st.button(f"{acao_btn} Endpoint"): process_update(Endpoint(nome, u, ip, "", m, **common))
        if is_editing: st.button("Cancelar", on_click=click_cancelar)

    # Lista de Dispositivos no Inventário
    with col_list:
        st.subheader("Lista do Inventário")
        devices = inv.list_devices()
        r, s, o = [d for d in devices if d.device_type=="ROUTER"], [d for d in devices if d.device_type=="SWITCH"], [d for d in devices if d.device_type not in ["ROUTER", "SWITCH"]]
        t_r, t_s, t_o, t_all = st.tabs([f"Routers ({len(r)})", f"Switches ({len(s)})", f"Outros ({len(o)})", f"Todos ({len(devices)})"])

        # Função para renderizar a lista de dispositivos com ícones coloridos
        def render_lista(lista, prefix):
            if not lista: st.info("Vazio.")
            for d in lista:
                cond, rk = getattr(d, 'condition', 'Funcional'), getattr(d, 'rack', 1)
                header = f"{d.name} | Bastidor {rk}"
                # Lógica de Ícones coloridos
                if cond == "Avariado": header += " 🔴" # Ícone Vermelho para Avaraiado
                elif cond == "Com Defeito": header += " 🟠" # Ícone Laranja para Com Defeito
                else: header += " 🟢" # Ícone Verde para Funcional

                # Expander com detalhes do dispositivo
                with st.expander(header):
                    st.write(f"**Estado:** {cond} | **Bastidor:** {rk} | **Modelo:** {d.model}")
                    st.write(f"**Serial:** {'Sim' if getattr(d, 'serial_interface', False) else 'Não'} | **MAC:** {getattr(d, 'mac_address', 'N/A')} | **IP:** {getattr(d, 'ipv4', 'N/A')}")
                    st.info(f"**OBS.:** {d.observations if d.observations else 'Sem observações.'}")
                    c1, c2 = st.columns(2)
                    c1.button("Editar", key=f"{prefix}_ed_{d.name}", on_click=click_editar, args=(d,))
                    if c2.button("Eliminar", key=f"{prefix}_el_{d.name}"):
                        log_event(f"ELIMINADO: {d.name} do Bastidor {rk}"); inv.remove_device(d.name); st.rerun()

        # Renderiza as listas em cada tab
        with t_r: render_lista(r, "r")
        with t_s: render_lista(s, "s")
        with t_o: render_lista(o, "o")
        with t_all: render_lista(devices, "t")
        
        # Legenda de Ícones
        st.write("")
        st.caption("💡 **Legenda de Estados:** 🟢 Funcional | 🟠 Com Defeito | 🔴 Avariado")

# --- 2. TAB CONSULTAS ---

# Área de consultas avançadas com múltiplos filtros

with tab_consultas:

    # Filtros de pesquisa
    st.subheader("Pesquisa Avançada")
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1: search_n = st.text_input("Filtrar por Nome", key="q_n")
    with r1_c2: search_t = st.selectbox("Filtrar por Tipo", ["Todos", "ROUTER", "SWITCH", "AP", "ENDPOINT"], key="q_t")
    with r1_c3: search_rk = st.selectbox("Filtrar por Bastidor", ["Todos", 1, 2, 3, 4, 5, 6], key="q_rk")

    # Segunda linha de filtros
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1: search_cond = st.selectbox("Filtrar por Estado", ["Todos", "Funcional", "Com Defeito", "Avariado"], key="q_cd")
    with r2_c2: search_ser = st.selectbox("Interface Serial?", ["Todos", "Sim", "Não"], key="q_ser")
    with r2_c3: search_mac = st.text_input("Filtrar por MAC", key="q_mac")
    with r2_c4: search_ip = st.text_input("Filtrar por IP", key="q_ip")

    # Botão para executar a pesquisa com os filtros aplicados
    if st.button("Executar Pesquisa", use_container_width=True):
        res = inv.list_devices()
        if search_n: res = [d for d in res if search_n.lower() in d.name.lower()]
        if search_t != "Todos": res = [d for d in res if d.device_type == search_t]
        if search_rk != "Todos": res = [d for d in res if getattr(d, 'rack', 1) == search_rk]
        if search_cond != "Todos": res = [d for d in res if getattr(d, 'condition', 'Funcional') == search_cond]
        if search_ser != "Todos": res = [d for d in res if getattr(d, 'serial_interface', False) == (search_ser == "Sim")]
        if search_mac: res = [d for d in res if search_mac.lower() in getattr(d, 'mac_address', '').lower()]
        if search_ip: res = [d for d in res if search_ip in getattr(d, 'ipv4', '')]

        if not res: st.warning("Nenhum dispositivo encontrado.")
        for r_res in res:
            header_q = f"{r_res.name} | Bastidor {getattr(r_res, 'rack', 1)}"
            # Adiciona ícones também nas consultas
            c_saude = getattr(r_res, 'condition', 'Funcional')
            if c_saude == "Avariado": header_q += " 🔴" # Ícone Vermelho para Avariado
            elif c_saude == "Com Defeito": header_q += " 🟠" # Ícone Laranja para Com Defeito
            else: header_q += " 🟢" # Ícone Verde para Funcional

            # Expander com detalhes do dispositivo
            with st.expander(header_q):
                st.write(f"**Tipo:** {r_res.device_type} | **Estado:** {c_saude} | **Modelo:** {r_res.model}")
                st.write(f"**MAC:** {getattr(r_res, 'mac_address', 'N/A')} | **IP:** {getattr(r_res, 'ipv4', 'N/A')}")
                st.info(f"**OBS.:** {r_res.observations if r_res.observations else 'N/A'}")

# --- 3. TAB TRÁFEGO ---

# Área de monitorização e atualização de tráfego dos Endpoints

with tab_trafego:
    # Lista de Endpoints para monitorização
    eps = [d for d in inv.list_devices() if isinstance(d, Endpoint)]

    # Se não houver Endpoints, exibe uma mensagem informativa
    if not eps: 
        st.info("Adicione Endpoints na Gestão para monitorizar o tráfego.")

    # Caso contrário, permite selecionar um Endpoint e atualizar o tráfego
    else:
        # Seleção do Endpoint
        target = st.selectbox("Endpoint", [e.name for e in eps], key="traffic_target_select")
        ep_obj = inv.get_endpoint(target)
        up = st.number_input("Upload (MB)", value=float(ep_obj.traffic_up_mb), key="input_traffic_up")
        down = st.number_input("Download (MB)", value=float(ep_obj.traffic_down_mb), key="input_traffic_down")
        if st.button("Atualizar Consumo"):
            ep_obj.traffic_up_mb, ep_obj.traffic_down_mb = up, down; st.rerun()
        st.bar_chart({e.name: e.traffic_up_mb + e.traffic_down_mb for e in eps})

# --- 4. TAB LIGAÇÕES ---

# Área para gerir ligações entre dispositivos (Routers, Switches, Endpoints)

with tab_ligacoes:

    # Lista de dispositivos que podem estabelecer ligações
    hosts = [d for d in inv.list_devices() if hasattr(d, "connected_devices") or hasattr(d, "connected_endpoints")]
    if not hosts:
        st.info("Crie Routers ou Switches para estabelecer ligações.")
    else:

        # Seleção do dispositivo base para gerir ligações
        h_name = st.selectbox("Equipamento Base", [h.name for h in hosts], key="host_link_select")
        h_obj = inv.devices.get(h_name)
        c1, c2 = st.columns(2)

        # Área para adicionar novas ligações
        with c1:
            target = st.selectbox("Ligar a:", [d.name for d in inv.list_devices() if d.name != h_name], key="target_link_select")
            if st.button("Ligar"):
                try:
                    if hasattr(h_obj, "connect_device"): h_obj.connect_device(target)
                    else: h_obj.connect_endpoint(target)
                    st.rerun()
                except Exception as e: st.error(e)

        # Área para listar e desligar ligações existentes
        with c2:
            cons = getattr(h_obj, "connected_devices", []) or getattr(h_obj, "connected_endpoints", [])
            for c in cons:
                if st.button(f"Desligar {c}", key=f"dis_{h_name}_{c}"):
                    if hasattr(h_obj, "disconnect_device"): h_obj.disconnect_device(c)
                    else: h_obj.disconnect_endpoint(c)
                    st.rerun()
