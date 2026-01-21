# Nome 1: Daniel Santos
# Nome 2: Sérgio Correia
# Nome 3: Tiago Costa
# Turma: GRSC0925
# Trabalho: Projeto Final UC00608 - Programação Alocada a Objetos (Em Python)
# DESCRIÇÃO DO PROGRAMA:
    # Este programa implementa um gestor de inventário de rede que permite:
    # - Adicionar, remover e listar dispositivos de rede (Router, Switch, AP, Endpoint)
    # - Pesquisar dispositivos por IPv4, tipo ou estado
    # - Monitorizar tráfego de endpoints (upload/download)
    # - Aplicar políticas de controlo de tráfego
    # - Guardar e carregar dados em ficheiro JSON para persistência

# ARQUITETURA:
    # - inventory.py: Classe NetworkInventory que gerencia a coleção de dispositivos
    # - devices.py: Classes para cada tipo de dispositivo (Router, Switch, AP, Endpoint)
    # - storage.py: Funções para serializar/deserializar dados em JSON
    # - utils.py: Funções auxiliares de input validado

# ======================== IMPORTAÇÕES ========================
# Importa a classe NetworkInventory que gerencia toda a coleção de dispositivos
from inventory import NetworkInventory

# Importa as classes dos diferentes tipos de dispositivos de rede
from devices import Router, Switch, AccessPoint, Endpoint

# Importa funções auxiliares para leitura de inputs validados e pausas
from utils import input_int, input_float, pause

# Importa funções para persistência de dados em formato JSON
from storage import save_to_json, load_from_json

# ======================== CONSTANTES ========================
# Nome do ficheiro de base de dados onde o inventário é persistido
FILE_DB = "inventario.json"

# --------------------------------------------------
# FUNÇÃO: menu_categorias()
# --------------------------------------------------
# PROPÓSITO: Exibir o menu principal com as 4 categorias principais
# PARÂMETROS: Nenhum
# RETORNA: Nenhum (apenas imprime no ecrã)
# O QUE FAZ:
#   - Apresenta 4 opções principais de categorias: Gestão, Consultas, Tráfego e Dados
#   - Opção 0 permite sair do programa
# UTILIZAÇÃO: Chamada no ciclo principal do main() para permitir navegação
# --------------------------------------------------
def menu_categorias():
    print("\n1 - [ Gestão de Dispositivos ]")
    print("2 - [ Consultas ]")
    print("3 - [ Tráfego ]")
    print("4 - [ Dados ]")
    print("0 - Sair")

# --------------------------------------------------
# FUNÇÃO: submenu_gestao()
# --------------------------------------------------
# PROPÓSITO: Exibir o submenu de gestão de dispositivos
# PARÂMETROS: Nenhum
# RETORNA: Nenhum (apenas imprime no ecrã)
# O QUE FAZ:
#   - Mostra as operações CRUD básicas: Adicionar, Remover e Listar dispositivos
#   - Opção 0 volta ao menu anterior
# UTILIZAÇÃO: Chamada quando o utilizador escolhe a opção 1 no menu principal
# --------------------------------------------------
def submenu_gestao():
    print("\n[ Gestão de Dispositivos ]")
    print("1 - Adicionar dispositivo")
    print("2 - Remover dispositivo")
    print("3 - Listar todos os dispositivos")
    print("0 - Voltar")

# --------------------------------------------------
# FUNÇÃO: submenu_consultas()
# --------------------------------------------------
# PROPÓSITO: Exibir o submenu de consultas/pesquisas
# PARÂMETROS: Nenhum
# RETORNA: Nenhum (apenas imprime no ecrã)
# O QUE FAZ:
#   - Mostra as diferentes formas de pesquisar dispositivos
#   - Permite pesquisa por IPv4, por tipo de dispositivo ou por estado (ativo/inativo)
# UTILIZAÇÃO: Chamada quando o utilizador escolhe a opção 2 no menu principal
# --------------------------------------------------
def submenu_consultas():
    print("\n[ Consultas ]")
    print("1 - Pesquisar dispositivo por IPv4")
    print("2 - Procurar dispositivos por tipo")
    print("3 - Listar dispositivos por estado")
    print("0 - Voltar")

