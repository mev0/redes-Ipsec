# redes-Ipsec

Examen: Automatización de Red Multimarca
Integrantes: Ian Spiner, Misael Villarroel y Martin Roloff

PROYECTO
Script de automatización en Python (script.py) para una red multimarca en GNS3:

Cisco: Configuración y gestión vía SSH utilizando la librería Netmiko.

MikroTik: Administración mediante API REST utilizando la librería Requests.

ENTORNO (Docker)
Entorno de ejecución aislado basado en Python 3.11-slim. Incluye:

Gestión de dependencias mediante requirements.txt (netmiko, requests, rich).

Herramientas de diagnóstico: iproute2, traceroute, ping, telnet, curl.

Editores de texto integrados: nano y vim.

EJECUCION
Construir la imagen: docker build -t red-auto:final ..

Validar direccionamiento IPv4 en la red de gestión OOB (192.168.122.0/24).

Ejecutar el script: python script.py.
