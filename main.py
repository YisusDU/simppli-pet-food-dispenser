import network
import socket
import time
from machine import Pin, PWM
import ntptime

# Configuración del servomotor
servo_pin = Pin(15, Pin.OUT)
servo = PWM(servo_pin, freq=50)

# Conectar a la red Wi-Fi
ssid = 'Wokwi-GUEST' #Modificar con el SSID de la red Real
password = '' #añadir la contraseña real
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    print("Conectando a Wi-Fi...")
    time.sleep(1)

print('Conectado a la red Wi-Fi:', wlan.ifconfig())

# Obtener y mostrar la dirección IP
ip_address = wlan.ifconfig()[0]
print('Conectado a la red Wi-Fi. Dirección IP:', ip_address)

# Configurar el servidor
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Escuchando en', addr)

# Función para mover el servomotor
def mover_servomotor(angulo):
    duty = int(40 + (angulo / 180) * 115)
    servo.duty(duty)
    time.sleep(1)

def abrir_servomotor():
    mover_servomotor(90)  # Abrir servomotor
    time.sleep(3)         # Mantener abierto por 3 segundos
    mover_servomotor(55)   # Cerrar servomotor

# Función para obtener la hora actual o simulada
def obtener_hora():
    try:
        # Sincronizar la hora con un servidor NTP
        ntptime.settime()
        # Obtener la hora actual
        hora_actual = time.localtime()
        print(f"Hora actual (NTP): {hora_actual[3]:02d}:{hora_actual[4]:02d}:{hora_actual[5]:02d}")
        return hora_actual
    except Exception as e:
        print("Error al sincronizar la hora con NTP:", e)
        # Usar una hora simulada si NTP falla
        hora_simulada = (2023, 10, 1, 12, 0, 0, 0, 0)  # Año, mes, día, hora, minuto, segundo, día de la semana, día del año
        print(f"Hora simulada: {hora_simulada[3]:02d}:{hora_simulada[4]:02d}:{hora_simulada[5]:02d}")
        return hora_simulada

# Horarios predeterminados
horarios = {
    "morning": "08:00",
    "afternoon": "14:00",
    "evening": "20:00"
}

# Función para verificar si es hora de dispensar comida
def verificar_horario(hora_actual):
    hora_actual_str = f"{hora_actual[3]:02d}:{hora_actual[4]:02d}"  # Formato HH:MM
    for horario in horarios.values():
        if hora_actual_str == horario:
            print(f"¡Es hora de dispensar comida! ({hora_actual_str})")
            abrir_servomotor()
            print("Hora de cerrar el dispensador")
            break

# Bucle principal
while True:
    # Obtener la hora actual o simulada
    hora_actual = obtener_hora()

    # Verificar si es hora de dispensar comida
    verificar_horario(hora_actual)

    # Manejar solicitudes HTTP
    cl, addr = s.accept()
    print('Cliente conectado desde', addr)
    request = cl.recv(1024)
    request = str(request)
    print('Solicitud recibida:', request)

    if '/dispense' in request:
        abrir_servomotor()
        response = 'Comida dispensada'
    elif '/update_times' in request:
        # Procesar los horarios recibidos
        body = request.split('\r\n\r\n')[1]  # Extraer el cuerpo de la solicitud
        if body:
            nuevos_horarios = eval(body)  # Convertir el JSON a un diccionario
            horarios.update(nuevos_horarios)
            response = 'Horarios actualizados'
        else:
            response = 'Error: No se recibieron datos'
    elif '/get_times' in request:
        # Devolver los horarios actuales
        response = str(horarios)
    else:
        response = 'Solicitud no válida'

    cl.send('HTTP/1.1 200 OK\n')
    cl.send('Content-Type: text/plain\n')
    cl.send('Connection: close\n\n')
    cl.send(response)
    cl.close()

    # Esperar un minuto antes de verificar la hora nuevamente
    time.sleep(60)