# --------------------------------------------------
# FUNÇÃO: submenu_trafego()
# --------------------------------------------------
# PROPÓSITO: Exibir o submenu de monitorização de tráfego
# PARÂMETROS: Nenhum
# RETORNA: Nenhum (apenas imprime no ecrã)
# O QUE FAZ:
#   - Mostra operações relacionadas com tráfego de dados de endpoints
#   - Permite atualizar tráfego, ver maiores consumidores e aplicar políticas de limite
# UTILIZAÇÃO: Chamada quando o utilizador escolhe a opção 3 no menu principal
# --------------------------------------------------
def submenu_trafego():
    print("\n[ Tráfego ]")
    print("1 - Atualizar tráfego de um endpoint")
    print("2 - Ver top consumidores de tráfego")
    print("3 - Aplicar política de tráfego")
    print("0 - Voltar")

# --------------------------------------------------
# FUNÇÃO: submenu_dados()
# --------------------------------------------------
# PROPÓSITO: Exibir o submenu de persistência de dados
# PARÂMETROS: Nenhum
# RETORNA: Nenhum (apenas imprime no ecrã)
# O QUE FAZ:
#   - Mostra opções para guardar e carregar dados em ficheiro JSON
#   - Permite persistência do inventário entre sessões do programa
# UTILIZAÇÃO: Chamada quando o utilizador escolhe a opção 4 no menu principal
# --------------------------------------------------
def submenu_dados():
    print("\n[ Dados ]")
    print("1 - Guardar dados")
    print("2 - Carregar dados")
    print("0 - Voltar")

# ======================== FUNÇÃO PRINCIPAL ========================
# FUNÇÃO: main()
# --------------------------------------------------
# PROPÓSITO: Ponto de entrada do programa - ciclo principal de navegação
# PARÂMETROS: Nenhum
# RETORNA: Nenhum (executa até o utilizador escolher sair)
# O QUE FAZ:
#   1. Cria uma instância da classe NetworkInventory (gestor do inventário)
#   2. Entra num ciclo infinito que mostra o menu de categorias
#   3. De acordo com a opção do utilizador, navega para diferentes submenus
#   4. Cada submenu tem o seu próprio ciclo com opções específicas
#   5. Executa as funções apropriadas (add_device, remove_device, etc.)
#   6. Sai do programa quando o utilizador escolhe a opção 0
# FLUXO:
#   - Menu Principal (categorias) → Submenus (operações) → Funções de lógica
# --------------------------------------------------
def main():
    # Cria a instância principal do inventário que armazena todos os dispositivos
    inv = NetworkInventory()

    # Ciclo principal do programa - continua até o utilizador sair
    while True:
        # Mostra o menu de categorias
        menu_categorias()
        
        # Lê a opção do utilizador (0-4)
        cat = input_int("Opção: ", 0, 4)

        # Opção 0: Sair do programa
        if cat == 0:
            print("A sair...")
            break

        # Opção 1: Gestão de Dispositivos (Adicionar, Remover, Listar)
        elif cat == 1:
            while True:
                # Mostra o submenu de gestão
                submenu_gestao()
                op = input_int("Opção: ", 0, 3)

                if op == 0:
                    break  # Volta ao menu principal
                elif op == 1:
                    add_device(inv)  # Função para adicionar dispositivo
                    pause()
                elif op == 2:
                    remove_device(inv)  # Função para remover dispositivo
                    pause()
                elif op == 3:
                    list_devices(inv)  # Função para listar todos os dispositivos
                    pause()

        # Opção 2: Consultas (Pesquisar por IPv4, Tipo, Estado)
        elif cat == 2:
            while True:
                # Mostra o submenu de consultas
                submenu_consultas()
                op = input_int("Opção: ", 0, 3)

                if op == 0:
                    break  # Volta ao menu principal
                elif op == 1:
                    search_ipv4(inv)  # Função para pesquisar por IPv4
                    pause()
                elif op == 2:
                    search_type(inv)  # Função para pesquisar por tipo de dispositivo
                    pause()
                elif op == 3:
                    list_by_status(inv)  # Função para listar por estado (ativo/inativo)
                    pause()

        # Opção 3: Tráfego (Atualizar, Ver Top Consumidores, Aplicar Política)
        elif cat == 3:
            while True:
                # Mostra o submenu de tráfego
                submenu_trafego()
                op = input_int("Opção: ", 0, 3)

                if op == 0:
                    break  # Volta ao menu principal
                elif op == 1:
                    update_endpoint_traffic(inv)  # Função para atualizar tráfego de endpoint
                    pause()
                elif op == 2:
                    top_consumers(inv)  # Função para ver top consumidores de tráfego
                    pause()
                elif op == 3:
                    apply_policy(inv)  # Função para aplicar política de tráfego
                    pause()

        # Opção 4: Dados (Guardar e Carregar Inventário)
        elif cat == 4:
            while True:
                # Mostra o submenu de dados
                submenu_dados()
                op = input_int("Opção: ", 0, 2)

                if op == 0:
                    break  # Volta ao menu principal
                elif op == 1:
                    do_save(inv)  # Função para guardar inventário em ficheiro JSON
                    pause()
                elif op == 2:
                    do_load(inv)  # Função para carregar inventário do ficheiro JSON
                    pause()

