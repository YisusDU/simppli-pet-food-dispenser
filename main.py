import network
import socket
import time
from machine import Pin, PWM
import ntptime

# Configuración del servomotor
servo_pin = Pin(15, Pin.OUT)
servo = PWM(servo_pin, freq=50)  # Frecuencia de 50 Hz para servomotores

# Conectar a la red Wi-Fi
ssid = 'Wokwi-GUEST'  # Reemplaza con tu SSID
password = ''  # Reemplaza con tu contraseña
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Esperar a que se conecte
while not wlan.isconnected():
    print("Conectando a Wi-Fi...")
    time.sleep(1)

print('Conectado a la red Wi-Fi:', wlan.ifconfig())

# Configurar el servidor
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Escuchando en', addr)

# Función para mover el servomotor a un ángulo específico
def mover_servomotor(angulo):
    duty = int(40 + (angulo / 180) * 115)  # Convertir ángulo a duty cycle
    servo.duty(duty)
    time.sleep(1)  # Esperar a que el servomotor se mueva

# Función para abrir el servomotor
def abrir_servomotor():
    mover_servomotor(90)  # Mover a 90 grados (posición abierta)
    time.sleep(3)  # Mantenerlo abierto por 3 segundos
    mover_servomotor(0)  # Mover a 0 grados (posición cerrada)

# Configuración de NTP
use_ntp = False  # Cambia a True si quieres usar NTP
if use_ntp:
    try:
        ntptime.host = "pool.ntp.org"  # Servidor NTP alternativo
        ntptime.settime()
    except Exception as e:
        print("Error al sincronizar la hora:", e)
        print("Usando hora predeterminada (12:00:00).")
        # Establecer una hora manualmente
        manual_time = (2023, 10, 1, 12, 0, 0, 0, 0)  # Año, mes, día, hora, minuto, segundo, día de la semana, día del año
        timestamp = time.mktime(manual_time)
        time.localtime(timestamp)
else:
    print("Usando hora simulada.")
    # Establecer una hora manualmente
    manual_time = (2023, 10, 1, 12, 0, 0, 0, 0)  # Año, mes, día, hora, minuto, segundo, día de la semana, día del año
    timestamp = time.mktime(manual_time)
    time.localtime(timestamp)

# Bucle principal
while True:
    # Obtener la hora actual
    current_time = time.localtime()
    print("Hora actual:", current_time)

    # Validar la hora para dispensar comida
    hour = current_time[3]  # Hora actual
    minute = current_time[4]  # Minuto actual

    # Horarios programados (hora, minuto)
    horarios = [
        (0, 0),   # 8:00 AM
        (14, 0),  # 2:00 PM
        (22, 42)   # 8:00 PM
    ]

    # Verificar si la hora actual coincide con algún horario programado
    for horario in horarios:
        if (hour, minute) == horario:
            print(f"Hora de dispensar comida a las {horario[0]:02d}:{horario[1]:02d}")
            abrir_servomotor()
            print("Cerrar servomotor")
            break  # Evitar dispensar múltiples veces si hay coincidencias

    # Manejar solicitudes HTTP
    cl, addr = s.accept()
    print('Cliente conectado desde', addr)
    request = cl.recv(1024)
    request = str(request)
    print('Solicitud recibida:', request)

    # Responder a la solicitud
    if '/dispense' in request:
        abrir_servomotor()
        response = 'Comida dispensada'
    else:
        response = 'Solicitud no válida'

    cl.send('HTTP/1.1 200 OK\n')
    cl.send('Content-Type: text/plain\n')
    cl.send('Connection: close\n\n')
    cl.send(response)
    cl.close()

    # Esperar un minuto antes de verificar la hora nuevamente
    time.sleep(60)