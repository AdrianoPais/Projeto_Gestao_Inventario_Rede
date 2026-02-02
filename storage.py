# Nome 1: Daniel Santos
# Nome 2: Sérgio Correia
# Nome 3: Tiago Costa
# Turma: GRSC0925
# Trabalho: Projeto Final UC00608 - Programação Alocada a Objetos (Em Python)

import json
import os
from datetime import datetime
from inventory import NetworkInventory
from devices import Router, Switch, AccessPoint, Endpoint

# ==================================================
# REGISTO DE EVENTOS (LOG)
# ==================================================

# Regista uma ação no ficheiro local logs.txt com timestamp

def log_event(mensagem: str):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {mensagem}\n")

# ==================================================
# GUARDA DE INVENTÁRIO EM JSON
# ==================================================

# Guarda todos os dispositivos do inventário num ficheiro JSON

def save_to_json(inv: NetworkInventory, filename: str):
    data = [d.to_dict() for d in inv.list_devices()]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==================================================
# LEITURA DE INVENTÁRIO A PARTIR DE JSON
# ==================================================

# Reconstrói o inventário de rede a partir de um ficheiro JSON

def load_from_json(filename: str) -> NetworkInventory:

    # Caso o ficheiro não exista, devolve um inventário vazio
    if not os.path.exists(filename):
        return NetworkInventory()

    # Leitura do ficheiro JSON
    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return NetworkInventory()

    # Criação do inventário
    inv = NetworkInventory()

    # Percorre todos os dispositivos guardados
    for item in data:
        t = item.get("type")

        # --------------------------------------------------
        # Campos comuns (com proteção para dados antigos)
        # --------------------------------------------------

        obs = item.get("observations", "")
        mod = item.get("model", "")
        ser_int = item.get("serial_interface", False)
        cond = item.get("condition", "Funcional")
        def_desc = item.get("defect_description", "")
        rk = item.get("rack", 1)

        # --------------------------------------------------
        # Reconstrução do objeto conforme o tipo
        # --------------------------------------------------

        if t == "ROUTER":
            obj = Router(
                name=item["name"],
                ipv4=item.get("ipv4", ""),
                ipv6=item.get("ipv6") or "",
                mac_address=item["mac_address"],
                model=mod,
                serial_interface=ser_int,
                observations=obs,
                condition=cond,
                defect_description=def_desc,
                rack=rk
            )
            obj.connected_devices = list(item.get("connected_devices", []))

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
                observations=obs,
                condition=cond,
                defect_description=def_desc,
                rack=rk
            )
            obj.connected_devices = list(item.get("connected_devices", []))

        elif t == "AP":
            obj = AccessPoint(
                name=item["name"],
                ssid=item["ssid"],
                model=mod,
                serial_interface=ser_int,
                observations=obs,
                condition=cond,
                defect_description=def_desc,
                rack=rk
            )
            obj.connected_endpoints = list(item.get("connected_endpoints", []))

        elif t == "ENDPOINT":
            obj = Endpoint(
                name=item["name"],
                user_id=item["user_id"],
                ipv4=item.get("ipv4", ""),
                ipv6=item.get("ipv6") or "",
                mac_address=item["mac_address"],
                model=mod,
                serial_interface=ser_int,
                observations=obs,
                condition=cond,
                defect_description=def_desc,
                rack=rk
            )

            # Contadores de tráfego
            obj.traffic_up_mb = float(item.get("traffic_up_mb", 0.0))
            obj.traffic_down_mb = float(item.get("traffic_down_mb", 0.0))

            # Estado de suspensão (caso exista)
            susp = item.get("suspended_until")
            obj.suspended_until = datetime.fromisoformat(susp) if susp else None

        else:
            continue

        # --------------------------------------------------
        # Estado do dispositivo e inserção no inventário
        # --------------------------------------------------

        obj.status = item.get("status", obj.status)
        inv.add_device(obj)

    return inv