# --------------------------------------------------
# Funções de lógica
# --------------------------------------------------

def add_device(inv: NetworkInventory):
    print("\n--- Adicionar dispositivo ---")
    print("Tipos: 1-ROUTER  2-SWITCH  3-AP  4-ENDPOINT")

    # Pede dados ao utilizador e busca o objeto correto (Router, Switch, etc)
    # Usa try/except para capturar erros de validação, como IPs inválidos

    opt = input_int("Escolha o tipo: ", 1, 4)

    try:
        if opt == 1:  # Router
            name = input("Nome: ").strip() # Inserir o nome que queremos dar ao Router
            ipv4 = input("IPv4 (Exemplo: 192.168.0.254): ").strip() # Inserir o IPv4
            ipv6 = input("IPv6 (Clicar ENTER para deixar vazio): ").strip()
            mac = input("MAC (Exemplo: AA:BB:CC:DD:EE:FF): ").strip()
            device = Router(name, ipv4, ipv6, mac)

        elif opt == 2: # Switch
            name = input("Nome: ").strip() # Inserir o nome que queremos dar ao Switch
            ipv4 = input("IPv4 (ENTER para vazio): ").strip() # Inserir o IPv4, opional
            mac = input("MAC (Exemplo: AA:BB:CC:DD:EE:FF): ").strip()
            ports = input_int("Nº de portas: ", 1, 9999) # Número de ports do Switch, até um máximo de 9999
            device = Switch(name, ipv4, mac, ports)

        elif opt == 3: # AP
            name = input("Nome: ").strip() # Inserir o nome que queremos dar ao AP
            ssid = input("SSID (Exemplo: ATEC_WiFi): ").strip() # Inserir o service set identifier
            device = AccessPoint(name, ssid)

        else: # Endpoint Device
            name = input("Nome: ").strip() # Inserir o nome que queremos dar ao endpoint device
            user_id = input("User ID (Exemplo: t0132000): ").strip() #
            ipv4 = input("IPv4: ").strip() # Inserir o IPv4
            ipv6 = input("IPv6 (Clicar ENTER para vazio): ").strip() # Inserir o IPv6, opcional
            mac = input("MAC (Exemplo: AA:BB:CC:DD:EE:FF): ").strip()
            device = Endpoint(name, user_id, ipv4, ipv6, mac)

        inv.add_device(device)
        print("Dispositivo adicionado com sucesso.")

    except ValueError as e:
        print(f"Erro: {e}")

