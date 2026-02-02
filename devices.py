# Nome 1: Daniel Santos
# Nome 2: Sérgio Correia
# Nome 3: Tiago Costa
# Turma: GRSC0925
# Trabalho: Projeto Final UC00608 - Programação Alocada a Objetos (Em Python)

# ==================================================
# IMPORTAÇÕES DE BIBLIOTECAS E UTILITÁRIOS
# ==================================================

from datetime import datetime, timedelta  # Importa módulos para manipulação de datas e tempos
from utils import is_valid_ipv4, is_valid_ipv6, is_valid_mac, normalize_mac  # Importa funções utilitárias para validação e normalização de endereços

# ==================================================
# CONSTANTES DE ESTADO
# ==================================================

# Estados possíveis para um dispositivo no sistema

ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"

# ==================================================
# CLASSE BASE: DEVICE
# ==================================================

# Classe base para todos os dispositivos da rede
# Define atributos e comportamentos comuns a todos os equipamentos

class Device:
    def __init__(self, name: str, device_type: str, model: str = "", 
                 serial_interface: bool = False, observations: str = "", 
                 condition: str = "Funcional", defect_description: str = "",
                 rack: int = 1):
        
        # Limpa espaços em branco do nome
        name = (name or "").strip()
        
        # Validação: o nome não pode ser vazio
        if not name:
            raise ValueError("name não pode ser vazio.")

        # Atributos comuns a todos os dispositivos
        self.name = name
        self.device_type = device_type
        self.model = (model or "").strip()
        self.serial_interface = serial_interface
        self.rack = rack
        self.condition = condition  
        self.defect_description = (defect_description or "").strip()
        self.status = ACTIVE
        self.observations = (observations or "").strip()


    # --------------------------------------------------
    # Método para alterar o estado do dispositivo
    # --------------------------------------------------

    def set_status(self, status: str):
        status = (status or "").strip().upper()
        
        # Apenas aceita estados válidos
        if status not in (ACTIVE, INACTIVE):
            raise ValueError("status tem de ser ACTIVE ou INACTIVE.")
        self.status = status

    # --------------------------------------------------
    # Converte o dispositivo para dicionário (JSON)
    # --------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "type": self.device_type,
            "name": self.name,
            "model": self.model,
            "serial_interface": self.serial_interface,
            "condition": self.condition,
            "defect_description": self.defect_description,
            "rack": self.rack,
            "status": self.status,
            "observations": self.observations,
        }

    # --------------------------------------------------
    # Representação textual do dispositivo
    # --------------------------------------------------

    def __str__(self):
        return f"[{self.device_type}] {self.name} (Mod: {self.model or '-'}) [Bastidor {self.rack}]"

# ==================================================
# CLASSE ROUTER
# ==================================================

# Representa um Router da rede
# Herda da classe Device

class Router(Device):
    def __init__(self, name: str, ipv4: str, ipv6: str, mac_address: str, 
                 model: str = "", serial_interface: bool = False, observations: str = "",
                 condition: str = "Funcional", defect_description: str = "", rack: int = 1):
        
        # Inicialização da classe base
        super().__init__(name=name, device_type="ROUTER", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        # Atributos específicos do Router
        self.ipv4 = (ipv4 or "").strip()
        self.ipv6 = (ipv6 or "").strip()
        self.mac_address = normalize_mac(mac_address)
        
        # Lista de dispositivos ligados a este router
        self.connected_devices = []

    # --------------------------------------------------
    # Liga um dispositivo ao router
    # --------------------------------------------------

    def connect_device(self, device_name):
        if device_name not in self.connected_devices:
            self.connected_devices.append(device_name)


    # --------------------------------------------------
    # Remove a ligação de um dispositivo ao router
    # --------------------------------------------------

    def disconnect_device(self, device_name):
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)

    # --------------------------------------------------
    # Converte o router para dicionário
    # --------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"ipv4": self.ipv4, "ipv6": self.ipv6, "mac_address": self.mac_address, "connected_devices": list(self.connected_devices)})
        return d

