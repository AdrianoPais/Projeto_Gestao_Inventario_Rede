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
# Se não existir, tenta carregar do ficheiro ou cria um novo
if 'inv' not in st.session_state:
    # Verifica se existe o ficheiro de inventário no disco
    if os.path.exists("inventario.json"):
        try: 
            # Tenta carregar o inventário existente
            st.session_state.inv = load_from_json("inventario.json")
        except: 
            # Se houver erro ao carregar, cria um inventário vazio
            st.session_state.inv = NetworkInventory()
    else:
        # Se o ficheiro não existe, cria um inventário vazio
        st.session_state.inv = NetworkInventory()

# Cria uma referência mais curta para o inventário (facilita o código)
inv = st.session_state.inv

# Verifica se existe um dispositivo em edição na sessão
# Esta variável guarda qual dispositivo está a ser editado (ou None se nenhum)
if 'editing_device' not in st.session_state:
    st.session_state.editing_device = None

# ==================================================
# FUNÇÕES AUXILIARES (LOGS E PDF)
# ==================================================

def log_event(mensagem):
    """
    Regista eventos/ações no ficheiro de logs.
    
    Esta função guarda um histórico de todas as ações realizadas na aplicação
    (criação, edição, eliminação de dispositivos) com data e hora.
    """
    # Obtém a data e hora atual no formato dia/mês/ano hora:minuto:segundo
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Abre o ficheiro logs.txt em modo "append" (adicionar ao final)
    with open("logs.txt", "a", encoding="utf-8") as f:
        # Escreve a mensagem com o timestamp no ficheiro
        f.write(f"[{timestamp}] {mensagem}\n")

def gerar_pdf(lista_dispositivos):

    """
    Gera um relatório em PDF com todos os dispositivos do inventário.
    
    Recebe uma lista de dispositivos e cria um documento PDF formatado
    com as informações de cada um.
    """

    # Cria um novo documento PDF
    pdf = FPDF()
    # Adiciona uma página ao PDF
    pdf.add_page()
    # Define a fonte para o título (Arial, Bold, tamanho 16)
    pdf.set_font("Arial", "B", 16)
    # Cria o título centrado do relatório
    pdf.cell(190, 10, "Inventario de Rede - Relatorio Oficial", 0, 1, "C")
    # Adiciona espaço após o título
    pdf.ln(10)
    
    # Percorre cada dispositivo da lista
    for d in lista_dispositivos:
        # Obtém o número do bastidor (rack) do dispositivo (padrão: 1)
        rk = getattr(d, 'rack', 1)
        # Obtém o estado de conservação (padrão: 'Funcional')
        cond = getattr(d, 'condition', 'Funcional')
        
        # Adiciona cabeçalho do dispositivo em negrito
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"{d.name} ({d.device_type}) - Bastidor {rk}", "T", 1)
        
        # Adiciona detalhes do dispositivo em fonte normal
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 7, f"Modelo: {d.model} | Saude: {cond}", 0, 1)
        pdf.cell(0, 7, f"Dados Técnicos: {str(d)}", 0, 1)
        # Adiciona espaçamento entre dispositivos
        pdf.ln(4)
    
    # Retorna o PDF como bytes (codificado em latin-1)
    return pdf.output(dest="S").encode("latin-1", errors="replace")

# ==================================================
# FUNÇÕES DE FORMULÁRIO
# ==================================================

def limpar_form():

    """
    Limpa todos os campos do formulário.
    
    Remove todos os valores guardados na sessão relacionados com o formulário
    de adicionar/editar dispositivos.
    """

    # Lista com todas as chaves (identificadores) dos campos do formulário
    keys = [
        "add_tipo_select", "add_nome_input", "add_modelo_input", 
        "add_serial_select", "add_obs_input", "add_saude_select", 
        "add_defeito_input", "add_rack_select", "add_ip_router", 
        "add_mac_router", "add_ports_sw", "add_giga_sw", "add_fast_sw", 
        "add_mac_sw", "add_ssid_ap", "add_uid_ep", "add_ip_ep", "add_mac_ep"
    ]
    # Percorre cada chave e remove-a da sessão se existir
    for k in keys:
        if k in st.session_state: 
            del st.session_state[k]

