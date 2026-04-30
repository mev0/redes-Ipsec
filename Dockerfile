# 1. Usar una imagen base ligera de Python
FROM python:3.11-slim

# 2. Establecer el directorio de trabajo
WORKDIR /app

# 3. Instalar herramientas de red, diagnóstico y edición
# Se incluyen curl, wget, traceroute, telnet, dnsutils y editores
RUN apt update && apt install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    netcat-openbsd \
    openssh-client \
    curl \
    wget \
    traceroute \
    telnet \
    dnsutils \
    nano \
    vim \
    less \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar el archivo de requerimientos (netmiko, requests, rich)
COPY requirements.txt .

# 5. Instalar las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto de los archivos del proyecto
COPY . .

# 7. Mantener el contenedor abierto para GNS3
CMD ["/bin/bash", "-i"]