def remove_device(inv: NetworkInventory):
    # Função para ir buscar todos os dispositivos criados até agora
    print("\n--- Remover dispositivo ---")
    name = input("Nome do dispositivo a remover: ").strip() # Inserir nome do Dispositivo a remover

    if inv.remove_device(name):
        print("Dispositivo removido.")
    else:
        print("Dispositivo não encontrado.")

def list_devices(inv: NetworkInventory):
    # Função para ir buscar todos os dispositivos criados até agora
    print("\n--- Lista de dispositivos ---")
    for d in inv.list_devices():
        print(d)

def search_ipv4(inv: NetworkInventory):
    # Pesquisa pelo dispositivo especifico pelo IPv4
    ipv4 = input("IPv4: ").strip()
    d = inv.find_by_ipv4(ipv4)
    print(d if d else "Dispositivo não encontrado.")

def search_type(inv: NetworkInventory):
    # Pesquisa pelo tipo de dispositivo
    t = input("Tipo: ").strip().upper()
    for d in inv.find_by_type(t):
        print(d)

def list_by_status(inv: NetworkInventory):
    # Lista pelo estado atual (Inativo ou Ativo)
    s = input("Estado: ").strip().upper()
    for d in inv.find_by_status(s):
        print(d)

def update_endpoint_traffic(inv: NetworkInventory):
    name = input("Nome do endpoint: ").strip()
    ep = inv.get_endpoint(name)
    if not ep:
        print("Endpoint não encontrado.")
        return

    up = input_float("Tráfego upload: ", 0)
    down = input_float("Tráfego download: ", 0)
    ep.add_traffic(up, down)
    print("Tráfego atualizado.")

def top_consumers(inv: NetworkInventory):
    n = input_int("Quantos quer ver? ", 1)
    for ep in inv.top_consumers(n):
        total = ep.traffic_up_mb + ep.traffic_down_mb
        print(f"{ep.name} - {total} MB")

def apply_policy(inv: NetworkInventory):
    limit = input_float("Limite total: ", 0)
    minutes = input_int("Minutos de suspensão: ", 1)
    inv.apply_traffic_policy(limit, minutes)

def do_save(inv: NetworkInventory):
    save_to_json(inv, FILE_DB)
    print("Dados guardados.")

def do_load(inv: NetworkInventory):
    inv.replace_with(load_from_json(FILE_DB))
    print("Dados carregados.")