def carregar_dados_para_form(device):

    """
    Preenche o formulário com os dados de um dispositivo existente.
    
    Usada quando queremos editar um dispositivo - carrega todos os seus
    dados para os campos do formulário.
    """

    # Carrega os dados comuns a todos os dispositivos
    st.session_state['add_tipo_select'] = device.device_type
    st.session_state['add_nome_input'] = device.name
    st.session_state['add_modelo_input'] = device.model
    st.session_state['add_serial_select'] = "Sim" if getattr(device, 'serial_interface', False) else "Não"
    st.session_state['add_obs_input'] = device.observations
    st.session_state['add_saude_select'] = getattr(device, 'condition', 'Funcional')
    st.session_state['add_defeito_input'] = getattr(device, 'defect_description', '')
    st.session_state['add_rack_select'] = getattr(device, 'rack', 1)

    # Carrega dados específicos dependendo do tipo de dispositivo
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
    Função chamada quando o utilizador clica no botão "Editar".
    
    Define o dispositivo em edição e carrega os seus dados para o formulário.
    """

    st.session_state.editing_device = device
    carregar_dados_para_form(device)

def click_cancelar():

    """
    Função chamada quando o utilizador clica no botão "Cancelar".
    
    Cancela a edição e limpa o formulário.
    """

    st.session_state.editing_device = None
    limpar_form()

# ==================================================
# SIDEBAR: GESTÃO E EXPORTAÇÕES (UMA POR LINHA)
# ==================================================

# A sidebar (barra lateral) contém botões para guardar/carregar dados e exportar o inventário
with st.sidebar:
    st.title("Gestão de Dados")
    
    # Botão para guardar manualmente o inventário no servidor (ficheiro)
    if st.button("Guardar no Servidor", use_container_width=True, key="btn_save_srv"):
        save_to_json(inv, "inventario.json")
        log_event("Guardado manual no servidor.")
        st.success("Dados guardados.")
    
    # Botão para recarregar os dados do ficheiro (descarta alterações não guardadas)
    if st.button("Recarregar do Ficheiro", use_container_width=True, key="btn_reload_srv"):
        st.session_state.inv = load_from_json("inventario.json")
        st.session_state.editing_device = None
        limpar_form()
        st.rerun()  # Reinicia a aplicação para mostrar os dados recarregados
    
    # Linha divisória visual
    st.divider()
    st.subheader("Exportar Inventário")
    
    # Converte todos os dispositivos para dicionários (formato para exportação)
    lista_dicts = [d.to_dict() for d in inv.list_devices()]
    
    # Verifica se o inventário está vazio
    if not lista_dicts:
        st.warning("Inventário vazio.")
    else:
        # Cria um DataFrame (tabela) do pandas com os dados
        df = pd.DataFrame(lista_dicts)

        # Botão para download do inventário em formato JSON
        st.download_button(
            label="📄 Download JSON", 
            data=json.dumps(lista_dicts, indent=2, ensure_ascii=False), 
            file_name="inventario.json", 
            mime="application/json",
            key="btn_json"
        )

        # Botão para download do inventário em formato CSV (compatível com Excel)
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name="inventario.csv",
            mime="text/csv",
            key="btn_csv"
        )

        # Botão para download do inventário em formato Excel (.xlsx)
        buffer = BytesIO()  # Cria um buffer em memória
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dispositivos')
        
        st.download_button(
            label="📗 Download Excel",
            data=buffer.getvalue(),
            file_name="inventario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_excel"
        )

        # Botão para download de relatório em PDF
        try:
            pdf_data = gerar_pdf(inv.list_devices())
            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name="relatorio_oficial.pdf",
                mime="application/pdf",
                key="btn_pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

# ==================================================
# ÁREA PRINCIPAL: CABEÇALHO E INTRODUÇÃO
# ==================================================

# Título principal da aplicação
st.title("🌐 Network Manager Pro")
st.markdown("---")

# Texto introdutório explicativo sobre a aplicação
st.markdown("""
### Bem-vindo ao Sistema de Gestão de Inventário de Rede

