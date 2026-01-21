import streamlit as st
from inventory import NetworkInventory
from devices import Router, Switch, AccessPoint, Endpoint
from storage import save_to_json, load_from_json
import os

# Configuração inicial
st.set_page_config(page_title="Network Manager Pro", layout="wide")

# --- INICIALIZAÇÃO DO INVENTÁRIO (SESSION STATE) ---
if 'inv' not in st.session_state:
    if os.path.exists("inventario.json"):
        st.session_state.inv = load_from_json("inventario.json")
    else:
        st.session_state.inv = NetworkInventory()

inv = st.session_state.inv

# --- SIDEBAR: GESTÃO DE DADOS ---
with st.sidebar:
    st.title("Save / Load Inventário")
    if st.button("Guardar no Ficheiro JSON"):
        save_to_json(inv, "inventario.json")
        st.success("Dados guardados!")
    
    if st.button("Recarregar do Ficheiro"):
        st.session_state.inv = load_from_json("inventario.json")
        st.rerun()

st.title("Gestão de Inventário de Rede")

# Definição dos Separadores baseados no teu main.py
tab_gestao, tab_consultas, tab_trafego = st.tabs([
    "Gestão", 
    "Consultas", 
    "Tráfego e Políticas"
])

# --- 1. TAB GESTÃO (Adicionar, Remover, Listar) ---
with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.subheader("Adicionar Dispositivo")
        tipo = st.selectbox("Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"])
        nome = st.text_input("Nome Único (Exemplo: R1, SW1, AP1, EP1)")
        
        # Campos dinâmicos baseados no construtor de cada classe
        if tipo == "ROUTER":
            ipv4 = st.text_input("IPv4 (Router)")
            mac = st.text_input("MAC (Router)")
            if st.button("Adicionar Router"):
                try:
                    inv.add_device(Router(nome, ipv4, "", mac))
                    st.success("Router adicionado com sucesso!")
                    st.rerun()
                except ValueError as e: st.error(e)

        elif tipo == "SWITCH":
            ports = st.number_input("Portas", 1, 48, 24)
            mac = st.text_input("MAC (Switch)")
            if st.button("Adicionar Switch"):
                try:
                    inv.add_device(Switch(nome, "", mac, ports))
                    st.success("Switch adicionado com sucesso!")
                    st.rerun()
                except ValueError as e: st.error(e)

        elif tipo == "AP":
            ssid = st.text_input("SSID")
            if st.button("Adicionar AP"):
                try:
                    inv.add_device(AccessPoint(nome, ssid))
                    st.success("AP adicionado com sucesso!")
                    st.rerun()
                except ValueError as e: st.error(e)

        elif tipo == "ENDPOINT":
            uid = st.text_input("User ID")
            ipv4 = st.text_input("IPv4 (Endpoint)")
            mac = st.text_input("MAC (Endpoint)")
            if st.button("Adicionar Endpoint"):
                try:
                    inv.add_device(Endpoint(nome, uid, ipv4, "", mac))
                    st.success("Endpoint adicionado com sucesso!")
                    st.rerun()
                except ValueError as e: st.error(e)

    with col_list:
        st.subheader("Lista de Dispositivos")
        devices = inv.list_devices()
        if not devices:
            st.info("Inventário vazio.")
        else:
            for d in devices:
                with st.expander(f"{d.name} ({d.device_type})"):
                    st.text(str(d))
                    if st.button("Eliminar", key=f"del_{d.name}"):
                        inv.remove_device(d.name)
                        st.rerun()

# --- 2. TAB CONSULTAS (Pesquisa por IP, Tipo, Estado) ---
with tab_consultas:
    st.subheader("Ferramentas de Pesquisa")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("**Por IPv4**")
        search_ip = st.text_input("Introduzir IP")
        if st.button("Pesquisar IP"):
            res = inv.find_by_ipv4(search_ip)
            if res: st.write(res)
            else: st.warning("Não encontrado.")

    with c2:
        st.markdown("**Por Tipo**")
        search_t = st.selectbox("Escolher Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"], key="stype")
        if st.button("Listar por Tipo"):
            results = inv.find_by_type(search_t)
            for r in results: st.write(r)

    with c3:
        st.markdown("**Por Estado**")
        search_s = st.selectbox("Estado", ["ACTIVE", "INACTIVE"])
        if st.button("Listar por Estado"):
            results = inv.find_by_status(search_s)
            for r in results: st.write(r)

# --- 3. TAB TRÁFEGO (Atualizar, Top Consumidores, Políticas) ---
with tab_trafego:
    st.subheader("Gestão de Tráfego de Endpoints")
    
    col_up, col_pol = st.columns(2)
    
    with col_up:
        st.markdown("### Atualizar Consumo")
        # Filtra apenas os nomes que são efetivamente Endpoints
        eps = [d.name for d in inv.list_devices() if isinstance(d, Endpoint)]
        
        if eps:
            target = st.selectbox("Selecionar dispositivo", eps)
            
            # Vamos buscar o objeto atual para mostrar os valores que já lá estão
            ep_obj = inv.get_endpoint(target)
            
            # Usamos o valor atual como 'value' padrão para o utilizador ver o que está lá
            up_val = st.number_input("Novo Upload (MB)", min_value=0.0, value=float(ep_obj.traffic_up_mb))
            down_val = st.number_input("Novo Download (MB)", min_value=0.0, value=float(ep_obj.traffic_down_mb))
            
            if st.button("Atualizar Tráfego"):
                if ep_obj is not None:
                    # Em vez de chamarmos o método .add_traffic() (que soma),
                    # atribuímos os valores diretamente para atualizar.
                    ep_obj.traffic_up_mb = up_val
                    ep_obj.traffic_down_mb = down_val
                    
                    st.success(f"Valores de tráfego de '{target}' atualizados com sucesso!")
                    st.rerun() # Atualiza a interface e o gráfico de Top Consumidores
                else:
                    st.error("Erro: Dispositivo não encontrado.")
        else:
            st.info("Adicione Endpoints na aba de Gestão para monitorizar tráfego.")
        
        st.markdown("---")
        st.markdown("### Top Consumidores")
        n_top = st.slider("Mostrar quantos?", 1, 10, 3)
        tops = inv.top_consumers(n_top)
        for i, t in enumerate(tops, 1):
            st.write(f"{i}. {t.name}: {t.traffic_up_mb + t.traffic_down_mb:.2f} MB")

    with col_pol:
        st.markdown("### Aplicar Política de Tráfego")
        limit = st.number_input("Limite Máximo (MB)", min_value=1.0, value=100.0)
        tempo = st.number_input("Minutos de Suspensão", min_value=1, value=30)
        
        if st.button("Executar Verificação de Limites"):
            afetados = inv.apply_traffic_policy(limit, tempo)
            if afetados:
                st.warning(f"{len(afetados)} dispositivos suspensos por excederem o limite!")
                for a in afetados:
                    st.write(f"- {a.name} (Até: {a.suspended_until})")
            else:
                st.success("Nenhum dispositivo excede o limite atual.")