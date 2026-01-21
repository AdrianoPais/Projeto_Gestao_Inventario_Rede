# MÓDULO: inventory.py
# PROPÓSITO: Gestão centralizada do inventário de dispositivos de rede

# DESCRIÇÃO:
    # Este módulo contém a classe NetworkInventory que é o coração do programa.
    # Gerencia a coleção completa de dispositivos de rede, aplicando regras de
    # integridade de dados, validações e operações de consulta/pesquisa.

# RESPONSABILIDADES PRINCIPAIS:
    # - Armazenar todos os dispositivos de rede em um dicionário centralizado
    # - Validar regras de negócio (MAC único, IPv4 único, nome único)
    # - Fornecer métodos de consulta (pesquisar por tipo, IPv4, estado)
    # - Gerenciar endpoints (tráfego, suspensões, políticas)
    # - Permitir persistência (save/load) de todo o inventário

# ESTRUTURA DE DADOS:
    # - devices: Dicionário onde:
      # - Chave (key): Nome do dispositivo (string única)
      # - Valor (value): Objeto do dispositivo (Router, Switch, AP, Endpoint)

# ======================== IMPORTAÇÕES ========================
# Importa a classe Endpoint para conseguir:
#   - Verificar se um dispositivo é Endpoint (usando isinstance)
#   - Aceder aos métodos específicos de Endpoint (add_traffic, suspend_for_minutes, etc.)
#   - Gerenciar suspensões e tráfego de endpoints
from devices import Endpoint

# ======================== CLASSE NETWORKINVENTORY ========================