# --------------------------------------------------
# FUNÇÃO: add_device()
# --------------------------------------------------
# PROPÓSITO: Adicionar um novo dispositivo de rede ao inventário
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (modifica o inventário e imprime mensagem de confirmação)
# O QUE FAZ:
#   1. Apresenta o menu de tipos de dispositivos (Router, Switch, AP, Endpoint)
#   2. Solicita dados específicos para cada tipo de dispositivo
#   3. Valida os dados introduzidos (ex: formato IPv4, MAC, etc.)
#   4. Cria uma instância da classe correspondente
#   5. Adiciona o dispositivo ao inventário
#   6. Trata erros de validação com try/except
# TIPOS DE DISPOSITIVOS:
#   - Router (1): Requer Nome, IPv4, IPv6 (opcional), MAC
#   - Switch (2): Requer Nome, IPv4 (opcional), MAC, Número de portas
#   - AccessPoint (3): Requer Nome, SSID
#   - Endpoint (4): Requer Nome, User ID, IPv4, IPv6 (opcional), MAC
# --------------------------------------------------
def add_device(inv: NetworkInventory):
    print("\n--- Adicionar dispositivo ---")
    print("Tipos: 1-ROUTER  2-SWITCH  3-AP  4-ENDPOINT")

    # Lê a opção do tipo de dispositivo
    opt = input_int("Escolha o tipo: ", 1, 4)

    try:
        # -------------------------
        # Criar ROUTER
        # -------------------------
        if opt == 1:
            # Solicita os dados do Router
            name = input("Nome: ").strip()
            ipv4 = input("IPv4: ").strip()
            ipv6 = input("IPv6 (ENTER para vazio): ").strip()
            mac = input("MAC: ").strip()

            # Cria instância da classe Router com os dados validados
            device = Router(
                name=name,
                ipv4=ipv4,
                ipv6=ipv6,
                mac_address=mac
            )

        # -------------------------
        # Criar SWITCH
        # -------------------------
        elif opt == 2:
            # Solicita os dados do Switch
            name = input("Nome: ").strip()
            ipv4 = input("IPv4 (ENTER para vazio): ").strip()
            mac = input("MAC: ").strip()
            # Número de portas deve estar entre 1 e 9999
            ports = input_int("Nº de portas: ", 1, 9999)

            # Cria instância da classe Switch com os dados validados
            device = Switch(
                name=name,
                ipv4=ipv4,
                mac_address=mac,
                ports=ports
            )

        # -------------------------
        # Criar ACCESS POINT
        # -------------------------
        elif opt == 3:
            # Solicita os dados do Access Point
            name = input("Nome: ").strip()
            ssid = input("SSID: ").strip()

            # Cria instância da classe AccessPoint com os dados validados
            device = AccessPoint(
                name=name,
                ssid=ssid
            )

        # -------------------------
        # Criar ENDPOINT
        # -------------------------
        else:
            # Solicita os dados do Endpoint (dispositivo do utilizador)
            name = input("Nome: ").strip()
            user_id = input("User ID (ex: nº aluno/email): ").strip()
            ipv4 = input("IPv4: ").strip()
            ipv6 = input("IPv6 (ENTER para vazio): ").strip()
            mac = input("MAC: ").strip()

            # Cria instância da classe Endpoint com os dados validados
            device = Endpoint(
                name=name,
                user_id=user_id,
                ipv4=ipv4,
                ipv6=ipv6,
                mac_address=mac
            )

        # Adiciona o dispositivo ao inventário
        inv.add_device(device)
        print("Dispositivo adicionado com sucesso.")

    except ValueError as e:
        # Captura erros de validação (ex: IPv4 inválido, MAC inválido, etc.)
        print(f"Erro: {e}")

# --------------------------------------------------
# FUNÇÃO: remove_device()
# --------------------------------------------------
# PROPÓSITO: Remover um dispositivo do inventário pelo nome
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (modifica o inventário e imprime confirmação)
# O QUE FAZ:
#   1. Solicita o nome do dispositivo a remover
#   2. Tenta encontrar e remover o dispositivo do inventário
#   3. Imprime mensagem confirmando sucesso ou falha
# --------------------------------------------------
def remove_device(inv: NetworkInventory):
    print("\n--- Remover dispositivo ---")
    # Solicita o nome do dispositivo a remover
    name = input("Nome do dispositivo a remover: ").strip()

    # Tenta remover o dispositivo
    if inv.remove_device(name):
        print("Dispositivo removido.")
    else:
        print("Dispositivo não encontrado.")

# --------------------------------------------------
# FUNÇÃO: list_devices()
# --------------------------------------------------
# PROPÓSITO: Listar todos os dispositivos do inventário
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (apenas imprime os dispositivos)
# O QUE FAZ:
#   1. Recupera a lista completa de dispositivos do inventário
#   2. Se a lista estiver vazia, exibe "(vazio)"
#   3. Senão, imprime os detalhes de cada dispositivo
# --------------------------------------------------
def list_devices(inv: NetworkInventory):
    print("\n--- Lista de dispositivos ---")
    # Obtém todos os dispositivos do inventário
    devices = inv.list_devices()

    # Verifica se existem dispositivos
    if not devices:
        print("(vazio)")
        return

    # Imprime cada dispositivo
    for d in devices:
        print(d)

# ======================== FUNÇÕES DE LÓGICA - CONSULTAS/PESQUISAS ========================

