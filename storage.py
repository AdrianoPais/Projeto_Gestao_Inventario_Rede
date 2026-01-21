
# MÓDULO: storage.py
# PROPÓSITO: Gestão de persistência de dados (serialização e desserialização)

# DESCRIÇÃO:
    # Este módulo é responsável por guardar e carregar dados do inventário de rede
    # em ficheiros JSON, permitindo que os dados persistam entre sessões do programa.
    
# FUNÇÕES PRINCIPAIS:
    # - save_to_json(): Serializa o inventário para formato JSON
    # - load_from_json(): Desserializa dados JSON para objetos Python

# DEPENDÊNCIAS:
    # - json: Módulo padrão para trabalhar com ficheiros JSON
    # - datetime: Módulo para trabalhar com datas e horas
    # - inventory.NetworkInventory: Classe que gerencia o inventário
    # - devices: Classes dos dispositivos de rede (Router, Switch, AP, Endpoint)

# ======================== IMPORTAÇÕES ========================
# Importa o módulo json para guardar e carregar dados em ficheiros JSON
import json

# Importa datetime para trabalhar com datas (suspensão dos endpoints)
from datetime import datetime

# Importa a classe NetworkInventory (gestor de dispositivos)
from inventory import NetworkInventory

# Importa as classes dos vários tipos de dispositivos
from devices import Router, Switch, AccessPoint, Endpoint

# ======================== FUNÇÕES DE PERSISTÊNCIA ========================

# --------------------------------------------------
# FUNÇÃO: save_to_json()
# --------------------------------------------------
# PROPÓSITO: Guardar o inventário completo em ficheiro JSON
# PARÂMETROS:
#   - inv (NetworkInventory): O inventário a guardar
#   - filename (str): Nome do ficheiro JSON (ex: "inventario.json")
# RETORNA: Nenhum (escreve ficheiro no disco)
# O QUE FAZ:
#   1. Percorre todos os dispositivos do inventário
#   2. Converte cada dispositivo para formato dicionário (serialização)
#   3. Abre (ou cria) um ficheiro em modo escrita
#   4. Escreve os dados em formato JSON legível (formatado com indentação)
#   5. Fecha o ficheiro automaticamente
# NOTES:
#   - encoding="utf-8" permite acentos e caracteres especiais
#   - ensure_ascii=False preserva caracteres acentuados no JSON
#   - indent=2 formata o JSON com indentação de 2 espaços (legível)
# ERROS POSSÍVEIS:
#   - IOError: Se não conseguir escrever no ficheiro
#   - AttributeError: Se um dispositivo não tiver método to_dict()
# --------------------------------------------------
def save_to_json(inv: NetworkInventory, filename: str):
    # Lista que vai conter todos os dispositivos em formato dicionário
    data = []

    # Percorre todos os dispositivos do inventário
    for d in inv.list_devices():
        # Converte cada objeto em dicionário usando o método to_dict() da classe
        # Cada dispositivo sabe como se serializar
        data.append(d.to_dict())

    # Abre (ou cria) o ficheiro em modo escrita ("w")
    # encoding="utf-8" permite acentos e caracteres especiais
    with open(filename, "w", encoding="utf-8") as f:
        # Guarda os dados em JSON formatado e legível
        # indent=2: indenta com 2 espaços para melhor legibilidade
        # ensure_ascii=False: preserva acentos no ficheiro JSON
        json.dump(data, f, indent=2, ensure_ascii=False)

