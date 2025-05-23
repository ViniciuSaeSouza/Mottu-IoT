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

/* --- Identificação do Dispositivo --- */
const char* GROUP_ID = "SmartPatio";
const char* DEVICE_ID = "PATIO_001";

/* --- Configurações de Rede Wi-Fi --- */
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

/* --- Configurações do Servidor MQTT --- */
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_USER = "";
const char* MQTT_PASSWORD = "";

/* --- Tópicos MQTT --- */
const char* TOPIC_SUBSCRIBE = "smartpatio/commands";
const char* TOPIC_PUBLISH = "smartpatio/status";

/* --- Definições de Hardware --- */
#define BUZZER_PIN 4
#define NEOPIXEL_PIN 2

/* --- Variáveis de Estado --- */
bool deviceActive = false;

// Variáveis para controle do piscar do NeoPixel
unsigned long lastBlinkTime = 0;
int blinkState = 0;
bool blinking = false;

Adafruit_NeoPixel neoPixel(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== Sistema Smart Patio ===");
  Serial.println("Iniciando...");

  pinMode(BUZZER_PIN, OUTPUT); // Inicializa pino do buzzer
  neoPixel.begin();            // Inicializa NeoPixel
  neoPixel.show();
  Serial.println("- Hardware configurado");

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
  tone(BUZZER_PIN, 2000); // Ativa buzzer só uma vez
}

void deactivateDevice() {
  Serial.println("\n[DISPOSITIVO] Desativando sistema...");
  publishStatus("DEVICE_DEACTIVATED");

  blinking = false; // Para o piscar do NeoPixel
  noTone(BUZZER_PIN); // Desativa buzzer só uma vez
  neoPixel.setPixelColor(0, neoPixel.Color(0, 255, 0)); // Verde indica inativo
  neoPixel.show();
}

void publishStatus(const char* status) {
  String message = String(GROUP_ID) + "|" + String(DEVICE_ID) + "|" + status;
  Serial.print("[STATUS] Publicando: ");
  Serial.println(message);

  mqttClient.publish(TOPIC_PUBLISH, message.c_str());
}