from netmiko import ConnectHandler
import requests
import time

# =========================
# CONFIGURACION
# =========================

R1 = {
    "device_type": "cisco_ios",
    "host": "192.168.122.10",
    "username": "docker",
    "password": "docker1",
}

R2 = {
    "device_type": "cisco_ios",
    "host": "192.168.122.20",
    "username": "docker",
    "password": "docker1",
}

R3_IP = "192.168.122.30"
AUTH = ("docker", "docker1")

# =========================
# CISCO
# =========================

def configurar_r1():
    print("\n--- Configurando R1 ---")
    try:
        conn = ConnectHandler(**R1)

        comandos = [
            # Ruta hacia MikroTik
            "ip route 192.168.30.0 255.255.255.0 200.1.13.2",

            # =========================
            # FASE 1 (IKE)
            # =========================
            "crypto isakmp policy 10",
            "encryption aes",
            "hash sha",
            "authentication pre-share",
            "group 2",
            "lifetime 86400",
            "exit",

            "crypto isakmp key vpn123 address 200.1.13.2",

            # =========================
            # FASE 2 (IPSEC)
            # =========================
            "crypto ipsec transform-set TS esp-aes esp-sha-hmac",
            "mode tunnel",
            "exit",

            # ACL interesante
            "access-list 110 permit ip 192.168.10.0 0.0.0.255 192.168.30.0 0.0.0.255",

            # Crypto map
            "crypto map VPN 10 ipsec-isakmp",
            "set peer 200.1.13.2",
            "set transform-set TS",
            "match address 110",
            "exit",

            # Aplicar a interfaz pública
            "interface g0/2",
            "crypto map VPN",
            "exit"
        ]

        print(conn.send_config_set(comandos))
        conn.disconnect()

    except Exception as e:
        print("Error en R1:", e)

def configurar_r2():
    print("\n--- Configurando R2 ---")
    try:
        conn = ConnectHandler(**R2)

        comandos = [
            "ip route 192.168.30.0 255.255.255.0 200.1.23.2"
        ]

        print(conn.send_config_set(comandos))
        conn.disconnect()

    except Exception as e:
        print("Error en R2:", e)

# =========================
# REST (MIKROTIK)
# =========================

def put(endpoint, data):
    url = f"http://{R3_IP}/rest{endpoint}"

    try:
        r = requests.put(url, json=data, auth=AUTH)

        print(f"\nPUT {endpoint}")
        print("STATUS:", r.status_code)
        print("RESP:", r.text)

    except Exception as e:
        print("Error REST:", e)


def configurar_mikrotik():
    print("\n--- Configurando MikroTik via REST ---")

    # Ruta
    put("/ip/route", {
        "dst-address": "192.168.10.0/24",
        "gateway": "200.1.13.1"
    })

    # Peer
    put("/ip/ipsec/peer", {
        "address": "200.1.13.1",
        "exchange-mode": "main",
        "name": "peer-r1"
    })

    # Identity
    put("/ip/ipsec/identity", {
        "peer": "peer-r1",
        "auth-method": "pre-shared-key",
        "secret": "vpn123"
    })

    # Policy
    put("/ip/ipsec/policy", {
        "src-address": "192.168.30.0/24",
        "dst-address": "192.168.10.0/24",
        "sa-dst-address": "200.1.13.1",
        "tunnel": "yes",
        "action": "encrypt",
        "peer": "peer-r1"
    })

# =========================
# LEVANTAR TUNEL
# =========================

def levantar_tunel():
    print("\n--- Generando tráfico para levantar IPsec ---")

    try:
        url = f"http://{R3_IP}/rest/ping"

        data = {
            "address": "192.168.10.1",
            "count": "3"
        }

        r = requests.post(url, json=data, auth=AUTH)

        print("Ping enviado desde R3")
        print("STATUS:", r.status_code)
        print("RESP:", r.text)

    except Exception as e:
        print("Error levantando túnel:", e)

# =========================
# VERIFICAR TUNEL
# =========================

def verificar_tunel():
    print("\n--- Verificando estado del túnel ---")

    try:
        url = f"http://{R3_IP}/rest/ip/ipsec/policy"

        r = requests.get(url, auth=AUTH)

        data = r.json()

        for policy in data:
            if policy.get("dst-address") == "192.168.10.0/24":

                estado = policy.get("ph2-state")

                print("Estado del túnel:", estado)

                if estado == "established":
                    print("TUNEL IPSEC ACTIVO")
                else:
                    print("TUNEL NO LEVANTADO")

    except Exception as e:
        print("Error verificando túnel:", e)

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("\n=== INICIO AUTOMATIZACION ===")

    configurar_r1()
    configurar_r2()
    configurar_mikrotik()

    time.sleep(3)

    levantar_tunel()

    time.sleep(3)

    verificar_tunel()

    print("\n=== FIN ===")
