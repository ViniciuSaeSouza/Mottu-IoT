# 🚦 SmartPatio IoT - Sprint 3 - Mottu Challenge

Sistema IoT para monitoramento e sinalização de motocicletas em pátios, desenvolvido para atender aos requisitos da Sprint 3 (FIAP, Outubro/2025).

## 📌 Resumo da Implementação

✅ **IoT com 2 atuadores distintos**: LED NeoPixel e Buzzer  
✅ **Comunicação MQTT em tempo real**: Via broker público HiveMQ  
✅ **Dashboard web**: Interface simples com dados em tempo real  
✅ **Persistência de dados**: Sistema de logs CSV automático  
✅ **Teste funcional**: Scripts de demonstração e validação  

---

## 🏗️ Arquitetura do Sistema

```
ESP32 (SmartPatio)
├── 💡 LED NeoPixel (sinalização visual)
├── 🔊 Buzzer (sinalização sonora)
├── 📡 WiFi + MQTT (comunicação)
└── 📊 Telemetria (status em tempo real)
    ↓
🌐 Broker MQTT (broker.hivemq.com)
    ↓
├── 🖥️ Dashboard Web (visualização)
├── 💾 Data Logger (persistência)
└── 🧪 Scripts de Teste (demonstração)
```

---

## 🚀 Configuração Rápida

### 1. Hardware/Simulação
- **Opção A**: Use o simulador [Wokwi](https://wokwi.com/) com o código `src/main.cpp`
- **Opção B**: ESP32 real com LED NeoPixel (pino 2) e Buzzer (pino 4)

### 2. Software
```bash
# Instalar dependências Python
./install.sh        # Linux/Mac
install.bat         # Windows

# Ou manualmente:
pip install paho-mqtt matplotlib pandas numpy
```

### 3. Execução
```bash
# 1. Subir o ESP32/Wokwi com src/main.cpp
# 2. Teste interativo
python demo.py

# 3. Demonstração automática
python demo.py auto

# 4. Data logger (opcional)
python data_logger.py

# 5. Abrir dashboard/index.html no navegador
```

---

## 🧪 Demonstração Funcional

### Cenário de Teste
1. **Dispositivo inativo**: LED verde fixo, buzzer desligado
2. **Comando ACTIVATE**: LED pisca (verde/vermelho/azul) + buzzer toca melodia
3. **Comando DEACTIVATE**: Volta ao estado inativo
4. **Telemetria**: Dados enviados a cada 5 segundos via MQTT

### Scripts de Teste
- `demo.py` - Interface interativa para envio de comandos
- `data_logger.py` - Coleta e armazena dados em CSV
- `dashboard/index.html` - Visualização web em tempo real

---

## 📊 Dados e Métricas

### Telemetria Coletada
```json
{
  "device_id": "TESTE",
  "timestamp": 1696175431000,
  "device_active": true,
  "led_blinking": true,
  "buzzer_active": true,
  "wifi_rssi": -45
}
```

### Persistência
- **Formato**: CSV com timestamp, tópico, dados JSON
- **Localização**: `smartpatio_data.csv`
- **Frequência**: Todos os eventos MQTT são registrados

---

## 📡 Comunicação MQTT

### Tópicos
```
smartpatio/commands/TESTE   → Comandos (ACTIVATE/DEACTIVATE/RESET)
smartpatio/status/TESTE     → Status do dispositivo
smartpatio/telemetry/TESTE  → Dados de telemetria JSON
```

### Broker
- **Host**: broker.hivemq.com
- **Porta**: 1883 (público, sem autenticação)
- **Protocolo**: MQTT v3.1.1

---

## 🎯 Atendimento aos Requisitos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| **3 sensores/atuadores** | ✅ | LED NeoPixel + Buzzer + WiFi RSSI |
| **Comunicação MQTT** | ✅ | Tempo real via HiveMQ |
| **Dashboard simples** | ✅ | HTML5 + JavaScript + Chart.js |
| **Persistência dados** | ✅ | CSV automático via Python |
| **Teste funcional** | ✅ | Scripts demo + logs automáticos |

---

## 📁 Estrutura do Projeto

```
smartPatio/
├── src/
│   └── main.cpp              # Firmware ESP32
├── dashboard/
│   └── index.html            # Dashboard web
├── demo.py                   # Script de teste interativo
├── data_logger.py            # Sistema de persistência
├── requirements.txt          # Dependências Python
├── install.bat / install.sh  # Scripts de instalação
└── README.md                 # Esta documentação
```

---

## 🔧 Tecnologias Utilizadas

- **Hardware**: ESP32, LED NeoPixel, Buzzer
- **Firmware**: Arduino/PlatformIO, WiFi, MQTT
- **Backend**: Python, paho-mqtt, pandas
- **Frontend**: HTML5, JavaScript, Chart.js
- **Comunicação**: MQTT (HiveMQ Cloud)
- **Dados**: CSV, JSON

---

## 📈 Resultados Esperados

### Performance
- **Latência MQTT**: < 500ms (rede local)
- **Frequência telemetria**: 5 segundos
- **Disponibilidade**: 99%+ (dependente da rede)

### Funcionalidades
- ✅ Ativação/desativação remota
- ✅ Feedback visual (LED colorido)
- ✅ Feedback sonoro (melodia)
- ✅ Monitoramento em tempo real
- ✅ Histórico persistente
- ✅ Dashboard responsivo

---

## 🎥 Demonstração

O sistema funciona com:
1. **ESP32/Wokwi** executando o firmware
2. **Dashboard** mostrando dados em tempo real
3. **Scripts Python** para controle e logging
4. **Comunicação MQTT** conectando tudo

**Resultado**: Sistema IoT funcional demonstrando integração completa entre hardware, comunicação e interface web.

---

## 👥 Equipe

- **Laura de Oliveira Cintra** - RM 558843
- **Maria Eduarda Alves da Paixão** - RM 558832
- **Vinicius Saes de Souza** - RM 554456

---