# --------------------------------------------------
# FUNÇÃO: search_ipv4()
# --------------------------------------------------
# PROPÓSITO: Pesquisar um dispositivo específico pelo seu endereço IPv4
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (apenas imprime os resultados)
# O QUE FAZ:
#   1. Solicita um endereço IPv4 ao utilizador
#   2. Procura o dispositivo com esse IPv4 no inventário
#   3. Se encontrado, exibe os detalhes do dispositivo
#   4. Se não encontrado, exibe mensagem de erro
# NOTA: Cada IPv4 é único, portanto há no máximo um resultado
# --------------------------------------------------
def search_ipv4(inv: NetworkInventory):
    print("\n--- Pesquisar por IPv4 ---")
    # Solicita o IPv4 a pesquisar
    ipv4 = input("IPv4: ").strip()

    # Procura o dispositivo com esse IPv4
    d = inv.find_by_ipv4(ipv4)
    if d:
        print("Dispositivo encontrado:")
        print(d)
    else:
        print("Dispositivo não encontrado.")

# --------------------------------------------------
# FUNÇÃO: search_type()
# --------------------------------------------------
# PROPÓSITO: Procurar todos os dispositivos de um tipo específico
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (apenas imprime os resultados)
# O QUE FAZ:
#   1. Solicita o tipo de dispositivo (ROUTER/SWITCH/AP/ENDPOINT)
#   2. Procura todos os dispositivos desse tipo no inventário
#   3. Se encontrados, lista todos os dispositivos desse tipo
#   4. Se não encontrados, exibe mensagem informativa
# TIPOS VÁLIDOS: ROUTER, SWITCH, AP, ENDPOINT
# --------------------------------------------------
def search_type(inv: NetworkInventory):
    print("\n--- Procurar por tipo ---")
    # Solicita o tipo de dispositivo a procurar
    t = input("Tipo (ROUTER/SWITCH/AP/ENDPOINT): ").strip().upper()

    # Procura todos os dispositivos do tipo especificado
    results = inv.find_by_type(t)
    if not results:
        print("Nenhum dispositivo encontrado.")
        return

    # Imprime todos os resultados encontrados
    for d in results:
        print(d)

# --------------------------------------------------
# FUNÇÃO: list_by_status()
# --------------------------------------------------
# PROPÓSITO: Listar todos os dispositivos com um estado específico
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (apenas imprime os resultados)
# O QUE FAZ:
#   1. Solicita o estado (ACTIVE ou INACTIVE)
#   2. Procura todos os dispositivos com esse estado
#   3. Se encontrados, lista todos os dispositivos com esse estado
#   4. Se não encontrados, exibe mensagem informativa
# ESTADOS VÁLIDOS: ACTIVE (ativo), INACTIVE (inativo)
# --------------------------------------------------
def list_by_status(inv: NetworkInventory):
    print("\n--- Listar por estado ---")
    # Solicita o estado a filtrar
    status = input("Estado (ACTIVE/INACTIVE): ").strip().upper()

    # Procura todos os dispositivos com esse estado
    results = inv.find_by_status(status)
    if not results:
        print("Nenhum dispositivo encontrado.")
        return

    # Imprime todos os resultados encontrados
    for d in results:
        print(d)

# ======================== FUNÇÕES DE LÓGICA - MONITORIZAÇÃO DE TRÁFEGO ========================