# --------------------------------------------------
# FUNÇÃO: load_from_json()
# --------------------------------------------------
# PROPÓSITO: Carregar o inventário a partir de um ficheiro JSON
# PARÂMETROS:
#   - filename (str): Nome do ficheiro JSON a carregar (ex: "inventario.json")
# RETORNA: NetworkInventory (novo inventário carregado com todos os dispositivos)
# O QUE FAZ:
#   1. Abre e lê o ficheiro JSON
#   2. Desserializa os dados JSON para dicionários Python
#   3. Cria um novo inventário vazio
#   4. Para cada dispositivo no JSON:
#      - Identifica o tipo do dispositivo
#      - Cria o objeto correspondente (Router, Switch, AP ou Endpoint)
#      - Restaura todos os atributos (status, tráfego, suspensões, etc.)
#      - Adiciona o dispositivo ao inventário
#   5. Devolve o inventário completo carregado
# TIPOS DE DISPOSITIVOS SUPORTADOS:
#   - ROUTER: Encaminhador de rede
#   - SWITCH: Comutador de rede
#   - AP: Ponto de acesso wireless
#   - ENDPOINT: Dispositivo do utilizador (laptop, telemóvel, etc.)
# NOTAS IMPORTANTES:
#   - Cada dispositivo é recriado com o método constructor padrão
#   - Atributos adicionais (status, tráfego, etc.) são restaurados após criação
#   - O inventário garante que não existem duplicatas de MAC ou IPv4
#   - Datas de suspensão são convertidas de ISO format para datetime
# ERROS TRATADOS:
#   - FileNotFoundError: Levantada se o ficheiro não existe
#   - ValueError: Levantada durante parsing de dados inválidos
#   - KeyError: Se campos obrigatórios faltam no JSON
# --------------------------------------------------
def load_from_json(filename: str) -> NetworkInventory:
    # Abre o ficheiro JSON em modo leitura ("r")
    # encoding="utf-8" permite ler acentos e caracteres especiais
    with open(filename, "r", encoding="utf-8") as f:
        # Lê o conteúdo JSON e converte para estruturas Python (listas e dicionários)
        data = json.load(f)

    # Cria um novo inventário vazio que será preenchido com os dados carregados
    inv = NetworkInventory()

    # Percorre cada item (dispositivo) guardado no ficheiro JSON
    for item in data:
        # Lê o tipo do dispositivo do dicionário
        # Cada dispositivo tem um campo "type" que o identifica
        t = item.get("type")

        # -------------------------
        # Caso seja um ROUTER
        # -------------------------

        if t == "ROUTER":
            # Cria um objeto Router com os dados guardados no JSON
            obj = Router(
                name=item["name"],                          # Nome do router
                ipv4=item["ipv4"],                          # Endereço IPv4 principal
                ipv6=item.get("ipv6") or "",               # Endereço IPv6 (opcional)
                mac_address=item["mac_address"]             # Endereço MAC de identificação
            )
            # Repõe o estado (ACTIVE ou INACTIVE)
            obj.status = item.get("status", obj.status)

            # Repõe os dispositivos ligados ao router
            obj.connected_devices = list(item.get("connected_devices", []))

        # -------------------------
        # Caso seja um SWITCH
        # -------------------------

        elif t == "SWITCH":
            # Cria um objeto Switch
            obj = Switch(
                name=item["name"],                          # Nome do switch
                ipv4=item.get("ipv4") or "",               # Endereço IPv4 (opcional)
                mac_address=item["mac_address"],            # Endereço MAC de identificação
                ports=int(item["ports"])                   # Número de portas (convertido para int)
            )
            # Repõe o estado
            obj.status = item.get("status", obj.status)

            # Restaura a lista de dispositivos conectados ao switch
            # Uma lista de nomes de dispositivos que estão ligados a este switch
            obj.connected_devices = list(item.get("connected_devices", []))

        # -------------------------
        # Caso seja um ACCESS POINT
        # -------------------------

        elif t == "AP":
            # Cria um objeto AccessPoint (ponto de acesso wireless)
            obj = AccessPoint(
                name=item["name"],                          # Nome do AP
                ssid=item["ssid"]                           # Nome da rede WiFi (SSID)
            )
            # Restaura o estado (ACTIVE ou INACTIVE)
            obj.status = item.get("status", obj.status)

            # Restaura a lista de endpoints conectados ao AP
            # Uma lista de nomes de dispositivos WiFi ligados a este AP
            obj.connected_endpoints = list(item.get("connected_endpoints", []))

        # -------------------------
        # Caso seja um ENDPOINT
        # -------------------------

        elif t == "ENDPOINT":
            # Cria um objeto Endpoint (dispositivo do utilizador)
            obj = Endpoint(
                name=item["name"],                          # Nome do dispositivo (ex: "Laptop João")
                user_id=item["user_id"],                   # ID do utilizador (ex: "t0132000" ou email)
                ipv4=item["ipv4"],                          # Endereço IPv4 do dispositivo
                ipv6=item.get("ipv6") or "",               # Endereço IPv6 (opcional)
                mac_address=item["mac_address"]             # Endereço MAC de identificação
            )
            # Restaura o estado (ACTIVE ou INACTIVE)
            obj.status = item.get("status", obj.status)

            # Repõe os valores de tráfego
            obj.traffic_up_mb = float(item.get("traffic_up_mb", 0.0))

            # Traffic download: quantidade de dados recebidos (em MB)
            obj.traffic_down_mb = float(item.get("traffic_down_mb", 0.0))

            # Repõe a informação de suspensão, se existir
            susp = item.get("suspended_until")

            if susp:
                try:
                    # Converte a string no formato ISO (ex: "2025-01-21T14:30:00")
                    # para um objeto datetime Python
                    obj.suspended_until = datetime.fromisoformat(susp)
                except ValueError:
                    # Se houver erro na conversão, ignora a suspensão
                    # (pode estar em formato inválido)
                    obj.suspended_until = None
            else:
                # Se não havia suspensão no JSON, mantém como None
                # (endpoint não está suspenso)
                obj.suspended_until = None

        # -------------------------
        # Caso o tipo seja desconhecido
        # -------------------------

        else:
            # Ignora dispositivos inválidos (salta para o próximo)
            # Assim não interrompe o carregamento de todo o inventário
            continue

        # Adiciona o dispositivo ao inventário
        # O inventário automaticamente:
        # - Valida os dados (MAC, IPv4, etc.)
        # - Evita duplicatas
        # - Mantém a integridade dos dados
        inv.add_device(obj)

    # Devolve o inventário completo carregado do ficheiro
    # Contém todos os dispositivos, seus estados, tráfego, suspensões, etc.
    return inv