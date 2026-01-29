from datetime import datetime, timedelta
from utils import is_valid_ipv4, is_valid_ipv6, is_valid_mac, normalize_mac

ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"

class Device:
    def __init__(self, name: str, device_type: str, model: str = "", 
                 serial_interface: bool = False, observations: str = "", 
                 condition: str = "Funcional", defect_description: str = "",
                 rack: int = 1):
        name = (name or "").strip()
        if not name:
            raise ValueError("name não pode ser vazio.")

        self.name = name
        self.device_type = device_type
        self.model = (model or "").strip()
        self.serial_interface = serial_interface
        self.rack = rack
        self.condition = condition  
        self.defect_description = (defect_description or "").strip()
        self.status = ACTIVE
        self.observations = (observations or "").strip()

    def set_status(self, status: str):
        status = (status or "").strip().upper()
        if status not in (ACTIVE, INACTIVE):
            raise ValueError("status tem de ser ACTIVE ou INACTIVE.")
        self.status = status

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

    def __str__(self):
        return f"[{self.device_type}] {self.name} (Mod: {self.model or '-'}) [Bastidor {self.rack}]"

# --- Classe Router ---
class Router(Device):
    def __init__(self, name: str, ipv4: str, ipv6: str, mac_address: str, 
                 model: str = "", serial_interface: bool = False, observations: str = "",
                 condition: str = "Funcional", defect_description: str = "", rack: int = 1):
        
        super().__init__(name=name, device_type="ROUTER", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        self.ipv4 = (ipv4 or "").strip()
        self.ipv6 = (ipv6 or "").strip()
        self.mac_address = normalize_mac(mac_address)
        self.connected_devices = []

    # MÉTODO ADICIONADO PARA CORREÇÃO DO ERRO
    def connect_device(self, device_name):
        if device_name not in self.connected_devices:
            self.connected_devices.append(device_name)

    def disconnect_device(self, device_name):
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"ipv4": self.ipv4, "ipv6": self.ipv6, "mac_address": self.mac_address, "connected_devices": list(self.connected_devices)})
        return d

# --- Classe Switch ---
class Switch(Device):
    def __init__(self, name: str, ipv4: str, mac_address: str, ports: int, 
                 eth_ports: int = 0, fast_eth_ports: int = 0, giga_eth_ports: int = 0,
                 model: str = "", serial_interface: bool = False, observations: str = "",
                 condition: str = "Funcional", defect_description: str = "", rack: int = 1):
        
        super().__init__(name=name, device_type="SWITCH", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        self.ipv4 = (ipv4 or "").strip()
        self.mac_address = normalize_mac(mac_address)
        self.ports = ports
        self.eth_ports = eth_ports
        self.fast_eth_ports = fast_eth_ports
        self.giga_eth_ports = giga_eth_ports
        self.connected_devices = []

    # MÉTODO ADICIONADO PARA CORREÇÃO DO ERRO
    def connect_device(self, device_name):
        if device_name not in self.connected_devices:
            self.connected_devices.append(device_name)

    def disconnect_device(self, device_name):
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"ipv4": self.ipv4, "mac_address": self.mac_address, "ports": self.ports, "connected_devices": list(self.connected_devices)})
        return d

# --- Classe AccessPoint ---
class AccessPoint(Device):
    def __init__(self, name: str, ssid: str, model: str = "", serial_interface: bool = False, 
                 observations: str = "", condition: str = "Funcional", 
                 defect_description: str = "", rack: int = 1):
        
        super().__init__(name=name, device_type="AP", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        self.ssid = (ssid or "").strip()
        self.connected_endpoints = []

    # MÉTODO ADICIONADO PARA CORREÇÃO DO ERRO
    def connect_endpoint(self, ep_name):
        if ep_name not in self.connected_endpoints:
            self.connected_endpoints.append(ep_name)

    def disconnect_endpoint(self, ep_name):
        if ep_name in self.connected_endpoints:
            self.connected_endpoints.remove(ep_name)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"ssid": self.ssid, "connected_endpoints": list(self.connected_endpoints)})
        return d

# --- Classe Endpoint ---
class Endpoint(Device):
    def __init__(self, name: str, user_id: str, ipv4: str, ipv6: str, mac_address: str, 
                 model: str = "", serial_interface: bool = False, observations: str = "",
                 condition: str = "Funcional", defect_description: str = "", rack: int = 1):
        
        super().__init__(name=name, device_type="ENDPOINT", model=model, 
                         serial_interface=serial_interface, observations=observations,
                         condition=condition, defect_description=defect_description, rack=rack)

        self.user_id = (user_id or "").strip()
        self.ipv4 = (ipv4 or "").strip()
        self.mac_address = normalize_mac(mac_address)
        self.traffic_up_mb = 0.0
        self.traffic_down_mb = 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"user_id": self.user_id, "ipv4": self.ipv4, "mac_address": self.mac_address, "traffic_up_mb": self.traffic_up_mb, "traffic_down_mb": self.traffic_down_mb})
        return d
