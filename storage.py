import json
from datetime import datetime
from inventory import NetworkInventory
from devices import Router, Switch, AccessPoint, Endpoint

def save_to_json(inv: NetworkInventory, filename: str):
    """
    Serializa todos os dispositivos para uma lista de dicionários
    e guarda-os num ficheiro JSON formatado.
    """
    data = []
    for d in inv.list_devices():
        # O método to_dict() em devices.py já foi atualizado para 
        # exportar 'serial_interface' como booleano.
        data.append(d.to_dict())

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_from_json(filename: str) -> NetworkInventory:
    """
    Lê o ficheiro JSON e reconstrói os objetos de rede, restaurando
    modelos, presença de interface serial, estados e observações.
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    inv = NetworkInventory()

    for item in data:
        t = item.get("type")
        
        # Extrai campos comuns a todos os equipamentos
        obs = item.get("observations", "")
        mod = item.get("model", "")
        
        # Recupera o estado da interface serial (booleano)
        # Se não existir (ficheiros antigos), assume False (Não).
        ser_int = item.get("serial_interface", False)

        # -------------------------
        # Caso seja um ROUTER
        # -------------------------
        if t == "ROUTER":
            obj = Router(
                name=item["name"],
                ipv4=item.get("ipv4", ""),
                ipv6=item.get("ipv6") or "",
                mac_address=item["mac_address"],
                model=mod,
                serial_interface=ser_int,
                observations=obs
            )
            obj.status = item.get("status", obj.status)
            obj.connected_devices = list(item.get("connected_devices", []))

        # -------------------------
        # Caso seja um SWITCH
        # -------------------------
        elif t == "SWITCH":
            obj = Switch(
                name=item["name"],
                ipv4=item.get("ipv4", ""),
                mac_address=item["mac_address"],
                ports=int(item["ports"]),
                eth_ports=item.get("eth_ports", 0),
                fast_eth_ports=item.get("fast_eth_ports", 0),
                giga_eth_ports=item.get("giga_eth_ports", 0),
                model=mod,
                serial_interface=ser_int,
                observations=obs
            )
            obj.status = item.get("status", obj.status)
            obj.connected_devices = list(item.get("connected_devices", []))

        # -------------------------
        # Caso seja um ACCESS POINT
        # -------------------------
        elif t == "AP":
            obj = AccessPoint(
                name=item["name"],
                ssid=item["ssid"],
                model=mod,
                serial_interface=ser_int,
                observations=obs
            )
            obj.status = item.get("status", obj.status)
            obj.connected_endpoints = list(item.get("connected_endpoints", []))

        # -------------------------
        # Caso seja um ENDPOINT
        # -------------------------
        elif t == "ENDPOINT":
            obj = Endpoint(
                name=item["name"],
                user_id=item["user_id"],
                ipv4=item.get("ipv4", ""),
                ipv6=item.get("ipv6") or "",
                mac_address=item["mac_address"],
                model=mod,
                serial_interface=ser_int,
                observations=obs
            )
            obj.status = item.get("status", obj.status)
            obj.traffic_up_mb = float(item.get("traffic_up_mb", 0.0))
            obj.traffic_down_mb = float(item.get("traffic_down_mb", 0.0))

            susp = item.get("suspended_until")
            if susp:
                try:
                    obj.suspended_until = datetime.fromisoformat(susp)
                except ValueError:
                    obj.suspended_until = None
            else:
                obj.suspended_until = None

        else:
            continue

        # Adiciona o objeto reconstruído ao inventário
        inv.add_device(obj)

    return inv