# ==================================================
# CLASSE SWITCH
# ==================================================

# Representa um Switch de rede
# Herda da classe Device

class Switch(Device):
    def __init__(self, name: str, ipv4: str, mac_address: str, ports: int, 
                 eth_ports: int = 0, fast_eth_ports: int = 0, giga_eth_ports: int = 0,
                 model: str = "", serial_interface: bool = False, observations: str = "",
                 condition: str = "Funcional", defect_description: str = "", rack: int = 1):
        
        # Inicialização da classe base
        super().__init__(name=name, device_type="SWITCH", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        # Atributos específicos do Switch
        self.ipv4 = (ipv4 or "").strip()
        self.mac_address = normalize_mac(mac_address)
        self.ports = ports
        self.eth_ports = eth_ports
        self.fast_eth_ports = fast_eth_ports
        self.giga_eth_ports = giga_eth_ports
        
        # Lista de dispositivos ligados ao switch
        self.connected_devices = []

    # --------------------------------------------------
    # Liga um dispositivo ao switch
    # --------------------------------------------------

    def connect_device(self, device_name):
        if device_name not in self.connected_devices:
            self.connected_devices.append(device_name)

    # --------------------------------------------------
    # Remove a ligação de um dispositivo ao switch
    # --------------------------------------------------

    def disconnect_device(self, device_name):
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)

    # --------------------------------------------------
    # Converte o switch para dicionário
    # --------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"ipv4": self.ipv4, "mac_address": self.mac_address, "ports": self.ports, "connected_devices": list(self.connected_devices)})
        return d

# ==================================================
# CLASSE ACCESS POINT
# ==================================================

# Representa um Access Point (AP)
# Herda da classe Device

class AccessPoint(Device):
    def __init__(self, name: str, ssid: str, model: str = "", serial_interface: bool = False, 
                 observations: str = "", condition: str = "Funcional", 
                 defect_description: str = "", rack: int = 1):
        
        # Inicialização da classe base
        super().__init__(name=name, device_type="AP", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        # SSID da rede wireless
        self.ssid = (ssid or "").strip()
        
        # Lista de endpoints ligados ao AP
        self.connected_endpoints = []

    # --------------------------------------------------
    # Liga um endpoint ao access point
    # --------------------------------------------------

    def connect_endpoint(self, ep_name):
        if ep_name not in self.connected_endpoints:
            self.connected_endpoints.append(ep_name)

    # --------------------------------------------------
    # Remove a ligação de um endpoint ao access point
    # --------------------------------------------------

    def disconnect_endpoint(self, ep_name):
        if ep_name in self.connected_endpoints:
            self.connected_endpoints.remove(ep_name)

    # --------------------------------------------------
    # Converte o access point para dicionário
    # --------------------------------------------------

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"ssid": self.ssid, "connected_endpoints": list(self.connected_endpoints)})
        return d

# ==================================================
# CLASSE ENDPOINT
# ==================================================

# Representa um dispositivo final (PC, portátil, etc.)
# Herda da classe Device

class Endpoint(Device):
    def __init__(self, name: str, user_id: str, ipv4: str, ipv6: str, mac_address: str, 
                 model: str = "", serial_interface: bool = False, observations: str = "",
                 condition: str = "Funcional", defect_description: str = "", rack: int = 1):
        
        # Inicialização da classe base
        super().__init__(name=name, device_type="ENDPOINT", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        # Atributos específicos do Endpoint
        self.user_id = (user_id or "").strip()
        self.ipv4 = (ipv4 or "").strip()
        self.mac_address = normalize_mac(mac_address)
        
        # Contadores de tráfego
        self.traffic_up_mb = 0.0
        self.traffic_down_mb = 0.0

    # --------------------------------------------------
    # Converte o endpoint para dicionário
    # --------------------------------------------------
    
    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"user_id": self.user_id, "ipv4": self.ipv4, "mac_address": self.mac_address, "traffic_up_mb": self.traffic_up_mb, "traffic_down_mb": self.traffic_down_mb})
        return d
