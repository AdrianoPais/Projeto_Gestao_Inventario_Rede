import streamlit as st
import json
import os
from inventory import NetworkInventory
from devices import Router, Switch, AccessPoint, Endpoint
from storage import save_to_json, load_from_json

# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(page_title="Network Manager Pro", layout="wide")

# --- INICIALIZAÇÃO DO INVENTÁRIO (SESSION STATE) ---
if 'inv' not in st.session_state:
    if os.path.exists("inventario.json"):
        try:
            st.session_state.inv = load_from_json("inventario.json")
        except:
            st.session_state.inv = NetworkInventory()
    else:
        st.session_state.inv = NetworkInventory()

inv = st.session_state.inv

# ==================================================
# SIDEBAR: GESTÃO DE DADOS E DOWNLOADS
# ==================================================
with st.sidebar:
    st.title("Gestão de Dados")
    
    if st.button("Guardar no Servidor"):
        save_to_json(inv, "inventario.json")
        st.success("Dados guardados no servidor.")
    
    if st.button("Recarregar do Ficheiro"):
        st.session_state.inv = load_from_json("inventario.json")
        st.rerun()
    
    st.divider()
    
    st.subheader("Download Local")
    inventory_data = [d.to_dict() for d in inv.list_devices()]
    json_string = json.dumps(inventory_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="Descarregar inventario.json",
        data=json_string,
        file_name="inventario.json",
        mime="application/json"
    )

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

# --- 1. TAB GESTÃO (Adicionar, Remover, Listar) ---
with tab_gestao:
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.subheader("Novo Dispositivo")
        tipo = st.selectbox("Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"])
        nome = st.text_input("Nome Unico (Ex: R1, SW1, EP1)").strip()
        
        # Novo campo de Modelo para todos os tipos
        modelo = st.text_input("Modelo (Ex: 2911, Catalyst, 2960)")
        
        # Campo de Observações comum a todos
        obs = st.text_area("Observacoes ou Defeitos", help="Registe aqui notas tecnicas ou avarias.")

        if tipo == "ROUTER":
            ipv4 = st.text_input("IPv4 (Opcional)")
            mac = st.text_input("MAC (Router)")
            if st.button("Adicionar Router"):
                try:
                    inv.add_device(Router(nome, ipv4, "", mac, model=modelo, observations=obs))
                    st.success(f"Router '{nome}' adicionado.")
                    st.rerun()
                except ValueError as e: st.error(f"Erro: {e}")

        elif tipo == "SWITCH":
            total_p = st.number_input("Nº Total de Portas", 1, 48, 24)
            
            st.write("Distribuição de Velocidade:")
            # Slider para Gigabit
            giga_p = st.slider("Portas GigabitEthernet (1000Mbps)", 0, total_p, 0)
            
            # Slider para Fast limitado pela sobra
            sobra_fast = total_p - giga_p
            fast_p = st.slider("Portas FastEthernet (100Mbps)", 0, sobra_fast, sobra_fast)
            
            # Resto são Ethernet
            eth_p = total_p - giga_p - fast_p
            st.info(f"Portas Ethernet (10Mbps) restantes: {eth_p}")
            
            mac = st.text_input("MAC (Switch)")
            if st.button("Adicionar Switch"):
                try:
                    inv.add_device(Switch(
                        nome, "", mac, total_p, 
                        eth_ports=eth_p, fast_eth_ports=fast_p, giga_eth_ports=giga_p,
                        model=modelo, observations=obs
                    ))
                    st.success(f"Switch '{nome}' adicionado.")
                    st.rerun()
                except ValueError as e: st.error(f"Erro: {e}")

        elif tipo == "AP":
            ssid = st.text_input("SSID da Rede")
            if st.button("Adicionar AP"):
                try:
                    inv.add_device(AccessPoint(nome, ssid, model=modelo, observations=obs))
                    st.success(f"AP '{nome}' adicionado.")
                    st.rerun()
                except ValueError as e: st.error(f"Erro: {e}")

        elif tipo == "ENDPOINT":
            uid = st.text_input("User ID")
            ipv4 = st.text_input("IPv4 (Opcional)")
            mac = st.text_input("MAC (Endpoint)")
            if st.button("Adicionar Endpoint"):
                try:
                    inv.add_device(Endpoint(nome, uid, ipv4, "", mac, model=modelo, observations=obs))
                    st.success(f"Endpoint '{nome}' adicionado.")
                    st.rerun()
                except ValueError as e: st.error(f"Erro: {e}")

    with col_list:
        st.subheader("Lista de Inventario")
        devices = inv.list_devices()
        if not devices:
            st.info("O inventario esta vazio.")
        else:
            for d in devices:
                with st.expander(f"{d.name} ({d.device_type}) - {d.status}"):
                    # Mostrar Modelo
                    if hasattr(d, "model") and d.model:
                        st.write(f"**Modelo:** {d.model}")
                    
                    st.text(str(d))
                    
                    # Mostrar Observações
                    if hasattr(d, "observations") and d.observations:
                        st.warning(f"Notas: {d.observations}")
                    
                    if st.button("Eliminar Dispositivo", key=f"del_{d.name}"):
                        inv.remove_device(d.name)
                        st.rerun()