# --------------------------------------------------
# FUNÇÃO: update_endpoint_traffic()
# --------------------------------------------------
# PROPÓSITO: Atualizar o tráfego de rede (upload/download) de um endpoint
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (modifica o endpoint e imprime confirmação)
# O QUE FAZ:
#   1. Solicita o nome do endpoint a atualizar
#   2. Procura o endpoint no inventário
#   3. Solicita valores de tráfego upload e download em MB
#   4. Adiciona os valores de tráfego ao endpoint
#   5. Exibe confirmação ou erro se o endpoint não for encontrado
# NOTA: Apenas endpoints podem ter tráfego monitorizado
# --------------------------------------------------
def update_endpoint_traffic(inv: NetworkInventory):
    print("\n--- Atualizar tráfego de um Endpoint ---")
    # Solicita o nome do endpoint
    name = input("Nome do endpoint: ").strip()

    # Procura o endpoint pelo nome
    endpoint = inv.get_endpoint(name)
    if not endpoint:
        print("Endpoint não encontrado.")
        return

    # Solicita os valores de tráfego (mínimo 0 MB)
    up = input_float("Adicionar traffic_up_mb (MB): ", 0)
    down = input_float("Adicionar traffic_down_mb (MB): ", 0)

    try:
        # Adiciona o tráfego ao endpoint
        endpoint.add_traffic(up_mb=up, down_mb=down)
        print("Tráfego atualizado.")
    except ValueError as e:
        # Trata erros de validação
        print(f"Erro: {e}")

# --------------------------------------------------
# FUNÇÃO: top_consumers()
# --------------------------------------------------
# PROPÓSITO: Exibir os N endpoints com maior consumo de tráfego
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (apenas imprime os resultados)
# O QUE FAZ:
#   1. Solicita quantos top consumidores o utilizador quer ver
#   2. Obtém a lista ordenada dos maiores consumidores
#   3. Imprime cada endpoint com total de tráfego (upload + download)
#   4. Se não houver endpoints, exibe mensagem informativa
# CÁLCULO: Total = traffic_up_mb + traffic_down_mb
# --------------------------------------------------
def top_consumers(inv: NetworkInventory):
    print("\n--- Top consumidores de tráfego ---")
    # Solicita quantos quer ver (entre 1 e 9999)
    n = input_int("Quantos quer ver? ", 1, 9999)

    # Obtém os N maiores consumidores ordenados por tráfego
    results = inv.top_consumers(n)
    if not results:
        print("Não existem endpoints.")
        return

    # Imprime os resultados com número, nome e estatísticas
    for i, ep in enumerate(results, start=1):
        # Calcula o tráfego total (upload + download)
        total = ep.traffic_up_mb + ep.traffic_down_mb
        print(f"{i}. {ep.name} (total={total} MB, up={ep.traffic_up_mb}, down={ep.traffic_down_mb})")

# --------------------------------------------------
# FUNÇÃO: apply_policy()
# --------------------------------------------------
# PROPÓSITO: Aplicar uma política de limite de tráfego e suspender endpoints
# PARÂMETROS: inv (NetworkInventory) - instância do inventário
# RETORNA: Nenhum (modifica endpoints e imprime resultados)
# O QUE FAZ:
#   1. Solicita o limite máximo permitido (em MB, upload + download)
#   2. Solicita a duração da suspensão em minutos
#   3. Aplica a política a todos os endpoints que excedem o limite
#   4. Suspende os endpoints afetados pelo tempo especificado
#   5. Exibe os endpoints suspensos e até quando
# FUNCIONAMENTO:
#   - Endpoints com tráfego total > limite serão suspensos
#   - Suspensão dura o número de minutos especificado
# --------------------------------------------------
def apply_policy(inv: NetworkInventory):
    print("\n--- Política de tráfego ---")

    # Solicita o limite máximo permitido (soma de upload + download)
    limit = input_float("Limite total (up+down) em MB: ", 0)

    # Solicita o tempo de suspensão (entre 1 e 100000 minutos)
    minutes = input_int("Suspender por quantos minutos? ", 1, 100000)

    # Aplica a política e obtém a lista de endpoints afetados
    affected = inv.apply_traffic_policy(
        limit_mb=limit,
        suspend_minutes=minutes
    )

    # Exibe os resultados
    if not affected:
        print("Nenhum endpoint foi suspenso.")
    else:
        print("Endpoints suspensos:")
        # Imprime cada endpoint suspenso com data/hora de fim de suspensão
        for ep in affected:
            print(f"- {ep.name} até {ep.suspended_until}")

