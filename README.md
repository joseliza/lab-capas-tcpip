# Laboratorio: capas TCP/IP con Wireshark

| Servicio | URL | Qué se ve en Wireshark |
|----------|-----|------------------------|
| HTTP     | `http://IP_PROFESOR:8080`  | Usuario y contraseña en claro |
| HTTPS    | `https://IP_PROFESOR:8443` | Solo TLS cifrado (certificado autofirmado: aceptar el aviso) |

## Arranque
    docker compose up -d --build     # levantar
    docker compose down              # parar

## Probarlo en casa

Necesitas Git y Docker con el plugin Compose. Wireshark es opcional pero es el objetivo del laboratorio.

Primero, descarga el repositorio (en Windows, dentro de la terminal de Ubuntu/WSL si sigues la opción A):

    git clone https://github.com/USUARIO/lab-capas-tcpip.git
    cd lab-capas-tcpip

> **Por qué importa el sistema operativo:** los contenedores usan `network_mode: host`
> (ver [Notas](#notas)). En Linux eso es nativo y funciona tal cual. En Windows, Docker
> corre dentro de una máquina virtual (WSL2), así que "host" es esa VM y no Windows;
> por eso conviene seguir las indicaciones de la sección de Windows.

### Linux (Docker Engine, sin Docker Desktop)

Ejemplo para Debian/Ubuntu (para otras distribuciones, ver <https://docs.docker.com/engine/install/>):

    # 1. Repositorio oficial de Docker
    sudo apt update
    sudo apt install -y ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 2. Docker Engine + Compose
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # 3. (Opcional) usar docker sin sudo; cierra sesión y vuelve a entrar después
    sudo usermod -aG docker $USER

    # 4. Comprobar
    docker run --rm hello-world
    docker compose version

Wireshark: `sudo apt install -y wireshark` (responde **Sí** a permitir capturas a usuarios no root
y añade tu usuario al grupo con `sudo usermod -aG wireshark $USER`).

Desplegar:

    docker compose up -d --build
    docker compose ps                # web y proxy en estado "running"

Probar: abre <http://localhost:8080> y <https://localhost:8443> (acepta el aviso del certificado).
Para capturar en local, en Wireshark elige la interfaz **`lo`** (loopback) con el filtro
`tcp port 8080 or tcp port 8443`. Si quieres que otro equipo de tu red se conecte, usa tu IP
de la LAN (`ip a`) y captura en `eth0`/`wlan0`.

Ver logs y parar:

    docker compose logs -f
    docker compose down

### Windows

Hay dos opciones. La **A** es la recomendada porque reproduce el comportamiento de Linux.

#### Opción A (recomendada): Docker Engine dentro de WSL2 (Ubuntu)

Requiere Windows 10 (21H2 o superior) o Windows 11 con virtualización activada en la BIOS/UEFI.

1. Abre **PowerShell como administrador** e instala WSL con Ubuntu, y reinicia si lo pide:

        wsl --install -d Ubuntu

2. Abre la aplicación **Ubuntu** del menú Inicio y crea tu usuario.
3. Dentro de Ubuntu, sigue exactamente los pasos de la sección **Linux** de arriba
   (instalación de Docker Engine). Si tu Ubuntu no tiene systemd, activa en `/etc/wsl.conf`:

        [boot]
        systemd=true

   y ejecuta `wsl --shutdown` desde PowerShell para reiniciarlo.
4. Clona el repositorio **dentro del sistema de ficheros de Ubuntu** (por ejemplo en `~/`), no en
   `/mnt/c/...`, y ejecuta `docker compose up -d --build`.
5. Desde el navegador de Windows abre <http://localhost:8080> y <https://localhost:8443>
   (WSL2 reenvía `localhost` a Windows).
6. Para que otros equipos de tu red accedan, en Windows 11 (22H2 o superior) crea o edita
   `%UserProfile%\.wslconfig` con

        [wsl2]
        networkingMode=mirrored

   y ejecuta `wsl --shutdown`. Así WSL comparte la red de Windows y usará tu IP de la LAN.
   Además tendrás que permitir los puertos 8080 y 8443 en el Firewall de Windows.

Wireshark en Windows (<https://www.wireshark.org/download.html>): instala también **Npcap** cuando
te lo ofrezca. Para ver el tráfico de la propia máquina, captura en **Npcap Loopback Adapter**
(o en la interfaz real si otro equipo se conecta). Con WSL2 en modo NAT, el tráfico a `localhost`
puede no verse como en Linux; con `mirrored` es más fiable.

#### Opción B: Docker Desktop

1. Instala Docker Desktop desde <https://www.docker.com/products/docker-desktop/> con el backend
   **WSL 2** (opción por defecto) y reinicia.
2. Abre **Settings > Resources > Network** y activa **Enable host networking**
   (requiere Docker Desktop 4.34 o superior). Sin esto, `network_mode: host` no hace que
   los puertos sean accesibles desde Windows.
3. En PowerShell, dentro de la carpeta del repositorio:

        docker compose up -d --build

4. Abre <http://localhost:8080> y <https://localhost:8443>.

> **Limitaciones en Windows:** la MAC que muestra `/capas` se lee de la tabla ARP del
> equipo donde corre el contenedor. En Windows ese equipo es la VM de WSL2/Docker
> Desktop, así que probablemente no verás la MAC real del cliente. Es una limitación del
> entorno de casa: en el aula, con Linux, funciona como se describe en este README.
> Si Docker Desktop da problemas con el modo host, usa la Opción A.

### Solución de problemas

| Síntoma | Causa y solución |
|---------|------------------|
| `port is already allocated` / `address already in use` | Otro programa usa 8080 u 8443. Ciérralo (`sudo ss -tlnp \| grep -E '8080\|8443'`). |
| `permission denied ... docker.sock` | Usa `sudo` o añade tu usuario al grupo `docker` y vuelve a iniciar sesión. |
| `docker: 'compose' is not a docker command` | Falta `docker-compose-plugin`. Instálalo. |
| El navegador avisa del certificado en `:8443` | Es normal (autofirmado). Avanzado > Continuar. |
| No capturas nada en Wireshark | Elige la interfaz correcta (`lo` en local, la real si viene otro equipo) y usa `http://` explícito. |

## Preparación
1. Averigua tu IP en la LAN (`ip a`) y pásala a los alumnos.
2. Abre Wireshark y captura en tu interfaz real (`eth0`/`wlan0`), no en `lo`:
   si los alumnos entran desde sus PCs verás sus MAC e IP reales.
   Filtro de captura: `tcp port 8080 or tcp port 8443`
3. Los alumnos deben escribir `http://` explícito y usar credenciales inventadas.

## Guion
1. **Handshake**: filtro `tcp.flags.syn == 1` -> SYN, SYN/ACK, ACK.
2. **Las 4 capas** en un mismo paquete: filtro `http.request.method == "POST"`.
   Desplegar Ethernet II (MAC) > IPv4 (IP, TTL) > TCP (puertos, seq/ack) > HTML Form URL Encoded (usuario y password).
3. **Impacto**: clic derecho > Follow > TCP Stream -> conversación completa con las credenciales.
4. **Cabeceras**: `Host`, `User-Agent` (revelan el navegador del alumno).
5. **Comparación HTTPS**: mismo login en `:8443`, filtro `tls`. Se ve
   `Client Hello` (con el SNI) y luego `Application Data` ilegible.
   Follow TCP Stream solo muestra basura cifrada.
6. **Cierre**: `tcp.flags.fin == 1`.

## Notas
- Los contenedores usan `network_mode: host`: comparten la red de tu equipo, no hay
  `ports:` ni NAT de Docker. Los puertos 8080 y 8443 de tu equipo deben estar libres.
- `/help` explica el uso a alumnos y profesor.
- `/capas` muestra por capas lo que ve el servidor, incluida la **MAC del alumno** leída de
  la tabla ARP del equipo (`/proc/net/arp`). Solo funciona si el alumno está en la misma LAN;
  si está en otra subred verás la MAC del router (o nada). Coincide con la MAC origen de
  `Ethernet II` en Wireshark.
- Nada se guarda: las credenciales solo se muestran en la respuesta.