# --- 2. TAB CONSULTAS ---
with tab_consultas:
    st.subheader("Ferramentas de Pesquisa")
    c1, c2, c3, c4 = st.columns(4) 
    
    with c1:
        st.markdown("**Por IPv4**")
        search_ip = st.text_input("Introduzir IP")
        if st.button("Pesquisar IP"):
            res = inv.find_by_ipv4(search_ip)
            if res: st.code(str(res))
            else: st.warning("Não encontrado.")

    with c2:
        st.markdown("**Por Tipo**")
        search_t = st.selectbox("Escolher Tipo", ["ROUTER", "SWITCH", "AP", "ENDPOINT"], key="stype")
        if st.button("Filtrar Tipo"):
            results = inv.find_by_type(search_t)
            for r in results: st.text(str(r))

    with c3:
        st.markdown("**Por Estado**")
        search_s = st.selectbox("Estado", ["ACTIVE", "INACTIVE"], key="sstatus")
        if st.button("Filtrar Estado"):
            results = inv.find_by_status(search_s)
            for r in results: st.text(str(r))
                
    with c4:
        st.markdown("**Conectividade**")
        st.write("Ver anfitrioes com carga.")
        if st.button("Listar Conectados"):
            results = [
                d for d in inv.list_devices() 
                if len(getattr(d, "connected_devices", [])) > 0 or 
                   len(getattr(d, "connected_endpoints", [])) > 0
            ]
            if not results:
                st.info("Sem ligacoes ativas.")
            else:
                for r in results:
                    n = len(getattr(r, "connected_devices", [])) or len(getattr(r, "connected_endpoints", []))
                    st.write(f"{r.name} ({r.device_type}): {n} ligacoes")

# --- 3. TAB TRÁFEGO ---
with tab_trafego:
    st.subheader("Estatisticas de Endpoints")
    col_up, col_pol = st.columns(2)
    
    endpoints = [d for d in inv.list_devices() if isinstance(d, Endpoint)]

    with col_up:
        st.markdown("### Atualizar Consumo")
        if endpoints:
            target = st.selectbox("Dispositivo", [e.name for e in endpoints])
            ep_obj = inv.get_endpoint(target)
            
            up_val = st.number_input("Novo Upload (MB)", min_value=0.0, value=float(ep_obj.traffic_up_mb))
            down_val = st.number_input("Novo Download (MB)", min_value=0.0, value=float(ep_obj.traffic_down_mb))
            
            if st.button("Confirmar Atualizacao"):
                if ep_obj:
                    ep_obj.traffic_up_mb = up_val
                    ep_obj.traffic_down_mb = down_val
                    st.success(f"Consumo de '{target}' atualizado.")
                    st.rerun()
        
        st.divider()
        st.markdown("### Top Consumidores")
        n_top = st.slider("Ver Top N", 1, 10, 3)
        top_list = inv.top_consumers(n_top)
        for i, t in enumerate(top_list, 1):
            total = t.traffic_up_mb + t.traffic_down_mb
            st.write(f"{i}. {t.name}: {total:.2f} MB")

    with col_pol:
        st.markdown("### Grafico de Consumo Total")
        if endpoints:
            chart_data = {e.name: (e.traffic_up_mb + e.traffic_down_mb) for e in endpoints}
            st.bar_chart(chart_data)
        else:
            st.info("Adicione Endpoints para ver graficos.")

        st.divider()
        st.markdown("### Politica de Suspensao")
        limit = st.number_input("Limite Maximo (MB)", min_value=1.0, value=100.0)
        tempo = st.number_input("Minutos de Castigo", min_value=1, value=30)
        
        if st.button("Aplicar Limites"):
            afetados = inv.apply_traffic_policy(limit, tempo)
            if afetados:
                st.warning(f"{len(afetados)} Endpoints suspensos.")
                for a in afetados: st.write(f"Suspenso: {a.name} (ate {a.suspended_until})")
            else:
                st.success("Tudo dentro dos limites.")

# --- 4. TAB LIGAÇÕES ---
with tab_ligacoes:
    st.subheader("Cablagem e Conectividade")
    hosts = [d for d in inv.list_devices() if d.device_type in ["ROUTER", "SWITCH"]]
    
    if not hosts:
        st.info("Necessita de um Router ou Switch para gerir ligacoes.")
    else:
        col_con, col_view = st.columns(2)
        with col_con:
            st.markdown("### Criar Ligacao")
            h_name = st.selectbox("Anfitriao", [h.name for h in hosts])
            others = [d.name for d in inv.list_devices() if d.name != h_name]
            t_name = st.selectbox("Dispositivo Remoto", others)
            
            if st.button("Ligar"):
                h_obj = inv.devices.get(h_name)
                try:
                    h_obj.connect_device(t_name)
                    st.success("Ligacao efetuada.")
                    st.rerun()
                except ValueError as e: st.error(e)

        with col_view:
            st.markdown("### Mapa de Portas")
            view_h = st.selectbox("Verificar:", [h.name for h in hosts], key="view_con")
            h_obj = inv.devices.get(view_h)
            cons = getattr(h_obj, "connected_devices", [])
            
            if not cons:
                st.write("Sem dispositivos ligados.")
            else:
                for c in cons:
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"Ligacao: {c}")
                    if c2.button("Desligar", key=f"dis_{view_h}_{c}"):
                        h_obj.disconnect_device(c)
                        st.rerun()
