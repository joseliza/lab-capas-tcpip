# Laboratorio: capas TCP/IP con Wireshark

| Servicio | URL | Qué se ve en Wireshark |
|----------|-----|------------------------|
| HTTP     | `http://IP_PROFESOR:8080`  | Usuario y contraseña en claro |
| HTTPS    | `https://IP_PROFESOR:8443` | Solo TLS cifrado (certificado autofirmado: aceptar el aviso) |

## Arranque
    docker compose up -d --build     # levantar
    docker compose down              # parar

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