class NetworkInventory:

    # MÉTODOS PRINCIPAIS:
        # - add_device(): Adicionar novo dispositivo (com validações)
        # - remove_device(): Remover dispositivo pelo nome
        # - list_devices(): Listar todos os dispositivos
        # - find_by_type(): Pesquisar por tipo de dispositivo
        # - find_by_status(): Pesquisar por estado (ativo/inativo)
        # - find_by_ipv4(): Pesquisar por endereço IP
        # - get_endpoint(): Obter endpoint específico
        # - top_consumers(): Obter maiores consumidores de tráfego
        # - apply_traffic_policy(): Aplicar políticas de limite de tráfego

    def __init__(self):

        # O QUE FAZ:
            # - Cria um dicionário vazio para armazenar dispositivos
            # - Inicializa a estrutura de dados do inventário

        # EXEMPLO DE USO:
            # inv = NetworkInventory()  # Cria inventário vazio
        # Dicionário que guarda todos os dispositivos da rede
        # Estrutura: { "nome_dispositivo": objeto_dispositivo, ... }

        self.devices = {}

    def replace_with(self, other_inv):

        # MÉTODO: replace_with()

        # O QUE FAZ:
            # - Substitui completamente o dicionário de dispositivos atual
            # - Descarta todos os dispositivos antigas
            # - Copia todas as referências do novo inventário
    
        # Substitui os dispositivos atuais pelos do outro inventário
        self.devices = other_inv.devices

    def add_device(self, device):

        # MÉTODO: add_device()

        # O QUE FAZ:
            # 1. Valida que o nome é único (não pode existir outro com mesmo nome)
            # 2. Valida que o MAC é único (se o dispositivo tiver MAC)
            # 3. Valida que o IPv4 é único (se o dispositivo tiver IPv4)
            # 4. Se passar em todas as validações, adiciona o dispositivo
            # 5. Se falhar, levanta uma exceção com mensagem de erro

        # Se o nome já existe no dicionário de dispositivos
        if device.name in self.devices:
            # Levanta exceção bloqueando a adição
            raise ValueError("Já existe um dispositivo com esse nome.")

        # Alguns dispositivos têm mac_address, outros não
        # getattr(obj, attr, default) devolve o atributo ou default se não existir
        new_mac = getattr(device, "mac_address", None)

        # Se o dispositivo tiver MAC (não é None e não é vazio)
        if new_mac:
            # Percorre todos os dispositivos já guardados no inventário
            for d in self.devices.values():
                # Vai buscar o MAC do dispositivo existente (se tiver)
                mac = getattr(d, "mac_address", None)

                # Se o dispositivo existente tiver MAC e for igual ao novo -> erro
                if mac and mac == new_mac:
                    raise ValueError("MAC duplicado no inventário.")

        # Alguns dispositivos têm ipv4, outros podem não ter (ou ser vazio)
        new_ipv4 = getattr(device, "ipv4", None)

        # Se o dispositivo tiver IPv4 (não é None e não é vazio)
        if new_ipv4:
            # Percorre todos os dispositivos já guardados no inventário
            for d in self.devices.values():
                # Vai buscar o IPv4 do dispositivo existente (se tiver)
                ipv4 = getattr(d, "ipv4", None)

                # Se o dispositivo existente tiver IPv4 e for igual ao novo -> erro
                if ipv4 and ipv4 == new_ipv4:
                    raise ValueError("IPv4 duplicado no inventário.")

        # Se passou em todas as validações, adiciona o dispositivo ao dicionário
        self.devices[device.name] = device

    def remove_device(self, name: str) -> bool:

        # MÉTODO: remove_device()
        # =======================

        # O QUE FAZ:
        #     1. Limpa espaços em branco do nome (strip)
        #     2. Verifica se o dispositivo existe no dicionário
        #     3. Se existe, remove-o e devolve True
        #     4. Se não existe, devolve False (sem erro)

        # Remove espaços no início e fim do nome (ex: " router " -> "router")
        name = (name or "").strip()

        # Se o dispositivo existe no dicionário
        if name in self.devices:
            # Remove (apaga) o dispositivo do dicionário
            del self.devices[name]
            # Devolve True indicando sucesso
            return True

        # Se o dispositivo não foi encontrado, devolve False
        return False

    def list_devices(self):

        # MÉTODO: list_devices()

        # O QUE FAZ:
        #     - Converte os valores do dicionário em lista Python
        #     - Cada elemento é um objeto de dispositivo (Router, Switch, AP, Endpoint)
        #     - A lista pode estar vazia se o inventário não tiver dispositivos

        # Devolve uma lista com todos os valores (objetos) do dicionário
        return list(self.devices.values())

    def find_by_type(self, device_type: str):

        # MÉTODO: find_by_type()
         
        # O QUE FAZ:
        #     1. Limpa e converte o tipo para maiúsculas (ex: "router" -> "ROUTER")
        #     2. Percorre todos os dispositivos do inventário
        #     3. Filtra apenas os que têm device_type igual ao procurado
        #     4. Devolve lista com resultados (pode estar vazia)

        device_type = (device_type or "").strip().upper()

        # Filtragem: percorre todos os dispositivos e retorna os que têm o tipo procurado
        # Usa list comprehension para eficiência
        return [d for d in self.devices.values() if d.device_type == device_type]

    def find_by_status(self, status: str):

        # MÉTODO: find_by_status()
         
        # O QUE FAZ:
        #     1. Limpa e converte o estado para maiúsculas (ex: "active" -> "ACTIVE")
        #     2. Percorre todos os dispositivos do inventário
        #     3. Filtra apenas os que têm status igual ao procurado
        #     4. Devolve lista com resultados

        status = (status or "").strip().upper()

        # Filtragem: retorna dispositivos com o status procurado
        return [d for d in self.devices.values() if d.status == status]

    def find_by_ipv4(self, ipv4: str):

        # MÉTODO: find_by_ipv4()
         
        # O QUE FAZ:
        #     1. Limpa espaços do IPv4
        #     2. Percorre todos os dispositivos do inventário
        #     3. Procura um que tenha esse IPv4
        #     4. Devolve o dispositivo encontrado ou None

        # Limpa espaços do IPv4
        ipv4 = (ipv4 or "").strip()

        # Percorre todos os dispositivos do inventário
        for d in self.devices.values():
            # Vai buscar o ipv4 do dispositivo (se existir, devolve None se não tiver)
            v = getattr(d, "ipv4", None)

            # Se o dispositivo tiver IPv4 e for igual ao procurado
            if v and v == ipv4:
                # Devolve o dispositivo encontrado
                return d

        # Se nenhum dispositivo tiver esse IPv4, devolve None
        return None

    def get_endpoint(self, name: str):

        # MÉTODO: get_endpoint()

        # O QUE FAZ:
        #     1. Limpa espaços do nome
        #     2. Procura o dispositivo no dicionário pelo nome
        #     3. Verifica se é realmente um Endpoint (usando isinstance)
        #     4. Devolve o Endpoint ou None

        # Limpa espaços do nome
        name = (name or "").strip()

        # Vai buscar diretamente ao dicionário pelo nome
        d = self.devices.get(name)

        # Se existir um dispositivo com esse nome E for um Endpoint
        # isinstance(d, Endpoint) verifica se o tipo é Endpoint
        if d and isinstance(d, Endpoint):
            # Devolve o Endpoint
            return d

        # Se não for endpoint, devolve None
        return None

    def top_consumers(self, n: int):

        # MÉTODO: top_consumers()
         
        # O QUE FAZ:
        #     1. Filtra apenas os dispositivos que são Endpoints
        #     2. Atualiza o estado de cada endpoint (verifica suspensões)
        #     3. Ordena os endpoints por tráfego total (upload + download) em ordem decrescente
        #     4. Devolve apenas os primeiros N
        #     5. Se n > total de endpoints, devolve todos

        # Cria uma lista só com endpoints (ignora Router, Switch, AP)
        endpoints = [d for d in self.devices.values() if isinstance(d, Endpoint)]

        # Antes de ordenar, atualiza o estado de cada endpoint
        # Isto verifica se alguma suspensão já terminou e atualiza o status
        for ep in endpoints:
            ep.refresh_status()

        # Ordena endpoints por consumo total (upload + download) do maior para o menor
        # reverse=True: ordem decrescente (maior primeiro)
        # key=lambda e: (e.traffic_up_mb + e.traffic_down_mb): função de ordenação
        endpoints.sort(key=lambda e: (e.traffic_up_mb + e.traffic_down_mb), reverse=True)

        # Devolve apenas os primeiros N endpoints
        # Se n > total de endpoints, Python devolve todos automaticamente
        return endpoints[:n]

    def apply_traffic_policy(self, limit_mb: float, suspend_minutes: int):

        # MÉTODO: apply_traffic_policy()

        # O QUE FAZ:
        #     1. Filtra apenas os Endpoints do inventário
        #     2. Para cada Endpoint:
        #        a. Atualiza o estado (verifica suspensões expiradas)
        #        b. Calcula o tráfego total (upload + download)
        #        c. Se tráfego > limite E ainda não está suspenso:
        #           - Suspende o endpoint pelo tempo especificado
        #           - Adiciona à lista de afetados
        #     3. Devolve lista dos endpoints que foram suspensos

        # Lista de endpoints que foram afetados/suspensos nesta execução
        affected = []

        # Cria uma lista só com endpoints
        endpoints = [d for d in self.devices.values() if isinstance(d, Endpoint)]

        # Percorre cada endpoint para verificar se viola o limite de tráfego
        for ep in endpoints:
            # Atualiza status antes de aplicar a regra
            # Isto verifica se alguma suspensão anterior já expirou
            ep.refresh_status()

            # Calcula o total de tráfego deste endpoint
            # Soma o tráfego enviado (upload) com o recebido (download)
            total = ep.traffic_up_mb + ep.traffic_down_mb

            # Se tráfego total > limite E endpoint ainda não está suspenso
            if total > limit_mb and not ep.is_suspended():
                # Suspende o endpoint pelo tempo especificado (em minutos)
                ep.suspend_for_minutes(suspend_minutes)
                
                # Adiciona à lista de endpoints afetados nesta execução
                affected.append(ep)

        # Devolve a lista dos endpoints suspensos nesta execução
        return affected