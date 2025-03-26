#include <WiFi.h>
#include <WebServer.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ESP32Servo.h>

// Ensure the ESP32Servo library is included correctly


// Configuración del servomotor
Servo servo;
const int servoPin = 15;
const int closedAngle = 55;
const int openAngle = 90;

// Configuración WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// Configuración NTP
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// Horarios predeterminados
String schedules[3][2] = {
  {"morning", "08:00"},
  {"afternoon", "14:00"},
  {"evening", "20:00"}
};

WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // Inicializar servo
  servo.attach(servoPin);
  closeServo();

  // Check if the servo is attached correctly

  
  // Conectar WiFi
  connectToWiFi();
  
  // Inicializar NTP
  timeClient.begin();
  timeClient.setTimeOffset(0);
  
  // Configurar endpoints del servidor web
  server.on("/", handleRoot);
  server.on("/dispense", handleDispense);
  server.on("/update_times", HTTP_POST, handleUpdateTimes);
  server.on("/get_times", handleGetTimes);
  
  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  server.handleClient();
  
  // Verificar horarios cada minuto
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck >= 60000) {
    lastCheck = millis();
    checkFeedingTime();
  }
}

void connectToWiFi() {
  Serial.print("Conectando a ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 10) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi conectado");
    Serial.println("Dirección IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Error al conectar WiFi");
  }
}

void moveServo(int angle) {
  int pulseWidth = map(angle, 0, 180, 500, 2500);
  servo.writeMicroseconds(pulseWidth);
  delay(1000);
}

void openServo() {
  moveServo(openAngle);
  delay(3000);
  moveServo(closedAngle);
}

void closeServo() {
  moveServo(closedAngle);
}

void checkFeedingTime() {
  timeClient.update();
  
  String currentTime = timeClient.getFormattedTime().substring(0, 5); // HH:MM
  Serial.println("Hora actual: " + currentTime);
  
  for (int i = 0; i < 3; i++) {
    if (currentTime == schedules[i][1]) {
      Serial.println("¡Es hora de alimentar! (" + currentTime + ")");
      openServo();
      break;
    }
  }
}

// Handlers del servidor web
void handleRoot() {
  server.send(200, "text/plain", "Bienvenido al dispensador de comida");
}

void handleDispense() {
  openServo();
  server.send(200, "text/plain", "Comida dispensada");
}

void handleUpdateTimes() {
  if (server.method() == HTTP_POST) {
    String body = server.arg("plain");
    
    // Parsear el JSON (simplificado)
    // Nota: En producción usa una librería como ArduinoJson
    for (int i = 0; i < 3; i++) {
      int pos = body.indexOf(schedules[i][0]);
      if (pos != -1) {
        int timeStart = body.indexOf("\"", pos + schedules[i][0].length() + 3) + 1;
        int timeEnd = body.indexOf("\"", timeStart);
        schedules[i][1] = body.substring(timeStart, timeEnd);
      }
    }
    
    server.send(200, "text/plain", "Horarios actualizados");
  } else {
    server.send(405, "text/plain", "Método no permitido");
  }
}

void handleGetTimes() {
  String response = "{";
  for (int i = 0; i < 3; i++) {
    response += "\"" + schedules[i][0] + "\":\"" + schedules[i][1] + "\"";
    if (i < 2) response += ",";
  }
  response += "}";
  
  server.send(200, "application/json", response);
}
