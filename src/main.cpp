#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>

/* --- Protótipos de Funções --- */
void connectWiFi();
void connectMQTT();
void reconnectMQTT();
void handleMQTTMessage(char* topic, byte* payload, unsigned int length);
void activateDevice();
void deactivateDevice();
void publishStatus(const char* status);
void publishTelemetry();

/* --- Identificação do Dispositivo --- */
const char* GROUP_ID = "SmartPatio";
#ifndef DEVICE_ID_STR
#define DEVICE_ID_STR TESTE
#endif
#define STR_HELPER(x) #x
#define STR(x) STR_HELPER(x)
static const char* DEVICE_ID = STR(DEVICE_ID_STR);

/* --- Configurações de Rede Wi-Fi --- */
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

/* --- Configurações do Servidor MQTT --- */
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "";
const char* MQTT_PASSWORD = "";

/* --- Tópicos MQTT --- */
char TOPIC_SUBSCRIBE[64];
char TOPIC_PUBLISH[64];
char TOPIC_TELEMETRY[64];

/* --- Definições de Hardware --- */
#define BUZZER_PIN 4
#define NEOPIXEL_PIN 2

/* --- Variáveis de Estado --- */
bool deviceActive = false;

// Variáveis para controle do piscar do NeoPixel
unsigned long lastBlinkTime = 0;
int blinkState = 0;
bool blinking = false;

// Musical tone variables
unsigned long lastToneTime = 0;
int toneIndex = 0;
bool shouldPlayTone = false;

// Telemetria
unsigned long lastTelemetryPublish = 0;

// Musical notes (frequencies in Hz) - Pop-style melody
int melody[] = {659, 698, 784, 659, 523, 587, 659, 523}; // E5, F5, G5, E5, C5, D5, E5, C5 (pop-style melody)
int melodyLength = 8;

// PWM settings for volume control
const int PWM_CHANNEL = 0;
const int PWM_RESOLUTION = 8;
int volumeLevel = 50; // Volume level (0-255, where 255 is max volume)

Adafruit_NeoPixel neoPixel(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Sistema Smart Patio ===");
  Serial.println("Iniciando...");

  pinMode(BUZZER_PIN, OUTPUT); // Inicializa pino do buzzer
  
  // Configure PWM for buzzer volume control
  ledcSetup(PWM_CHANNEL, 1000, PWM_RESOLUTION); // 1000Hz base frequency
  ledcAttachPin(BUZZER_PIN, PWM_CHANNEL);
  
  neoPixel.begin();            // Inicializa NeoPixel
  neoPixel.show();
  Serial.println("- Hardware configurado");

  // Concatena tópico de inscrição com ID do dispositivo
  snprintf(TOPIC_SUBSCRIBE, sizeof(TOPIC_SUBSCRIBE), "smartpatio/commands/%s", DEVICE_ID);
  snprintf(TOPIC_PUBLISH, sizeof(TOPIC_PUBLISH), "smartpatio/status/%s", DEVICE_ID);
  snprintf(TOPIC_TELEMETRY, sizeof(TOPIC_TELEMETRY), "smartpatio/telemetry/%s", DEVICE_ID);

  connectWiFi();   // Conecta ao Wi-Fi
  connectMQTT();   // Conecta ao MQTT
}

void loop() {
  if (!mqttClient.connected()) {
    reconnectMQTT(); // Tenta reconectar ao MQTT se desconectado
  }
  mqttClient.loop();

  // Pisca o NeoPixel se estiver em modo "blinking"
  if (blinking) {
    unsigned long now = millis();
    if (now - lastBlinkTime > 100) { // Troca de cor a cada 100ms
      lastBlinkTime = now;
      switch (blinkState) {
        case 0:
          neoPixel.setPixelColor(0, neoPixel.Color(0, 255, 0)); // Verde
          break;
        case 1:
          neoPixel.setPixelColor(0, neoPixel.Color(255, 0, 0)); // Vermelho
          break;
        case 2:
          neoPixel.setPixelColor(0, neoPixel.Color(0, 0, 255)); // Azul
          break;
      }
      neoPixel.show();
      blinkState = (blinkState + 1) % 3;
    }
  }
  
  // Play musical tone pattern
  if (shouldPlayTone) {
    unsigned long now = millis();
    if (now - lastToneTime > 400) { // Each note plays for 400ms
      lastToneTime = now;
      toneIndex = (toneIndex + 1) % melodyLength;
      
      // Use PWM for volume control instead of tone()
      ledcWriteTone(PWM_CHANNEL, melody[toneIndex]);
      ledcWrite(PWM_CHANNEL, volumeLevel); // Set volume level
    }
  }
  
  // Publica telemetria a cada 5 segundos
  unsigned long now = millis();
  if (now - lastTelemetryPublish > 5000) {
    publishTelemetry();
    lastTelemetryPublish = now;
  }
  
}

