from flask import Flask, render_template_string, request

app = Flask(__name__)

BASE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Laboratorio de capas TCP/IP</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:720px;margin:3rem auto;padding:0 1rem;color:#222}
 .badge{display:inline-block;padding:.2rem .6rem;border-radius:1rem;color:#fff;font-size:.85rem}
 .http{background:#c0392b}.https{background:#27ae60}
 form{display:grid;gap:.8rem;margin:1.5rem 0}
 input,button{padding:.6rem;font-size:1rem}
 .aviso{background:#fff3cd;border:1px solid #e0c36a;padding:.7rem;border-radius:.4rem;font-size:.9rem}
 code{background:#eee;padding:.1rem .3rem}
 td{padding:.2rem .8rem .2rem 0}
 .glosario td{vertical-align:top;border-top:1px solid #ddd;padding:.4rem .8rem .4rem 0;font-size:.9rem}
 .glosario td:first-child{white-space:nowrap}
</style></head><body>
<h1>Acceso <span class="badge {{ esquema }}">{{ esquema|upper }}</span></h1>
{{ contenido|safe }}
</body></html>"""

FORM = """
<p class="aviso">Usa credenciales <b>inventadas</b>. Se están capturando los paquetes de esta red
con fines didácticos.</p>
<form method="post" action="/login">
  <input name="usuario" placeholder="Usuario" required autocomplete="off">
  <input name="password" type="password" placeholder="Contraseña" required autocomplete="off">
  <button>Entrar</button>
</form>
<p><a href="/capas">¿Desde dónde me ves?</a> · <a href="/help">Ayuda</a></p>
"""

RESULTADO = """
<p>El servidor ha recibido:</p>
<table><tr><td>Usuario</td><td><code>{{ usuario }}</code></td></tr>
<tr><td>Contraseña</td><td><code>{{ password }}</code></td></tr></table>
<p>Ahora mira Wireshark. <a href="/">Volver</a></p>
"""

CAPAS = """
<p>Así te ve el servidor, capa por capa (modelo TCP/IP):</p>
<table>
<tr><th colspan="2" align="left">4. Aplicación</th></tr>
<tr><td>Protocolo</td><td><code>{{ esquema|upper }}</code></td></tr>
<tr><td>Navegador (<code>User-Agent</code>)</td><td><code>{{ ua }}</code></td></tr>
<tr><th colspan="2" align="left">3. Transporte</th></tr>
<tr><td>Puerto origen (tuyo)</td><td><code>{{ puerto }}</code></td></tr>
<tr><td>Puerto destino (servidor)</td><td><code>{{ puerto_destino }}</code></td></tr>
<tr><th colspan="2" align="left">2. Internet</th></tr>
<tr><td>IP origen (tuya)</td><td><code>{{ ip }}</code></td></tr>
<tr><th colspan="2" align="left">1. Enlace / acceso a red</th></tr>
<tr><td>Tu MAC (origen de la trama)</td><td>{% if mac_alumno %}<code>{{ mac_alumno }}</code>{% elif local %}<i>no tiene (tráfico local)</i>{% else %}<i>no disponible</i>{% endif %}</td></tr>
<tr><td>MAC del servidor (destino de la trama)</td><td><code>{{ mac }}</code></td></tr>
<tr><td>Interfaz / MTU</td><td><code>{{ interfaz or "?" }} / {{ mtu }}</code></td></tr>
</table>
{% if local %}<p class="aviso"><b>Estás accediendo desde el propio servidor</b> (<code>127.0.0.1</code>):
el tráfico va por la interfaz virtual <code>lo</code>, que no es Ethernet, así que no hay trama ni
MAC (verás <code>00:00:00:00:00:00</code>) y Wireshark no lo muestra en <code>eth0</code>. Entra desde otro equipo con
<code>http://IP_DEL_SERVIDOR:8080/capas</code>, o captura en <code>lo</code>.</p>{% endif %}
<p class="aviso">Las MAC solo viajan dentro de la red local (cada router las sustituye).
Si ves tu MAC aquí es porque estás en la misma LAN que el servidor y la ha aprendido por
ARP. Si estás en otra subred, saldrá <i>no disponible</i> o la MAC del router. Compárala con
la cabecera <code>Ethernet II</code> de la captura y con <code>ip link</code> (Linux) o
<code>ipconfig /all</code> (Windows).</p>
<p><a href="/">Volver</a> · <a href="/help#glosario">¿Qué significa cada término?</a></p>
"""


AYUDA = """
<h2>Cómo usar el laboratorio</h2>
<h3>Alumnos</h3>
<ol>
 <li>Entra en <code>http://IP_PROFESOR:8080</code> (escribe <code>http://</code> completo).</li>
 <li>Escribe un usuario y una contraseña <b>inventados</b> y pulsa Entrar.</li>
 <li>Repite en <code>https://IP_PROFESOR:8443</code> (acepta el aviso del certificado autofirmado).</li>
</ol>
<h3>Profesor: Wireshark</h3>
<ol>
 <li>Captura en la interfaz real (<code>eth0</code>/<code>wlan0</code>), no en <code>lo</code>.
     Filtro de captura: <code>tcp port 8080 or tcp port 8443</code></li>
 <li>Handshake: <code>tcp.flags.syn == 1</code></li>
 <li>Capas de un paquete: <code>http.request.method == "POST"</code> y despliega
     Ethernet &rarr; IP &rarr; TCP &rarr; HTTP.</li>
 <li>Clic derecho &rarr; Follow &rarr; TCP Stream: se ven usuario y contraseña.</li>
 <li>Compara con HTTPS: filtro <code>tls</code>. Solo se ve tráfico cifrado.</li>
</ol>
<h3 id="glosario">Glosario</h3>
<table class="glosario">
<tr><td><b>Aplicación</b></td><td>Capa 4 de TCP/IP. Es la que usan los programas (navegador, correo...). Aquí viven protocolos como HTTP.</td></tr>
<tr><td><b>HTTP</b></td><td>Protocolo de la web. Viaja <b>en texto plano</b>: cualquiera que capture los paquetes puede leerlo.</td></tr>
<tr><td><b>HTTPS</b></td><td>HTTP dentro de un túnel cifrado (TLS). Lo capturado es ilegible sin la clave.</td></tr>
<tr><td><b>TLS</b></td><td>Protocolo que cifra la comunicación y autentica al servidor mediante un certificado.</td></tr>
<tr><td><b>Certificado autofirmado</b></td><td>Certificado creado por el propio servidor, sin una autoridad que lo avale. Por eso el navegador avisa.</td></tr>
<tr><td><b>User-Agent</b></td><td>Cabecera HTTP con la que el navegador se identifica (nombre, versión, sistema operativo).</td></tr>
<tr><td><b>Transporte</b></td><td>Capa 3 de TCP/IP. Entrega los datos al programa correcto y, con TCP, de forma fiable y ordenada.</td></tr>
<tr><td><b>TCP</b></td><td>Protocolo de transporte con conexión: confirma la recepción y reenvía lo perdido.</td></tr>
<tr><td><b>Puerto</b></td><td>Número (0-65535) que identifica el programa dentro de un equipo. HTTP usa 80, HTTPS 443; aquí 8080 y 8443.</td></tr>
<tr><td><b>Puerto origen</b></td><td>Puerto temporal que elige tu navegador para esta conexión. Cambia en cada conexión.</td></tr>
<tr><td><b>Puerto destino</b></td><td>Puerto donde escucha el servidor (8080 o 8443).</td></tr>
<tr><td><b>Handshake (SYN, SYN/ACK, ACK)</b></td><td>Saludo de tres pasos con el que TCP abre una conexión antes de enviar datos.</td></tr>
<tr><td><b>FIN</b></td><td>Indicador TCP que avisa de que un extremo cierra la conexión.</td></tr>
<tr><td><b>Secuencia / ACK</b></td><td>Números TCP que ordenan los bytes y confirman lo recibido.</td></tr>
<tr><td><b>Internet</b></td><td>Capa 2 de TCP/IP. Direcciona y encamina los paquetes entre redes (protocolo IP).</td></tr>
<tr><td><b>IP origen</b></td><td>Dirección IP del equipo que envía. Identifica al equipo en la red, a diferencia de la MAC, que identifica la tarjeta.</td></tr>
<tr><td><b>TTL</b></td><td>Tiempo de vida del paquete IP: cada router lo reduce en 1 y, al llegar a 0, se descarta (evita bucles).</td></tr>
<tr><td><b>Subred / LAN</b></td><td>LAN: red local. Subred: tramo de red con el mismo rango de IP. Entre subredes hace falta un router.</td></tr>
<tr><td><b>Enlace / acceso a red</b></td><td>Capa 1 de TCP/IP. Mueve tramas entre equipos conectados directamente (Ethernet, Wi-Fi).</td></tr>
<tr><td><b>Trama</b></td><td>Unidad de datos de la capa de enlace. Encapsula al paquete IP.</td></tr>
<tr><td><b>Ethernet II</b></td><td>Formato de trama más usado. Su cabecera lleva MAC destino, MAC origen y el tipo de protocolo que transporta.</td></tr>
<tr><td><b>MAC</b></td><td>Dirección física de 48 bits de una tarjeta de red (ej. <code>7a:7a:7c:91:3c:9e</code>). Solo vale dentro de la red local.</td></tr>
<tr><td><b>MTU</b></td><td>Tamaño máximo, en bytes, de datos que cabe en una trama de esa interfaz (normalmente 1500 en Ethernet). Si un paquete es mayor, se fragmenta.</td></tr>
<tr><td><b>Interfaz</b></td><td>Conexión de red del equipo (<code>eth0</code>, <code>wlan0</code>, <code>docker0</code>, <code>lo</code>...).</td></tr>
<tr><td><b>ARP</b></td><td>Protocolo que averigua la MAC que corresponde a una IP de la red local. El equipo guarda el resultado en su tabla ARP.</td></tr>
<tr><td><b>lo (loopback)</b></td><td>Interfaz virtual del propio equipo (127.0.0.1). Su tráfico nunca sale a la red.</td></tr>
<tr><td><b>Follow TCP Stream</b></td><td>Función de Wireshark que reconstruye y muestra la conversación completa de una conexión TCP.</td></tr>
<tr><td><b>Client Hello / SNI</b></td><td>Primer mensaje TLS del cliente. El SNI indica el nombre del servidor al que quiere conectarse y va sin cifrar.</td></tr>
<tr><td><b>Application Data</b></td><td>Datos de aplicación ya cifrados dentro de TLS. En Wireshark solo se ven bytes ilegibles.</td></tr>
</table>
<p><a href="/">Volver</a> · <a href="/capas">Ver mis datos de conexión</a></p>
"""


def buscar_arp(ip):
    """Devuelve (mac, interfaz) del vecino con esa IP según la tabla ARP del equipo."""
    try:
        with open("/proc/net/arp") as f:
            for linea in list(f)[1:]:
                campos = linea.split()
                if campos[0] == ip and campos[3] != "00:00:00:00:00:00":
                    return campos[3], campos[5]
    except OSError:
        pass
    return None, None


def leer_interfaz(interfaz, dato):
    try:
        with open(f"/sys/class/net/{interfaz}/{dato}") as f:
            return f.read().strip()
    except OSError:
        return "no disponible"


def esquema():
    # nginx informa del esquema original en X-Forwarded-Proto
    return request.headers.get("X-Forwarded-Proto", "http")


def pagina(plantilla, **ctx):
    contenido = render_template_string(plantilla, esquema=esquema(), **ctx)
    return render_template_string(BASE, esquema=esquema(), contenido=contenido)


@app.get("/")
def index():
    return pagina(FORM)


@app.post("/login")
def login():
    return pagina(RESULTADO, usuario=request.form.get("usuario", ""),
                  password=request.form.get("password", ""))


@app.get("/capas")
def capas():
    ip = request.headers.get("X-Real-IP", request.remote_addr)
    puerto = request.headers.get("X-Real-Port", request.environ.get("REMOTE_PORT", "ver en Wireshark"))
    destino = request.headers.get("X-Forwarded-Port", request.host.partition(":")[2] or "80")
    local = ip.startswith("127.") or ip == "::1"
    mac_alumno, interfaz = (None, "lo") if local else buscar_arp(ip)
    return pagina(CAPAS, ip=ip, puerto=puerto, puerto_destino=destino,
                  mac_alumno=mac_alumno, interfaz=interfaz or "",
                  local=local,
                  mac=leer_interfaz(interfaz, "address") if interfaz else "no disponible",
                  mtu=leer_interfaz(interfaz, "mtu") if interfaz else "no disponible",
                  ua=request.headers.get("User-Agent", ""))


@app.get("/help")
def ayuda():
    return pagina(AYUDA)
