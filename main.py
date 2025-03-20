# Importar las bibliotecas necesarias
import network
import socket
import time
from machine import Pin
import ntptime

# Configuración del servomotor
servo = Pin(15, Pin.OUT)  # Cambia el número de pin según tu conexión

# Conectar a la red Wi-Fi
ssid = 'Wokwi-GUEST'  # Reemplaza con tu SSID
password = ''  # Reemplaza con tu contraseña
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Esperar a que se conecte
while not wlan.isconnected():
    time.sleep(1)

print('Conectado a la red Wi-Fi:', wlan.ifconfig())

# Configurar el servidor
addr = socket.getaddrinfo('0.0.0.0', 80)[0]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Escuchando en', addr)

# Función para abrir el servomotor
def abrir_servomotor():
    servo.on()  # Activar el servomotor
    time.sleep(3)  # Mantenerlo abierto por 3 segundos
    servo.off()  # Cerrar el servomotor

# Bucle principal
while True:
    # Obtener la hora actual
    try:
        ntptime.settime()  # Sincronizar la hora
    except Exception as e:
        print("Error al sincronizar la hora:", e)
        continue  # Saltar al siguiente ciclo si hay un error

    current_time = time.localtime()  # Obtener la hora actual
    try:
        hour = current_time[3]  # Obtener la hora
    except IndexError:
        print("Error al obtener la hora actual.")
        continue  # Saltar al siguiente ciclo si hay un error


    # Validar la hora para dispensar comida
    if hour == 8:  # Hora de la mañana
        abrir_servomotor()
    elif hour == 14:  # Hora de la tarde
        abrir_servomotor()
    elif hour == 20:  # Hora de la noche
        abrir_servomotor()

    # Manejar solicitudes HTTP
    cl, addr = s.accept()
    print('Cliente conectado desde', addr)
    request = cl.recv(1024)
    cl.close()
