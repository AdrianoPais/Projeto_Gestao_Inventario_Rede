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
        # O método to_dict() já inclui as observações e IPv4 opcional
        data.append(d.to_dict())

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_from_json(filename: str) -> NetworkInventory:
    """
    Lê o ficheiro JSON e reconstrói os objetos de rede com base no tipo,
    restaurando estados, ligações e observações técnicas.
    """
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    inv = NetworkInventory()

    for item in data:
        t = item.get("type")
        
        # Extrai observações comuns a todos os tipos
        obs = item.get("observations", "")

        # -------------------------
        # Caso seja um ROUTER
        # -------------------------
        if t == "ROUTER":
            obj = Router(
                name=item["name"],
                ipv4=item.get("ipv4", ""), # IPv4 opcional
                ipv6=item.get("ipv6") or "",
                mac_address=item["mac_address"],
                observations=obs            # Restauro de observações
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
                observations=obs            # Restauro de observações
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
                observations=obs            # Restauro de observações
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
                ipv4=item.get("ipv4", ""), # IPv4 opcional
                ipv6=item.get("ipv6") or "",
                mac_address=item["mac_address"],
                observations=obs            # Restauro de observações
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

        # Adiciona o objeto reconstruído ao novo inventário
        inv.add_device(obj)

    return inv