Esta plataforma permite gerir de forma eficiente todos os equipamentos de rede da organização.

**Funcionalidades principais:**
- Adicionar, editar e remover dispositivos (Routers, Switches, Access Points, Endpoints)
- Consultar e filtrar equipamentos por diversos critérios
- Monitorizar tráfego de rede dos endpoints
- Gerir ligações entre dispositivos
- Exportar dados em múltiplos formatos (JSON, CSV, Excel, PDF)

**Como usar:**
1. Utilize a aba **Gestão** para adicionar ou modificar dispositivos
2. Use **Consultas** para pesquisas avançadas
3. Monitorize consumos na aba **Tráfego**
4. Configure conexões em **Ligações**

Contamos com a colaboração de todos para manter o inventário correto!
""")

# ==================================================
# TABS PRINCIPAIS
# ==================================================

# --- 1. TAB GESTÃO ---

# Cria as 4 abas principais da aplicação
tab_gestao, tab_consultas, tab_trafego, tab_ligacoes = st.tabs(["Gestão", "Consultas", "Tráfego", "Ligações"])

# TAB GESTÃO: Para adicionar, editar e listar dispositivos
with tab_gestao:
    # Divide a aba em 2 colunas: formulário à esquerda, lista à direita
    col_add, col_list = st.columns([1, 2])
    
    # Verifica se estamos em modo de edição ou adição
    is_editing = st.session_state.editing_device is not None
    dev_edit = st.session_state.editing_device
    acao_btn = "Atualizar" if is_editing else "Adicionar"  # Muda o texto do botão

    # COLUNA DA ESQUERDA: Formulário para adicionar/editar dispositivos
    with col_add:
        st.subheader("Dispositivo")
        
        # Campo para selecionar o tipo de dispositivo (desabilitado em modo edição)
        tipo = st.selectbox("Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"], disabled=is_editing, key="add_tipo_select")
        
        # Campos comuns a todos os tipos de dispositivos
        nome = st.text_input("Nome Único", key="add_nome_input").strip()
        modelo = st.text_input("Modelo", key="add_modelo_input")
        rack = st.selectbox("Bastidor (1-6)", [1, 2, 3, 4, 5, 6], key="add_rack_select")
        ser_sel = st.selectbox("Interface Serial?", ["Não", "Sim"], key="add_serial_select")
        saude = st.selectbox("Estado de Conservação", ["Funcional", "Com Defeito", "Avariado"], key="add_saude_select")
        
        # Campo de descrição de defeito só aparece se o estado for "Com Defeito"
        defeito_desc = st.text_input("Descreva o Defeito", key="add_defeito_input") if saude == "Com Defeito" else ""
        obs = st.text_area("Observações Gerais", key="add_obs_input")

        def process_update(new_obj):
            """
            Processa a adição ou atualização de um dispositivo.
            
            Se estamos em modo edição, remove o dispositivo antigo primeiro.
            Depois adiciona o novo dispositivo ao inventário.
            """
            if is_editing:
                # Remove o dispositivo antigo
                inv.remove_device(dev_edit.name)
                log_event(f"EDITADO: {dev_edit.name} (Novo Bastidor: {rack})")
            else: 
                # Regista a criação de um novo dispositivo
                log_event(f"CRIADO: {nome} no Bastidor {rack}")
            
            # Adiciona o dispositivo (novo ou editado) ao inventário
            inv.add_device(new_obj)
            # Sai do modo de edição
            st.session_state.editing_device = None
            # Limpa o formulário e reinicia a página
            limpar_form()
            st.rerun()

        # Dicionário com os parâmetros comuns a todos os dispositivos
        common = {
            "model": modelo, 
            "serial_interface": (ser_sel == "Sim"), 
            "observations": obs, 
            "condition": saude, 
            "defect_description": defeito_desc, 
            "rack": rack
        }
        
        # Campos e botões específicos para cada tipo de dispositivo
        if tipo == "ROUTER":
            # Campos específicos do Router
            ipv4 = st.text_input("IPv4", key="add_ip_router")
            mac = st.text_input("MAC", key="add_mac_router")
            if st.button(f"{acao_btn} Router"): 
                process_update(Router(nome, ipv4, "", mac, **common))
        
        elif tipo == "SWITCH":
            # Campos específicos do Switch
            p = st.number_input("Portas", 1, 48, 24, key="add_ports_sw")
            g = st.slider("Gigabit", 0, p, key="add_giga_sw")
            f = st.slider("Fast", 0, p, key="add_fast_sw")
            mac = st.text_input("MAC", key="add_mac_sw")
            if st.button(f"{acao_btn} Switch"): 
                process_update(Switch(nome, "", mac, p, p-g-f, f, g, **common))
        
        elif tipo == "AP":
            # Campos específicos do Access Point
            ssid = st.text_input("SSID", key="add_ssid_ap")
            if st.button(f"{acao_btn} AP"): 
                process_update(AccessPoint(nome, ssid, **common))
        
        elif tipo == "ENDPOINT":
            # Campos específicos do Endpoint
            u = st.text_input("User ID", key="add_uid_ep")
            ip = st.text_input("IPv4", key="add_ip_ep")
            m = st.text_input("MAC", key="add_mac_ep")
            if st.button(f"{acao_btn} Endpoint"): 
                process_update(Endpoint(nome, u, ip, "", m, **common))
        
        # Botão de cancelar só aparece em modo edição
        if is_editing: 
            st.button("Cancelar", on_click=click_cancelar)

    # COLUNA DA DIREITA: Lista de dispositivos existentes
    with col_list:
        st.subheader("Lista do Inventário")
        
        # Obtém todos os dispositivos e separa-os por tipo
        devices = inv.list_devices()
        r = [d for d in devices if d.device_type=="ROUTER"]      # Lista de routers
        s = [d for d in devices if d.device_type=="SWITCH"]      # Lista de switches
        o = [d for d in devices if d.device_type not in ["ROUTER", "SWITCH"]]  # Outros (AP e Endpoints)
        
        # Cria sub-abas para organizar por tipo
        t_r, t_s, t_o, t_all = st.tabs([
            f"Routers ({len(r)})", 
            f"Switches ({len(s)})", 
            f"Outros ({len(o)})", 
            f"Todos ({len(devices)})"
        ])

        def render_lista(lista, prefix):
            """
            Renderiza uma lista de dispositivos com expansores.
            
            Cada dispositivo aparece num expander com botões de editar e eliminar.
            O ícone colorido indica o estado: 🟢 Funcional, 🟠 Com Defeito, 🔴 Avariado
            """
            # Se a lista estiver vazia, mostra mensagem informativa
            if not lista: 
                st.info("Vazio.")
            
            # Percorre cada dispositivo da lista
            for d in lista:
                # Obtém o estado e o bastidor
                cond = getattr(d, 'condition', 'Funcional')
                rk = getattr(d, 'rack', 1)
                
                # Cria o cabeçalho com ícone colorido conforme o estado
                header = f"{d.name} | Bastidor {rk}"
                if cond == "Avariado": 
                    header += " 🔴"  # Vermelho para avariado
                elif cond == "Com Defeito": 
                    header += " 🟠"  # Laranja para com defeito
                else: 
                    header += " 🟢"  # Verde para funcional
                
                # Cria um expander (caixa expansível) para cada dispositivo
                with st.expander(header):
                    # Mostra informações detalhadas
                    st.write(f"**Estado:** {cond} | **Bastidor:** {rk} | **Modelo:** {d.model}")
                    st.write(f"**Serial:** {'Sim' if getattr(d, 'serial_interface', False) else 'Não'} | **MAC:** {getattr(d, 'mac_address', 'N/A')} | **IP:** {getattr(d, 'ipv4', 'N/A')}")
                    st.info(f"**OBS.:** {d.observations if d.observations else 'Sem observações.'}")
                    
                    # Cria 2 colunas para os botões de editar e eliminar
                    c1, c2 = st.columns(2)
                    
                    # Botão Editar
                    c1.button("Editar", key=f"{prefix}_ed_{d.name}", on_click=click_editar, args=(d,))
                    
                    # Botão Eliminar
                    if c2.button("Eliminar", key=f"{prefix}_el_{d.name}"):
                        log_event(f"ELIMINADO: {d.name} do Bastidor {rk}")
                        inv.remove_device(d.name)
                        st.rerun()  # Reinicia para atualizar a lista

        # Renderiza cada lista na sua respetiva sub-aba
        with t_r: render_lista(r, "r")
        with t_s: render_lista(s, "s")
        with t_o: render_lista(o, "o")
        with t_all: render_lista(devices, "t")

        # Legenda explicativa dos ícones
        st.write("")
        st.caption("💡 **Legenda de Estados:** 🟢 Funcional | 🟠 Com Defeito | 🔴 Avariado")

# --- 2. TAB CONSULTAS ---

# TAB CONSULTAS: Para pesquisas avançadas com múltiplos filtros
with tab_consultas:
    st.subheader("Pesquisa Avançada")
    
    # Primeira linha de filtros: Nome, Tipo, Bastidor
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    with r1_c1: 
        search_n = st.text_input("Filtrar por Nome", key="q_n")
    with r1_c2: 
        search_t = st.selectbox("Filtrar por Tipo", ["Todos", "ROUTER", "SWITCH", "AP", "ENDPOINT"], key="q_t")
    with r1_c3: 
        search_rk = st.selectbox("Filtrar por Bastidor", ["Todos", 1, 2, 3, 4, 5, 6], key="q_rk")

    # Segunda linha de filtros: Estado, Serial, MAC, IP
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1: 
        search_cond = st.selectbox("Filtrar por Estado", ["Todos", "Funcional", "Com Defeito", "Avariado"], key="q_cd")
    with r2_c2: 
        search_ser = st.selectbox("Interface Serial?", ["Todos", "Sim", "Não"], key="q_ser")
    with r2_c3: 
        search_mac = st.text_input("Filtrar por MAC", key="q_mac")
    with r2_c4: 
        search_ip = st.text_input("Filtrar por IP", key="q_ip")

    # Botão para executar a pesquisa
    if st.button("Executar Pesquisa", use_container_width=True):
        # Começa com todos os dispositivos
        res = inv.list_devices()
        
        # Aplica cada filtro sequencialmente (apenas se o filtro foi preenchido)
        if search_n: 
            res = [d for d in res if search_n.lower() in d.name.lower()]
        if search_t != "Todos": 
            res = [d for d in res if d.device_type == search_t]
        if search_rk != "Todos": 
            res = [d for d in res if getattr(d, 'rack', 1) == search_rk]
        if search_cond != "Todos": 
            res = [d for d in res if getattr(d, 'condition', 'Funcional') == search_cond]
        if search_ser != "Todos": 
            res = [d for d in res if getattr(d, 'serial_interface', False) == (search_ser == "Sim")]
        if search_mac: 
            res = [d for d in res if search_mac.lower() in getattr(d, 'mac_address', '').lower()]
        if search_ip: 
            res = [d for d in res if search_ip in getattr(d, 'ipv4', '')]

        # Mostra os resultados
        if not res: 
            st.warning("Nenhum dispositivo encontrado.")
        
        # Mostra cada resultado num expander
        for r_res in res:
            header_q = f"{r_res.name} | Bastidor {getattr(r_res, 'rack', 1)}"
            
            # Adiciona ícone colorido conforme o estado
            c_saude = getattr(r_res, 'condition', 'Funcional')
            if c_saude == "Avariado": 
                header_q += " 🔴"
            elif c_saude == "Com Defeito": 
                header_q += " 🟠"
            else: 
                header_q += " 🟢"

            # Mostra informações do dispositivo encontrado
            with st.expander(header_q):
                st.write(f"**Tipo:** {r_res.device_type} | **Estado:** {c_saude} | **Modelo:** {r_res.model}")
                st.write(f"**MAC:** {getattr(r_res, 'mac_address', 'N/A')} | **IP:** {getattr(r_res, 'ipv4', 'N/A')}")
                st.info(f"**OBS.:** {r_res.observations if r_res.observations else 'N/A'}")

# --- 3. TAB TRÁFEGO ---

# TAB TRÁFEGO: Para monitorizar o consumo de dados dos endpoints
with tab_trafego:
    # Filtra apenas os dispositivos do tipo Endpoint
    eps = [d for d in inv.list_devices() if isinstance(d, Endpoint)]
    
    # Verifica se existem endpoints
    if not eps: 
        st.info("Adicione Endpoints na Gestão para monitorizar o tráfego.")
    else:
        # Permite selecionar qual endpoint monitorizar
        target = st.selectbox("Endpoint", [e.name for e in eps], key="traffic_target_select")
        ep_obj = inv.get_endpoint(target)
        
        # Campos para atualizar o tráfego (upload e download em MB)
        up = st.number_input("Upload (MB)", value=float(ep_obj.traffic_up_mb), key="input_traffic_up")
        down = st.number_input("Download (MB)", value=float(ep_obj.traffic_down_mb), key="input_traffic_down")
        
        # Botão para guardar as alterações
        if st.button("Atualizar Consumo"):
            ep_obj.traffic_up_mb = up
            ep_obj.traffic_down_mb = down
            st.rerun()  # Reinicia para mostrar os valores atualizados
        
        # Gráfico de barras mostrando o tráfego total (upload + download) de todos os endpoints
        st.bar_chart({e.name: e.traffic_up_mb + e.traffic_down_mb for e in eps})

# --- 4. TAB LIGAÇÕES ---

# TAB LIGAÇÕES: Para gerir conexões entre dispositivos
with tab_ligacoes:
    # Filtra dispositivos que podem ter conexões (Routers e Switches)
    hosts = [d for d in inv.list_devices() if hasattr(d, "connected_devices") or hasattr(d, "connected_endpoints")]
    
    # Verifica se existem dispositivos que possam estabelecer ligações
    if not hosts:
        st.info("Crie Routers ou Switches para estabelecer ligações.")
    else:
        # Seleciona o equipamento base (onde vamos gerir as ligações)
        h_name = st.selectbox("Equipamento Base", [h.name for h in hosts], key="host_link_select")
        h_obj = inv.devices.get(h_name)
        
        # Divide em 2 colunas: ligar dispositivos e desligar dispositivos
        c1, c2 = st.columns(2)
        
        # COLUNA 1: Ligar novos dispositivos
        with c1:
            # Seleciona qual dispositivo conectar (excluindo o próprio)
            target = st.selectbox("Ligar a:", [d.name for d in inv.list_devices() if d.name != h_name], key="target_link_select")
            
            # Botão para estabelecer a ligação
            if st.button("Ligar"):
                try:
                    # Verifica qual método usar (connect_device ou connect_endpoint)
                    if hasattr(h_obj, "connect_device"): 
                        h_obj.connect_device(target)
                    else: 
                        h_obj.connect_endpoint(target)
                    st.rerun()  # Reinicia para mostrar a nova ligação
                except Exception as e: 
                    st.error(e)  # Mostra erro se a ligação falhar
        
        # COLUNA 2: Desligar dispositivos conectados
        with c2:
            # Obtém a lista de dispositivos conectados
            cons = getattr(h_obj, "connected_devices", []) or getattr(h_obj, "connected_endpoints", [])
            
            # Cria um botão para desligar cada dispositivo conectado
            for c in cons:
                if st.button(f"Desligar {c}", key=f"dis_{h_name}_{c}"):
                    # Verifica qual método usar para desconectar
                    if hasattr(h_obj, "disconnect_device"): 
                        h_obj.disconnect_device(c)
                    else: 
                        h_obj.disconnect_endpoint(c)
                    st.rerun()  # Reinicia para atualizar a lista