# ======================== FUNÇÕES DE LÓGICA - PERSISTÊNCIA DE DADOS ========================

# --------------------------------------------------
# FUNÇÃO: do_save()
# --------------------------------------------------
# PROPÓSITO: Guardar o inventário em ficheiro JSON
# PARÂMETROS: inv (NetworkInventory) - instância do inventário a guardar
# RETORNA: Nenhum (guarda ficheiro e imprime confirmação)
# O QUE FAZ:
#   1. Serializa o inventário para formato JSON
#   2. Escreve os dados no ficheiro (inventario.json)
#   3. Imprime confirmação de sucesso ou erro
# FICHEIRO: inventario.json (definido na constante FILE_DB)
# --------------------------------------------------
def do_save(inv: NetworkInventory):
    try:
        # Guarda o inventário em ficheiro JSON
        save_to_json(inv, FILE_DB)
        print(f"Dados guardados em {FILE_DB}")
    except Exception as e:
        # Trata qualquer erro que possa ocorrer na gravação
        print(f"Erro a guardar: {e}")

# --------------------------------------------------
# FUNÇÃO: do_load()
# --------------------------------------------------
# PROPÓSITO: Carregar um inventário previamente guardado em ficheiro JSON
# PARÂMETROS: inv (NetworkInventory) - instância do inventário a substituir
# RETORNA: Nenhum (substitui inventário com dados carregados)
# O QUE FAZ:
#   1. Tenta ler o ficheiro JSON (inventario.json)
#   2. Desserializa os dados para objetos Python
#   3. Substitui o inventário atual com os dados carregados
#   4. Imprime confirmação de sucesso, aviso se ficheiro não existe, ou erro
# FICHEIRO: inventario.json (definido na constante FILE_DB)
# ERROS TRATADOS:
#   - FileNotFoundError: Se o ficheiro não existe ainda
#   - Exception: Qualquer outro erro durante a leitura/desserialização
# --------------------------------------------------
def do_load(inv: NetworkInventory):
    try:
        # Carrega o inventário do ficheiro JSON
        new_inv = load_from_json(FILE_DB)

        # Substitui os dados atuais pelos carregados
        inv.replace_with(new_inv)

        print(f"Dados carregados de {FILE_DB}")

    except FileNotFoundError:
        # Aviso se o ficheiro ainda não foi criado
        print("Ainda não existe ficheiro para carregar.")
    except Exception as e:
        # Trata qualquer outro erro que possa ocorrer na leitura
        print(f"Erro a carregar: {e}")


# --------------------------------------------------
# Entrada do programa
# --------------------------------------------------
# EXPLICAÇÃO:
#   Esta é a secção de entrada padrão do Python.
#   O "if __name__ == '__main__':" verifica se o script está sendo executado diretamente
#   (e não sendo importado como módulo noutro ficheiro).
#   Se for executado diretamente, chama a função main() que inicia o programa.
# --------------------------------------------------

def main():
    # Cria um inventário vazio
    inv = NetworkInventory()

    # Ciclo principal do programa
    while True:
        menu_categorias()
        # Lê a opção do utilizador
        op = input_int("Opção: ", 0, 11)

        if op == 0:
            print("A sair...")
            break
        elif op == 1:
            add_device(inv)
            pause()
        elif op == 2:
            remove_device(inv)
            pause()
        elif op == 3:
            list_devices(inv)
            pause()
        elif op == 4:
            search_ipv4(inv)
            pause()
        elif op == 5:
            search_type(inv)
            pause()
        elif op == 6:
            list_by_status(inv)
            pause()
        elif op == 7:
            update_endpoint_traffic(inv)
            pause()
        elif op == 8:
            top_consumers(inv)
            pause()
        elif op == 9:
            apply_policy(inv)
            pause()
        elif op == 10:
            do_save(inv)
            pause()
        elif op == 11:
            do_load(inv)
            pause()

# Ponto de entrada do programa
if __name__ == "__main__":
    main()