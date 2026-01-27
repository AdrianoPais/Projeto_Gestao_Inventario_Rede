# Importa datetime e timedelta para gerir datas e tempos de suspensão
from datetime import datetime, timedelta

# Importa funções de validação (IPs e MAC) e normalização de MAC
from utils import is_valid_ipv4, is_valid_ipv6, is_valid_mac, normalize_mac

# Constantes para o estado dos dispositivos
ACTIVE = "ACTIVE"
INACTIVE = "INACTIVE"

# --------------------------------------------------
# Classe base Device (equipamento genérico)
# --------------------------------------------------

class Device:
    def __init__(self, name: str, device_type: str, observations: str = ""):
        # Remove espaços e valida o nome
        name = (name or "").strip()
        if not name:
            raise ValueError("name não pode ser vazio.")

        self.name = name
        self.device_type = device_type
        self.status = ACTIVE
        # Novo campo para registar defeitos ou notas técnicas
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
            "status": self.status,
            "observations": self.observations, # Incluído na serialização
        }

    def __str__(self):
        return f"[{self.device_type}] name={self.name} status={self.status}"


# --------------------------------------------------
# Classe Router (herda de Device)
# --------------------------------------------------

class Router(Device):
    def __init__(self, name: str, ipv4: str, ipv6: str, mac_address: str, observations: str = ""):
        super().__init__(name=name, device_type="ROUTER", observations=observations)

        # IPv4 AGORA É OPCIONAL: Valida apenas se for preenchido
        ipv4 = (ipv4 or "").strip()
        if ipv4 and (not is_valid_ipv4(ipv4)):
            raise ValueError("IPv4 inválido no Router.")
        self.ipv4 = ipv4

        ipv6 = (ipv6 or "").strip()
        if ipv6 and (not is_valid_ipv6(ipv6)):
            raise ValueError("IPv6 inválido no Router.")
        self.ipv6 = ipv6

        mac_address = normalize_mac(mac_address)
        if not is_valid_mac(mac_address):
            raise ValueError("MAC inválido no Router.")
        self.mac_address = mac_address

        self.connected_devices = []

    def connect_device(self, device_name: str):
        device_name = (device_name or "").strip()
        if not device_name:
            raise ValueError("Nome do dispositivo a ligar não pode ser vazio.")
        if device_name in self.connected_devices:
            raise ValueError("Esse dispositivo já está ligado ao Router.")
        self.connected_devices.append(device_name)

    def disconnect_device(self, device_name: str):
        device_name = (device_name or "").strip()
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "ipv4": self.ipv4,
            "ipv6": self.ipv6,
            "mac_address": self.mac_address,
            "connected_devices": list(self.connected_devices),
        })
        return d


# --------------------------------------------------
# Classe Switch (herda de Device)
# --------------------------------------------------

class Switch(Device):
    def __init__(self, name: str, ipv4: str, mac_address: str, ports: int, observations: str = ""):
        super().__init__(name=name, device_type="SWITCH", observations=observations)

        ipv4 = (ipv4 or "").strip()
        if ipv4 and (not is_valid_ipv4(ipv4)):
            raise ValueError("IPv4 inválido no Switch.")
        self.ipv4 = ipv4

        mac_address = normalize_mac(mac_address)
        if not is_valid_mac(mac_address):
            raise ValueError("MAC inválido no Switch.")
        self.mac_address = mac_address

        if ports <= 0:
            raise ValueError("ports tem de ser > 0.")
        self.ports = ports
        self.connected_devices = []

    def connect_device(self, device_name: str):
        device_name = (device_name or "").strip()
        if not device_name:
            raise ValueError("Nome do dispositivo a ligar não pode ser vazio.")
        if device_name in self.connected_devices:
            raise ValueError("Esse dispositivo já está ligado ao Switch.")
        if len(self.connected_devices) >= self.ports:
            raise ValueError("Não é possível ligar: Switch sem portas livres.")
        self.connected_devices.append(device_name)

    def disconnect_device(self, device_name: str):
        device_name = (device_name or "").strip()
        if device_name in self.connected_devices:
            self.connected_devices.remove(device_name)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "ipv4": self.ipv4,
            "mac_address": self.mac_address,
            "ports": self.ports,
            "connected_devices": list(self.connected_devices),
        })
        return d


