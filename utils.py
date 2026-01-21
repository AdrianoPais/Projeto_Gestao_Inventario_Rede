# Importa o módulo re para trabalhar com expressões regulares (regex)
import re

# Importa ip_address para validar endereços IPv4 e IPv6
from ipaddress import ip_address

# --------------------------------------------------
# Função de pausa (usada no menu)
# --------------------------------------------------

def pause():
    # Espera que o utilizador carregue ENTER
    # Usado para não limpar o ecrã logo a seguir
    input("\nENTER para continuar...")

# --------------------------------------------------
# Função para ler um número inteiro com validação
# --------------------------------------------------

def input_int(msg, min_v=None, max_v=None):
    # Ciclo infinito até o utilizador introduzir um valor válido
    while True:
        try:
            # Tenta converter o input para inteiro
            v = int(input(msg))

            # Se existir valor mínimo e o número for menor, dá erro
            if min_v is not None and v < min_v:
                print(f"Tem de ser >= {min_v}")
                continue

            # Se existir valor máximo e o número for maior, dá erro
            if max_v is not None and v > max_v:
                print(f"Tem de ser <= {max_v}")
                continue

            # Se passar todas as validações, devolve o valor
            return v

        except ValueError:
            # Executado se a conversão para inteiro falhar
            print("Valor inválido (inteiro).")

# --------------------------------------------------
# Função para ler um número decimal (float) com validação
# --------------------------------------------------

def input_float(msg, min_v=None):
    # Ciclo infinito até o utilizador introduzir um valor válido
    while True:
        try:
            # Tenta converter o input para float
            v = float(input(msg))

            # Se existir valor mínimo e o número for menor, dá erro
            if min_v is not None and v < min_v:
                print(f"Tem de ser >= {min_v}")
                continue

            # Se passar as validações, devolve o valor
            return v

        except ValueError:
            # Executado se a conversão para float falhar
            print("Valor inválido (número).")

# --------------------------------------------------
# Função para validar endereços IPv4
# --------------------------------------------------

def is_valid_ipv4(value: str) -> bool:
    try:
        # Converte a string para um objeto IP
        ip = ip_address(value)

        # Verifica se a versão do IP é 4
        return ip.version == 4

    except ValueError:
        # Se der erro, o IP não é válido
        return False

# --------------------------------------------------
# Função para validar endereços IPv6
# --------------------------------------------------

def is_valid_ipv6(value: str) -> bool:
    try:
        # Converte a string para um objeto IP
        ip = ip_address(value)

        # Verifica se a versão do IP é 6
        return ip.version == 6

    except ValueError:
        # Se der erro, o IP não é válido
        return False

# --------------------------------------------------
# Função para normalizar MAC address
# --------------------------------------------------

def normalize_mac(mac: str) -> str:
    # Remove espaços, converte para maiúsculas
    # e substitui "-" por ":"
    # Exemplo: aa-bb-cc-dd-ee-ff -> AA:BB:CC:DD:EE:FF
    mac = mac.strip().upper().replace("-", ":")
    return mac

# --------------------------------------------------
# Função para validar MAC address
# --------------------------------------------------

def is_valid_mac(mac: str) -> bool:
    # Normaliza primeiro o MAC
    mac = normalize_mac(mac)

    # Expressão regular para validar o formato do MAC
    # Exemplo válido: AA:BB:CC:DD:EE:FF
    pattern = r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$"

    # Retorna True se corresponder ao padrão, False caso contrário
    return re.match(pattern, mac) is not None