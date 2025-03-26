#include <WiFi.h>
#include <WebServer.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

// Configuración fija para Wokwi
#define WOKWI_IP "10.10.0.2"  // IP del servidor web en Wokwi
#define WOKWI_SSID "Wokwi-GUEST"

// Configuración del servo
ESP32Servo myservo;
const int servoPin = 15;
const int closedPos = 55;    // Posición cerrado
const int openPos = 90;      // Posición abierto

// Configuración de tiempo
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -21600); // Offset -6h para Centroamérica

// Configuración del servidor web
WebServer server(80);

// Estructura de horarios
struct Schedule {
  const char* periodo;
  String hora;
};
Schedule horarios[3] = {
  {"morning", "08:00"},
  {"afternoon", "14:00"},
  {"evening", "20:00"}
};

void setup() {
  Serial.begin(115200);
  
  // Inicializar servo
  ESP32PWM::allocateTimer(0);
  myservo.setPeriodHertz(50);
  myservo.attach(servoPin, 500, 2500);
  cerrarServo();

  // Conectar a WiFi
  conectarWiFi();
  
  // Configurar NTP
  timeClient.begin();
  timeClient.setUpdateInterval(60000);  // Actualizar cada minuto

  // Configurar endpoints del servidor web
  server.on("/", manejarRaiz);
  server.on("/dispensar", HTTP_POST, manejarDispensar);
  server.on("/actualizar", HTTP_POST, manejarActualizar);
  server.on("/horarios", HTTP_GET, manejarHorarios);
  
  server.begin();
  Serial.println("Servidor web iniciado");
}

void loop() {
  server.handleClient();
  verificarHora();
  delay(100); // Reducir carga de CPU
}

//*********************
// Funciones principales
//*********************

void conectarWiFi() {
  Serial.print("Conectando a ");
  Serial.println(WOKWI_SSID);
  
  WiFi.begin(WOKWI_SSID, "", 6);  // Canal 6 para mejor rendimiento
  
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 15) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConectado! IP: " + WiFi.localIP().toString());
    timeClient.forceUpdate();  // Sincronizar hora inmediatamente
  } else {
    Serial.println("\nError de conexión WiFi");
  }
}

void verificarHora() {
  static unsigned long ultimaVerificacion = 0;
  if (millis() - ultimaVerificacion >= 60000) {
    ultimaVerificacion = millis();
    
    timeClient.update();
    String horaActual = timeClient.getFormattedTime().substring(0, 5);
    
    Serial.print("Hora actual: ");
    Serial.println(horaActual);

    for (auto &horario : horarios) {
      if (horaActual == horario.hora) {
        dispensarComida();
        break;
      }
    }
  }
}

//*********************
// Control del servo
//*********************

void abrirServo() {
  myservo.write(openPos);
  delay(1000); // Tiempo para llegar a posición
}

void cerrarServo() {
  myservo.write(closedPos);
  delay(1000); // Tiempo para llegar a posición
}

void dispensarComida() {
  Serial.println("Dispensando comida...");
  abrirServo();
  delay(3000);  // Mantener abierto 3 segundos
  cerrarServo();
}

//*********************
// Manejo del servidor web
//*********************

void manejarRaiz() {
  server.send(200, "text/plain", "Sistema dispensador de comida activo");
}

void manejarDispensar() {
  dispensarComida();
  server.send(200, "application/json", "{\"estado\":\"comida dispensada\"}");
}

void manejarActualizar() {
  if (server.method() == HTTP_POST) {
    String cuerpo = server.arg("plain");
    actualizarHorarios(cuerpo);
    server.send(200, "application/json", "{\"estado\":\"horarios actualizados\"}");
  }
}

void manejarHorarios() {
  String respuesta = "{";
  for (int i = 0; i < 3; i++) {
    respuesta += "\"" + String(horarios[i].periodo) + "\":\"" + horarios[i].hora + "\"";
    if (i < 2) respuesta += ",";
  }
  respuesta += "}";
  server.send(200, "application/json", respuesta);
}

//*********************
// Funciones auxiliares
//*********************

void actualizarHorarios(String json) {
  for (int i = 0; i < 3; i++) {
    int indice = json.indexOf(horarios[i].periodo);
    if (indice != -1) {
      int inicioHora = json.indexOf(":", indice) + 2;
      int finHora = json.indexOf("\"", inicioHora);
      horarios[i].hora = json.substring(inicioHora, finHora);
    }
  }
  Serial.println("Horarios actualizados:");
  for (auto &h : horarios) {
    Serial.printf("%s: %s\n", h.periodo, h.hora.c_str());
  }
}