# --------------------------------------------------
# Classe AccessPoint (herda de Device)
# --------------------------------------------------

class AccessPoint(Device):
    def __init__(self, name: str, ssid: str, observations: str = ""):
        super().__init__(name=name, device_type="AP", observations=observations)

        ssid = (ssid or "").strip()
        if not ssid:
            raise ValueError("ssid não pode ser vazio.")
        self.ssid = ssid
        self.connected_endpoints = []

    def connect_endpoint(self, endpoint_name: str):
        endpoint_name = (endpoint_name or "").strip()
        if not endpoint_name:
            raise ValueError("Nome do endpoint não pode ser vazio.")
        if endpoint_name in self.connected_endpoints:
            raise ValueError("Esse endpoint já está ligado ao AP.")
        self.connected_endpoints.append(endpoint_name)

    def disconnect_endpoint(self, endpoint_name: str):
        endpoint_name = (endpoint_name or "").strip()
        if endpoint_name in self.connected_endpoints:
            self.connected_endpoints.remove(endpoint_name)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "ssid": self.ssid,
            "connected_endpoints": list(self.connected_endpoints),
        })
        return d


# --------------------------------------------------
# Classe Endpoint (herda de Device)
# --------------------------------------------------

class Endpoint(Device):
    def __init__(self, name: str, user_id: str, ipv4: str, ipv6: str, mac_address: str, observations: str = ""):
        super().__init__(name=name, device_type="ENDPOINT", observations=observations)

        user_id = (user_id or "").strip()
        if not user_id:
            raise ValueError("user_id não pode ser vazio.")
        self.user_id = user_id

        # IPv4 AGORA É OPCIONAL: Valida apenas se for preenchido
        ipv4 = (ipv4 or "").strip()
        if ipv4 and (not is_valid_ipv4(ipv4)):
            raise ValueError("IPv4 inválido no Endpoint.")
        self.ipv4 = ipv4

        ipv6 = (ipv6 or "").strip()
        if ipv6 and (not is_valid_ipv6(ipv6)):
            raise ValueError("IPv6 inválido no Endpoint.")
        self.ipv6 = ipv6

        mac_address = normalize_mac(mac_address)
        if not is_valid_mac(mac_address):
            raise ValueError("MAC inválido no Endpoint.")
        self.mac_address = mac_address

        self.traffic_up_mb = 0.0
        self.traffic_down_mb = 0.0
        self.suspended_until = None

    def add_traffic(self, up_mb: float, down_mb: float):
        if up_mb < 0 or down_mb < 0:
            raise ValueError("Tráfego não pode ser negativo.")
        self.traffic_up_mb += up_mb
        self.traffic_down_mb += down_mb

    def is_suspended(self) -> bool:
        if self.suspended_until is None:
            return False
        return datetime.now() < self.suspended_until

    def suspend_for_minutes(self, minutes: int):
        if minutes <= 0:
            raise ValueError("minutes tem de ser > 0.")
        self.suspended_until = datetime.now() + timedelta(minutes=minutes)
        self.status = INACTIVE

    def refresh_status(self):
        if self.suspended_until is not None and datetime.now() >= self.suspended_until:
            self.suspended_until = None
            self.status = ACTIVE

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "user_id": self.user_id,
            "ipv4": self.ipv4,
            "ipv6": self.ipv6,
            "mac_address": self.mac_address,
            "traffic_up_mb": self.traffic_up_mb,
            "traffic_down_mb": self.traffic_down_mb,
            "suspended_until": self.suspended_until.isoformat() if self.suspended_until else None,
        })
        return d
