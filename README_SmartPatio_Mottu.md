
# 🚦 SmartPatio IoT - Mottu Challenge

Este repositório contém o firmware e documentação do **SmartPatio**, um sistema IoT para monitoramento e sinalização de motocicletas em pátios, desenvolvido para o Mottu Challenge (FIAP, Maio/2025).

---

## 📌 Visão Geral

O projeto visa otimizar a localização de motocicletas nos pátios da empresa Mottu, utilizando ESP32, sinalização visual (NeoPixel) e sonora (buzzer), comunicação via MQTT e integração com aplicativo mobile.

---

## 🧰 Tecnologias Utilizadas

- **ESP32**: Microcontrolador com Wi-Fi.
- **MQTT (HiveMQ Cloud ou outro broker)**: Protocolo leve de mensagens.
- **Adafruit NeoPixel**: LED RGB endereçável.
- **Buzzer**: Sinalização sonora.
- **PlatformIO/Arduino**: Ambiente de desenvolvimento.
- **Wokwi**: Simulador de hardware.
- **MQTT Explorer**: Monitoramento e envio de comandos MQTT.

---

## ⚙️ Funcionalidades

- Conexão automática à rede Wi-Fi e broker MQTT.
- Recebimento de comandos MQTT (`ACTIVATE`, `DEACTIVATE`, `RESET`).
- Sinalização visual: NeoPixel pisca alternando entre verde, vermelho e azul ao ativar.
- Sinalização sonora: Buzzer ativo ao receber comando de ativação.
- Publicação de status no tópico MQTT.
- Reconexão automática em caso de perda de conexão.
- Feedback visual de status de conexão (cores do NeoPixel).
- (Opcional) Integração futura com triangulação Wi-Fi para rastreamento.

---

## 📡 Triangulação de Sinal (Conceito Teórico)

Para aumentar a precisão na localização das motocicletas em pátios maiores, propõe-se uma camada adicional de rastreamento com triangulação baseada na intensidade do sinal Wi-Fi (RSSI) entre múltiplos pontos de escuta (ESP32).

### 📍 Como funciona:
- Múltiplos dispositivos ESP32 ficam fixos no pátio e atuam como “beacons passivos”.
- Cada moto emite pacotes periódicos contendo seu ID único.
- Os pontos fixos registram a intensidade do sinal (RSSI) desses pacotes.
- A média ponderada da intensidade dos sinais recebidos por cada ponto é usada para estimar a zona aproximada da moto.

> ⚠️ Esta funcionalidade é teórica nesta versão do projeto e poderá ser implementada futuramente via banco de dados e backend de mapeamento.

---

## 📁 Estrutura do Projeto

```
smartPatio/
├── src/
│   └── main.cpp          # Código-fonte principal do firmware
├── platformio.ini        # Configuração do PlatformIO
├── wokwi.toml            # Configuração para simulação Wokwi
└── README.md             # Este documento
```

---

## 🚀 Como Utilizar

1. **Configurar Wi-Fi e MQTT**
   - Edite as variáveis `WIFI_SSID`, `WIFI_PASSWORD`, `MQTT_BROKER`, `MQTT_PORT` em `src/main.cpp` conforme sua rede e broker.

2. **Compilar e enviar para o ESP32**
   - Use o PlatformIO no VS Code:
     ```
     pio run --target upload
     ```

3. **Simular no Wokwi**
   - Ajuste o caminho do firmware no `wokwi.toml` conforme sua pasta de build.
   - Compile o projeto e inicie a simulação no Wokwi.

4. **Monitorar e controlar via MQTT**
   - Use o MQTT Explorer para conectar ao broker.
   - Publique comandos no tópico `smartpatio/commands`:
     - `ACTIVATE` — Ativa sinalização visual e sonora.
     - `DEACTIVATE` — Desativa sinalização.
     - `RESET` — Reinicia o dispositivo.
   - Veja os status publicados em `smartpatio/status`.

---

## 📊 Resultados Esperados

- Redução do tempo de localização de motocicletas.
- Melhoria na eficiência operacional do pátio.
- Facilidade de integração com sistemas mobile e web.
- Expansão futura com localização por zonas via triangulação.

---

## 👥 Equipe

- **Laura de Oliveira Cintra** - RM 558843
- **Maria Eduarda Alves da Paixão** - RM 558832
- **Vinicius Saes de Souza** - RM 554456

---