void connectWiFi() {
  Serial.println("\n[WiFi] Iniciando conexão...");
  Serial.print("SSID: ");
  Serial.println(WIFI_SSID);

  neoPixel.setPixelColor(0, neoPixel.Color(0, 0, 255)); // Azul: conectando
  neoPixel.show();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long connectionStart = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - connectionStart < 15000) {
    Serial.print(".");
    delay(100);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Conexão estabelecida!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi] Falha na conexão!");
    neoPixel.setPixelColor(0, neoPixel.Color(255, 0, 0)); // Vermelho: erro
    neoPixel.show();
    while(true);
  }
}

void connectMQTT() {
  Serial.println("\n[MQTT] Conectando ao broker...");
  Serial.print("Broker: ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.println(MQTT_PORT);

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(handleMQTTMessage);

  String clientId = "ESP32-" + String(DEVICE_ID);
  Serial.print("Client ID: ");
  Serial.println(clientId);

  unsigned long connectionStart = millis();

  while (!mqttClient.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)) {
    Serial.print("[MQTT] Tentativa de conexão falhou. Estado: ");
    Serial.println(mqttClient.state());

    neoPixel.setPixelColor(0, neoPixel.Color(255, 165, 0)); // Laranja: tentando
    neoPixel.show();

    if (millis() - connectionStart > 10000) break;
    delay(500);
  }

  if (mqttClient.connected()) {
    Serial.println("[MQTT] Conectado com sucesso!");
    mqttClient.subscribe(TOPIC_SUBSCRIBE);
    Serial.print("Inscrito no tópico: ");
    Serial.println(TOPIC_SUBSCRIBE);

    neoPixel.setPixelColor(0, neoPixel.Color(0, 255, 0)); // Verde: conectado
    neoPixel.show();
    publishStatus("CONNECTED");
  } else {
    Serial.println("[MQTT] Falha permanente na conexão!");
    neoPixel.setPixelColor(0, neoPixel.Color(255, 0, 0)); // Vermelho: erro
    neoPixel.show();
    while(true);
  }
}

void reconnectMQTT() {
  Serial.println("\n[MQTT] Conexão perdida! Reconectando...");
  neoPixel.setPixelColor(0, neoPixel.Color(255, 255, 0)); // Amarelo: reconectando
  neoPixel.show();
  connectMQTT();
}

void handleMQTTMessage(char* topic, byte* payload, unsigned int length) {
  Serial.println("\n[MQTT] Nova mensagem recebida");
  Serial.print("Tópico: ");
  Serial.println(topic);

  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';

  Serial.print("Conteúdo: ");
  Serial.println(message);

  // Processa comandos recebidos via MQTT
  if (strcmp(message, "ACTIVATE") == 0) {
    deviceActive = true;
    activateDevice();
  } else if (strcmp(message, "DEACTIVATE") == 0) {
    deviceActive = false;
    deactivateDevice();
  } else if (strcmp(message, "RESET") == 0) {
    publishStatus("RESTARTING");
    delay(100);
    ESP.restart();
  }
}

void activateDevice() {
  Serial.println("\n[DISPOSITIVO] Ativando sistema...");
  publishStatus("DEVICE_ACTIVE");

  blinking = true; // Inicia o piscar do NeoPixel
  blinkState = 0;
  lastBlinkTime = millis();
  
  // Start musical tone pattern
  shouldPlayTone = true;
  toneIndex = 0;
  lastToneTime = millis();
  
  // Use PWM for volume control
  ledcWriteTone(PWM_CHANNEL, melody[0]);
  ledcWrite(PWM_CHANNEL, volumeLevel); // Set volume level
}

void deactivateDevice() {
  Serial.println("\n[DISPOSITIVO] Desativando sistema...");
  publishStatus("DEVICE_DEACTIVATED");

  blinking = false; // Para o piscar do NeoPixel
  shouldPlayTone = false; // Stop musical tone
  ledcWrite(PWM_CHANNEL, 0); // Turn off PWM (volume = 0)
  neoPixel.setPixelColor(0, neoPixel.Color(0, 255, 0)); // Verde indica inativo
  neoPixel.show();
}

void publishStatus(const char* status) {
  String message = String(GROUP_ID) + "|" + String(DEVICE_ID) + "|" + status;
  Serial.print("[STATUS] Publicando: ");
  Serial.println(message);

  mqttClient.publish(TOPIC_PUBLISH, message.c_str());
}

void publishTelemetry() {
  if (mqttClient.connected()) {
    // Cria JSON com dados de telemetria
    String telemetry = "{";
    telemetry += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
    telemetry += "\"timestamp\":" + String(millis()) + ",";
    telemetry += "\"device_active\":" + String(deviceActive ? "true" : "false") + ",";
    telemetry += "\"led_blinking\":" + String(blinking ? "true" : "false") + ",";
    telemetry += "\"buzzer_active\":" + String(shouldPlayTone ? "true" : "false") + ",";
    telemetry += "\"wifi_rssi\":" + String(WiFi.RSSI());
    telemetry += "}";
    
    Serial.print("[TELEMETRIA] Publicando: ");
    Serial.println(telemetry);
    
    mqttClient.publish(TOPIC_TELEMETRY, telemetry.c_str());
  }
}